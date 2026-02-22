F13::
{
    if WinActive("ahk_exe DaVinci Resolve.exe")
    {
        WinActivate "ahk_exe DaVinci Resolve.exe"
        Sleep 150
        Send "^+!r"
    }
}
