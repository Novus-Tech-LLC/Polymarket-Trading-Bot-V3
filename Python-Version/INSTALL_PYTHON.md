# Installing Python 3.9+ for Polymarket Copy Trading Bot

## Quick Installation

Run the installation helper script:
```powershell
.\install_python.ps1
```

This script will guide you through the installation process.

## Installation Methods

### Method 1: Microsoft Store (Recommended for Windows 10/11)

**Easiest method - automatically adds Python to PATH**

1. Open Microsoft Store
2. Search for "Python 3.11" or "Python 3.12"
3. Click "Install"
4. Wait for installation
5. **Restart your terminal**

**Advantages:**
- ✅ Automatically adds to PATH
- ✅ Easy updates through Store
- ✅ No manual configuration needed

### Method 2: Direct Download from python.org

**Most control over installation**

1. Visit: https://www.python.org/downloads/
2. Download Python 3.9+ (3.11 or 3.12 recommended)
3. Run the installer
4. **IMPORTANT:** Check "Add Python to PATH" during installation
5. Click "Install Now"
6. **Restart your terminal**

**Download Links:**
- Python 3.12: https://www.python.org/downloads/release/python-3120/
- Python 3.11: https://www.python.org/downloads/release/python-3117/
- Python 3.10: https://www.python.org/downloads/release/python-31011/
- Python 3.9: https://www.python.org/downloads/release/python-3913/

### Method 3: Using winget (Windows Package Manager)

**Command-line installation**

```powershell
# Install Python 3.12
winget install Python.Python.3.12

# Or Python 3.11
winget install Python.Python.3.11
```

**Note:** winget is available on Windows 10 (1809+) and Windows 11

## Verification

After installation, verify Python works:

```powershell
# Check version
python --version
# Should show: Python 3.9.x or higher

# Check pip
python -m pip --version
# Should show: pip version
```

## Troubleshooting

### Python installed but not in PATH

If `python --version` doesn't work after installation:

1. **Find Python installation:**
   ```powershell
   Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\Programs\Python" -Recurse -Filter "python.exe"
   ```

2. **Add to PATH manually:**
   - Press `Win + X` → System → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" → Edit
   - Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python312`
   - Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python312\Scripts`
   - Click OK on all dialogs
   - **Restart terminal**

3. **Or reinstall with "Add to PATH" checked**

### Multiple Python Versions

If you have multiple Python versions:

```powershell
# Use Python Launcher
py --list          # List all versions
py -3.11 -m src.main  # Use specific version
```

### Still Not Working?

1. **Restart your computer** (sometimes needed for PATH changes)
2. **Open a new terminal** (PATH changes require new session)
3. **Check in Command Prompt** (not just PowerShell)
4. **Run the diagnostic script:**
   ```powershell
   .\check_python.ps1
   ```

## Next Steps

Once Python is installed:

1. **Install dependencies:**
   ```powershell
   cd PythonVersion
   pip install -r requirements.txt
   ```

2. **Create .env file** (copy from TypeScriptVersion or create new)

3. **Run the bot:**
   ```powershell
   python -m src.main
   ```

## System Requirements

- **Windows:** Windows 10 or later
- **Python:** 3.9, 3.10, 3.11, or 3.12
- **RAM:** 2GB minimum (4GB recommended)
- **Disk:** 500MB free space

## Need Help?

If you're still having issues:
1. Run `.\check_python.ps1` for diagnostics
2. Check `FIX_PYTHON.md` for common issues
3. Verify installation in a new terminal window
