#Requires AutoHotkey v2.0

F13::
{
    if WinActive("ahk_exe Resolve.exe")
    {
        WinActivate "ahk_exe Resolve.exe"
        Sleep 150
        Send "^+!r"
    }
}
