# coding=utf-8
# Main code taken from https://github.com/zhiyiYo/PyQt-Frameless-Window
import ctypes
import sys
from ctypes import POINTER, Structure, c_int, WinDLL, c_bool, sizeof, pointer, byref, windll
from ctypes.wintypes import DWORD, HWND, ULONG, POINT, RECT, UINT, LONG, LPCVOID
from enum import Enum

import win32con
import win32gui


class WINDOWCOMPOSITIONATTRIB(Enum):
    WCA_UNDEFINED = 0
    WCA_NCRENDERING_ENABLED = 1
    WCA_NCRENDERING_POLICY = 2
    WCA_TRANSITIONS_FORCEDISABLED = 3
    WCA_ALLOW_NCPAINT = 4
    WCA_CAPTION_BUTTON_BOUNDS = 5
    WCA_NONCLIENT_RTL_LAYOUT = 6
    WCA_FORCE_ICONIC_REPRESENTATION = 7
    WCA_EXTENDED_FRAME_BOUNDS = 8
    WCA_HAS_ICONIC_BITMAP = 9
    WCA_THEME_ATTRIBUTES = 10
    WCA_NCRENDERING_EXILED = 11
    WCA_NCADORNMENTINFO = 12
    WCA_EXCLUDED_FROM_LIVEPREVIEW = 13
    WCA_VIDEO_OVERLAY_ACTIVE = 14
    WCA_FORCE_ACTIVEWINDOW_APPEARANCE = 15
    WCA_DISALLOW_PEEK = 16
    WCA_CLOAK = 17
    WCA_CLOAKED = 18
    WCA_ACCENT_POLICY = 19
    WCA_FREEZE_REPRESENTATION = 20
    WCA_EVER_UNCLOAKED = 21
    WCA_VISUAL_OWNER = 22
    WCA_HOLOGRAPHIC = 23
    WCA_EXCLUDED_FROM_DDA = 24
    WCA_PASSIVEUPDATEMODE = 25
    WCA_USEDARKMODECOLORS = 26
    WCA_CORNER_STYLE = 27
    WCA_PART_COLOR = 28
    WCA_DISABLE_MOVESIZE_FEEDBACK = 29
    WCA_LAST = 30


class ACCENT_STATE(Enum):
    """ Client area status enumeration class """
    ACCENT_DISABLED = 0
    ACCENT_ENABLE_GRADIENT = 1
    ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
    ACCENT_ENABLE_BLURBEHIND = 3           # Aero effect
    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4    # Acrylic effect
    ACCENT_ENABLE_HOSTBACKDROP = 5         # Mica effect
    ACCENT_INVALID_STATE = 6


class ACCENT_POLICY(Structure):
    """ Specific attributes of client area """

    _fields_ = [
        ("AccentState",     DWORD),
        ("AccentFlags",     DWORD),
        ("GradientColor",   DWORD),
        ("AnimationId",     DWORD),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attribute",   DWORD),
        # Pointer() receives any ctypes type and returns a pointer type
        ("Data",        POINTER(ACCENT_POLICY)),
        ("SizeOfData",  ULONG),
    ]


class DWMNCRENDERINGPOLICY(Enum):
    DWMNCRP_USEWINDOWSTYLE = 0
    DWMNCRP_DISABLED = 1
    DWMNCRP_ENABLED = 2
    DWMNCRP_LAS = 3


class DWM_WINDOW_CORNER_PREFERENCE(Enum):
    DWMWCP_DEFAULT = 0
    DWMWCP_DONOTROUND = 1
    DWMWCP_ROUND = 2
    DWMWCP_ROUNDSMALL = 3


