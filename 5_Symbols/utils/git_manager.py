"""
Git management utility for Stream Deck automation
"""

import subprocess
from typing import Tuple, List

class GitManager:
    """Manage Git operations"""

    def __init__(self, repo_path: str):
        """
        Initialize Git manager

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path

    def git_command(self, command: List[str]) -> Tuple[str, str, int]:
        """
        Execute a git command

        Args:
            command: Git command as list of arguments

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        result = subprocess.run(
            ['git', '-C', self.repo_path] + command,
            capture_output=True,
            text=True
        )
        return result.stdout, result.stderr, result.returncode

    def status(self) -> str:
        """
        Get git status

        Returns:
            Short status output
        """
        stdout, stderr, code = self.git_command(['status', '--short'])
        return stdout

    def get_current_branch(self) -> str:
        """
        Get current branch name

        Returns:
            Branch name
        """
        stdout, stderr, code = self.git_command(['branch', '--show-current'])
        return stdout.strip()

    def quick_commit(self, message: str) -> bool:
        """
        Quick commit all changes

        Args:
            message: Commit message

        Returns:
            True if successful
        """
        self.git_command(['add', '.'])
        stdout, stderr, code = self.git_command(['commit', '-m', message])
        return code == 0

    def push(self, remote: str = 'origin', branch: str = None) -> bool:
        """
        Push to remote

        Args:
            remote: Remote name (default: origin)
            branch: Branch name (default: current branch)

        Returns:
            True if successful
        """
        if branch is None:
            branch = self.get_current_branch()

        stdout, stderr, code = self.git_command(['push', remote, branch])
        return code == 0

    def pull(self, remote: str = 'origin', branch: str = None) -> bool:
        """
        Pull from remote

        Args:
            remote: Remote name (default: origin)
            branch: Branch name (default: current branch)

        Returns:
            True if successful
        """
        if branch is None:
            branch = self.get_current_branch()

        stdout, stderr, code = self.git_command(['pull', remote, branch])
        return code == 0

    def stash(self) -> bool:
        """
        Stash current changes

        Returns:
            True if successful
        """
        stdout, stderr, code = self.git_command(['stash'])
        return code == 0

    def stash_pop(self) -> bool:
        """
        Pop stashed changes

        Returns:
            True if successful
        """
        stdout, stderr, code = self.git_command(['stash', 'pop'])
        return code == 0

    def switch_branch(self, branch: str) -> bool:
        """
        Switch to a different branch

        Args:
            branch: Branch name

        Returns:
            True if successful
        """
        stdout, stderr, code = self.git_command(['switch', branch])
        return code == 0

    def get_log(self, count: int = 10) -> str:
        """
        Get recent commit log

        Args:
            count: Number of commits to retrieve

        Returns:
            Formatted log output
        """
        stdout, stderr, code = self.git_command([
            'log',
            f'-{count}',
            '--oneline',
            '--decorate'
        ])
        return stdout
