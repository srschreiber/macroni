import enum
import pyautogui


class InputType(enum.Enum):
    # Letters
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    F = "f"
    G = "g"
    H = "h"
    I = "i"
    J = "j"
    K = "k"
    L = "l"
    M = "m"
    N = "n"
    O = "o"
    P = "p"
    Q = "q"
    R = "r"
    S = "s"
    T = "t"
    U = "u"
    V = "v"
    W = "w"
    X = "x"
    Y = "y"
    Z = "z"

    # Numbers
    NUM_0 = "0"
    NUM_1 = "1"
    NUM_2 = "2"
    NUM_3 = "3"
    NUM_4 = "4"
    NUM_5 = "5"
    NUM_6 = "6"
    NUM_7 = "7"
    NUM_8 = "8"
    NUM_9 = "9"

    # Special characters / Symbols
    SPACE = "space"
    EXCLAMATION = "!"
    AT = "@"
    HASH = "#"
    DOLLAR = "$"
    PERCENT = "%"
    CARET = "^"
    AMPERSAND = "&"
    ASTERISK = "*"
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    MINUS = "-"
    UNDERSCORE = "_"
    EQUALS = "="
    PLUS = "+"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    BACKSLASH = "\\"
    PIPE = "|"
    SEMICOLON = ";"
    COLON = ":"
    APOSTROPHE = "'"
    QUOTE = '"'
    COMMA = ","
    PERIOD = "."
    LESS_THAN = "<"
    GREATER_THAN = ">"
    SLASH = "/"
    QUESTION = "?"
    BACKTICK = "`"
    TILDE = "~"

    # Modifier keys
    SHIFT = "shift"
    CTRL = "ctrl"
    ALT = "alt"
    CMD = "cmd"
    COMMAND = "command"
    OPTION = "option"

    # Function keys
    F1 = "f1"
    F2 = "f2"
    F3 = "f3"
    F4 = "f4"
    F5 = "f5"
    F6 = "f6"
    F7 = "f7"
    F8 = "f8"
    F9 = "f9"
    F10 = "f10"
    F11 = "f11"
    F12 = "f12"

    # Navigation keys
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    HOME = "home"
    END = "end"
    PAGE_UP = "pageup"
    PAGE_DOWN = "pagedown"

    # Special keys
    ENTER = "enter"
    RETURN = "return"
    TAB = "tab"
    BACKSPACE = "backspace"
    DELETE = "delete"
    ESC = "esc"
    ESCAPE = "escape"

    # Mouse inputs
    LEFT_CLICK = "left_click"
    RIGHT_CLICK = "right_click"
    MIDDLE_CLICK = "middle_click"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"

def left_click():
    send_input("mouse", "left", "down")

def send_input(type, key, action):
    """
    type: "keyboard" or "mouse"
    key: for keyboard, the key name; for mouse, "left", "right", or "middle"
    action: "down" or "up"
    """
    if type == "keyboard":
        if action == "down":
            pyautogui.keyDown(key)
        elif action == "up":
            pyautogui.keyUp(key)
    elif type == "mouse":
        if action == "down":
            pyautogui.mouseDown(button=key)
        elif action == "up":
            pyautogui.mouseUp(button=key)