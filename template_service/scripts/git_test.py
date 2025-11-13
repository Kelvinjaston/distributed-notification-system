#!/usr/bin/env python3
"""
Git test runner script for Template Service.

This script runs unit tests and integration tests before push,
ensuring code quality and test coverage.
"""

import subprocess
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent

def run_pytest():
    """Run pytest with coverage report."""
    print("=" * 60)
    print("Running pytest with coverage report...")
    print("=" * 60)
    
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--cov=app",
        "--cov=services",
        "--cov-report=html",
        "--cov-report=term",
        "--junit-xml=test-results.xml",
    ]
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode

def run_unit_tests():
    """Run only unit tests."""
    print("\n" + "=" * 60)
    print("Running unit tests...")
    print("=" * 60)
    
    cmd = [
        "pytest",
        "tests/unit/",
        "-v",
        "--tb=short",
    ]
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode

def run_integration_tests():
    """Run only integration tests."""
    print("\n" + "=" * 60)
    print("Running integration tests...")
    print("=" * 60)
    
    cmd = [
        "pytest",
        "tests/integration/",
        "-v",
        "--tb=short",
    ]
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode

def main():
    """Main test runner."""
    print("Template Service - Git Test Runner")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "unit":
            return run_unit_tests()
        elif test_type == "integration":
            return run_integration_tests()
        elif test_type == "all":
            return run_pytest()
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: git_test.py [unit|integration|all]")
            return 1
    else:
        # Run all tests by default
        return run_pytest()

if __name__ == "__main__":
    sys.exit(main())
