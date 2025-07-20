"""
Screen capture and OCR functionality for detecting available letters.
Supports both OCR text recognition and window-specific capture.
"""
import re
import time
from typing import List, Optional, Tuple, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from PIL.Image import Image

try:
    import cv2
    import numpy as np
    import pyautogui
    import pytesseract
    from PIL import Image, ImageEnhance
    SCREEN_DEPS_AVAILABLE = True
except ImportError:
    SCREEN_DEPS_AVAILABLE = False
    Image = None
    ImageEnhance = None


class ScreenCapture:
    """Handle screen capture and letter detection."""
    
    def __init__(self):
        """Initialize screen capture with dependency check."""
        if not SCREEN_DEPS_AVAILABLE:
            raise ImportError(
                "Screen capture dependencies not installed. "
                "Install with: pip install -e .[screen]"
            )
        
        # Disable pyautogui failsafe for smoother operation
        pyautogui.FAILSAFE = False
        
        # Common letter patterns for different games
        self.letter_patterns = {
            'scrabble': r'[A-Z]',
            'wordle': r'[A-Z]',
            'generic': r'[A-Za-z]'
        }
    
    def capture_screen_region(self, 
                            x: int = None, 
                            y: int = None, 
                            width: int = None, 
                            height: int = None) -> 'Image':
        """
        Capture a specific region of the screen.
        
        Args:
            x, y: Top-left corner coordinates (None for full screen)
            width, height: Region dimensions (None for full screen)
            
        Returns:
            PIL Image of the captured region
        """
        if all(param is None for param in [x, y, width, height]):
            # Full screen capture
            screenshot = pyautogui.screenshot()
        else:
            # Region capture
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        return screenshot
    
    def capture_window_by_title(self, window_title: str, 
                               delay_mode: str = 'countdown',
                               delay_seconds: int = 0,
                               bring_to_front: bool = False,
                               crop_to_center: bool = True,
                               crop_width_percent: float = 0.5,
                               crop_height_percent: float = 0.75,
                               crop_vertical_start: float = 0.2) -> Optional['Image']:
        """
        Capture a specific window by its title with various timing options.
        
        Args:
            window_title: Partial or full window title to match
            delay_mode: 'countdown', 'manual', 'immediate', or 'background'
            delay_seconds: Seconds to wait (for countdown mode)
            bring_to_front: Whether to bring window to front before capture
            crop_to_center: Whether to crop to center region of window
            crop_width_percent: Width percentage to crop (0.5 = middle 50%)
            crop_height_percent: Height percentage to crop (0.7 = 70% height)
            crop_vertical_start: Vertical start position as percentage (0.2 = start at 20%)
            
        Returns:
            PIL Image of the window (cropped if requested) or None if not found
        """
        try:
            # Use pygetwindow to find the window
            import pygetwindow as gw
            
            # Get all window titles and find matches
            all_titles = gw.getAllTitles()
            matching_titles = [title for title in all_titles if window_title.lower() in title.lower()]
            
            if not matching_titles:
                return None
            
            # Use the first matching title to get the window
            target_title = matching_titles[0]
            
            # Get window geometry using the exact title
            try:
                geometry = gw.getWindowGeometry(target_title)
                window_left, window_top, window_width, window_height = geometry
                
                # Validate geometry - check if coordinates are reasonable
                if window_width <= 0 or window_height <= 0:
                    return None
                
                # Check if window is completely off-screen (basic validation)
                screen_width, screen_height = pyautogui.size()
                if (window_left + window_width < 0 or window_top + window_height < 0 or 
                    window_left > screen_width or window_top > screen_height):
                    pass  # Continue anyway
                    
            except Exception as e:
                return None
            
            # Handle different delay modes
            if delay_mode == 'countdown':
                for i in range(delay_seconds, 0, -1):
                    time.sleep(1)
                
            elif delay_mode == 'manual':
                input(f"Press Enter when ready to capture window '{window_title}'...")
                
            elif delay_mode == 'background':
                # Capture without bringing to front - just get the window bounds
                pass
                
            # Only bring to front if requested (not recommended for background capture)
            if bring_to_front and delay_mode != 'background':
                try:
                    gw.activate(target_title)
                    time.sleep(0.5)  # Give time for window to come to front
                except Exception as e:
                    print(f"Warning: Could not bring window to front: {e}")
            
            # Capture the window region using the geometry we got
            try:
                screenshot = pyautogui.screenshot(region=(
                    int(window_left), int(window_top), int(window_width), int(window_height)
))
                
                # Apply cropping if requested
                if crop_to_center:
                    original_width = screenshot.width
                    original_height = screenshot.height
                    
                    # Calculate crop dimensions
                    crop_width = int(original_width * crop_width_percent)
                    crop_height = int(original_height * crop_height_percent)
                    
                    # Calculate crop position (centered horizontally, positioned vertically)
                    crop_left = (original_width - crop_width) // 2
                    crop_top = int(original_height * crop_vertical_start)
                    crop_right = crop_left + crop_width
                    crop_bottom = crop_top + crop_height
                    
                    # Ensure crop boundaries are within image
                    crop_left = max(0, crop_left)
                    crop_top = max(0, crop_top)
                    crop_right = min(original_width, crop_right)
                    crop_bottom = min(original_height, crop_bottom)
                    
                    # Crop the image
                    screenshot = screenshot.crop((crop_left, crop_top, crop_right, crop_bottom))
                
                return screenshot
                
            except Exception as screenshot_error:
                # Fallback 1: Try capturing without region (full screen) and crop later
                try:
                    full_screenshot = pyautogui.screenshot()
                    # Crop to the window region if coordinates are valid
                    if (window_left >= 0 and window_top >= 0 and 
                        window_left + window_width <= full_screenshot.width and 
                        window_top + window_height <= full_screenshot.height):
                        
                        cropped = full_screenshot.crop((
                            int(window_left), int(window_top), 
                            int(window_left + window_width), int(window_top + window_height)
                        ))
                        return cropped
                    else:
                        return None
                        
                except Exception as fallback_error:
                    return None
            
        except Exception as e:
            return None
    
    def preprocess_image(self, image: 'Image') -> 'Image':
        """
        Preprocess image for better OCR results, focusing on black text only.
        
        Args:
            image: PIL Image to preprocess
            
        Returns:
            Preprocessed PIL Image with only black text preserved
        """
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert to numpy array for color filtering
        img_array = np.array(image)
        
        img_array = cv2.GaussianBlur(img_array, (5, 5), 6)
        
        # Create mask for black/dark text
        # Define what we consider "black" - adjust these thresholds as needed
        black_threshold = 30  # Pixels darker than this are considered black (more selective)
        
        # Calculate grayscale values
        gray_values = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        
        # Create mask for black text (dark pixels)
        black_mask = gray_values < black_threshold
        
        # Create binary image: black text on white background
        binary_image = np.ones_like(gray_values) * 255  # Start with white background
        binary_image[black_mask] = 0  # Set black text pixels to black

        # Convert to PIL Image
        result_image = Image.fromarray(binary_image.astype(np.uint8), mode='L')
        
        return result_image
    
    def extract_text_with_ocr(self, 
                             image: 'Image', 
                             preprocess: bool = True) -> str:
        """
        Extract text from image using OCR with improved filtering.
        
        Args:
            image: PIL Image to process
            preprocess: Whether to preprocess image for better OCR
            
        Returns:
            Extracted text string with filtered characters
        """
        if preprocess:
            image = self.preprocess_image(image)
        
        try:
            # Disable dictionaries and optimize for single letter recognition
            # The game text is individual letters, not real words
            config = '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ load_system_dawg=false load_freq_dawg=false'
            
            text = pytesseract.image_to_string(image, config=config)
    
            # Clean up the text - remove spaces, newlines, and non-alphabetic characters
            cleaned_text = ''.join(char.upper() for char in text if char.isalpha())

            return cleaned_text
            
        except Exception as e:
            return ""
    
    def find_letters_in_text(self, 
                           text: str, 
                           pattern_type: str = 'generic') -> List[str]:
        """
        Extract individual letters from OCR text.
        
        Args:
            text: Input text from OCR
            pattern_type: Type of letter pattern to use
            
        Returns:
            List of detected letters
        """
        pattern = self.letter_patterns.get(pattern_type, self.letter_patterns['generic'])
        letters = re.findall(pattern, text)
        return [letter.upper() for letter in letters]
    
    def detect_letters_from_screen(self, 
                                 window_title: Optional[str] = None,
                                 preprocess: bool = True,
                                 crop_to_center: bool = True,
                                 crop_width_percent: float = 0.26,
                                 crop_height_percent: float = 0.55,
                                 crop_vertical_start: float = 0.35) -> List[str]:
        """
        Main method to detect letters from screen.
        
        Args:
            window_title: Specific window to capture (None for full screen)
            preprocess: Whether to preprocess image for OCR
            crop_to_center: Whether to crop to center region of window
            crop_width_percent: Width percentage to crop (0.26 = middle 26%)
            crop_height_percent: Height percentage to crop (0.55 = 55% height)
            crop_vertical_start: Vertical start position as percentage (0.35 = start at 35%)
            
        Returns:
            List of detected letters
        """
        # Capture image
        if window_title:
            image = self.capture_window_by_title(window_title, 'background', 3, False,
                                               crop_to_center, crop_width_percent, crop_height_percent, crop_vertical_start)
            if image is None:
                return []
        else:
            image = self.capture_screen_region()
        
        # Extract text using OCR
        text = self.extract_text_with_ocr(image, preprocess)
        
        # Find letters in the text
        letters = self.find_letters_in_text(text, 'generic')
        
        return letters
    
    def save_debug_image(self, image: 'Image', filename: str = "debug_capture.png"):
        """Save captured image for debugging purposes."""
        debug_path = Path(filename)
        image.save(debug_path)
        print(f"Debug image saved to: {debug_path.absolute()}")
    
    def interactive_region_select(self) -> Tuple[int, int, int, int]:
        """
        Interactive region selection using mouse.
        
        Returns:
            Tuple of (x, y, width, height) for selected region
        """
        print("Click and drag to select the region containing letters...")
        print("Press ESC to cancel")
        
        try:
            # This is a simplified version - in practice you'd want a more sophisticated UI
            print("Move mouse to top-left corner and press Enter...")
            input("Press Enter when ready...")
            x1, y1 = pyautogui.position()
            
            print("Move mouse to bottom-right corner and press Enter...")
            input("Press Enter when ready...")
            x2, y2 = pyautogui.position()
            
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            print(f"Selected region: ({x}, {y}, {width}, {height})")
            return (x, y, width, height)
            
        except KeyboardInterrupt:
            print("Region selection cancelled")
            return (0, 0, 0, 0)


def list_available_windows() -> List[str]:
    """List all available window titles for selection."""
    if not SCREEN_DEPS_AVAILABLE:
        print("Screen capture dependencies not installed.")
        return []
    
    try:
        import pygetwindow as gw
        titles = gw.getAllTitles()
        # Filter out empty titles and system windows
        filtered_titles = [title for title in titles if title.strip() and not title.startswith('_')]
        return sorted(set(filtered_titles))  # Remove duplicates and sort

    except Exception as e:
        print(f"Error listing windows: {e}")
        return []

