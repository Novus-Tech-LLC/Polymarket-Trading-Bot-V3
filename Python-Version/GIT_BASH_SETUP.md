# Setting Up Python in Git Bash

## Issue: `pip: command not found`

If you're using Git Bash and getting "pip: command not found", here's how to fix it:

## Solution 1: Use Python Module Syntax (Recommended)

Instead of `pip`, use `python -m pip`:

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Or if you have python3
python3 -m pip install -r requirements.txt
```

## Solution 2: Use the Install Script

Run the provided script:

```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

## Solution 3: Add Python to Git Bash PATH

Git Bash may not see Python if it's not in the Windows PATH. To fix:

1. **Find Python installation:**
   ```bash
   # In Git Bash, try:
   /c/Users/$USER/AppData/Local/Programs/Python/Python*/python.exe
   # Or
   /c/Python*/python.exe
   ```

2. **Add to Git Bash PATH:**
   Edit `~/.bashrc` or `~/.bash_profile`:
   ```bash
   # Add Python to PATH
   export PATH="/c/Users/$USER/AppData/Local/Programs/Python/Python312:/c/Users/$USER/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
   ```
   (Replace Python312 with your actual version)

3. **Reload:**
   ```bash
   source ~/.bashrc
   ```

## Solution 4: Use Windows Command Prompt or PowerShell

Git Bash sometimes has PATH issues. Use Windows terminal instead:

```cmd
# In Command Prompt or PowerShell
cd PythonVersion
python -m pip install -r requirements.txt
python -m src.main
```

## Quick Commands for Git Bash

```bash
# Check Python
python --version
# or
python3 --version

# Install dependencies (use module syntax)
python -m pip install -r requirements.txt

# Run the bot
python -m src.main
```

## Verify Installation

After installing dependencies:

```bash
python -c "import pymongo; print('✓ pymongo installed')"
python -c "import web3; print('✓ web3 installed')"
python -c "import requests; print('✓ requests installed')"
```

## Troubleshooting

### Python not found in Git Bash

1. **Check if Python is installed:**
   ```bash
   /c/Windows/System32/cmd.exe /c python --version
   ```

2. **If Python works in CMD but not Git Bash:**
   - Python is installed but not in Git Bash PATH
   - Use Solution 3 above to add to PATH
   - Or use Windows terminal instead

### pip not found

Always use `python -m pip` instead of just `pip` in Git Bash:

```bash
# ❌ This might not work
pip install -r requirements.txt

# ✅ This will work
python -m pip install -r requirements.txt
```

## Recommended: Use Windows Terminal

For best compatibility, use:
- **Windows Terminal** (recommended)
- **PowerShell**
- **Command Prompt**

Git Bash can work but may require PATH configuration.
