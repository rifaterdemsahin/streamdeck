; Red Marker for DaVinci Resolve
#HotIf WinActive("ahk_exe Resolve.exe")

F13::
{
    Send "^+!r"  ; Ctrl+Alt+Shift+R
}

#HotIf
