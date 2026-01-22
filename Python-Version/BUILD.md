# Building PythonVersion

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify build:**
   ```bash
   python build.py
   ```

3. **Run the bot:**
   ```bash
   python -m src.main
   ```
   or
   ```bash
   python -m src
   ```

## Installation Options

### Option 1: Install as package (recommended)
```bash
pip install -e .
```

Then run:
```bash
polymarket-bot
```

### Option 2: Run directly
```bash
python -m src.main
```

### Option 3: Using Makefile
```bash
make install  # Install dependencies
make build    # Verify build
make run      # Run the bot
```

## Build Verification

The `build.py` script checks:
- ✅ All required files exist
- ✅ All imports work correctly
- ✅ No syntax errors

## Project Structure

```
PythonVersion/
├── src/                    # Source code
│   ├── config/            # Configuration modules
│   ├── interfaces/        # Type definitions
│   ├── models/            # Database models
│   ├── services/          # Core services
│   ├── utils/             # Utilities
│   └── main.py            # Entry point
├── logs/                  # Log files (auto-created)
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
├── pyproject.toml        # Modern Python project config
├── build.py              # Build verification script
└── README.md             # Documentation
```

## Troubleshooting

### Import Errors
If you see import errors, make sure you're running from the `PythonVersion` directory:
```bash
cd PythonVersion
python -m src.main
```

### Missing Dependencies
Install all dependencies:
```bash
pip install -r requirements.txt
```

### CLOB Client Not Implemented
The CLOB client is a placeholder. See `src/utils/create_clob_client.py` for implementation details.
