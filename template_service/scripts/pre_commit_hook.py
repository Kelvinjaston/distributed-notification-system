#!/usr/bin/env python3
"""
Pre-commit hook script for the Template Service.

This script is run before each commit and ensures:
1. Code formatting complies with Black
2. No imports are unused
3. No obvious style violations
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """Run a command and return the return code."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode

def main():
    """Run pre-commit checks."""
    print("Running pre-commit checks...")
    
    # Get the list of staged files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Error: Failed to get staged files")
        return 1
    
    staged_files = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]
    
    if not staged_files:
        print("No Python files to check.")
        return 0
    
    print(f"Checking {len(staged_files)} file(s)...")
    
    # Check with Black
    print("\n1. Checking code formatting...")
    black_result = run_command(["black", "--check"] + staged_files)
    if black_result != 0:
        print("❌ Black formatting check failed. Run 'black .' to fix.")
        return 1
    
    print("✅ Black formatting check passed.")
    
    # Check for unused imports
    print("\n2. Checking for unused imports...")
    for file in staged_files:
        check_result = run_command(["pylint", "--disable=all", "--enable=unused-import", file])
        if check_result != 0:
            print(f"❌ Unused imports found in {file}")
            return 1
    
    print("✅ No unused imports found.")
    
    print("\n✅ All pre-commit checks passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
