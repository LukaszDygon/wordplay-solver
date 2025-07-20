#!/usr/bin/env python3
"""Command-line interface for Wordplay Solver."""
import argparse
import sys
from pathlib import Path

from wordplay_solver.solver import WordSolver
from collections import defaultdict

# Optional screen capture import
try:
    from wordplay_solver.screen_capture import ScreenCapture, list_available_windows
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    SCREEN_CAPTURE_AVAILABLE = False

def display_comprehensive_results(word_scores, current_window=None, screen_capture=None):
    """Display comprehensive word results with top 5 scoring words and top 5 for each letter count."""
    if not word_scores:
        print("\nNo valid words found with the given letters.\n")
        return
    
    # Display top 5 scoring words overall
    print("\n=== TOP 5 SCORING WORDS ===")
    top_5_scores = word_scores[:5]
    top_words = [f"{word.upper()}({score})" for word, score, length in top_5_scores]
    print(", ".join(top_words))
    
    # Group words by length
    words_by_length = defaultdict(list)
    for word, score, length in word_scores:
        if length >= 4:  # Only show 4+ letter words
            words_by_length[length].append((word, score, length))
    
    # Display top 5 words for each letter count (4+ letters)
    if words_by_length:
        print("\n=== TOP WORDS BY LENGTH (4+ LETTERS) ===")
        for length in sorted(words_by_length.keys()):
            words_for_length = words_by_length[length][:5]  # Top 5 for this length
            length_words = [f"{word.upper()}({score})" for word, score, _ in words_for_length]
            print(f"{length}: {', '.join(length_words)}")
    
    # Word selection and typing interface
    if current_window and screen_capture:
        print("\nSelect word to type (1-5 for top words, {length}.{order} for length-specific, Enter to skip):")
    else:
        print("\nSelect word (1-5 for top words, {length}.{order} for length-specific, Enter to skip):")
    
    try:
        selection = input("> ").strip()
        if selection:
            selected_word = parse_word_selection(selection, top_5_scores, words_by_length)
            if selected_word:
                if current_window and screen_capture:
                    type_word_in_game(selected_word, current_window)
                else:
                    print(f"Selected word: {selected_word}")
            else:
                print("Invalid selection.")
    except KeyboardInterrupt:
        print("\nSkipping word selection.")
    
    print()  # Extra newline for spacing

def parse_word_selection(selection, top_5_scores, words_by_length):
    """Parse user selection and return the selected word."""
    try:
        # Check if it's a simple number (1-5 for top scoring words)
        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(top_5_scores):
                word, score, length = top_5_scores[index]
                return word.upper()
            else:
                return None
        
        # Check if it's length.order format (e.g., "7.2" for 2nd best 7-letter word)
        elif '.' in selection:
            parts = selection.split('.')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                length = int(parts[0])
                order = int(parts[1]) - 1  # Convert to 0-based index
                
                if length in words_by_length and 0 <= order < len(words_by_length[length]):
                    word, score, _ = words_by_length[length][order]
                    return word.upper()
                else:
                    return None
        
        return None
    except (ValueError, IndexError):
        return None

def type_word_in_game(word, window_title):
    """Type the selected word in the game window."""
    try:
        import pyautogui
        import subprocess
        import time
        
        print(f"Typing '{word}' in game window...")
        
        # Activate the window using AppleScript (macOS-specific)
        try:
            # Simple approach: try to activate the application that contains the window
            # Extract likely app name from window title
            app_name = "Word Play"  # Default for the game
            if "Word Play" in window_title:
                app_name = "Word Play"
            elif "Windsurf" in window_title:
                app_name = "Windsurf"
            
            # Use simple AppleScript to activate the application
            applescript = f'tell application "{app_name}" to activate'
            
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True, timeout=3)
            
            if result.returncode != 0:
                # Fallback: try to click on the window using pyautogui
                print(f"AppleScript failed, trying fallback method...")
                # Just proceed without window activation - pyautogui will type to focused window
            
            time.sleep(0.5)  # Give time for window to come to front
            
        except subprocess.TimeoutExpired:
            print("Window activation timed out, proceeding anyway...")
        except Exception as e:
            print(f"Window activation failed: {e}, proceeding anyway...")
        
        # Type the word
        pyautogui.typewrite(word.lower(), interval=0.05)  # Small delay between keystrokes
        time.sleep(0.1)
        
        # Press Enter
        pyautogui.press('enter')
        time.sleep(1)
        
        # Long press backspace (hold for 1 second)
        pyautogui.keyDown('backspace')
        time.sleep(1.0)
        pyautogui.keyUp('backspace')
        
        print(f"Successfully typed '{word}'!")
        
    except ImportError:
        print("Typing functionality requires pyautogui and pygetwindow")
    except Exception as e:
        print(f"Error typing word: {e}")