class DWMWINDOWATTRIBUTE(Enum):
    DWMWA_NCRENDERING_ENABLED = 1
    DWMWA_NCRENDERING_POLICY = 2
    DWMWA_TRANSITIONS_FORCEDISABLED = 3
    DWMWA_ALLOW_NCPAINT = 4
    DWMWA_CAPTION_BUTTON_BOUNDS = 5
    DWMWA_NONCLIENT_RTL_LAYOUT = 6
    DWMWA_FORCE_ICONIC_REPRESENTATION = 7
    DWMWA_FLIP3D_POLICY = 8
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    DWMWA_HAS_ICONIC_BITMAP = 10
    DWMWA_DISALLOW_PEEK = 11
    DWMWA_EXCLUDED_FROM_PEEK = 12
    DWMWA_CLOAK = 13
    DWMWA_CLOAKED = 14
    DWMWA_FREEZE_REPRESENTATION = 15
    DWMWA_PASSIVE_UPDATE_MODE = 16
    DWMWA_USE_HOSTBACKDROPBRUSH = 17

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_WINDOW_CORNER_PREFERENCE = 33

    DWMWA_BORDER_COLOR = 20
    DWMWA_CAPTION_COLOR = 21
    DWMWA_TEXT_COLOR = 22
    DWMWA_VISIBLE_FRAME_BORDER_THICKNESS = 23
    DWMWA_LAST = 24


class MARGINS(Structure):
    _fields_ = [
        ("cxLeftWidth",     c_int),
        ("cxRightWidth",    c_int),
        ("cyTopHeight",     c_int),
        ("cyBottomHeight",  c_int),
    ]


class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved",      POINT),
        ("ptMaxSize",       POINT),
        ("ptMaxPosition",   POINT),
        ("ptMinTrackSize",  POINT),
        ("ptMaxTrackSize",  POINT),
    ]


class PWINDOWPOS(Structure):
    _fields_ = [
        ('hWnd',            HWND),
        ('hwndInsertAfter', HWND),
        ('x',               c_int),
        ('y',               c_int),
        ('cx',              c_int),
        ('cy',              c_int),
        ('flags',           UINT)
    ]


class NCCALCSIZE_PARAMS(Structure):
    _fields_ = [
        ('rgrc', RECT*3),
        ('lppos', POINTER(PWINDOWPOS))
    ]


LPNCCALCSIZE_PARAMS = POINTER(NCCALCSIZE_PARAMS)

user32 = WinDLL("user32")
dwmapi = WinDLL("dwmapi")
SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
DwmExtendFrameIntoClientArea = dwmapi.DwmExtendFrameIntoClientArea
DwmSetWindowAttribute = dwmapi.DwmSetWindowAttribute
SetWindowCompositionAttribute.restype = c_bool
DwmExtendFrameIntoClientArea.restype = LONG
DwmSetWindowAttribute.restype = LONG
SetWindowCompositionAttribute.argtypes = [
    c_int,
    POINTER(WINDOWCOMPOSITIONATTRIBDATA),
]
DwmSetWindowAttribute.argtypes = [c_int, DWORD, LPCVOID, DWORD]
DwmExtendFrameIntoClientArea.argtypes = [c_int, POINTER(MARGINS)]

# Initialize structure
accentPolicy = ACCENT_POLICY()
winCompAttrData = WINDOWCOMPOSITIONATTRIBDATA()
winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
winCompAttrData.SizeOfData = sizeof(accentPolicy)
winCompAttrData.Data = pointer(accentPolicy)


def setAcrylicEffect(hWnd, gradientColor="#99F2F2F2"):
    """ Add the acrylic effect to the window

    Parameters
    ----------
    hWnd: int or `sip.voidptr`
        Window handle

    gradientColor: str
        Hexadecimal acrylic mixed color, corresponding to four RGBA channels
    """
    gradientColor = DWORD(int(gradientColor.replace("#", ""), base=16))
    # animationId = DWORD(animationId)
    # accentFlags = DWORD(0x20 | 0x40 | 0x80 | 0x100) if enableShadow else DWORD(0)
    accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_ACRYLICBLURBEHIND.value
    accentPolicy.GradientColor = gradientColor
    accentPolicy.AccentFlags = ACCENT_STATE.ACCENT_ENABLE_TRANSPARENTGRADIENT.value
    # accentPolicy.AnimationId = animationId
    winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
    SetWindowCompositionAttribute(int(hWnd), pointer(winCompAttrData))


