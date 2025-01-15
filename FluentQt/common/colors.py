# coding=utf-8
import binascii
from typing import Union, Optional, TypeVar
from winreg import QueryValueEx, HKEY_CURRENT_USER, OpenKey, ConnectRegistry

from qtpy.QtGui import QColor

from .theme import fTheme


class Color:
    def __init__(self, color: str):
        self._color = color

    def set(self, color: str):
        self._color = color

    def get(self) -> str:
        return self._color

    def getColor(self) -> QColor:
        return QColor(self._color)

    def replace(self, __old: str, __new: str) -> str:
        return self._color.replace(__old, __new)

    def getAlphaAndColor(self) -> tuple[float | int, str]:
        alpha = 1
        if len(self._color) == 9:
            alpha = int(self._color[1:3], 16) / 255
            color = f"#{self._color[3:9]}"
        else:
            color = f"#{self._color[1:7]}"

        return alpha, color


class FAccentColor:
    _accent_color: Color

    def __init__(self):
        self._accent_color = Color("#00000000")

    def set(self, color: str):
        self._accent_color.set(color)

    def get(self) -> str:
        return self._accent_color.get()

    def getColor(self) -> QColor:
        return self._accent_color.getColor()

    def replace(self, __old: str, __new: str) -> str:
        return self._accent_color.replace(__old, __new)

    def getAlphaAndColor(self) -> tuple[float | int, str]:
        return self._accent_color.getAlphaAndColor()


class FColor:
    def __init__(self, dark: Union[str, 'FColor', FAccentColor], light: Optional[Union[str, 'FColor', FAccentColor]] = None, func = None):
        self.dark: Union[Color, FColor, FAccentColor] = Color(dark) if isinstance(dark, str) else dark

        self.light: Union[Color, FColor, FAccentColor] = (Color(light) if isinstance(light, str) else light) if light else self.dark
        self._func = func

    def get(self) -> str:
        color = self.dark.get() if fTheme.isDark() else self.light.get()
        if self._func:
            color = self._func(color)
        return color

    def getColor(self) -> QColor:
        return self.dark.getColor() if fTheme.isDark() else self.light.getColor()

    def replace(self, __old: str, __new: str) -> str:
        return self.dark.replace(__old, __new) if fTheme.isDark() else self.light.replace(__old, __new)

    def getAlphaAndColor(self) -> tuple[float | int, str]:
        return self.dark.getAlphaAndColor() if fTheme.isDark() else self.light.getAlphaAndColor()


class FColorWithFallback(FColor):
    def __init__(self, dark: Union[str, FColor, FAccentColor], light: Optional[Union[str, FColor, FAccentColor]] = None, dark_fallback: Optional[Union[str, FColor, FAccentColor]] = None, light_fallback: Optional[Union[str, FColor, FAccentColor]] = None, func = None):
        super().__init__(dark, light, func)
        self.dark_fallback: Union[Color, FColor, FAccentColor] = Color(dark_fallback) if isinstance(dark_fallback, str) else dark_fallback
        self.light_fallback: Union[Color, FColor, FAccentColor] = (Color(light_fallback) if isinstance(light_fallback, str) else light_fallback) if light_fallback else self.dark_fallback

    @property
    def fallback(self) -> Union[str, FColor, FAccentColor]:
        return self.dark_fallback if fTheme.isDark() else self.light_fallback


class FAccentColors:

    SystemAccentColorLight3 = FAccentColor()
    SystemAccentColorLight2 = FAccentColor()
    SystemAccentColorLight1 = FAccentColor()
    SystemAccentColor = FAccentColor()
    SystemAccentColorDark1 = FAccentColor()
    SystemAccentColorDark2 = FAccentColor()
    SystemAccentColorDark3 = FAccentColor()

    def __init__(self):
        self.update_accent_colors()

    @staticmethod
    def get_accent_colors() -> str:
        """

        :return:
        """
        registry = ConnectRegistry(None, HKEY_CURRENT_USER)
        key = OpenKey(registry, r'SOFTWARE\\Microsoft\Windows\\CurrentVersion\\Explorer\\Accent')
        key_value = QueryValueEx(key, 'AccentPalette')
        return binascii.hexlify(key_value[0]).decode('utf-8')

    @staticmethod
    def get_accent(accent: str) -> tuple:
        """

        :param accent:
        :return:
        """
        accent = tuple(int(accent[i:i + 2], 16) for i in (0, 2, 4))
        return accent[0], accent[1], accent[2]

    def update_accent_colors(self, accents: str | None = None) -> None:
        """
        Applies the accent colors to the theme.
        """
        accents = accents if accents else self.get_accent_colors()
        self.SystemAccentColorLight3.set(f"#{accents[0:6]}")
        self.SystemAccentColorLight2.set(f"#{accents[8:14]}")
        self.SystemAccentColorLight1.set(f"#{accents[16:22]}")
        self.SystemAccentColor.set(f"#{accents[24:30]}")
        self.SystemAccentColorDark1.set(f"#{accents[32:38]}")
        self.SystemAccentColorDark2.set(f"#{accents[40:46]}")
        self.SystemAccentColorDark3.set(f"#{accents[48:54]}")


