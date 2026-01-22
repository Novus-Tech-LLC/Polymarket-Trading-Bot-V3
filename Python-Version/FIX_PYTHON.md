# Fixing Python Installation Issues

## Quick Check

Run the PowerShell script to check for Python:
```powershell
.\check_python.ps1
```

## Common Issues and Solutions

### Issue 1: Python Not in PATH

**Symptoms:**
- `python --version` returns "Python was not found"
- Python is installed but can't be run from command line

**Solution:**

1. **Find Python Installation:**
   ```powershell
   # Check common locations
   Get-ChildItem "C:\Python*" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue
   Get-ChildItem "$env:LOCALAPPDATA\Programs\Python" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue
   ```

2. **Add to PATH Manually:**
   - Press `Win + X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add:
     - `C:\Python39` (or your Python version)
     - `C:\Python39\Scripts`
   - Click "OK" on all dialogs
   - **Restart your terminal/PowerShell**

3. **Or Reinstall Python:**
   - Download from https://www.python.org/downloads/
   - During installation, **check "Add Python to PATH"**
   - This is the easiest solution

### Issue 2: Python Not Installed

**Solution:**
1. Download Python 3.9+ from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Choose "Install Now" or "Customize installation"
5. After installation, restart your terminal

### Issue 3: Multiple Python Versions

**Solution:**
Use the Python Launcher (`py` command):
```powershell
# List available Python versions
py --list

# Run with specific version
py -3.11 -m src.main
```

### Issue 4: Using Full Path

If Python is installed but not in PATH, you can use the full path:

```powershell
# Find Python
$pythonPath = Get-ChildItem "C:\Python*" -Recurse -Filter "python.exe" | Select-Object -First 1

# Run with full path
& $pythonPath.FullName -m src.main
```

## Verify Installation

After fixing, verify Python works:

```powershell
python --version
# Should show: Python 3.9.x or higher

python -m pip --version
# Should show: pip version
```

## Alternative: Use Python from Microsoft Store

If you have Windows Store access:
1. Open Microsoft Store
2. Search for "Python 3.11" or "Python 3.12"
3. Install it
4. It should automatically be added to PATH

## Still Having Issues?

1. **Restart your computer** after adding Python to PATH
2. **Open a new terminal/PowerShell window** (PATH changes require new session)
3. **Check if Python works in Command Prompt** (not just PowerShell)
4. **Verify PATH** in System Environment Variables

## Quick Test

Once Python is working, test with:
```powershell
cd PythonVersion
python --version
python -c "print('Python is working!')"
```

If both commands work, you're ready to run the bot!
