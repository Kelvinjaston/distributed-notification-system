#!/usr/bin/env python
"""
Setup script to initialize the project.
Installs dependencies, creates databases, runs migrations.
"""
import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_command(command: str, description: str) -> bool:
    """Run a shell command."""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed: {e.stderr}")
        return False


def main():
    """Run setup steps."""
    logger.info("=== Template Service Setup ===\n")

    steps = [
        ("pip install -r requirements.txt", "Install Python dependencies"),
        ("python scripts/migrate.py", "Initialize database"),
        ("python scripts/health_check.py", "Run health checks"),
    ]

    success = True
    for command, description in steps:
        if not run_command(command, description):
            success = False
            logger.error(f"Setup failed at: {description}")
            break
        logger.info("")

    if success:
        logger.info("=== Setup Complete ===")
        logger.info("You can now run: uvicorn app.main:app --reload")
        return 0
    else:
        logger.error("=== Setup Failed ===")
        return 1


if __name__ == "__main__":
    sys.exit(main())
