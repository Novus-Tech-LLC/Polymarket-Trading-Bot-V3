"""
Entry point for running as a module: python -m src
"""
from src.main import main
import asyncio
import sys

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
