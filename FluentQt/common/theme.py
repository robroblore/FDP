# coding=utf-8
import sys
import threading
from enum import Enum

from qtpy.QtGui import QPalette
from qtpy.QtCore import QObject, Signal, Qt
from qtpy.QtWidgets import QMenu, QFrame, QApplication, QDialog, QWidget


import darkdetect

from ..common import windows_effects
# noinspection PyUnresolvedReferences
from .. import icons
# noinspection PyUnresolvedReferences
# from qfluentwidgets import resource


def set_acrylic_round_corners(menu: QMenu | QFrame | QDialog, blur_color: str | None = "#F2F2F299") -> None:
    """
    Make the corners of the specified menu round with a radius of 8px.

    :param menu: the menu to make the corners round.
    :param blur_color:
    """
    hwnd = int(menu.winId())
    windows_effects.setAcrylicEffect(hwnd, blur_color)
    windows_effects.setRoundedCorners(hwnd)


def remove_acrylic_round_corners(menu: QMenu | QFrame | QDialog) -> None:
    hwnd = int(menu.winId())
    windows_effects.removeBackgroundEffect(hwnd)
    windows_effects.removeRoundedCorners(hwnd)


class Theme(Enum):
    DARK = True
    LIGHT = False
    AUTO = None


def get_system_theme() -> Theme:
    return Theme(darkdetect.isDark())


