#HotIf WinActive("ahk_exe Resolve.exe")

F13::
{
    WinActivate "ahk_exe Resolve.exe"  ; force Resolve to stay focused
    Sleep 100
    Send "^+!r"  ; Ctrl+Alt+Shift+R
}

#HotIf
