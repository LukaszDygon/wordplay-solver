"""Wordplay Solver - Find the highest scoring words from given letters."""
from typing import Dict, Optional, Tuple

__version__ = "0.1.0"

from wordplay_solver.scoring import calculate_word_score, get_letter_values
from wordplay_solver.solver import WordSolver
from wordplay_solver.dictionary import Dictionary, load_dictionary

# Optional screen capture imports
try:
    from wordplay_solver.screen_capture import ScreenCapture, list_available_windows
    __all__ = ['WordSolver', 'Dictionary', 'ScreenCapture', 'calculate_word_score', 
               'get_letter_values', 'load_dictionary', 'list_available_windows', 'find_best_word']
except ImportError:
    __all__ = ['WordSolver', 'Dictionary', 'calculate_word_score', 
               'get_letter_values', 'load_dictionary', 'find_best_word']

# For backward compatibility
def find_best_word(letters: str, custom_values: Optional[Dict[str, int]] = None) -> Tuple[str, int]:
    """
    Find the highest scoring word from the given letters.
    
    This is a convenience function that creates a WordSolver instance and calls its method.
    For better performance with multiple calls, create a WordSolver instance directly.
    
    Args:
        letters: String of available letters (can include custom values, e.g., 'a1b3')
        custom_values: Optional custom letter values from config file
        
    Returns:
        Tuple of (best_word, score)
    """
    solver = WordSolver()
    return solver.find_best_word(letters, custom_values)