class FTheme(QObject):

    accentColorChangedSignal: Signal = Signal()
    """The signal for the accent color. Emits when it changes."""
    themeChangedSignal: Signal = Signal()
    _themeChangedSignalInternal: Signal = Signal()
    """The signal for the theme. Emits when it changes state."""
    micaChangedSignal: Signal = Signal()
    """The signal for the mica effect. Emits when it changes state."""
    app: QApplication = None

    def __init__(self, dark: Theme = Theme.AUTO, mica: bool = False) -> None:
        """
        Applies the windows fluent theme to the window.

        :param dark: if the theme is dark or not. If null, the system default theme will be applied.
        :param mica: if the mica effect is applied or not to the window.
        """
        super().__init__()
        self._theme: Theme = Theme(dark)
        """Stores the theme state. True if the theme is set to dark, False if it is set to light and null if it is set
        to system default."""
        self._actual_theme: Theme = get_system_theme() if self._theme is Theme.AUTO else self._theme
        """Stores the actual theme state. True if the theme is set to dark and False if it is set to light."""
        self.mica: bool = mica
        """Stores the mica effect state. True if the mica effect is set, False if not."""
        self.use_immersive_title_bar: bool = False
        """Stores the immersive title bar state. True if the title bar is immersive, False if not."""

        self._system_theme = get_system_theme()

        self.text_font_family: str = "Segoe UI Variable Text"
        """The font of the theme."""
        self.text_font_size: str = "14"
        """The font size of the theme."""
        self.font_weight: str = "400"
        """The font weight of the theme."""
        if sys.getwindowsversion().build >= 22000:
            self.icon_font_family = "Segoe Fluent Icons"
        else:
            self.icon_font_family = "Segoe MDL2 Assets"

        self.getUserStyleSheet = lambda: ""

    def set_app(self, app: QApplication, dark: Theme = "", mica: bool | None = None):
        app.setStyle("Fusion")
        if not self.app:
            threading.Thread(target=lambda: darkdetect.listener(lambda theme: self._themeChangedSignalInternal.emit()), daemon=True).start()
            self._themeChangedSignalInternal.connect(self._on_system_theme_change)
            app.paletteChanged.connect(lambda: self.apply_theme())
        self.app = app
        self.apply_theme(dark, mica)

    def switch_mica(self) -> None:
        """
        Switch the state of the mica effect (on or off).
        """
        self.set_mica(mica=not self.mica)

    def set_mica(self, mica: bool = True) -> None:
        """
        Applies the mica effect to the window to the selected state.

        :param mica: if the mica effect should be used.
        """
        self.apply_theme(mica=mica)

    def switch_theme(self) -> None:
        """
        Switch the window's theme (Dark or Light).
        """
        if self._theme is not Theme.AUTO:
            self.apply_theme(dark=Theme(not self._theme.value))
        else:
            self.apply_theme(dark=Theme(not get_system_theme()))

    def getTheme(self) -> Theme:
        return self._theme

    def set_theme(self, dark: Theme) -> None:
        """
        Applies the selected theme to the window.

        :param dark: if the dark theme should be used instead of the light theme. If null the system default theme will
        be chosen.
        """
        self.apply_theme(dark=dark)

    def isDark(self) -> bool:
        return self._actual_theme.value

    def dark(self) -> None:
        """
         Applies the dark theme to the window.
        """
        self.apply_theme(dark=Theme.LIGHT)

    def light(self) -> None:
        """
         Applies the light theme to the window.
        """
        self.apply_theme(dark=Theme.LIGHT)

    def update(self, widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def apply_theme(self, dark: Theme = "", mica: bool = None, accents: str | None = None) -> None:
        """
        Applies the selected theme with the selected state of the mica effect.

        :param dark: if the dark theme should be used instead of the light theme. If null the system default theme will
        be chosen.
        :param mica: if the mica effect should be used or not.
        :param accents:
        """
        from .colors import FAccentColors, Accents
        if self.app:
            old_mica = self.mica
            old_theme = self._actual_theme
            old_accent_color = FAccentColors.SystemAccentColor

            if dark != "":
                self._theme = Theme(dark)

            if mica:
                self.mica = mica

            Accents.update_accent_colors(accents)

            self._actual_theme = get_system_theme() if self._theme is Theme.AUTO else self._theme
            QApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark if self._actual_theme is Theme.DARK else Qt.ColorScheme.Light)
            windows_effects.SetMenuTheme(self._actual_theme is Theme.DARK)

            if self.mica != old_mica:
                self.micaChangedSignal.emit()
            if self._actual_theme != old_theme:
                self.themeChangedSignal.emit()
            if FAccentColors.SystemAccentColor != old_accent_color:
                self.accentColorChangedSignal.emit()

            self.app.setStyleSheet(self.get_stylesheet())
            self.apply_palette()

    def _on_system_theme_change(self):
        if self._theme is Theme.AUTO:
            self.apply_theme()

    def apply_palette(self):
        # if self._actual_theme == Theme.DARK:
        #     self._apply_dark_palette()
        # else:
        #     self._apply_light_palette()

        self.blockSignals(True)

        from .colors import FColors
        new_pal = self.app.palette()
        new_pal.setColor(QPalette.ColorRole.Link, FColors.AccentTextFillColorPrimary.getColor())
        new_pal.setColor(QPalette.ColorRole.LinkVisited, FColors.AccentTextFillColorPrimary.getColor())
        self.app.setPalette(new_pal)

        self.blockSignals(False)

    # def _apply_dark_palette(self):
    #     self._disconnectPaletteListener()
    #
    #     from .colors import FColors
    #     new_pal = self.app.palette()
    #     new_pal.setColor(QPalette.ColorRole.Link, FColors.AccentTextFillColorPrimary.getColor())
    #     new_pal.setColor(QPalette.ColorRole.LinkVisited, FColors.AccentTextFillColorPrimary.getColor())
    #     self.app.setPalette(new_pal)
    #
    #     self._connectPaletteListener()
    #
    # def _apply_light_palette(self):
    #     self._disconnectPaletteListener()
    #
    #     from .colors import FColors
    #     new_pal = self.app.palette()
    #     new_pal.setColor(QPalette.ColorRole.Link, FColors.AccentTextFillColorPrimary.getColor())
    #     new_pal.setColor(QPalette.ColorRole.LinkVisited, FColors.AccentTextFillColorPrimary.getColor())
    #     self.app.setPalette(new_pal)
    #
    #     self._connectPaletteListener()

    def get_stylesheet(self) -> str:
        """
        Returns the stylesheet with the correct colors.

        :return: returns the stylesheet.
        """
        from .colors import FColors
        style1 = (f'''/*BACKGROUND*/                    
                    * {{
                        color: {FColors.TextFillColorPrimary.get()};
                        font-size: {self.text_font_size}px;
                        font-family: {self.text_font_family};
                        font-weight: {self.font_weight};
                        outline: none;
                    }}
                    *:disabled {{
                        color: {FColors.TextFillColorDisabled.get()};
                    }}


                    /*FRAME*/
                    QFrame, FFrame {{
                        border-radius: 8px;
                    }}
                    
                    QFrame, QWidget, FFrame[opacity="0"] {{
                        background: {FColors.SystemControlTransparent.get()};
                        border: 0px solid {FColors.SystemControlTransparent.get()};
                    }}
                    
                    FFrame[opacity="1"] {{
                        background-color: {FColors.LayerFillColorDefault.get()};
                        border: 0px solid {FColors.SystemControlTransparent.get()};
                    }}
                    
                    FFrame[opacity="2"] {{
                        background-color: {FColors.SolidBackgroundFillColorBase.get()};
                        border: 0px solid {FColors.SystemControlTransparent.get()};
                    }}
                    
                    FDialogFrame {{
                        background-color: {FColors.SolidBackgroundFillColorBase.get()};
                        border: 1px solid {FColors.SurfaceStrokeColorDefault.get()};
                    }}
                    
                    FDialogContentFrame{{
                        background-color: {FColors.LayerFillColorAlt.get()};
                        border-bottom: 1px solid {FColors.CardStrokeColorDefault.get()};
                        border-bottom-left-radius: 0px;
                        border-bottom-right-radius: 0px;
                    }}
                    
                    QMainWindow {{
                        background: {FColors.ApplicationPageBackgroundTheme.get()};
                    }}
                    FMainWindow {{
                        background: {FColors.SystemControlTransparent.get() if self.mica and sys.getwindowsversion().build >= 22000 else FColors.ApplicationPageBackgroundTheme.get()};
                    }}
                    
                    FExpander FFrame[opacity="1"] {{
                        border-radius: 4px;
                        border-top-left-radius: 0px;
                        border-top-right-radius: 0px;
                        background-color: {FColors.CardBackgroundFillColorSecondary.get()};
                        border: 1px solid {FColors.ControlStrokeColorOnAccentDisabled.get()};
                        border-top: 0px solid {FColors.CardStrokeColorDefault.get()};
                    }}
                    
                    /*TOOLTIP*/
                    
                    QToolTip {{
                        font-size: {str(int(self.text_font_size) - 2)}px;
                        background-color: {FColors.SystemChromeMediumLowColor.get()};
                        border: 1px solid {FColors.SurfaceStrokeColorFlyout.get()};
                        border-radius: 4px;
                        padding: 6px 3px;
                    }}

                    /*GROUPBOX*/

                    QGroupBox {{
                        margin-top: 10px;
                        padding-top: 5px;
                    }}
                    QGroupBox::title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 2px 10px;
                        margin-left: 8px;
                        border-radius: 4px;
                    }}


                    /*LABEL*/

                    QLabel, FLabel[textStyle=body]{{
                        background: {FColors.SystemControlTransparent.get()};
                        color: {FColors.TextFillColorPrimary.get()};
                        border: 0px solid {FColors.SystemControlTransparent.get()};
                    }}
                    FLabel[textStyle=caption] {{
                        font-size: {str(int(self.text_font_size) - 2)}px;
                    }}
                    FLabel[textStyle=bodyStrong] {{
                        font-size: {str(int(self.text_font_size))}px;
                        font-weight: {str(int(self.font_weight) + 200)};
                    }}
                    FLabel[textStyle=subtitle] {{
                        font-size: {str(int(self.text_font_size) + 6)}px;
                        font-weight: {str(int(self.font_weight) + 200)};
                    }}
                    FLabel[textStyle=title] {{
                        font-size: {str(int(self.text_font_size) + 14)}px;
                        font-weight: {str(int(self.font_weight) + 200)};
                    }}
                    FLabel[textStyle=titleLarge] {{
                        font-size: {str(int(self.text_font_size) + 36)}px;
                        font-weight: {str(int(self.font_weight) + 200)};
                    }}FLabel[textStyle=display] {{
                        font-size: {str(int(self.text_font_size) + 54)}px;
                        font-weight: {str(int(self.font_weight) + 200)};
                    }}
                    


                    /*MENUBAR*/

                    QMenuBar {{
                        background: {FColors.SubtleFillColorTransparent.get()};
                        padding: 4px;
                    }}
                    QMenuBar::item {{
                        padding: 8px 12px;
                        margin-right: 4px;
                        border-radius: 4px;
                    }}
                    QMenuBar::item:pressed {{
                        background-color: {FColors.SubtleFillColorTertiary.get()};
                    }}
                    QMenuBar::item:selected {{
                        background-color: {FColors.SubtleFillColorSecondary.get()};
                    }}
                    
                    
                    /*PUSHBUTTON, TOOLBUTTON AND COMBOBOX*/

                    QPushButton, QToolButton, QComboBox {{
                        color: {FColors.TextFillColorPrimary.get()};
                        background-color: {FColors.ControlFillColorDefault.get()};
                        border: 1px solid {FColors.ControlStrokeColorDefault.get()};
                        border-radius: 4px;
                        height: 30px;
                        padding: 0px 11px;
                    }}
                    QComboBox {{
                        padding: 0px 19px;
                    }}
                    QComboBox::drop-down {{
                        background-color: {FColors.SystemControlTransparent.get()};
                    }}
                    QComboBox::down-arrow {{
                        image: url(:/ComboBox/img {FColors.img_color.get()}/ComboBox.svg);
                    }}
                    QComboBox::down-arrow:disabled {{
                        image: url(:/ComboBox/img {FColors.img_color.get()}/ComboBoxDisabled.svg);
                    }}
                    QToolButton {{
                        height: 27px;
                        width: 33px;
                        padding: 0px;
                    }}
                    FPushButton[hasIcon=true] {{
                        padding: 0px 11px 0px 36px;
                    }}
                    FPushButton[hasMenu=true] {{
                        padding: 0px 33px 0px 11px;
                    }}
                    FPushButton[hasMenu=true][hasIcon=true] {{
                        padding: 0px 33px 0px 36px;
                    }}
                    FToolButton[hasMenu=true] {{
                        width: 59px;
                    }}
                    FDialogButtonFrame QPushButton {{
                        margin-right: 2px;
                    }}
                    
                    QPushButton:hover, QToolButton:hover, QComboBox:hover {{
                        background-color: {FColors.ControlFillColorSecondary.get()};
                    }}
                    QPushButton:pressed, QToolButton:pressed, QComboBox:pressed {{
                        color: {FColors.TextFillColorSecondary.get()};
                        background-color: {FColors.ControlFillColorTertiary.get()};
                        border: 1px solid {FColors.ControlStrokeColorDefault.get()};
                    }}
                    QPushButton:disabled, QToolButton:disabled, QComboBox:disabled {{
                        color: {FColors.TextFillColorDisabled.get()};
                        background-color: {FColors.ControlFillColorDisabled.get()};
                        border: 1px solid {FColors.ControlStrokeColorDefault.get()};
                    }}
                    
                    /*FPushButton[isTransparent=true]*/
                    
                    FPushButton[isTransparent=true], FToolButton[isTransparent=true] {{
                        background-color: {FColors.ControlFillColorTransparent.get()};
                        border: 0px solid {FColors.ControlFillColorTransparent.get()};
                        height: 32px;
                        padding: 0px 12px;
                    }}
                    FToolButton[isTransparent=true] {{
                        height: 29px;
                        width: 35px;
                        padding: 0px;
                    }}
                    FPushButton[isTransparent=true][hasIcon=true] {{
                        padding: 0px 12px 0px 37px;
                    }}
                    FPushButton[isTransparent=true][hasMenu=true] {{
                        padding: 0px 34px 0px 12px;
                    }}
                    FPushButton[isTransparent=true][hasMenu=true][hasIcon=true] {{
                        padding: 0px 34px 0px 37px;
                    }}
                    FToolButton[isTransparent=true][hasMenu=true] {{
                        padding: 0px 27px 0px 0px;
                    }}
                    
                    FPushButton[isTransparent=true], FToolButton[isTransparent=true] {{
                        background-color: {FColors.SubtleFillColorTransparent.get()};
                        border: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    FPushButton[isTransparent=true]:hover, FToolButton[isTransparent=true]:hover {{
                        background-color: {FColors.SubtleFillColorSecondary.get()};
                        border: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    FPushButton[isTransparent=true]:pressed, FToolButton[isTransparent=true]:pressed {{
                        background-color: {FColors.SubtleFillColorTertiary.get()};
                        border: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    FPushButton[isTransparent=true]:disabled, FToolButton[isTransparent=true]:disabled {{
                        background-color: {FColors.ControlFillColorTransparent.get()};
                        border: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}

                    
                    /*Accent for FPushButton and FToolButton*/

                    FPushButton[isAccent=true], FToolButton[isAccent=true], QPushButton:checked, QToolButton:checked {{
                        color: {FColors.TextOnAccentFillColorPrimary.get()};
                        background-color: {FColors.AccentFillColorDefault.get()};
                        border: 1px solid {FColors.AccentControlElevationBorder.get()};
                    }}
                    FPushButton[isAccent=true]:hover, FToolButton[isAccent=true]:hover, QPushButton:checked:hover, QToolButton:checked:hover {{
                        color: {FColors.TextOnAccentFillColorPrimary.get()};
                        background-color: {FColors.AccentFillColorSecondary.get()};
                        border: 1px solid {FColors.AccentControlElevationBorder.get()};
                    }}
                    FPushButton[isAccent=true]:pressed, FToolButton[isAccent=true]:pressed, QPushButton:checked:pressed, QToolButton:checked:pressed {{
                        color: {FColors.TextOnAccentFillColorSecondary.get()};
                        background-color: {FColors.AccentFillColorTertiary.get()};
                        border: 1px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    FPushButton[isAccent=true]:disabled, FToolButton[isAccent=true]:disabled, QPushButton:checked:disabled, QToolButton:checked:disabled {{
                        color: {FColors.TextOnAccentFillColorDisabled.get()};
                        background-color: {FColors.AccentFillColorDisabled.get()};
                        border: 1px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    
                    FPushButton[isTransparent=true][isAccent=true], FToolButton[isTransparent=true][isAccent=true], FPushButton[isTransparent=true]:checked, FToolButton[isTransparent=true]:checked,
                    FPushButton[isTransparent=true][isAccent=true]:hover, FToolButton[isTransparent=true][isAccent=true]:hover, FPushButton[isTransparent=true]:checked:hover, FToolButton[isTransparent=true]:checked:hover,
                    FPushButton[isTransparent=true][isAccent=true]:pressed, FToolButton[isTransparent=true][isAccent=true]:pressed, FPushButton[isTransparent=true]:checked:pressed, FToolButton[isTransparent=true]:checked:pressed,
                    FPushButton[isTransparent=true][isAccent=true]:disabled, FToolButton[isTransparent=true][isAccent=true]:disabled, FPushButton[isTransparent=true]:checked:disabled, FToolButton[isTransparent=true]:checked:disabled {{
                        border: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    
                    
                    /*FHyperLinkButton*/
                    
                    FHyperLinkButton {{
                        color: {FColors.AccentTextFillColorPrimary.get()};
                        background: {FColors.ControlFillColorTransparent.get()};
                        border: 0px solid {FColors.SubtleFillColorTransparent.get()};
                        height: 32px;
                    }}
                    FHyperLinkButton:hover {{
                        color: {FColors.AccentTextFillColorSecondary.get()};
                        background: {FColors.SubtleFillColorSecondary.get()};
                        border: 0px solid {FColors.SubtleFillColorTransparent.get()};
                    }}
                    FHyperLinkButton:pressed {{
                        color: {FColors.AccentTextFillColorTertiary.get()};
                        background: {FColors.SubtleFillColorTertiary.get()};
                        border: 0px solid {FColors.SubtleFillColorTransparent.get()};
                    }}
                    FHyperLinkButton:disabled {{
                        color: {FColors.AccentTextFillColorDisabled.get()};
                        background: {FColors.ControlFillColorTransparent.get()};
                        border: 0px solid {FColors.SubtleFillColorTransparent.get()};
                    }}


                    /*FSplitPushButton FPushButton and FSplitToolButton FToolButton*/
                    
                    FSplitPushButton FPushButton, FSplitToolButton FToolButton {{
                        border-top-right-radius: 0px;
                        border-bottom-right-radius: 0px;
                    }}
                    FSplitToolButton FToolButton {{
                        width: 31px;
                    }}
                    FSplitPushButton FPushButton {{
                        height: 25px;
                    }}
                    FSplitToolButton FToolButton[isTransparent=true] {{
                        width: 33px;
                    }}
                    FSplitPushButton FPushButton[isTransparent=true] {{
                        height: 27px;
                    }}
                    
                    FSplitPushButton FPushButton, FSplitToolButton FToolButton,
                    FSplitPushButton FPushButton:hover, FSplitToolButton FToolButton:hover,
                    FSplitPushButton FPushButton:pressed, FSplitToolButton FToolButton:pressed,
                    FSplitPushButton FPushButton:disabled, FSplitToolButton FToolButton:disabled {{
                        border-right: 1px solid {FColors.ControlStrokeColorDefault.get()};
                    }} 
                    
                    FSplitPushButton FPushButton[isAccent=true], FSplitToolButton FToolButton[isAccent=true], FSplitPushButton FPushButton:checked, FSplitToolButton FToolButton:checked,
                    FSplitPushButton FPushButton[isAccent=true]:hover, FSplitToolButton FToolButton[isAccent=true]:hover, FSplitPushButton FPushButton:checked:hover, FSplitToolButton FToolButton:checked:hover,
                    FSplitPushButton FPushButton[isAccent=true]:pressed, FSplitToolButton FToolButton[isAccent=true]:pressed, FSplitPushButton FPushButton:checked:pressed, FSplitToolButton FToolButton:checked:pressed {{
                        border: 1px solid {FColors.AccentControlElevationBorder.get()};
                        border-right: 1px solid {FColors.ControlStrokeColorOnAccentTertiary.get()};
                    }}
                    FSplitPushButton FPushButton[isAccent=true]:pressed, FSplitToolButton FToolButton[isAccent=true]:pressed, FSplitPushButton FPushButton:checked:pressed, FSplitToolButton FToolButton:checked:pressed {{
                        border-right: 1px solid {FColors.ControlStrokeColorOnAccentTertiary.get()};
                    }}
                    
                    
                    /*FSplitDropButton*/
                                   
                    FSplitPushButton FSplitDropButton, FSplitToolButton FSplitDropButton {{
                        border-radius: 4px;
                        border-top-left-radius: 0px;
                        border-bottom-left-radius: 0px;
                        height: 26px;
                        width: 31px;
                    }}
                    FSplitPushButton FSplitDropButton {{
                        height: 25px;
                    }}
                    FSplitPushButton FSplitDropButton[isTransparent=true], FSplitToolButton FSplitDropButton[isTransparent=true] {{
                        height: 28px;
                        width: 32px;
                        border-left: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    FSplitPushButton FSplitDropButton[isTransparent=true] {{
                        height: 27px;
                    }}
                    FSplitPushButton FSplitDropButton, FSplitToolButton FSplitDropButton,
                    FSplitPushButton FSplitDropButton:hover, FSplitToolButton FSplitDropButton:hover,
                    FSplitPushButton FSplitDropButton:pressed, FSplitToolButton FSplitDropButton:pressed,
                    FSplitPushButton FSplitDropButton:disabled, FSplitToolButton FSplitDropButton:disabled {{
                        border-left: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    
                    FSplitPushButton FSplitDropButton[isAccent=true], FSplitToolButton FSplitDropButton[isAccent=true], FSplitPushButton FSplitDropButton:checked, FSplitToolButton FSplitDropButton:checked,
                    FSplitPushButton FSplitDropButton[isAccent=true]:hover, FSplitToolButton FSplitDropButton[isAccent=true]:hover, FSplitPushButton FSplitDropButton:checked:hover, FSplitToolButton FSplitDropButton:checked:hover,
                    FSplitPushButton FSplitDropButton[isAccent=true]:pressed, FSplitToolButton FSplitDropButton[isAccent=true]:pressed, FSplitPushButton FSplitDropButton:checked:pressed, FSplitToolButton FSplitDropButton:checked:pressed {{
                        border: 1px solid {FColors.AccentControlElevationBorder.get()};
                        border-left: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    FSplitPushButton FSplitDropButton[isAccent=true]:disabled, FSplitToolButton FSplitDropButton[isAccent=true]:disabled, FSplitPushButton FSplitDropButton:checked:disabled, FSplitToolButton FSplitDropButton:checked:disabled {{
                        border-left: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}


                    /*MENU AND QCOMBOBOXMENU*/
                    
                    QMenu, QComboBox QListView, QAbstractItemView#CompleterPopup{{
                        background-color: {FColors.AcrylicFillColorDefault.fallback.get()};
                        border: 1px solid {FColors.SurfaceStrokeColorDefault.get()};
                        padding: 2px 0px 2px 0px;
                        border-radius: 0px;
                        background-clip: clip;
                    }}
                    QMenu::right-arrow {{
                        left: 2px;
                        down: 2px;
                        width: 22px;
                        height: 22px;
                        image: url(:/qfluentwidgets/images/tree_view/TreeViewClose_white.svg);
                    }}

                    QMenu::indicator {{
                        width: 13px;
                        height: 13px;
                    }}

                    /*QMenu::indicator:checked {{
                        image: url(:/CheckBox/img {FColors.img_color.light.get()}/CheckBox.svg);
                    }}

                    QMenu::indicator:checked:selected {{
                        image: url(:/CheckBox/img {FColors.img_color.light.get()}/CheckBox.svg);
                    }}*/
                    
                    QMenu::indicator:checked {{
                        image: none;
                    }}

                    QMenu::item, QComboBox QListView::item, QAbstractItemView#CompleterPopup::item {{
                        color: {FColors.TextFillColorPrimary.get()};
                        background-color: {FColors.SubtleFillColorTransparent.get()};
                        border: 1px solid {FColors.SubtleFillColorTransparent.get()};
                        margin: 2px 4px 2px 4px;
                        padding: 6px 11px 6px 11px;
                        border-radius: 4px;
                        min-width: 67px;
                    }}
                    QMenu[hasIcon=true]::item, QComboBox QListView::item, QAbstractItemView#CompleterPopup::item {{
                        padding-left: 18px;
                    }}
                    QMenu::icon, QComboBox QListView::icon, QAbstractItemView#CompleterPopup::icon {{
                        min-width: 37px;
                    }}
                    QMenu::item:selected,
                    QComboBox QListView::item:selected,
                    QAbstractItemView#CompleterPopup::item:hover {{
                        background-color: {FColors.SubtleFillColorSecondary.get()};
                    }}
                    QMenu::item:pressed, QAbstractItemView#CompleterPopup::item:selected {{
                        color: {FColors.TextFillColorSecondary.get()};
                        background-color: {FColors.SubtleFillColorTertiary.get()};
                    }}
                    QMenu::item:disabled, QAbstractItemView#CompleterPopup::item:disabled {{
                        color: {FColors.TextFillColorDisabled.get()};
                    }}
                    
                    QMenu::item:checked,
                    QComboBox QListView::item:checked,
                    QAbstractItemView#CompleterPopup::item:hover {{
                        color: {FColors.TextOnAccentFillColorPrimary.get()};
                        background-color: {FColors.AccentFillColorDefault.get()};
                        border: 1px solid {FColors.AccentControlElevationBorder.get()};
                    }}
                    QMenu::item:checked:selected,
                    QComboBox QListView::item:checked:selected,
                    QAbstractItemView#CompleterPopup::item:checked:hover {{
                        background-color: {FColors.AccentFillColorSecondary.get()};
                    }}
                    QMenu::item:checked:pressed, QAbstractItemView#CompleterPopup::item:checked:pressed {{
                        color: {FColors.TextOnAccentFillColorSecondary.get()};
                        background-color: {FColors.AccentFillColorTertiary.get()};
                        border: 1px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    QMenu::item:checked:disabled, QAbstractItemView#CompleterPopup::item:checked:disabled {{
                        color: {FColors.TextOnAccentFillColorDisabled.get()};
                        background-color: {FColors.AccentFillColorDisabled.get()};
                        border: 1px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    
                    QMenu::separator {{
                        height: 1px;
                        background: {FColors.DividerStrokeColorDefault.get()};
                        margin: 1px 0px 1px 0px;
                    }}
        ''')

        style2 = (f''' /*CHECKBOX*/

                    QCheckBox {{
                        background-color: {FColors.SystemControlTransparent.get()};
                    }}

                    QCheckBox::indicator,
                    QTreeView::indicator {{
                        background-color: {FColors.ControlAltFillColorSecondary.get()};
                        border: 1px solid {FColors.ControlStrongStrokeColorDefault.get()};
                        width: 18px;
                        height: 18px;
                        border-radius: 4px;
                        margin-right: 3px;
                    }}

                    QTreeView::indicator {{
                        margin-left: 6px;
                        margin-right: 12px;
                    }}

                    QCheckBox::indicator:unchecked:hover,
                    QTreeView::indicator:unchecked:hover,
                    QTreeView::indicator:unchecked:selected:hover {{
                        background-color: {FColors.ControlAltFillColorTertiary.get()};
                    }}

                    QCheckBox::indicator:unchecked:pressed,
                    QTreeView::indicator:unchecked:pressed {{
                        background-color: {FColors.ControlAltFillColorQuarternary.get()};
                        border: 1px solid {FColors.ControlStrongStrokeColorDisabled.get()};
                    }}

                    QCheckBox::indicator:unchecked:disabled,
                    QTreeView::indicator:unchecked:disabled {{
                        background-color: {FColors.SystemControlTransparent.get()};
                        border: 1px solid {FColors.ControlStrongStrokeColorDisabled.get()};
                    }}

                    QCheckBox::indicator:checked,
                    QCheckBox::indicator:indeterminate,
                    QTreeView::indicator:checked,
                    QTreeView::indicator:indeterminate {{
                        background-color: {FColors.AccentFillColorDefault.get()};
                        border: 1px solid {FColors.AccentFillColorDefault.get()};
                    }}

                    QCheckBox::indicator:checked,
                    QTreeView::indicator:checked {{
                        image: url(:/CheckBox/img {FColors.img_color.get()}/CheckBox.svg);
                    }}

                    QCheckBox::indicator:indeterminate,
                    QTreeView::indicator:indeterminate {{
                        image: url(:/CheckBox/img {FColors.img_color.get()}/CheckBoxIndeterminate.svg);
                    }}

                    QCheckBox::indicator:checked:hover,
                    QCheckBox::indicator:indeterminate:hover,
                    QTreeView::indicator:checked:hover,
                    QTreeView::indicator:indeterminate:hover {{
                        background-color: {FColors.AccentFillColorSecondary.get()};
                        border: 1px solid {FColors.AccentFillColorSecondary.get()};
                    }}

                    QCheckBox::indicator:checked:pressed,
                    QCheckBox::indicator:indeterminate:pressed,
                    QTreeView::indicator:checked:pressed,
                    QTreeView::indicator:indeterminate:pressed {{
                        background-color: {FColors.AccentFillColorTertiary.get()};
                        border: 1px solid {FColors.AccentFillColorTertiary.get()};
                    }}

                    QCheckBox::indicator:checked:pressed,
                    QTreeView::indicator:checked:pressed {{
                        image: url(:/CheckBox/img {FColors.img_color.get()}/CheckBoxPressed.svg);
                    }}

                    QCheckBox::indicator:indeterminate:pressed,
                    QTreeView::indicator:indeterminate:pressed {{
                        image: url(:/CheckBox/img {FColors.img_color.get()}/CheckBoxIndeterminatePressed.svg);
                    }}

                    QCheckBox::indicator:checked:disabled,
                    QCheckBox::indicator:indeterminate:disabled,
                    QTreeView::indicator:checked:disabled,
                    QTreeView::indicator:indeterminate:disabled {{
                        background-color: {FColors.AccentFillColorDisabled.get()};
                        border: 1px solid {FColors.AccentFillColorDisabled.get()};
                    }}
                    
                    QCheckBox::indicator:checked:disabled,
                    QTreeView::indicator:checked:disabled {{
                        image: url(:/CheckBox/img {FColors.img_color.get()}/CheckBoxDisabled.svg);
                    }}

                    QCheckBox::indicator:indeterminate:disabled,
                    QTreeView::indicator:indeterminate:disabled {{
                        image: url(:/CheckBox/img {FColors.img_color.get()}/CheckBoxIndeterminateDisabled.svg);
                    }}
                    
                    FToggleSwitch::indicator {{
                        width: 38px;
                        height: 18px;
                        border-radius: 10px;
                    }}
                    
                    FToggleSwitch::indicator:unchecked:pressed {{
                        border: 1px solid {FColors.ControlStrongStrokeColorDefault.get()};
                    }}
                    
                    FToggleSwitch::indicator:checked {{
                        image: None;
                    }}
                    
                    FToggleSwitch::indicator:checked:pressed {{
                        image: None;
                    }}
                    
                    FToggleSwitch::indicator:checked:disabled {{
                        image: None;
                    }}

                    /*RADIOBUTTON*/

                    QRadioButton {{
                        min-height: 20px;
                        max-height: 20px;
                        font-size: {self.text_font_size}px;
                    }}

                    QRadioButton::indicator {{
                        width: 18px;
                        height: 18px;
                        border-radius: 10px;
                        border: 1px solid {FColors.ControlStrongStrokeColorDefault.get()};
                        background-color: {FColors.ControlAltFillColorSecondary.get()};
                        margin-right: 4px;
                    }}

                    QRadioButton::indicator:hover {{
                        background-color: {FColors.ControlAltFillColorTertiary.get()};
                    }}

                    QRadioButton::indicator:pressed {{
                        background-color: {FColors.ControlAltFillColorQuarternary.get()};
                        border: 1px solid {FColors.ControlStrongStrokeColorDisabled.get()};
                        image: url(:/RadioButton/img {FColors.img_color.get()}/RadioButton.svg);
                    }}

                    QRadioButton::indicator:checked {{
                        background-color: {FColors.AccentFillColorDefault.get()};
                        border: 1px solid {FColors.AccentFillColorDefault.get()};
                        image: url(:/RadioButton/img {FColors.img_color.get()}/RadioButton.svg);
                    }}

                    QRadioButton::indicator:checked:hover {{
                        image: url(:/RadioButton/img {FColors.img_color.get()}/RadioButtonHover.svg);
                        background-color: {FColors.AccentFillColorSecondary.get()};
                        border: 1px solid {FColors.AccentFillColorSecondary.get()};
                    }}

                    QRadioButton::indicator:checked:pressed {{
                        image: url(:/RadioButton/img {FColors.img_color.get()}/RadioButtonPressed.svg);
                        background-color: {FColors.AccentFillColorTertiary.get()};
                        border: 1px solid {FColors.AccentFillColorTertiary.get()};
                    }}

                    QRadioButton:disabled {{
                        color: rgb(150, 150, 150);
                    }}

                    QRadioButton::indicator:disabled {{
                        border: 1px solid {FColors.ControlStrongStrokeColorDisabled.get()};
                        background-color: {FColors.ControlFillColorDisabled.get()};
                    }}
                    QRadioButton::indicator:checked:disabled {{
                        background-color: {FColors.AccentFillColorDisabled.get()};
                        border: 1px solid {FColors.AccentFillColorDisabled.get()};
                    }}

                    /*LINEEDIT*/

                    QLineEdit, QTextEdit, QPlainTextEdit {{
                        background-color: {FColors.ControlFillColorDefault.get()};
                        border: 1px solid {FColors.ControlStrokeColorDefault.get()};
                        border-bottom: 1px solid {FColors.ControlStrongStrokeColorDefault.get()};
                        color: {FColors.TextFillColorPrimary.get()};
                        font-size:  {self.text_font_size}px;
                        font-family: {self.text_font_family};
                        font-weight: {self.font_weight};
                        border-radius: 4px;
                        padding: 5px 8px 6px 8px;
                        selection-background-color: {FColors.AccentFillColorSelectedTextBackground.get()};
                    }}
                    QTextEdit, QPlainTextEdit  {{
                        padding: 0px 0px 0px 10px;
                    }}
                    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
                        background-color: {FColors.ControlFillColorSecondary.get()};
                    }}
                    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                        background-color: {FColors.ControlFillColorInputActive.get()};
                        border-bottom: 2px solid {FColors.AccentFillColorDefault.get()};
                        padding-bottom: 5px;
                    }}
                    FLineEdit:focus {{
                        border-bottom: 2px solid {FColors.SystemControlTransparent.get()};
                    }}
                    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
                        background-color: {FColors.ControlFillColorDisabled.get()};
                        border: 1px solid {FColors.ControlStrokeColorDefault.get()};
                    }}


                    /*PROGRESSBAR*/

                    QProgressBar:vertical {{
                        background-color: qlineargradient(spread:reflect, x1:0.5, y1:0.5, x2:1, y2:0.5, stop:0.119403 
                        {FColors.ControlStrongStrokeColorDefault.get()}, stop:0.273632 {FColors.SystemControlTransparent.get()});
                    }}
                    QProgressBar:horizontal {{
                        background-color: qlineargradient(spread:reflect, x1:0.5, y1:0.5, x2:0.5, y2:1, stop:0.119403 
                        {FColors.ControlStrongStrokeColorDefault.get()}, stop:0.273632 {FColors.SystemControlTransparent.get()});
                    }}
                    QProgressBar::chunk {{
                        background-color: {FColors.AccentFillColorDefault.get()};
                        border-radius: 1px;
                    }}
                    QProgressBar::chunk[progressState=paused] {{
                        background-color: {FColors.SystemFillColorCaution.get()};
                    }}
                    QProgressBar::chunk[progressState=error] {{
                        background-color: {FColors.SystemFillColorCritical.get()};
                    }}
                    QProgressBar::chunk:disabled {{
                        background-color: {FColors.AccentFillColorDisabled.get()};
                    }}


                    /*SCROLLVERTICAL*/

                    QScrollBar, QScrollArea > QWidget > QScrollBar {{
                        background-color: {FColors.AcrylicFillColorDefault.get()};
                        padding: 3px;
                        border-radius: 6px;
                        width: 12px;
                        margin: 0px 0px 0px 0px;
                    }}
                    QScrollBar::handle {{
                        background-color: {FColors.ControlStrongFillColorDefault.get()};
                        border-radius: 3px;
                        min-height: 25px;
                        margin: 15px 0px 15px 0px;
                    }}
                    QScrollBar::sub-line:vertical {{
                        image: url(:/ScrollVertical/img {FColors.img_color.get()}/ScrollTop.png);
                        subcontrol-position: top;
                        subcontrol-origin: margin;
                    }}
                    QScrollBar::sub-line:vertical:hover {{
                        image: url(:/ScrollVertical/img {FColors.img_color.get()}/ScrollTopHover.png);
                    }}
                    QScrollBar::sub-line:vertical:pressed {{
                        image: url(:/ScrollVertical/img {FColors.img_color.get()}/ScrollTopPressed.png);
                    }}
                    QScrollBar::add-line:vertical {{
                        image: url(:/ScrollVertical/img {FColors.img_color.get()}/ScrollBottom.png);
                        subcontrol-position: bottom;
                        subcontrol-origin: margin;
                    }}
                    QScrollBar::add-line:vertical:hover {{
                        image: url(:/ScrollVertical/img {FColors.img_color.get()}/ScrollBottomHover.png);
                    }}
                    QScrollBar::add-line:vertical:pressed {{
                        image: url(:/ScrollVertical/img {FColors.img_color.get()}/ScrollBottomPressed.png);
                    }}
                    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                        background: {FColors.SystemControlTransparent.get()};
                    }}

                    /*SCROLLHORIZONTAL*/
                    QScrollBar::sub-line:horizontal {{
                        image: url(:/ScrollHorizontal/img {FColors.img_color.get()}/ScrollLeft.png);
                        subcontrol-position: left;
                        subcontrol-origin: margin;
                    }}
                    QScrollBar::sub-line:horizontal:hover {{
                        image: url(:/ScrollHorizontal/img {FColors.img_color.get()}/ScrollLeftHover.png);
                    }}
                    QScrollBar::sub-line:horizontal:pressed {{
                        image: url(:/ScrollHorizontal/img {FColors.img_color.get()}/ScrollLeftPressed.png);
                    }}
                    QScrollBar::add-line:horizontal {{
                        image: url(:/ScrollHorizontal/img {FColors.img_color.get()}/ScrollRight.png);
                        subcontrol-position: right;
                        subcontrol-origin: margin;
                    }}
                    QScrollBar::add-line:horizontal:hover {{
                        image: url(:/ScrollHorizontal/img {FColors.img_color.get()}/ScrollRightHover.png);
                    }}
                    QScrollBar::add-line:horizontal:pressed {{
                        image: url(:/ScrollHorizontal/img {FColors.img_color.get()}/ScrollRightPressed.png);
                    }}
                    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                        background: none;
                    }}


                    /*TREEWIDGET*/


                    QTreeView {{
                        background-color: {FColors.SystemControlTransparent.get()};
                        border: 0px solid {FColors.SystemControlTransparent.get()};
                        padding: 4px;
                        show-decoration-selected: 1;
                    }}
                    FNavTreeWidget {{
                        padding: 0px;
                    }}

                    QTreeView QHeaderView {{
                        background-color: {FColors.SystemControlTransparent.get()};
                        border: 0px solid {FColors.SystemControlTransparent.get()};
                        border-radius: 4px;
                    }}
                    
                    QTreeView QHeaderView::section {{
                        color: {FColors.TextFillColorPrimary.get()};
                        background-color: {FColors.ControlFillColorDefault.get()};
                        padding: 2px;
                        padding-left: 12px;
                        border-radius: 4px;
                    }}
                    QTreeView QHeaderView::section:hover {{
                        background-color: {FColors.ControlFillColorSecondary.get()};
                    }}
                    QTreeView QHeaderView::section:pressed {{
                        color: {FColors.TextFillColorSecondary.get()};
                        background-color: {FColors.ControlFillColorTertiary.get()};
                    }}
                    QTreeView QHeaderView::section:disabled {{
                        color: {FColors.TextFillColorDisabled.get()};
                        background-color: {FColors.ControlFillColorDisabled.get()};
                    }}

                    QTreeView QHeaderView::section:first {{
                        border-top-right-radius: 0px;
                        border-bottom-right-radius: 0px;
                    }}
                    QTreeView QHeaderView::section:middle {{
                        border-radius: 0px;
                    }}
                    QTreeView QHeaderView::section:last {{
                        border-top-left-radius: 0px;
                        border-bottom-left-radius: 0px;
                    }}
                    QTreeView QHeaderView::section:first,
                    QTreeView QHeaderView::section:middle{{
                        border-right: 1px solid {FColors.ControlStrokeColorDefault.get()};
                    }}

                    QTreeView::item {{
                        background-color: {FColors.SystemControlTransparent.get()};
                        color: {FColors.TextFillColorPrimary.get()};
                        height: 30px;
                        margin-top: 4px;
                    }}
                    FNavTreeWidget::item {{
                        height: 36px;
                    }}
                    QTreeView::item:middle,
                    QTreeView::item:last {{
                        padding-left: 12px;
                    }}
                    QTreeView::item:last {{
                        border-top-right-radius: 4px;
                        border-bottom-right-radius: 4px;
                    }}
                    
                    QTreeView::item:selected {{
                        background-color: {FColors.SubtleFillColorSecondary.get()};
                    }}
                    QTreeView[pressedItem=true]::item:selected {{
                        color: {FColors.TextFillColorSecondary.get()};
                    }}
                    QTreeView::item:hover {{
                        background-color: {FColors.SubtleFillColorSecondary.get()};
                    }}
                    QTreeView::item:disabled {{
                        color: {FColors.TextFillColorDisabled.get()};
                        background-color: {FColors.SystemControlTransparent.get()};
                    }}
                    TreeView::item:selected,
                    TreeWidget::item:selected {{
                        background-color: {FColors.SystemControlTransparent.get()};
                    }}
                    TreeView::item:hover,
                    TreeWidget::item:hover {{
                        background-color: {FColors.SystemControlTransparent.get()};
                    }}
                    TreeView::item:disabled,
                    TreeWidget::item:disabled {{
                        background-color: {FColors.SystemControlTransparent.get()};
                    }}

                    QTreeView::branch {{
                        margin-top: 4px;
                    }}
                    QTreeView::branch:hover {{
                        border: 0px;
                    }} 
                    QTreeView::branch:closed:has-children {{
                        image: url(:/TreeView/img {FColors.img_color.get()}/TreeViewClose.svg);
                    }}
                    QTreeView::branch:open:has-children {{
                        image: url(:/TreeView/img {FColors.img_color.get()}/TreeViewOpen.svg);
                    }}
                    FNavTreeWidget::branch:closed:has-children {{
                        image: None;
                    }}
                    FNavTreeWidget::branch:open:has-children {{
                        image: None;
                    }}
                    
                    
                    /*SLIDER*/
                    
                    QSlider::groove {{
                        border: 0px solid {FColors.ControlFillColorTransparent.get()};
                    }}
                    QSlider::groove:horizontal {{
                        height: 22px;
                    }}
                    QSlider::groove:vertical {{
                        width: 22px;
                    }}
                    
                    QSlider::handle {{
                        background: {FColors.AccentFillColorDefault.get()};
                        border: 5px solid {FColors.ControlSolidFillColorDefault.get()};
                        border-radius: 11px;
                    }}
                    QSlider::handle:horizontal {{
                        width: 12px;
                        height: 22px;
                    }}
                    QSlider::handle:vertical {{
                        height: 12px;
                        width: 22px;
                    }}
                    
                    QSlider::handle:hover {{
                        background: {FColors.AccentFillColorSecondary.get()};
                        border-width: 4px;
                        border-radius: 11px;
                    }}
                    QSlider::handle:horizontal:hover {{
                        width: 14px;
                    }}
                    QSlider::handle:vertical:hover {{
                        height: 14px;
                    }}
                    
                    QSlider::handle:pressed {{
                        background: {FColors.AccentFillColorTertiary.get()};
                        border-width: 6px;
                        border-radius: 11px;
                    }}
                    QSlider::handle:disabled {{
                        background: {FColors.AccentFillColorDisabled.get()};
                    }}
                    QSlider::handle:horizontal:pressed {{
                        width: 10px;
                    }}
                    QSlider::handle:vertical:pressed {{
                        height: 10px;
                    }}
                    
                    QSlider::add-page, QSlider::sub-page {{
                        border-radius: 2px;
                    }}
                    QSlider[invertedAppearance=false]::sub-page:horizontal,
                    QSlider[invertedAppearance=true]::add-page:horizontal,
                    QSlider[invertedAppearance=true]::sub-page:vertical,
                    QSlider[invertedAppearance=false]::add-page:vertical {{
                        background: {FColors.AccentFillColorDefault.get()};
                    }}
                    QSlider[invertedAppearance=true]::sub-page:horizontal,
                    QSlider[invertedAppearance=false]::add-page:horizontal,
                    QSlider[invertedAppearance=false]::sub-page:vertical,
                    QSlider[invertedAppearance=true]::add-page:vertical {{
                        background: {FColors.ControlStrongFillColorDefault.get()};
                    }}
                    
                    QSlider[invertedAppearance=false]::sub-page:horizontal:disabled,
                    QSlider[invertedAppearance=true]::add-page:horizontal:disabled,
                    QSlider[invertedAppearance=true]::sub-page:vertical:disabled,
                    QSlider[invertedAppearance=false]::add-page:vertical:disabled {{
                        background: {FColors.AccentFillColorDisabled.get()};
                    }}
                    QSlider[invertedAppearance=true]::sub-page:horizontal:disabled,
                    QSlider[invertedAppearance=false]::add-page:horizontal:disabled,
                    QSlider[invertedAppearance=false]::sub-page:vertical:disabled,
                    QSlider[invertedAppearance=true]::add-page:vertical:disabled {{
                        background: {FColors.ControlStrongFillColorDisabled.get()};
                    }} 
                    
                    QSlider::sub-page:horizontal {{
                        margin: 9px 8px 9px 0px;
                    }}
                    QSlider::sub-page:vertical {{
                        margin: 0px 9px 8px 9px;
                    }}
                    QSlider::add-page:horizontal {{
                        margin: 9px 0px 9px 6px;
                    }}
                    QSlider::add-page:vertical {{
                        margin: 6px 9px 0px 9px;
                    }}
                    
                    *#accent_text {{
                        color: {FColors.AccentTextFillColorPrimary.get()};
                    }}
                    *#accent_text:hover {{
                        color: {FColors.AccentTextFillColorSecondary.get()};
                    }}
                    *#accent_text:pressed {{
                        color: {FColors.AccentTextFillColorTertiary.get()};
                    }}
                    *#accent_text:disabled {{
                        color: {FColors.AccentTextFillColorDisabled.get()};
                    }}

                    ''')
        return style1 + style2 + self.getUserStyleSheet()


fTheme = FTheme()
