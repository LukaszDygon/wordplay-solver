#!/usr/bin/env python3
"""
Wordplay Solver - Find the highest scoring words from given letters.
This is a standalone version that doesn't require package installation.
"""
import os
import sys
import argparse
import configparser
from pathlib import Path
from typing import Dict, Optional, List, Set, Tuple
from collections import Counter

# Standard Scrabble letter values
STANDARD_LETTER_VALUES = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4,
    'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3,
    'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8,
    'y': 4, 'z': 10
}

class Dictionary:
    """Dictionary for word validation."""
    
    def __init__(self, dict_path: Optional[str] = None):
        """Initialize the dictionary."""
        self.words = self._load_dictionary(dict_path)
    
    def _load_dictionary(self, dict_path: Optional[str] = None) -> Set[str]:
        """Load words from dictionary file."""
        words = set()
        
        # If a dictionary path is provided, try to load it
        if dict_path and os.path.exists(dict_path):
            try:
                with open(dict_path, 'r') as f:
                    words = {line.strip().lower() for line in f if line.strip().isalpha()}
            except Exception as e:
                print(f"Warning: Could not load dictionary from {dict_path}: {e}")
        
        # Always try to download the latest dictionary
        try:
            import urllib.request
            import ssl
            
            print("Downloading dictionary...")
            url = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
            context = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, context=context) as response:
                downloaded_words = response.read().decode('utf-8').splitlines()
                words.update(word.strip().lower() for word in downloaded_words if word.strip().isalpha())
                
            # Save the downloaded words if a path was provided
            if dict_path:
                try:
                    os.makedirs(os.path.dirname(dict_path), exist_ok=True)
                    with open(dict_path, 'w') as f:
                        for word in sorted(words):
                            f.write(f"{word}\n")
                except Exception as e:
                    print(f"Warning: Could not save dictionary to {dict_path}: {e}")
                    
        except Exception as e:
            print(f"Warning: Could not download dictionary: {e}")
            if not words:
                raise RuntimeError("No dictionary available. Please check your internet connection or provide a dictionary file with --dict")
        
        return words
    
    def is_valid_word(self, word: str) -> bool:
        """Check if a word exists in the dictionary."""
        return word.lower() in self.words
    
    def get_words_with_letters(self, letters: str) -> Set[str]:
        """Get all valid words that can be formed from the given letters."""
        letter_count = Counter(letters.lower())
        valid_words = set()
        
        for word in self.words:
            # Only include words of 4 or more letters
            if len(word) < 4:
                continue
                
            word_count = Counter(word)
            if all(word_count[char] <= letter_count.get(char, 0) for char in word_count):
                valid_words.add(word)
        
        return valid_words

class WordSolver:
    """Solver for finding the highest scoring word from given letters."""
    
    def __init__(self, dict_path: Optional[str] = None):
        """Initialize the solver with a dictionary."""
        self.dictionary = Dictionary(dict_path)
    
    def calculate_word_score(self, word: str, letter_values: Dict[str, int]) -> int:
        """Calculate the score of a word based on letter values."""
        return sum(letter_values.get(letter.lower(), 0) for letter in word if letter.isalpha())
    
    def parse_letter_input(self, letter_str: str) -> Dict[str, int]:
        """Parse input string with optional custom letter values."""
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
    
    def find_best_words(self, letters: str, custom_values: Optional[Dict[str, int]] = None) -> Dict[str, List[Tuple[str, int]]]:
        """
        Find the best scoring words from the given letters.
        
        Args:
            letters: Input string that may contain:
                    - Letters to use
                    - Custom values (e.g., 'a1b3')
                    - Position constraints (e.g., 's=e' to force 'e' in the word)
        
        Returns:
            Dict with two keys:
            - 'top_words': List of (word, score) tuples for top 5 scoring words
            - 'by_length': Dict mapping word lengths to list of (word, score) tuples
        """
        # Parse position constraints (e.g., 's=a1b2' means 'a' at position 1, 'b' at position 2)
        position_constraints = {}
        if 's=' in letters:
            parts = letters.split('s=')
            letters = parts[0].strip()
            constraint_str = parts[1].strip()
            
            # Parse the constraint string (e.g., 'a1b2c3')
            i = 0
            while i < len(constraint_str):
                if constraint_str[i].isalpha():
                    char = constraint_str[i].lower()
                    i += 1
                    # Extract the position number
                    pos_str = ''
                    while i < len(constraint_str) and constraint_str[i].isdigit():
                        pos_str += constraint_str[i]
                        i += 1
                    if pos_str:
                        position = int(pos_str)
                        if position > 0:  # 1-based position
                            position_constraints[position] = char
                else:
                    i += 1
        
        # Extract just the letters from the input (remove any numbers)
        input_letters = ''.join([c.lower() for c in letters if c.isalpha()])
        
        # Parse any inline custom values (e.g., 'a1b3')
        inline_values = self.parse_letter_input(letters)
        
        # Combine with custom values (custom values take precedence)
        if custom_values:
            letter_values = {**inline_values, **custom_values}
        else:
            letter_values = inline_values
        
        # If no custom values were provided, use standard values for any missing letters
        for letter in input_letters:
            if letter not in letter_values:
                letter_values[letter] = STANDARD_LETTER_VALUES.get(letter, 1)
        
        # Get all valid words that can be formed from the input letters
        valid_words = self.dictionary.get_words_with_letters(input_letters)
        
        # Apply position constraints if any
        if position_constraints:
            filtered_words = []
            for word in valid_words:
                valid = True
                for pos, char in position_constraints.items():
                    if pos > len(word) or word[pos-1] != char:
                        valid = False
                        break
                if valid:
                    filtered_words.append(word)
            valid_words = filtered_words
        
        if not valid_words:
            return {'top_words': [], 'by_length': {}}
        
        # Calculate score for each word and store with score
        word_scores = []
        for word in valid_words:
            score = self.calculate_word_score(word, letter_values)
            word_scores.append((word, score, len(word)))
        
        # Sort by score (descending), then length (descending), then word (ascending)
        word_scores.sort(key=lambda x: (-x[1], -x[2], x[0]))
        
        # Get top 5 words overall
        top_words = [(word, score) for word, score, _ in word_scores[:5]]
        
        # Group words by length and get top 5 for each length (4 and above)
        by_length = {}
        if word_scores:
            min_length = 4
            max_length = max(l for _, _, l in word_scores)
            for length in range(min_length, max_length + 1):
                length_words = [(w, s) for w, s, l in word_scores if l == length]
                if length_words:  # Only include lengths that have words
                    by_length[length] = length_words[:5]  # Top 2 words for this length
        
        return {
            'top_words': top_words,
            'by_length': by_length
        }