def interactive_loop(solver, custom_values=None, screen_capture=None):
    """Run the solver in an interactive loop."""
    print("=== Wordplay Solver - Interactive Mode ===")
    print("Enter letters (e.g., 'letters' or 'a1b3c3' for custom values)")
    
    # Window selection for screen capture if available
    current_window = None
    if screen_capture:
        print("\nScreen capture available!")
        try:
            choice = input("Would you like to select a window for screen capture? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                windows = list_available_windows()
                if windows:
                    print("\nAvailable windows:")
                    for i, title in enumerate(windows, 1):
                        print(f"  {i}. {title}")
                    
                    try:
                        selection = input("\nSelect window number (or press Enter to skip): ").strip()
                        if selection:
                            idx = int(selection) - 1
                            if 0 <= idx < len(windows):
                                current_window = windows[idx]
                                print(f"Selected window: '{current_window}'")
                                print("Press Enter (empty input) to capture from this window")
                            else:
                                print("Invalid selection, continuing without window selection")
                    except ValueError:
                        print("Invalid input, continuing without window selection")
                else:
                    print("No windows available for selection")
        except KeyboardInterrupt:
            print("\nSkipping window selection")
    
    if current_window:
        print(f"\nWindow mode: '{current_window}' - Press Enter to capture")
    
    print("Type '/exit' or press Ctrl+C to quit\n")
    
    while True:
        try:
            # Get user input
            user_input = input("Enter letters: ").strip()
            
            # Check for exit command
            if user_input.lower() == '/exit':
                print("Goodbye!")
                break
                
            # Handle empty input for window capture
            if not user_input:
                if current_window and screen_capture:
                    detected_letters = screen_capture.detect_letters_from_screen(window_title=current_window)
                    if detected_letters:
                        letters = ''.join(detected_letters)
                        print(f"Detected letters: {letters}")
                    else:
                        print(f"No letters detected from window '{current_window}'")
                        continue
                else:
                    continue
            else:
                # Use the input as letters directly
                letters = user_input
                
            # Find all words with scores
            word_scores = solver.find_all_words_with_scores(letters, custom_values)
            
            # Display comprehensive results
            display_comprehensive_results(word_scores, current_window, screen_capture)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

def main():
    """Run the wordplay solver in interactive mode."""
    parser = argparse.ArgumentParser(description='Interactive wordplay solver - find the highest scoring words from given letters.')
    parser.add_argument('--dict', '-d', help='Path to custom dictionary file')
    

    
    args = parser.parse_args()
    
    # No custom letter values - simplified to use standard Scrabble values only
    custom_values = None
    
    # Initialize screen capture if available and needed
    screen_capture = None
    if SCREEN_CAPTURE_AVAILABLE:
        try:
            screen_capture = ScreenCapture()
        except ImportError as e:
            print(f"Screen capture not available: {e}", file=sys.stderr)
            if any(hasattr(args, attr) and getattr(args, attr) for attr in ['screen', 'window']):
                print("Install screen capture dependencies with: pip install -e .[screen]")
                return 1
    
    # Initialize the solver
    try:
        solver = WordSolver(args.dict)
        
        # Always run in interactive mode
        interactive_loop(solver, custom_values, screen_capture)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
