#!/usr/bin/env python3
"""Command-line interface for Wordplay Solver."""
import argparse
import sys
from pathlib import Path

from wordplay_solver.solver import WordSolver
from wordplay_solver.scoring import get_letter_values

def interactive_loop(solver, custom_values=None):
    """Run the solver in an interactive loop."""
    print("Wordplay Solver - Interactive Mode")
    print("Enter letters (e.g., 'letters' or 'a1b3c3' for custom values)")
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
                
            # Find the best word
            best_word, score = solver.find_best_word(user_input, custom_values)
            
            # Display results
            if best_word:
                print(f"\nBest word: {best_word}")
                print(f"Score: {score}\n")
            else:
                print("\nNo valid words found with the given letters.\n")
                
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
    custom_values = None
    if args.config:
        try:
            custom_values = get_letter_values(args.config)
        except Exception as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
            return 1
    
    # Initialize the solver
    try:
        solver = WordSolver(args.dict)
        
        # Interactive mode
        if args.interactive or not args.letters:
            interactive_loop(solver, custom_values)
            return 0
            
        # Single-run mode
        best_word, score = solver.find_best_word(args.letters, custom_values)
        
        if best_word:
            print(f"Best word: {best_word}")
            print(f"Score: {score}")
        else:
            print("No valid words found with the given letters.")
            return 1
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
