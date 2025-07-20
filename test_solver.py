#!/usr/bin/env python3
"""Test script for the wordplay solver."""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from wordplay_solver import WordSolver, Dictionary, get_letter_values

def test_basic_functionality():
    """Test basic functionality with a simple word."""
    print("Testing basic functionality...")
    solver = WordSolver()
    
    # Test with a simple word
    word, score = solver.find_best_word("test")
    print(f"Best word from 'test': {word} (score: {score})")
    
    # Test with more letters
    word, score = solver.find_best_word("letters")
    print(f"Best word from 'letters': {word} (score: {score})")
    
    # Test with custom letter values
    word, score = solver.find_best_word("a1b3c3d2e1f4")
    print(f"Best word from 'a1b3c3d2e1f4': {word} (score: {score})")

def test_with_custom_config():
    """Test with custom configuration."""
    print("\nTesting with custom configuration...")
    # Create a custom config file
    config_content = """[letter_values]
a = 10
b = 2
c = 2
d = 2
e = 10
"""
    with open("test_config.ini", "w") as f:
        f.write(config_content)
    
    # Test with custom values
    from wordplay_solver.scoring import get_letter_values
    custom_values = get_letter_values("test_config.ini")
    
    solver = WordSolver()
    word, score = solver.find_best_word("abcde", custom_values)
    print(f"Best word with custom values: {word} (score: {score})")
    
    import os
    os.remove("test_config.ini")

def test_dictionary_loading():
    """Test that the dictionary loads correctly."""
    print("\nTesting dictionary loading...")
    from wordplay_solver.dictionary import Dictionary
    
    # This will download the dictionary if not already present
    dict_obj = Dictionary()
    test_words = ["test", "python", "example", "wordplay"]
    
    print("Checking dictionary for test words:")
    for word in test_words:
        exists = dict_obj.is_valid_word(word)
        print(f"  - {word}: {'Found' if exists else 'Not found'}")

if __name__ == "__main__":
    print("=== Wordplay Solver Tests ===\n")
    test_basic_functionality()
    test_with_custom_config()
    test_dictionary_loading()
    print("\n=== Tests Complete ===")
