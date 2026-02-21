"""
Clipboard management utility for Stream Deck automation
"""

import platform
import subprocess

def get_clipboard() -> str:
    """
    Get text from clipboard

    Returns:
        Clipboard content as string
    """
    system = platform.system()

    if system == "Windows":
        return _get_clipboard_windows()
    elif system == "Darwin":  # macOS
        return _get_clipboard_macos()
    elif system == "Linux":
        return _get_clipboard_linux()
    else:
        raise OSError(f"Unsupported platform: {system}")

def set_clipboard(text: str):
    """
    Set clipboard content

    Args:
        text: Text to copy to clipboard
    """
    system = platform.system()

    if system == "Windows":
        _set_clipboard_windows(text)
    elif system == "Darwin":  # macOS
        _set_clipboard_macos(text)
    elif system == "Linux":
        _set_clipboard_linux(text)
    else:
        raise OSError(f"Unsupported platform: {system}")

def _get_clipboard_windows() -> str:
    """Get clipboard on Windows using PowerShell"""
    result = subprocess.run(
        ['powershell', '-command', 'Get-Clipboard'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def _set_clipboard_windows(text: str):
    """Set clipboard on Windows using PowerShell"""
    subprocess.run(
        ['powershell', '-command', f'Set-Clipboard -Value "{text}"'],
        capture_output=True,
        text=True
    )

def _get_clipboard_macos() -> str:
    """Get clipboard on macOS using pbpaste"""
    result = subprocess.run(
        ['pbpaste'],
        capture_output=True,
        text=True
    )
    return result.stdout

def _set_clipboard_macos(text: str):
    """Set clipboard on macOS using pbcopy"""
    subprocess.run(
        ['pbcopy'],
        input=text.encode('utf-8'),
        capture_output=True
    )

def _get_clipboard_linux() -> str:
    """Get clipboard on Linux using xclip"""
    result = subprocess.run(
        ['xclip', '-selection', 'clipboard', '-o'],
        capture_output=True,
        text=True
    )
    return result.stdout

def _set_clipboard_linux(text: str):
    """Set clipboard on Linux using xclip"""
    subprocess.run(
        ['xclip', '-selection', 'clipboard'],
        input=text.encode('utf-8'),
        capture_output=True
    )
