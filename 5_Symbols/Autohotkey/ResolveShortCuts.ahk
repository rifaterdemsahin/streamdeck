#HotIf WinActive("ahk_exe Resolve.exe")

F13::
{
    ; Click timeline area first to ensure focus, then send marker shortcut
    Click 700, 800  ; approximate timeline coordinates on your screen
    Sleep 50
    Send "^+!r"  ; Ctrl+Alt+Shift+R
}

#HotIf
