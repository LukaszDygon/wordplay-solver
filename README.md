# Wordplay Solver

A Python script that finds the highest scoring words from a given set of letters using Scrabble-like scoring rules.

## Features

- Accepts a string of letters as input
- Uses standard English dictionary for word validation
- Implements standard Scrabble letter values
- Supports custom letter values via config file
- Allows inline letter value overrides (e.g., "a1b3c3")
- Finds the highest scoring valid word

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Single Run Mode

```bash
python -m wordplay_solver <letters> [--config CONFIG_FILE] [--dict DICTIONARY_FILE]
```

### Interactive Mode

```bash
python -m wordplay_solver --interactive [--config CONFIG_FILE] [--dict DICTIONARY_FILE]
# or simply
python -m wordplay_solver
```

### Examples

Basic usage:
```bash
python -m wordplay_solver "letters"
```

With inline letter values:
```bash
python -m wordplay_solver "a1b3c3d2e1f4"
```

With custom config file:
```bash
python -m wordplay_solver "letters" --config example_config.ini
```

Interactive mode with custom dictionary:
```bash
python -m wordplay_solver -i --dict /path/to/dictionary.txt
```

## Configuration

Create a `config.ini` file in the project root to override default letter values:

```ini
[letter_values]
a = 1
b = 3
c = 3
# ... and so on
```

## License

MIT