Accents = FAccentColors()


class FColors:
    img_color = FColor("dark", "light")

    SystemAltHighColor = FColor("#FF000000", "#FFFFFFFF")
    SystemAltLowColor = FColor("#33000000", "#33FFFFFF")
    SystemAltMediumColor = FColor("#99000000", "#99FFFFFF")
    SystemAltMediumHighColor = FColor("#CC000000", "#CCFFFFFF")
    SystemAltMediumLowColor = FColor("#66000000", "#66FFFFFF")
    SystemBaseHighColor = FColor("#FFFFFFFF", "#FF000000")
    SystemBaseLowColor = FColor("#33FFFFFF", "#33000000")
    SystemBaseMediumColor = FColor("#99FFFFFF", "#99000000")
    SystemBaseMediumHighColor = FColor("#CCFFFFFF", "#CC000000")
    SystemBaseMediumLowColor = FColor("#66FFFFFF", "#66000000")
    SystemChromeAltLowColor = FColor("#FFF2F2F2", "#FF171717")
    SystemChromeBlackHighColor = FColor("#FF000000", "#FF000000")
    SystemChromeBlackLowColor = FColor("#33000000", "#33000000")
    SystemChromeBlackMediumLowColor = FColor("#66000000", "#66000000")
    SystemChromeBlackMediumColor = FColor("#CC000000", "#CC000000")
    SystemChromeDisabledHighColor = FColor("#FF333333", "#FFCCCCCC")
    SystemChromeDisabledLowColor = FColor("#FF858585", "#FF7A7A7A")
    SystemChromeGrayColor = FColor("#FF767676", "#FF767676")
    SystemChromeHighColor = FColor("#FF767676", "#FFCCCCCC")
    SystemChromeLowColor = FColor("#FF171717", "#FFF2F2F2")
    SystemChromeMediumColor = FColor("#FF1F1F1F", "#FFE6E6E6")
    SystemChromeMediumLowColor = FColor("#FF2B2B2B", "#FFF2F2F2")
    SystemChromeWhiteColor = FColor("#FFFFFFFF", "#FFFFFFFF")
    SystemErrorTextColor = FColor("#FFFFF000", "#FFC50500")
    SystemListLowColor = FColor("#19FFFFFF", "#19000000")
    SystemListMediumColor = FColor("#33FFFFFF", "#33000000")

    TextFillColorPrimary = FColor("#FFFFFF", "#E4000000")
    TextFillColorSecondary = FColor("#C5FFFFFF", "#9E000000")
    TextFillColorTertiary = FColor("#87FFFFFF", "#72000000")

    TextFillColorDisabled = FColor("#5DFFFFFF", "#5C000000")
    TextFillColorInverse = FColor("#E4000000", "#FFFFFF")

    AccentTextFillColorDisabled = FColor("#5DFFFFFF", "#5C000000")
    TextOnAccentFillColorSelectedText = FColor("#FFFFFF", "#FFFFFF")
    TextOnAccentFillColorPrimary = FColor("#000000", "#FFFFFF")
    TextOnAccentFillColorSecondary = FColor("#80000000", "#B3FFFFFF")
    TextOnAccentFillColorDisabled = FColor("#87FFFFFF", "#FFFFFF")

    ControlFillColorDefault = FColor("#0FFFFFFF", "#B3FFFFFF")
    ControlFillColorSecondary = FColor("#15FFFFFF", "#80F9F9F9")
    ControlFillColorTertiary = FColor("#08FFFFFF", "#4DF9F9F9")
    ControlFillColorDisabled = FColor("#0BFFFFFF", "#4DF9F9F9")
    ControlFillColorTransparent = FColor("#00000000")
    ControlFillColorInputActive = FColor("#B31E1E1E", "#FFFFFF")

    ControlStrongFillColorDefault = FColor("#8BFFFFFF", "#72000000")
    ControlStrongFillColorDisabled = FColor("#3FFFFFFF", "#51000000")

    ControlSolidFillColorDefault = FColor("#454545", "#FFFFFF")

    SubtleFillColorTransparent = FColor("#00FFFFFF", "#00FFFFFF")
    SubtleFillColorSecondary = FColor("#0FFFFFFF", "#09000000")
    SubtleFillColorTertiary = FColor("#0AFFFFFF", "#06000000")
    SubtleFillColorDisabled = FColor("#00FFFFFF", "#00FFFFFF")

    ControlAltFillColorTransparent = FColor("#00FFFFFF", "#00FFFFFF")
    ControlAltFillColorSecondary = FColor("#19000000", "#06000000")
    ControlAltFillColorTertiary = FColor("#0BFFFFFF", "#0F000000")
    ControlAltFillColorQuarternary = FColor("#12FFFFFF", "#18000000")
    ControlAltFillColorDisabled = FColor("#00FFFFFF", "#00FFFFFF")

    ControlOnImageFillColorDefault = FColor("#B31C1C1C", "#C9FFFFFF")
    ControlOnImageFillColorSecondary = FColor("#1A1A1A", "#F3F3F3")
    ControlOnImageFillColorTertiary = FColor("#131313", "#EBEBEB")
    ControlOnImageFillColorDisabled = FColor("#1E1E1E", "#00FFFFFF")

    AccentFillColorDisabled = FColor("#28FFFFFF", "#37000000")

    ControlStrokeColorDefault = FColor("#12FFFFFF", "#0F000000")
    ControlStrokeColorSecondary = FColor("#18FFFFFF", "#29000000")
    ControlStrokeColorOnAccentDefault = FColor("#14FFFFFF", "#14FFFFFF")
    ControlStrokeColorOnAccentSecondary = FColor("#23000000", "#66000000")
    ControlStrokeColorOnAccentTertiary = FColor("#37000000", "#37000000")
    ControlStrokeColorOnAccentDisabled = FColor("#33000000", "#0F000000")

    ControlStrokeColorForStrongFillWhenOnImage = FColor("#6B000000", "#59FFFFFF")

    CardStrokeColorDefault = FColor("#19000000", "#0F000000")
    CardStrokeColorDefaultSolid = FColor("#1C1C1C", "#EBEBEB")

    ControlStrongStrokeColorDefault = FColor("#8BFFFFFF", "#72000000")
    ControlStrongStrokeColorDisabled = FColor("#28FFFFFF", "#37000000")

    SurfaceStrokeColorDefault = FColor("#66757575", "#66757575")
    SurfaceStrokeColorFlyout = FColor("#33000000", "#0F000000")
    SurfaceStrokeColorInverse = FColor("#0F000000", "#15FFFFFF")

    DividerStrokeColorDefault = FColor("#15FFFFFF", "#0F000000")

    FocusStrokeColorOuter = FColor("#FFFFFF", "#E4000000")
    FocusStrokeColorInner = FColor("#B3000000", "#B3FFFFFF")

    CardBackgroundFillColorDefault = FColor("#0DFFFFFF", "#B3FFFFFF")
    CardBackgroundFillColorSecondary = FColor("#08FFFFFF", "#80F6F6F6")

    SmokeFillColorDefault = FColor("#4D000000", "#4D000000")

    LayerFillColorDefault = FColor("#4C3A3A3A", "#80FFFFFF")
    LayerFillColorAlt = FColor("#0DFFFFFF", "#FFFFFF")
    LayerOnAcrylicFillColorDefault = FColor("#09FFFFFF", "#40FFFFFF")
    LayerOnAccentAcrylicFillColorDefault = FColor("#09FFFFFF", "#40FFFFFF")

    LayerOnMicaBaseAltFillColorDefault = FColor("#733A3A3A", "#B3FFFFFF")
    LayerOnMicaBaseAltFillColorSecondary = FColor("#0FFFFFFF", "#0A000000")
    LayerOnMicaBaseAltFillColorTertiary = FColor("#2C2C2C", "#F9F9F9")
    LayerOnMicaBaseAltFillColorTransparent = FColor("#00FFFFFF", "#00000000")

    SolidBackgroundFillColorBase = FColor("#202020", "#F3F3F3")
    SolidBackgroundFillColorSecondary = FColor("#1C1C1C", "#EEEEEE")
    SolidBackgroundFillColorTertiary = FColor("#282828", "#F9F9F9")
    SolidBackgroundFillColorQuarternary = FColor("#2C2C2C", "#FFFFFF")
    SolidBackgroundFillColorTransparent = FColor("#00202020", "#00F3F3F3")
    SolidBackgroundFillColorBaseAlt = FColor("#0A0A0A", "#DADADA")

    SystemFillColorSuccess = FColor("#6CCB5F", "#0F7B0F")
    SystemFillColorCaution = FColor("#FCE100", "#9D5D00")
    SystemFillColorCritical = FColor("#FF99A4", "#C42B1C")
    SystemFillColorNeutral = FColor("#8BFFFFFF", "#72000000")
    SystemFillColorSolidNeutral = FColor("#9D9D9D", "#8A8A8A")
    SystemFillColorAttentionBackground = FColor("#08FFFFFF", "#80F6F6F6")
    SystemFillColorSuccessBackground = FColor("#393D1B", "#DFF6DD")
    SystemFillColorCautionBackground = FColor("#433519", "#FFF4CE")
    SystemFillColorCriticalBackground = FColor("#442726", "#FDE7E9")
    SystemFillColorNeutralBackground = FColor("#08FFFFFF", "#06000000")
    SystemFillColorSolidAttentionBackground = FColor("#2E2E2E", "#F7F7F7")
    SystemFillColorSolidNeutralBackground = FColor("#2E2E2E", "#F3F3F3")

    AccentTextFillColorPrimary = FColor(Accents.SystemAccentColorLight3, Accents.SystemAccentColorDark2)
    AccentTextFillColorSecondary = FColor(Accents.SystemAccentColorLight3, Accents.SystemAccentColorDark3)
    AccentTextFillColorTertiary = FColor(Accents.SystemAccentColorLight2, Accents.SystemAccentColorDark1)

    AccentFillColorSelectedTextBackground = Accents.SystemAccentColor

    AccentFillColorDefault = FColor(Accents.SystemAccentColorLight2, Accents.SystemAccentColorDark1)
    AccentFillColorSecondary = FColor(Accents.SystemAccentColorLight2, Accents.SystemAccentColorDark1, lambda x: f"#CC{x[1:7]}")
    AccentFillColorTertiary = FColor(Accents.SystemAccentColorLight2, Accents.SystemAccentColorDark1, lambda x: f"#CC{x[1:7]}")

    SystemFillColorAttention = FColor(Accents.SystemAccentColorLight2, Accents.SystemAccentColor)

    SystemControlTransparent = FColor("#00000000")

    SystemControlHighlightListAccentVeryHigh = FColor(Accents.SystemAccentColor, func=lambda x: f"#E6{x[1:7]}")
    SystemControlHighlightListAccentMediumLow = FColor(Accents.SystemAccentColor, func=lambda x: f"#BF{x[1:7]}")

    ApplicationPageBackgroundTheme = SolidBackgroundFillColorBase
    DefaultTextForegroundTheme = TextFillColorPrimary
    SystemControlFocusVisualPrimary = FocusStrokeColorOuter
    SystemControlFocusVisualSecondary = FocusStrokeColorInner

    SolidBackgroundFillColorLayer = FColor("#2B2B2B")

    AccentControlElevationBorder = ControlStrokeColorOnAccentDefault

    SystemChromeMediumHighColor = FColor("#FF323232", "#FFE6E6E6")
    SystemChromeAltMediumHighColor = FColor("#CC1F1F1F", "#CCFFFFFF")
    SystemChromeAltHighColor = FColor("#FF1C1C1C", "#FFFFFFFF")

    SystemControlAcrylic = FColorWithFallback(SystemChromeAltHighColor, None, SystemChromeMediumColor, func=lambda x: f"#CC{x[1:7]}")

    SystemControlAccentAcrylicAccentMediumHigh = FColorWithFallback(Accents.SystemAccentColor, None, Accents.SystemAccentColor, func=lambda x: f"#B3{x[1:7]}")

    SystemControlAccentDark1AcrylicAccentDark1 = FColorWithFallback(Accents.SystemAccentColorDark1, None, Accents.SystemAccentColorDark1, func=lambda x: f"#CC{x[1:7]}")

    SystemControlAccentDark2AcrylicAccentDark2MediumHigh = FColorWithFallback(Accents.SystemAccentColorDark2, None, Accents.SystemAccentColorDark2, func=lambda x: f"#B3{x[1:7]}")

    SystemControlAcrylicMediumHigh = FColorWithFallback(SystemChromeAltHighColor, None, SystemChromeMediumColor, func=lambda x: f"#B3{x[1:7]}")

    SystemControlChromeMediumLowAcrylicMedium = FColorWithFallback(SystemChromeAltHighColor, None, SystemChromeMediumLowColor, func=lambda x: f"#99{x[1:7]}")

    SystemControlBaseHighAcrylic = FColorWithFallback(SystemChromeAltHighColor, None, SystemBaseHighColor, func=lambda x: f"#CC{x[1:7]}")

    SystemControlBaseHighAcrylicMediumHigh = FColorWithFallback(SystemChromeAltHighColor, None, SystemBaseHighColor, func=lambda x: f"#B3{x[1:7]}")

    SystemControlBaseHighAcrylicMedium = FColorWithFallback(SystemChromeAltHighColor, None, SystemBaseHighColor, func=lambda x: f"#99{x[1:7]}")

    SystemControlChromeLowAcrylic = FColorWithFallback(SystemChromeAltHighColor, None, SystemChromeLowColor, func=lambda x: f"#CC{x[1:7]}")

    SystemControlChromeMediumAcrylicMedium = FColorWithFallback(SystemChromeAltHighColor, None, SystemChromeMediumColor, func=lambda x: f"#99{x[1:7]}")

    SystemControlChromeHighAcrylicMedium = FColorWithFallback(SystemChromeAltHighColor, None, SystemChromeHighColor, func=lambda x: f"#99{x[1:7]}")

    SystemControlBaseLowAcrylic = FColorWithFallback(SystemChromeAltHighColor, None, SystemBaseLowColor, func=lambda x: f"#CC{x[1:7]}")

    SystemControlBaseMediumLowAcrylicMedium = FColorWithFallback(SystemChromeAltHighColor, None, SystemBaseMediumLowColor, func=lambda x: f"#99{x[1:7]}")

    SystemControlAltLowAcrylic = FColorWithFallback(SystemChromeAltHighColor, None, SystemAltLowColor, func=lambda x: f"#CC{x[1:7]}")

    SystemControlAltMediumLowAcrylicMedium = FColorWithFallback(SystemChromeAltHighColor, None, SystemAltMediumLowColor, func=lambda x: f"#99{x[1:7]}")

    SystemControlAltHighAcrylic = FColorWithFallback(SystemChromeAltHighColor, None, SystemAltHighColor, func=lambda x: f"#CC{x[1:7]}")

    SystemControlTransientBorder = FColor("#5C000000", "#24000000")

    AcrylicFillColorDefault = FColorWithFallback("#CC2C2C2C", "#CCFCFCFC", "#2C2C2C", "#F9F9F9")

    AcrylicFillColorDefaultInverse = FColorWithFallback("#CCFCFCFC", "#CC2C2C2C", "#F9F9F9", "#2C2C2C")

    AcrylicFillColorBase = FColorWithFallback("#CC1C1C1C", "#CCF3F3F3", "#1C1C1C", "#EEEEEE")

    AccentAcrylicFillColorDefault = FColorWithFallback(Accents.SystemAccentColorDark1, Accents.SystemAccentColorLight3, Accents.SystemAccentColorDark1, Accents.SystemAccentColorLight3, func=lambda x: f"#CC{x[1:7]}")

    AccentAcrylicFillColorBase = FColorWithFallback(Accents.SystemAccentColorDark2, Accents.SystemAccentColorLight3, Accents.SystemAccentColorDark2, Accents.SystemAccentColorLight3, func=lambda x: f"#CC{x[1:7]}")

    SystemControlBackgroundAltMedium = SystemAltMediumColor
    SystemControlBackgroundAltMediumLow = SystemAltMediumLowColor
    SystemControlBackgroundChromeBlackLow = SystemChromeBlackLowColor
    SystemControlBackgroundChromeMediumLow = SystemChromeMediumLowColor
    SystemControlDisabledAccent = Accents.SystemAccentColor
    SystemControlDisabledBaseHigh = SystemBaseHighColor
    SystemControlDisabledBaseLow = SystemBaseLowColor
    SystemControlDisabledBaseMediumLow = SystemBaseMediumLowColor
    SystemControlDisabledChromeDisabledHigh = SystemChromeDisabledHighColor
    SystemControlDisabledChromeDisabledLow = SystemChromeDisabledLowColor
    SystemControlDisabledChromeHigh = SystemChromeHighColor
    SystemControlDisabledChromeMediumLow = SystemChromeMediumLowColor
    SystemControlDisabledListMedium = SystemListMediumColor
    SystemControlDisabledTransparent = FColor("#00000000")
    SystemControlRevealFocusVisual = Accents.SystemAccentColor
    SystemControlForegroundChromeHigh = SystemChromeHighColor
    SystemControlForegroundChromeDisabledLow = SystemChromeDisabledLowColor
    SystemControlForegroundChromeGray = SystemChromeGrayColor
    SystemControlHighlightAccent = Accents.SystemAccentColor
    SystemControlHighlightAltAccent = Accents.SystemAccentColor
    SystemControlHighlightAltAltHigh = SystemAltHighColor
    SystemControlHighlightAltBaseHigh = SystemBaseHighColor
    SystemControlHighlightAltBaseLow = SystemBaseLowColor
    SystemControlHighlightAltBaseMedium = SystemBaseMediumColor
    SystemControlHighlightAltBaseMediumHigh = SystemBaseMediumHighColor
    SystemControlHighlightAltAltMediumHigh = SystemAltMediumHighColor
    SystemControlHighlightAltBaseMediumLow = SystemBaseMediumLowColor
    SystemControlHighlightAltListAccentHigh = FColor(Accents.SystemAccentColor, func=lambda x: f"#E6{x[1:7]}")
    SystemControlHighlightAltListAccentLow = FColor(Accents.SystemAccentColor, func=lambda x: f"#99{x[1:7]}")
    SystemControlHighlightAltListAccentMedium = FColor(Accents.SystemAccentColor, func=lambda x: f"#CC{x[1:7]}")
    SystemControlHighlightAltChromeWhite = SystemChromeWhiteColor
    SystemControlHighlightAltTransparent = FColor("#00000000")
    SystemControlHighlightBaseHigh = SystemBaseHighColor
    SystemControlHighlightBaseLow = SystemBaseLowColor
    SystemControlHighlightBaseMedium = SystemBaseMediumColor
    SystemControlHighlightBaseMediumHigh = SystemBaseMediumHighColor
    SystemControlHighlightBaseMediumLow = SystemBaseMediumLowColor
    SystemControlHighlightChromeAltLow = SystemChromeAltLowColor
    SystemControlHighlightChromeHigh = SystemChromeHighColor
    SystemControlHighlightListAccentHigh = FColor(Accents.SystemAccentColor, func=lambda x: f"#E6{x[1:7]}")
    SystemControlHighlightListAccentLow = FColor(Accents.SystemAccentColor, func=lambda x: f"#99{x[1:7]}")
    SystemControlHighlightListAccentMedium = FColor(Accents.SystemAccentColor, func=lambda x: f"#CC{x[1:7]}")
    SystemControlHighlightListMedium = SystemListMediumColor
    SystemControlHighlightListLow = SystemListLowColor
    SystemControlHighlightChromeWhite = SystemChromeWhiteColor
    SystemControlHighlightTransparent = FColor("#00000000")
    SystemControlHyperlinkText = Accents.SystemAccentColor
    SystemControlHyperlinkBaseHigh = SystemBaseHighColor
    SystemControlHyperlinkBaseMedium = SystemBaseMediumColor
    SystemControlHyperlinkBaseMediumHigh = SystemBaseMediumHighColor
    SystemControlPageBackgroundAltMedium = SystemAltMediumColor
    SystemControlPageBackgroundAltHigh = SystemAltHighColor
    SystemControlPageBackgroundMediumAltMedium = SystemAltMediumColor
    SystemControlPageBackgroundBaseLow = SystemBaseLowColor
    SystemControlPageBackgroundBaseMedium = SystemBaseMediumColor
    SystemControlPageBackgroundListLow = SystemListLowColor
    SystemControlPageBackgroundChromeLow = SystemChromeLowColor
    SystemControlPageBackgroundChromeMediumLow = SystemChromeMediumLowColor
    SystemControlPageBackgroundTransparent = FColor("#00000000")
    SystemControlPageTextBaseHigh = SystemBaseHighColor
    SystemControlPageTextBaseMedium = SystemBaseMediumColor
    SystemControlPageTextChromeBlackMediumLow = SystemChromeBlackMediumLowColor
    SystemControlErrorTextForeground = SystemErrorTextColor
    SystemControlTransientBackground = FColorWithFallback(SystemChromeAltHighColor, None, SystemChromeMediumLowColor)
    SystemControlDescriptionTextForeground = SystemControlPageTextBaseMedium
