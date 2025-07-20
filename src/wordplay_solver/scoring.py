"""Scoring module for wordplay solver."""
import configparser
from pathlib import Path
from typing import Dict, Optional

# Standard Scrabble letter values
STANDARD_LETTER_VALUES = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4,
    'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3,
    'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8,
    'y': 4, 'z': 10
}

def get_letter_values(config_path: Optional[str] = None) -> Dict[str, int]:
    """
    Get letter values, optionally loading overrides from a config file.
    
    Args:
        config_path: Optional path to config file with [letter_values] section
        
    Returns:
        Dictionary mapping letters to their point values
    """
    letter_values = STANDARD_LETTER_VALUES.copy()
    
    if config_path and Path(config_path).exists():
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if 'letter_values' in config:
            for letter, value in config['letter_values'].items():
                if len(letter) == 1 and letter.isalpha():
                    try:
                        letter_values[letter.lower()] = int(value)
                    except (ValueError, TypeError):
                        pass  # Skip invalid values
    
    return letter_values

def parse_letter_input(letter_str: str) -> Dict[str, int]:
    """
    Parse input string with optional custom letter values.
    
    Format: "a1b3c3" where letters can be followed by numbers.
    If no number is provided, the standard value is used.
    
    Args:
        letter_str: Input string of letters with optional values
        
    Returns:
        Dictionary mapping letters to their values
    """
    letters = {}
    i = 0
    n = len(letter_str)
    
    while i < n:
        if not letter_str[i].isalpha():
            i += 1
            continue
            
        char = letter_str[i].lower()
        i += 1
        
        # Check if next characters form a number
        num_str = ''
        while i < n and letter_str[i].isdigit():
            num_str += letter_str[i]
            i += 1
            
        value = int(num_str) if num_str else STANDARD_LETTER_VALUES.get(char, 1)
        letters[char] = value
    
    return letters

def calculate_word_score(word: str, letter_values: Optional[Dict[str, int]] = None) -> int:
    """
    Calculate the score of a word based on letter values.
    
    Args:
        word: The word to score
        letter_values: Optional custom letter values, uses standard if None
        
    Returns:
        The total score of the word
    """
    if letter_values is None:
        letter_values = STANDARD_LETTER_VALUES
        
    return sum(letter_values.get(letter.lower(), 0) for letter in word if letter.isalpha())
