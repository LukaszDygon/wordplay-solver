# Windsurf Rules for Wordplay Solver

## Project Overview
This is a Python CLI tool that finds the highest scoring words from given letters using Scrabble-like scoring rules. The project supports both single-run and interactive modes, with customizable letter values and dictionary sources.

## Project Structure
```
wordplay-solver/
├── src/wordplay_solver/          # Main package source
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # CLI entry point
│   ├── dictionary.py            # Dictionary loading and validation
│   ├── scoring.py               # Letter scoring logic
│   └── solver.py                # Core word-finding algorithms
├── wordplay_solver.py           # Standalone script (legacy)
├── test_solver.py               # Test file
├── colins.txt                   # Dictionary file (3MB+)
├── example_config.ini           # Example configuration
├── pyproject.toml               # Python project configuration
└── README.md                    # Project documentation
```

## Key Technical Details

### Entry Points
- **Package mode**: `python -m wordplay_solver` (preferred)
- **Standalone**: `python wordplay_solver.py` (legacy)
- **Installed**: `wordplay-solver` command (after pip install)

### Core Functionality
- **Input parsing**: Supports plain letters ("abcdef") and custom values ("a1b3c3d2e1f4")
- **Dictionary**: Downloads from GitHub or uses local file
- **Scoring**: Standard Scrabble values with config file overrides
- **Output**: Top 5 words overall + best words by length
- **Screen Capture**: OCR-based letter detection from screen/windows (optional)
- **Window Integration**: Capture letters from specific game windows
- **Region Selection**: Interactive screen region selection for precise capture

### Configuration
- Uses `.ini` files for custom letter values
- Example config in `example_config.ini`
- Standard Scrabble values as defaults

## Development Guidelines

### Code Style
- **Formatter**: Black (line length 88)
- **Import sorting**: isort
- **Type checking**: mypy
- **Testing**: pytest

### Dependencies
- **Runtime**: Pure Python 3.8+ (no external deps for basic functionality)
- **Screen Capture**: pillow, pytesseract, pyautogui, opencv-python, numpy (optional)
- **Development**: pytest, black, isort, mypy
- **System Requirements**: Tesseract OCR for screen capture (brew install tesseract on macOS)

### Architecture Patterns
- **Modular design**: Separate concerns (dictionary, scoring, solving)
- **CLI interface**: argparse with interactive mode support
- **Error handling**: Graceful fallbacks for missing files/network
- **Type hints**: Full typing support throughout

## Common Tasks

### Running the solver
```bash
# Interactive mode (default)
python -m wordplay_solver

# Single word
python -m wordplay_solver "letters"

# With custom values
python -m wordplay_solver "a1b3c3d2e1f4"

# With config file
python -m wordplay_solver "letters" --config custom_config.ini

# Screen capture modes (requires screen dependencies)
python -m wordplay_solver --screen              # Full screen capture
python -m wordplay_solver --window "Game"       # Specific window
python -m wordplay_solver --region 100 200 300 150  # Screen region
python -m wordplay_solver --list-windows        # List available windows
```

### Development workflow
```bash
# Install dev dependencies
pip install -e '.[dev]'
# or with uv:
uv pip install -e '.[dev]'

# Install with screen capture support
pip install -e '.[screen]'
# or with uv:
uv pip install -e '.[screen]'

# Install system dependencies (macOS)
brew install tesseract

# Run tests
pytest test_solver.py

# Format code
black src/ *.py
isort src/ *.py

# Type check
mypy src/

# Test screen capture functionality
python -c "from wordplay_solver.screen_capture import demo_screen_capture; demo_screen_capture()"
```

### Building and distribution
```bash
# Build package
python -m build

# Install locally
pip install -e .
```

## Important Files to Know

### Core Logic Files
- `src/wordplay_solver/solver.py` - Main word-finding algorithm
- `src/wordplay_solver/scoring.py` - Letter value calculations
- `src/wordplay_solver/dictionary.py` - Word validation logic

### Configuration Files
- `pyproject.toml` - Project metadata, dependencies, tool config
- `example_config.ini` - Template for custom letter values

### Data Files
- `colins.txt` - Large dictionary file (3MB+, don't edit directly)

## Coding Conventions

### When making changes:
1. **Maintain backward compatibility** with the standalone `wordplay_solver.py`
2. **Update both entry points** if changing core logic
3. **Add type hints** to all new functions
4. **Update tests** in `test_solver.py`
5. **Follow existing error handling patterns** (graceful degradation)

### When adding features:
1. **Consider config file support** for new parameters
2. **Add CLI arguments** to both entry points
3. **Update README.md** with usage examples
4. **Test with both small and large dictionaries**

### Performance considerations:
- Dictionary loading can be slow (3MB+ file)
- Word generation scales with letter count
- Consider memory usage with large word lists

## Testing Notes
- `test_solver.py` contains the main test suite
- Tests cover basic functionality, edge cases, and error conditions
- Run tests before committing changes

## Deployment Notes
- Package is configured for PyPI distribution
- Uses hatchling as build backend
- MIT license
- Supports Python 3.8+

## Common Issues & Solutions
1. **Dictionary not found**: Falls back to downloading from GitHub
2. **Network issues**: Graceful degradation to smaller word lists
3. **Invalid input**: Clear error messages and examples
4. **Performance**: Consider caching for repeated runs

## AI Assistant Guidelines
When working on this project:
- Always test both entry points (`__main__.py` and `wordplay_solver.py`)
- Respect the modular architecture - don't put everything in one file
- Consider the user experience - this is a CLI tool meant to be user-friendly
- Maintain the balance between features and simplicity
- When adding dependencies, update both `pyproject.toml` and consider standalone compatibility
