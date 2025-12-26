import enum
from pynput import keyboard, mouse
import time
import random


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


keyboard_controller = keyboard.Controller()
mouse_controller = mouse.Controller()

# Map key names to pynput Key objects
SPECIAL_KEYS = {
    "shift": keyboard.Key.shift,
    "ctrl": keyboard.Key.ctrl,
    "alt": keyboard.Key.alt,
    "cmd": keyboard.Key.cmd,
    "command": keyboard.Key.cmd,
    "option": keyboard.Key.alt,
    "f1": keyboard.Key.f1,
    "f2": keyboard.Key.f2,
    "f3": keyboard.Key.f3,
    "f4": keyboard.Key.f4,
    "f5": keyboard.Key.f5,
    "f6": keyboard.Key.f6,
    "f7": keyboard.Key.f7,
    "f8": keyboard.Key.f8,
    "f9": keyboard.Key.f9,
    "f10": keyboard.Key.f10,
    "f11": keyboard.Key.f11,
    "f12": keyboard.Key.f12,
    "up": keyboard.Key.up,
    "down": keyboard.Key.down,
    "left": keyboard.Key.left,
    "right": keyboard.Key.right,
    "home": keyboard.Key.home,
    "end": keyboard.Key.end,
    "pageup": keyboard.Key.page_up,
    "pagedown": keyboard.Key.page_down,
    "enter": keyboard.Key.enter,
    "return": keyboard.Key.enter,
    "tab": keyboard.Key.tab,
    "backspace": keyboard.Key.backspace,
    "delete": keyboard.Key.delete,
    "esc": keyboard.Key.esc,
    "escape": keyboard.Key.esc,
    "space": keyboard.Key.space,
}


def left_click():
    send_input("mouse", "left", "down")
    time.sleep(0.05 + random.uniform(0, 0.05))  # small random delay
    send_input("mouse", "left", "up")


def press_and_release(delay_ms, *keys):
    """
    Press multiple keys in order, then release them in reverse order.

    delay_ms: Time in milliseconds between each press/release action
    *keys: Variable number of key names to press

    Example: press_and_release(50, "shift", "a")
             -> press shift, wait, press a, wait, release a, wait, release shift
    """

    # sprinkle some randomness in delay
    delay_ms
    delay_s = delay_ms / 1000.0

    def rand_delay_s():
        two_percent = delay_ms * 0.02
        return (random.uniform(-two_percent, two_percent) + delay_ms) / 1000.0

    # Press all keys in order
    for key in keys:
        send_input("keyboard", key, "down")
        if delay_ms > 0:
            time.sleep(rand_delay_s() / 2)

    time.sleep(rand_delay_s())
    # Release all keys in reverse order
    for key in reversed(keys):
        send_input("keyboard", key, "up")
        if delay_s > 0:
            time.sleep(rand_delay_s() / 2)


def send_input(type, key, action):
    """
    type: "keyboard" or "mouse"
    key: for keyboard, the key name; for mouse, "left", "right", or "middle"
    action: "down" or "up"
    """
    if type == "keyboard":
        # Convert key name to pynput key
        pynput_key = SPECIAL_KEYS.get(key.lower(), key)

        if action == "down":
            keyboard_controller.press(pynput_key)
        elif action == "up":
            keyboard_controller.release(pynput_key)
    elif type == "mouse":
        # Convert button name to pynput button
        button = getattr(mouse.Button, key)

        if action == "down":
            mouse_controller.press(button)
        elif action == "up":
            mouse_controller.release(button)
