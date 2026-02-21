#!/usr/bin/env python3
"""
Link Checker for Stream Deck Project

This script scans all markdown and HTML files in the project to check:
- Internal file references (relative paths)
- External URLs
- Broken links
- And provides options to fix them automatically
"""

import os
import re
import requests
import pathlib
from urllib.parse import urlparse
from typing import List, Dict, Set, Tuple
from pathlib import Path
import sys
import time
import argparse

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.logger import setup_logger
    logger = setup_logger('link_checker')
except ImportError:
    # Fallback logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('link_checker')

class LinkChecker:
    def __init__(self, root_path: str = ".", timeout: int = 10, max_retries: int = 3):
        self.root_path = Path(root_path).resolve()
        self.timeout = timeout
        self.max_retries = max_retries
        self.checked_urls: Set[str] = set()
        self.url_cache: Dict[str, bool] = {}
        self.file_extensions = {'.md', '.html', '.htm', '.txt'}

    def find_files_to_check(self) -> List[Path]:
        """Find all markdown and HTML files in the project."""
        files = []
        for ext in self.file_extensions:
            files.extend(self.root_path.rglob(f'*{ext}'))
        return sorted(files)

    def extract_links_from_markdown(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from markdown content."""
        links = []

        # Markdown link patterns
        patterns = [
            # [text](url)
            r'\[([^\]]+)\]\(([^)]+)\)',
            # ![alt](url) for images
            r'!\[([^\]]*)\]\(([^)]+)\)',
            # Reference style: [text][ref] or [ref]: url
            r'\[([^\]]+)\]\[([^\]]+)\]',
            r'^[ ]*\[([^\]]+)\]:\s*(.+)

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main()),
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks (```) and inline code (`)
            if '```' in line or (line.strip().startswith('`') and line.strip().endswith('`')):
                continue

            for pattern in patterns:
                matches = re.finditer(pattern, line, re.MULTILINE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        link_text = match.group(1)
                        link_url = match.group(2).strip()

                        # Skip URLs that look like code (contain ${} or unusual characters)
                        if '${' in link_url or 'result[' in link_url or ':200' in link_url:
                            continue

                        links.append((link_url, line_num, link_text))

        return links

    def extract_links_from_html(self, content: str, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all links from HTML content."""
        links = []

        # HTML link patterns
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    link_url = match.group(1).strip()
                    link_text = match.group(2) if len(match.groups()) > 1 else ""

                    # Skip JavaScript template literals (dynamic content)
                    if '${' in link_url or '}' in link_url:
                        continue

                    # Skip template placeholders
                    if '_HERE' in link_url.upper() or 'PATH_HERE' in link_url.upper():
                        continue

                    links.append((link_url, line_num, link_text))

        return links

    def is_external_url(self, url: str) -> bool:
        """Check if URL is external (has scheme and netloc)."""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)

    def check_file_exists(self, file_path: str, relative_to: Path) -> Tuple[bool, str]:
        """Check if a local file exists."""
        try:
            # Handle absolute paths
            if file_path.startswith('/'):
                resolved_path = Path(file_path)
            else:
                # Handle relative paths
                resolved_path = (relative_to.parent / file_path).resolve()

            if resolved_path.exists():
                return True, str(resolved_path)
            else:
                return False, f"File not found: {resolved_path}"
        except Exception as e:
            return False, f"Error checking file: {e}"

    def check_url(self, url: str) -> Tuple[bool, str]:
        """Check if external URL is accessible."""
        if url in self.url_cache:
            return self.url_cache[url], "cached"

        # Skip certain URLs that might be problematic
        if any(skip in url.lower() for skip in ['localhost', '127.0.0.1', 'example.com']):
            return True, "skipped (local/development URL)"

        for attempt in range(self.max_retries):
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                success = response.status_code < 400
                message = f"HTTP {response.status_code}"
                self.url_cache[url] = success
                return success, message
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    self.url_cache[url] = False
                    return False, f"Request failed: {e}"
                time.sleep(1)  # Wait before retry

        return False, "Max retries exceeded"

    def check_link(self, url: str, file_path: Path) -> Tuple[bool, str]:
        """Check if a link is valid."""
        if self.is_external_url(url):
            return self.check_url(url)
        else:
            # Handle markdown renderer links (markdown_renderer.html#file.md)
            if 'markdown_renderer.html#' in url:
                base_url = url.split('#')[0]
                file_part = url.split('#')[1] if '#' in url else ''

                # Check if the markdown renderer exists
                base_check = self.check_file_exists(base_url, file_path)
                if not base_check[0]:
                    return base_check

                # If there's a file part, check if that file exists
                if file_part and '.' in file_part:  # Looks like a file extension
                    file_check = self.check_file_exists(file_part, self.root_path)
                    if not file_check[0]:
                        return False, f"Markdown renderer exists but referenced file not found: {file_part}"
                    return True, f"Valid markdown renderer link to {file_part}"

                return True, "Valid markdown renderer link"

            return self.check_file_exists(url, file_path)

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for links and check them."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract links based on file type
            if file_path.suffix.lower() == '.md':
                links = self.extract_links_from_markdown(content, file_path)
            elif file_path.suffix.lower() in ['.html', '.htm']:
                links = self.extract_links_from_html(content, file_path)
            else:
                links = []

            for url, line_num, link_text in links:
                # Skip anchor links and empty URLs
                if not url or url.startswith('#') or url == '':
                    continue

                is_valid, message = self.check_link(url, file_path)

                if not is_valid:
                    issues.append({
                        'file': str(file_path.relative_to(self.root_path)),
                        'line': line_num,
                        'url': url,
                        'text': link_text,
                        'error': message,
                        'type': 'external' if self.is_external_url(url) else 'internal'
                    })

        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")

        return issues

    def scan_project(self) -> List[Dict]:
        """Scan the entire project for broken links."""
        logger.info(f"Scanning project: {self.root_path}")
        files = self.find_files_to_check()
        logger.info(f"Found {len(files)} files to check")

        all_issues = []
        for i, file_path in enumerate(files, 1):
            logger.info(f"Checking {i}/{len(files)}: {file_path.relative_to(self.root_path)}")
            issues = self.scan_file(file_path)
            all_issues.extend(issues)

        return all_issues

    def fix_internal_link(self, issue: Dict) -> bool:
        """Attempt to fix an internal link issue."""
        file_path = self.root_path / issue['file']
        url = issue['url']

        # Try common fixes for internal links
        potential_fixes = [
            url,  # Original
            url.lstrip('./'),  # Remove leading ./
            f"./{url}",  # Add leading ./
            url.replace('\\', '/'),  # Fix Windows paths
        ]

        for fix in potential_fixes:
            is_valid, _ = self.check_file_exists(fix, file_path)
            if is_valid:
                logger.info(f"Found working alternative: {fix}")
                return self.replace_link_in_file(file_path, issue['line'], issue['url'], fix)

        return False

    def replace_link_in_file(self, file_path: Path, line_num: int, old_url: str, new_url: str) -> bool:
        """Replace a link in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Replace the URL in the line
                if file_path.suffix.lower() == '.md':
                    # Markdown link replacement
                    old_pattern = rf'\[([^\]]+)\]\({re.escape(old_url)}\)'
                    new_link = f'[{issue["text"]}]({new_url})'
                    new_line = re.sub(old_pattern, new_link, line)
                else:
                    # Simple string replacement for HTML
                    new_line = line.replace(old_url, new_url)

                if new_line != line:
                    lines[line_num - 1] = new_line

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"Fixed link in {file_path}:{line_num}")
                    return True

        except Exception as e:
            logger.error(f"Error fixing link in {file_path}: {e}")

        return False

    def generate_report(self, issues: List[Dict]) -> str:
        """Generate a report of all issues found."""
        report = []
        report.append("# Link Check Report")
        report.append(f"**Total issues found:** {len(issues)}")
        report.append("")

        if issues:
            # Group by file
            by_file = {}
            for issue in issues:
                file_name = issue['file']
                if file_name not in by_file:
                    by_file[file_name] = []
                by_file[file_name].append(issue)

            for file_name, file_issues in by_file.items():
                report.append(f"## {file_name}")
                report.append(f"**Issues:** {len(file_issues)}")
                report.append("")

                for issue in file_issues:
                    status = "❌" if issue['type'] == 'external' else "📁"
                    report.append(f"- **Line {issue['line']}:** {status} `{issue['url']}`")
                    report.append(f"  - Error: {issue['error']}")
                    if issue['text']:
                        report.append(f"  - Text: {issue['text']}")
                    report.append("")
        else:
            report.append("✅ No broken links found!")

        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Check and fix links in the project")
    parser.add_argument("--fix", action="store_true", help="Automatically fix internal link issues")
    parser.add_argument("--output", type=str, help="Output report file")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for URL checks")
    parser.add_argument("--path", type=str, default=".", help="Root path to scan")

    args = parser.parse_args()

    checker = LinkChecker(root_path=args.path, timeout=args.timeout)
    issues = checker.scan_project()

    # Generate report
    report = checker.generate_report(issues)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    # Auto-fix internal links if requested
    if args.fix:
        logger.info("Attempting to auto-fix internal links...")
        fixed_count = 0
        for issue in issues:
            if issue['type'] == 'internal':
                if checker.fix_internal_link(issue):
                    fixed_count += 1

        logger.info(f"Fixed {fixed_count} internal links")

    # Summary
    external_issues = [i for i in issues if i['type'] == 'external']
    internal_issues = [i for i in issues if i['type'] == 'internal']

    logger.info(f"Scan complete: {len(issues)} total issues")
    logger.info(f"  - External URL issues: {len(external_issues)}")
    logger.info(f"  - Internal file issues: {len(internal_issues)}")

    return len(issues)

if __name__ == "__main__":
    sys.exit(main())