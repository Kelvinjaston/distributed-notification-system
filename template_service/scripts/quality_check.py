#!/usr/bin/env python3
"""
Script to check for code quality issues using various linters and type checkers.

Runs:
- Pylint: Python code analysis
- Mypy: Static type checking
- Flake8: Style guide enforcement
- Black: Code formatting check
"""

import subprocess
import sys
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path(__file__).parent.parent
PYTHON_FILES = ["app", "services", "tests", "scripts"]

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode

def main():
    """Run all quality checks."""
    errors = []
    
    # Check if tools are installed
    tools_to_check = ["pylint", "mypy", "flake8", "black"]
    
    # Run Black formatting check
    print("\n1. Checking code formatting with Black...")
    black_cmd = ["black", "--check", "--diff"] + PYTHON_FILES
    if run_command(black_cmd, "Black code formatter check") != 0:
        errors.append("Black formatting issues found")
    
    # Run Flake8
    print("\n2. Checking style with Flake8...")
    flake8_cmd = ["flake8"] + PYTHON_FILES
    if run_command(flake8_cmd, "Flake8 style check") != 0:
        errors.append("Flake8 style issues found")
    
    # Run Pylint
    print("\n3. Checking with Pylint...")
    pylint_cmd = ["pylint"] + PYTHON_FILES
    if run_command(pylint_cmd, "Pylint analysis") != 0:
        errors.append("Pylint issues found")
    
    # Run Mypy
    print("\n4. Type checking with Mypy...")
    mypy_cmd = ["mypy"] + PYTHON_FILES
    if run_command(mypy_cmd, "Mypy type checking") != 0:
        errors.append("Mypy type checking issues found")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("QUALITY CHECK SUMMARY")
    print("=" * 60)
    
    if errors:
        print(f"\n{len(errors)} issue(s) found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("\n✅ All quality checks passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
