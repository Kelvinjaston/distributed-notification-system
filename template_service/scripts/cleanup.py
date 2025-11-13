#!/usr/bin/env python3
"""
Cleanup script for Template Service.

This script removes unnecessary files and organizes the project structure
to be Pylance-compatible.
"""

import os
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).parent.parent

# Files and directories to remove
FILES_TO_REMOVE = [
    "app/api.py",  # Old file - replaced with app/api/routes.py
]

DIRS_TO_REMOVE = [
    # Add any unnecessary directories here
]

def cleanup():
    """Remove unnecessary files."""
    print("=" * 60)
    print("TEMPLATE SERVICE CLEANUP")
    print("=" * 60)
    
    # Remove files
    print("\n📁 Removing unnecessary files...")
    for file_path in FILES_TO_REMOVE:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"✅ Deleted: {file_path}")
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")
        else:
            print(f"⏭️  Skipped (not found): {file_path}")
    
    # Remove directories
    print("\n📁 Removing unnecessary directories...")
    for dir_path in DIRS_TO_REMOVE:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"✅ Deleted directory: {dir_path}")
            except Exception as e:
                print(f"❌ Failed to delete directory {dir_path}: {e}")
        else:
            print(f"⏭️  Skipped directory (not found): {dir_path}")
    
    print("\n" + "=" * 60)
    print("✅ CLEANUP COMPLETE")
    print("=" * 60)
    print("\nYour project is now organized for Pylance compatibility!")
    print("Run: python scripts/structure_report.py to verify the structure")

if __name__ == "__main__":
    cleanup()
