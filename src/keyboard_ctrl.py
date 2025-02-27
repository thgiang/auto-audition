# Ref: https://stackoverflow.com/a/13615802

import ctypes
from ctypes import wintypes
import time

user32 = ctypes.WinDLL('user32', use_last_error=True)

class InputType:
  INPUT_MOUSE    = 0
  INPUT_KEYBOARD = 1
  INPUT_HARDWARE = 2

class KeyEvent:
  KEYEVENTF_EXTENDEDKEY = 0x0001
  KEYEVENTF_KEYUP       = 0x0002
  KEYEVENTF_UNICODE     = 0x0004
  KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

class KeyDef:
  """
  Ref: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
  """
  VK_TAB  = 0x09
  VK_MENU = 0x12
  VK_BACKSPACE = 0x08
  VK_SPACE = 0x20
  VK_F5 = 0x74
  VK_F6 = 0x75
  VK_F7 = 0x76

  VK_NUMPAD1 = 0x61 # 97
  VK_NUMPAD2 = 0x62 # 98
  VK_NUMPAD3 = 0x63 # 99
  VK_NUMPAD4 = 0x64 # 100
  VK_NUMPAD5 = 0x65 # 101
  VK_NUMPAD6 = 0x66 # 102
  VK_NUMPAD7 = 0x67 # 103
  VK_NUMPAD8 = 0x68 # 104
  VK_NUMPAD9 = 0x69 # 105

  W_KEY = 0x57
  A_KEY = 0x41
  S_KEY = 0x53
  D_KEY = 0x44

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KeyEvent.KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

class KeyboardCtrl:
  PRESS_SLEEP = 0.04

  @staticmethod
  def press_key(hexKeyCode):
      x = INPUT(type=InputType.INPUT_KEYBOARD,
                ki=KEYBDINPUT(wVk=hexKeyCode))
      user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

  @staticmethod
  def release_key(hexKeyCode):
      x = INPUT(type=InputType.INPUT_KEYBOARD,
                ki=KEYBDINPUT(wVk=hexKeyCode,
                              dwFlags=KeyEvent.KEYEVENTF_KEYUP))
      user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

  @staticmethod
  def press_and_release(hexKeyCode):
    KeyboardCtrl.press_key(hexKeyCode)
    time.sleep(KeyboardCtrl.PRESS_SLEEP)
    KeyboardCtrl.release_key(hexKeyCode)
    time.sleep(KeyboardCtrl.PRESS_SLEEP)

def AltTab():
    """Press Alt+Tab and hold Alt key for 2 seconds
    in order to see the overlay.
    """
    KeyboardCtrl.press_key(KeyDef.VK_MENU)   # Alt
    KeyboardCtrl.press_key(KeyDef.VK_TAB)    # Tab
    KeyboardCtrl.release_key(KeyDef.VK_TAB)  # Tab~
    time.sleep(2)
    KeyboardCtrl.release_key(KeyDef.VK_MENU) # Alt~

if __name__ == "__main__":
    AltTab()