def load_letter_values(config_path: Optional[str] = None) -> Dict[str, int]:
    """Load letter values from config file."""
    if not config_path or not os.path.exists(config_path):
        return {}
    
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if 'letter_values' in config:
            return {k.lower(): int(v) for k, v in config['letter_values'].items() 
                   if len(k) == 1 and k.isalpha() and v.isdigit()}
    except Exception as e:
        print(f"Warning: Could not load letter values from {config_path}: {e}")
    
    return {}

def interactive_loop(solver: WordSolver, custom_values: Optional[Dict[str, int]] = None):
    """Run the solver in an interactive loop."""
    print("\n=== Wordplay Solver - Interactive Mode ===")
    print("Enter letters (e.g., 'letters' or 'a1b3c3' for custom values)")
    print("Add 's=a1b2c3' to force specific letters at positions (e.g., 'artistic s=t1i2c3' to require 't' in position 1, 'i' in 2, 'c' in 3)")
    print("Type 'exit' or press Ctrl+C to quit\n")
    
    while True:
        try:
            # Get user input
            user_input = input("Enter letters: ").strip()
            
            # Check for exit command
            if user_input.lower() in ('exit', 'quit', 'q'):
                print("Goodbye!")
                break
                
            if not user_input:
                continue
                
            # Find the best words
            results = solver.find_best_words(user_input, custom_values)
            
            # Display results
            if not results['top_words']:
                print("\nNo valid words found with the given letters.\n")
                continue
                
            print("\n=== Top 5 Words ===")
            for i, (word, score) in enumerate(results['top_words'], 1):
                print(f"{i}. {word.upper()} (Score: {score})")
                
            if results['by_length']:
                print("\n=== Best by Length ===")
                for length in sorted(results['by_length'].keys()):
                    words = results['by_length'][length]
                    word_list = ", ".join(f"{w.upper()} ({s})" for w, s in words)
                    print(f"{length} letters: {word_list}")
            
            print()  # Add a blank line after results
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

def main():
    """Run the wordplay solver from the command line."""
    parser = argparse.ArgumentParser(description='Find the highest scoring word from given letters.')
    parser.add_argument('letters', nargs='?', help='Letters to use (e.g., "letters" or "a1b3c3" for custom values)')
    parser.add_argument('--dict', '-d', help='Path to custom dictionary file')
    parser.add_argument('--config', '-c', help='Path to config file with custom letter values')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Load custom letter values from config file if provided
    custom_values = load_letter_values(args.config) if args.config else {}
    
    # Initialize the solver
    try:
        solver = WordSolver(args.dict)
        
        # Interactive mode
        if args.interactive or not args.letters:
            interactive_loop(solver, custom_values)
            return 0
            
        # Single-run mode
        results = solver.find_best_words(args.letters, custom_values)
        
        if not results['top_words']:
            print("No valid words found with the given letters.")
            return 1
            
        print("=== Top 5 Words ===")
        for i, (word, score) in enumerate(results['top_words'], 1):
            print(f"{i}. {word.upper()} (Score: {score})")
            
        if results['by_length']:
            print("\n=== Best by Length ===")
            for length in sorted(results['by_length'].keys()):
                words = results['by_length'][length]
                word_list = ", ".join(f"{w.upper()} ({s})" for w, s in words)
                print(f"{length} letters: {word_list}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
