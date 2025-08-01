# Wordplay Solver

A Python script that finds the highest scoring words from a given set of letters using Scrabble-like scoring rules.

## Features

- Accepts a string of letters as input
- Uses standard English dictionary for word validation
- Implements standard Scrabble letter values
- Supports custom letter values via config file
- Allows inline letter value overrides (e.g., "a1b3c3")
- Finds the highest scoring valid word
- **NEW:** Screen capture and OCR for automatic letter detection
- **NEW:** Window-specific capture for game integration
- **NEW:** Interactive region selection for precise capture

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the basic package:
   ```bash
   pip install -e .
   ```
3. For screen capture functionality, install with screen capture dependencies:
   ```bash
   pip install -e '.[screen]'
   ```
   
   **Note:** Screen capture requires additional system dependencies:
   - **macOS:** Install Tesseract OCR: `brew install tesseract`
   - **Linux:** Install Tesseract OCR: `sudo apt-get install tesseract-ocr`
   - **Windows:** Download and install Tesseract from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

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

### Screen Capture Mode (requires screen capture dependencies)

Capture letters from full screen:
```bash
python -m wordplay_solver --screen
```

Capture from specific window:
```bash
python -m wordplay_solver --window "Game Window"
```

Capture from specific screen region:
```bash
python -m wordplay_solver --region 100 200 300 150
```

List available windows:
```bash
python -m wordplay_solver --list-windows
```

### Interactive Mode with Screen Capture

Run interactive mode with screen capture commands:
```bash
python -m wordplay_solver --interactive
```

Then use these commands:
- `screen` - Capture letters from full screen
- `window <title>` - Capture from specific window
- `region` - Select screen region interactively
- `windows` - List available windows
- Or enter letters manually as usual

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
