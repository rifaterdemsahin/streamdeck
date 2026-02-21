"""
Notification utility for Stream Deck automation
Shows Windows notifications
"""

import platform
import subprocess

def show_notification(title: str, message: str, duration: int = 5):
    """
    Show system notification

    Args:
        title: Notification title
        message: Notification message
        duration: Duration in seconds (Windows only)
    """
    system = platform.system()

    if system == "Windows":
        _show_windows_notification(title, message, duration)
    elif system == "Darwin":  # macOS
        _show_macos_notification(title, message)
    elif system == "Linux":
        _show_linux_notification(title, message)
    else:
        print(f"{title}: {message}")

def _show_windows_notification(title: str, message: str, duration: int):
    """Show Windows 10/11 notification using PowerShell"""
    # Escape quotes in message
    message = message.replace('"', '""')
    title = title.replace('"', '""')

    ps_script = f'''
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $template = @"
    <toast>
        <visual>
            <binding template="ToastGeneric">
                <text>{title}</text>
                <text>{message}</text>
            </binding>
        </visual>
    </toast>
    "@

    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Stream Deck Automation").Show($toast)
    '''

    subprocess.run(
        ['powershell', '-Command', ps_script],
        capture_output=True,
        text=True
    )

def _show_macos_notification(title: str, message: str):
    """Show macOS notification using osascript"""
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(['osascript', '-e', script], capture_output=True)

def _show_linux_notification(title: str, message: str):
    """Show Linux notification using notify-send"""
    subprocess.run(['notify-send', title, message], capture_output=True)
