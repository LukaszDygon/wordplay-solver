"""Solver module for finding the highest scoring word."""
from typing import Dict, Optional, Tuple
from collections import Counter

from wordplay_solver.dictionary import Dictionary
from wordplay_solver.scoring import calculate_word_score, parse_letter_input

class WordSolver:
    """Solver for finding the highest scoring word from given letters."""
    
    def __init__(self, dict_path: Optional[str] = None):
        """
        Initialize the solver with a dictionary.
        
        Args:
            dict_path: Optional path to custom dictionary file
        """
        self.dictionary = Dictionary(dict_path)
    
    def find_best_word(self, letters: str, custom_values: Optional[Dict[str, int]] = None) -> Tuple[str, int]:
        """
        Find the highest scoring word that can be formed from the given letters.
        
        Args:
            letters: String of available letters (can include custom values, e.g., 'a1b3')
            custom_values: Optional custom letter values from config file
            
        Returns:
            Tuple of (best_word, score)
        """
        # Parse any inline custom values (e.g., 'a1b3')
        inline_values = parse_letter_input(letters)
        
        # Combine with config file values (config values take precedence)
        if custom_values:
            letter_values = {**inline_values, **custom_values}
        else:
            letter_values = inline_values
        
        # Get all valid words that can be formed from the letters
        valid_words = self.dictionary.get_words_with_letters(''.join(letter_values.keys()))
        
        if not valid_words:
            return "", 0
        
        # Calculate score for each word and find the best one
        best_word = ""
        best_score = -1
        
        for word in valid_words:
            score = calculate_word_score(word, letter_values)
            if score > best_score or (score == best_score and len(word) > len(best_word)):
                best_word = word
                best_score = score
        
        return best_word, best_score
