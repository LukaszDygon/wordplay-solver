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

def calculate_length_bonus(word_length: int) -> int:
    """
    Calculate length bonus points for a word based on its length.
    
    Length bonuses:
    - +5 points for 5th, 6th, 7th letters
    - +10 points for 8th, 9th letters
    - +15 points for 10th, 11th letters
    - +20 points for 12th, 13th, 14th letters
    - +25 points for 15th, 16th, 17th letters
    - +30 points for 18th letter
    - +40 points for 19th letter
    - +50 points for 20th letter
    
    Args:
        word_length: Length of the word
        
    Returns:
        Total length bonus points
    """
    # Accumulated bonus points by word length
    length_bonuses = {
        0: 0, 1: 0, 2: 0, 3: 0, 4: 0,           # No bonus for 4 letters or less
        5: 5, 6: 10, 7: 15,                      # +5 each for 5th, 6th, 7th
        8: 25, 9: 35,                            # +10 each for 8th, 9th (15 + 10, 15 + 20)
        10: 50, 11: 65,                          # +15 each for 10th, 11th (35 + 15, 35 + 30)
        12: 85, 13: 105, 14: 125,               # +20 each for 12th, 13th, 14th
        15: 150, 16: 175, 17: 200,              # +25 each for 15th, 16th, 17th
        18: 230,                                 # +30 for 18th
        19: 270,                                 # +40 for 19th
        20: 320                                  # +50 for 20th
    }
    
    # Return the bonus for the exact length, or the highest available if longer than 20
    return length_bonuses.get(word_length, length_bonuses[20])

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
    Calculate the score of a word based on letter values plus length bonuses.
    
    Args:
        word: The word to score
        letter_values: Optional custom letter values, uses standard if None
        
    Returns:
        The total score of the word including length bonuses
    """
    if letter_values is None:
        letter_values = STANDARD_LETTER_VALUES
    
    # Calculate base score from letter values
    base_score = sum(letter_values.get(letter.lower(), 0) for letter in word if letter.isalpha())
    
    # Calculate length bonus
    length_bonus = calculate_length_bonus(len(word))
    
    return base_score + length_bonus
