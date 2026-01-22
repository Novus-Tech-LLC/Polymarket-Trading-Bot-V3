"""
Build script to verify PythonVersion structure and imports
"""
import sys
import os
from pathlib import Path

def check_imports():
    """Check if all imports work correctly"""
    print("🔍 Checking imports...")
    
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path.parent))
    
    errors = []
    
    try:
        from src.config import env
        print("✓ src.config.env")
    except Exception as e:
        errors.append(f"✗ src.config.env: {e}")
    
    try:
        from src.config import copy_strategy
        print("✓ src.config.copy_strategy")
    except Exception as e:
        errors.append(f"✗ src.config.copy_strategy: {e}")
    
    try:
        from src.config import db
        print("✓ src.config.db")
    except Exception as e:
        errors.append(f"✗ src.config.db: {e}")
    
    try:
        from src.utils import errors
        print("✓ src.utils.errors")
    except Exception as e:
        errors.append(f"✗ src.utils.errors: {e}")
    
    try:
        from src.utils import constants
        print("✓ src.utils.constants")
    except Exception as e:
        errors.append(f"✗ src.utils.constants: {e}")
    
    try:
        from src.utils import logger
        print("✓ src.utils.logger")
    except Exception as e:
        errors.append(f"✗ src.utils.logger: {e}")
    
    try:
        from src.models import user_history
        print("✓ src.models.user_history")
    except Exception as e:
        errors.append(f"✗ src.models.user_history: {e}")
    
    try:
        from src.interfaces import user
        print("✓ src.interfaces.user")
    except Exception as e:
        errors.append(f"✗ src.interfaces.user: {e}")
    
    if errors:
        print("\n❌ Import errors found:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ All imports successful!")
        return True

def check_structure():
    """Check if all required files exist"""
    print("\n📁 Checking file structure...")
    
    required_files = [
        "src/__init__.py",
        "src/main.py",
        "src/config/__init__.py",
        "src/config/env.py",
        "src/config/copy_strategy.py",
        "src/config/db.py",
        "src/utils/__init__.py",
        "src/utils/errors.py",
        "src/utils/constants.py",
        "src/utils/logger.py",
        "src/utils/fetch_data.py",
        "src/utils/get_my_balance.py",
        "src/utils/create_clob_client.py",
        "src/utils/post_order.py",
        "src/utils/health_check.py",
        "src/models/__init__.py",
        "src/models/user_history.py",
        "src/interfaces/__init__.py",
        "src/interfaces/user.py",
        "src/services/__init__.py",
        "src/services/trade_monitor.py",
        "src/services/trade_executor.py",
        "requirements.txt",
        "README.md",
        "setup.py",
    ]
    
    base_path = Path(__file__).parent
    missing = []
    
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing:
        print("\n❌ Missing files:")
        for file_path in missing:
            print(f"  {file_path}")
        return False
    else:
        print("\n✅ All required files present!")
        return True

if __name__ == "__main__":
    print("🔨 Building PythonVersion...\n")
    
    structure_ok = check_structure()
    imports_ok = check_imports()
    
    print("\n" + "="*50)
    if structure_ok and imports_ok:
        print("✅ Build successful!")
        sys.exit(0)
    else:
        print("❌ Build failed!")
        sys.exit(1)
