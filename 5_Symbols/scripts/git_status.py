#!/usr/bin/env python3
"""
Script Name: git_status.py
Purpose: Check Git repository status
Author: Rifat Erdem Sahin
Description: Shows current branch and uncommitted changes
"""

import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.git_manager import GitManager
from utils.notification import show_notification

logger = setup_logger('git_status')

def main():
    """Get and display Git status"""
    try:
        # Get current working directory or use configured repo path
        repo_path = os.getenv('GIT_REPO_PATH', os.getcwd())
        logger.info(f"Checking Git status for: {repo_path}")

        git_mgr = GitManager(repo_path)

        # Get current branch
        branch = git_mgr.get_current_branch()

        # Get status
        status = git_mgr.status()

        if not status.strip():
            message = f"Branch: {branch}\nStatus: Clean"
        else:
            lines = status.strip().split('\n')
            file_count = len(lines)
            message = f"Branch: {branch}\nModified: {file_count} files"

        show_notification("Git Status", message)
        logger.info(f"Git status checked: {branch}")

        return 0

    except Exception as e:
        logger.error(f"Failed to get Git status: {e}", exc_info=True)
        show_notification("Git Error", str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
