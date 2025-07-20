"""Dictionary module for word validation."""
import os
import sys
from pathlib import Path
from typing import Set, Optional

# Try to import pkg_resources, but don't fail if not available
try:
    import pkg_resources
    PKG_RESOURCES_AVAILABLE = True
except ImportError:
    PKG_RESOURCES_AVAILABLE = False

# Default dictionary path (will be created if not exists)
DEFAULT_DICT_PATH = Path.home() / '.wordplay_solver' / 'dictionary.txt'
DEFAULT_DICT_URL = 'https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt'


def ensure_dictionary_exists(dict_path: Optional[Path] = None) -> Path:
    """
    Ensure the dictionary file exists, downloading it if necessary.
    
    Args:
        dict_path: Path to dictionary file, uses default if None
        
    Returns:
        Path to the dictionary file
    """
    if dict_path is None:
        dict_path = DEFAULT_DICT_PATH
    
    dict_path = Path(dict_path).expanduser().resolve()
    
    try:
        import urllib.request
        import ssl
        
        # Create directory if it doesn't exist
        dict_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Always download the latest dictionary
        print(f"Downloading dictionary to {dict_path}...")
        context = ssl._create_unverified_context()
        req = urllib.request.Request(
            DEFAULT_DICT_URL,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, context=context) as response, open(dict_path, 'wb') as out_file:
            out_file.write(response.read())
            
    except Exception as e:
        if not dict_path.exists():
            raise RuntimeError(f"Failed to download dictionary: {e}")
        print(f"Warning: Could not update dictionary, using existing file at {dict_path}")
    
    if not dict_path.exists() or dict_path.stat().st_size == 0:
        raise RuntimeError(f"Dictionary file is empty or could not be created at {dict_path}")
    
    return dict_path

def load_dictionary(dict_path: Optional[Path] = None) -> Set[str]:
    """
    Load words from dictionary file.
    
    Args:
        dict_path: Path to dictionary file, uses default if None
        
    Returns:
        Set of valid words in lowercase
    """
    dict_path = ensure_dictionary_exists(dict_path)
    
    with open(dict_path, 'r', encoding='utf-8') as f:
        return {line.strip().lower() for line in f if line.strip().isalpha()}

class Dictionary:
    """Dictionary for word validation."""
    
    def __init__(self, dict_path: Optional[Path] = None):
        """
        Initialize the dictionary.
        
        Args:
            dict_path: Path to dictionary file, uses default if None
        """
        self.words = load_dictionary(dict_path)
    
    def is_valid_word(self, word: str) -> bool:
        """
        Check if a word exists in the dictionary.
        
        Args:
            word: Word to check
            
        Returns:
            True if the word is valid, False otherwise
        """
        return word.lower() in self.words
    
    def get_words_with_letters(self, letters: str) -> Set[str]:
        """
        Get all valid words that can be formed from the given letters.
        
        Args:
            letters: String of available letters
            
        Returns:
            Set of valid words
        """
        from collections import Counter
        
        letter_count = Counter(letters.lower())
        valid_words = set()
        
        for word in self.words:
            word_count = Counter(word)
            if all(word_count[char] <= letter_count.get(char, 0) for char in word_count):
                valid_words.add(word)
        
        return valid_words