def setMicaEffect(hWnd, isDarkMode=False):
    """ Add the mica effect to the window (Win11 only)

    Parameters
    ----------
    hWnd: int or `sip.voidptr`
        Window handle

    isDarkMode: bool
        whether to use dark mode mica effect
    """

    hWnd = int(hWnd)
    margins = MARGINS(-1, -1, -1, -1)
    DwmExtendFrameIntoClientArea(hWnd, byref(margins))

    winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
    accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_HOSTBACKDROP.value
    SetWindowCompositionAttribute(hWnd, pointer(winCompAttrData))

    if isDarkMode:
        winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_USEDARKMODECOLORS.value
        SetWindowCompositionAttribute(hWnd, pointer(winCompAttrData))

    if sys.getwindowsversion().build < 22523:
        DwmSetWindowAttribute(hWnd, 1029, byref(c_int(1)), 4)
    else:
        DwmSetWindowAttribute(hWnd, 38, byref(c_int(2)), 4)


def setAeroEffect(hWnd):
    """ Add the aero effect to the window

    Parameters
    ----------
    hWnd: int or `sip.voidptr`
        Window handle
    """
    winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
    accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_BLURBEHIND.value
    SetWindowCompositionAttribute(int(hWnd), pointer(winCompAttrData))


def addWindowAnimation(hWnd):
    """ Enables the maximize and minimize animation of the window

    Parameters
    ----------
    hWnd : int or `sip.voidptr`
        Window handle
    """
    hWnd = int(hWnd)
    style = win32gui.GetWindowLong(hWnd, win32con.GWL_STYLE)
    win32gui.SetWindowLong(hWnd, win32con.GWL_STYLE, style | win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_CAPTION | win32con.CS_DBLCLKS | win32con.WS_THICKFRAME)


def removeBackgroundEffect(hWnd):
    """ Remove background effect

    Parameters
    ----------
    hWnd: int or `sip.voidptr`
        Window handle
    """
    accentPolicy.AccentState = ACCENT_STATE.ACCENT_DISABLED.value
    SetWindowCompositionAttribute(int(hWnd), pointer(winCompAttrData))


def addMenuShadowEffect(hWnd):
    """ Add DWM shadow to menu

    Parameters
    ----------
    hWnd: int or `sip.voidptr`
        Window handle
    """
    hWnd = int(hWnd)
    DwmSetWindowAttribute(hWnd, DWMWINDOWATTRIBUTE.DWMWA_NCRENDERING_POLICY.value, byref(c_int(DWMNCRENDERINGPOLICY.DWMNCRP_ENABLED.value)), 4)
    margins = MARGINS(-1, -1, -1, -1)
    DwmExtendFrameIntoClientArea(hWnd, byref(margins))


def removeShadowEffect(hWnd):
    """ Remove DWM shadow from the window

    Parameters
    ----------
    hWnd: int or `sip.voidptr`
        Window handle
    """
    hWnd = int(hWnd)
    DwmSetWindowAttribute(int(hWnd), DWMWINDOWATTRIBUTE.DWMWA_NCRENDERING_POLICY.value, byref(c_int(DWMNCRENDERINGPOLICY.DWMNCRP_DISABLED.value)), 4)


def setRoundedCorners(hWnd):
    DwmSetWindowAttribute(int(hWnd), DWMWINDOWATTRIBUTE.DWMWA_WINDOW_CORNER_PREFERENCE.value, byref(c_int(DWM_WINDOW_CORNER_PREFERENCE.DWMWCP_ROUND.value)), 4)


def removeRoundedCorners(hWnd):
    DwmSetWindowAttribute(int(hWnd), DWMWINDOWATTRIBUTE.DWMWA_WINDOW_CORNER_PREFERENCE.value, byref(c_int(DWM_WINDOW_CORNER_PREFERENCE.DWMWCP_DONOTROUND.value)), 4)


def SetImmersiveTitleBar(hWnd, isDarkMode=False):
    DwmSetWindowAttribute(int(hWnd), DWMWINDOWATTRIBUTE.DWMWA_USE_IMMERSIVE_DARK_MODE.value, byref(c_int(1 if isDarkMode else 0)), 4)

class AppMode:
    Default = 0
    AllowDark = 1
    ForceDark = 2
    ForceLight = 3
    Max = 4

uxtheme = ctypes.WinDLL("uxtheme.dll")
SetPreferredAppMode = uxtheme[135]
FlushMenuThemes = uxtheme[136]

def SetMenuTheme(IsDarkMode: bool):
    FlushMenuThemes()
    SetPreferredAppMode(AppMode.ForceDark if IsDarkMode else AppMode.ForceLight)