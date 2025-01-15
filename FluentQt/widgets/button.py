# coding=utf-8
from typing import Union, Optional

from qtpy.QtCore import QSize, QRectF, QEvent, QPoint, Signal, Qt, QObject, QPropertyAnimation, QEasingCurve, Property
from qtpy.QtGui import QIcon, QPainter, QPixmap, QCursor, QMouseEvent, QPaintEvent, QFocusEvent
from qtpy.QtWidgets import QPushButton, QToolButton, QWidget, QRadioButton, QSizePolicy, QHBoxLayout, QMenu

from . import FMenu
from .menu import FAction
from .. import fTheme
from ..common import FColors
from ..common.icon_animation import TranslateAnimation
from ..common.icon import drawIcon, FIconBase, FFontIcon
from ..common.overload import Overload
from ..common.widget_mouse_event import WidgetMouseEvent
from ..common.windows_effects import addMenuShadowEffect


class ButtonBase:
    def __init__(self, *args, **kwargs) -> None:
        self.isPressed: bool = False
        self.isHover: bool = False
        self.widgetMouseEvent = WidgetMouseEvent(self)

        self._accent: bool = False
        self._transparent: bool = False
        self._icon: Optional[Union[QIcon, QPixmap, str, FIconBase]] = None

        self.arrowAni = TranslateAnimation(self, installEventFilter=False)
        self._hasBeenPressed = False
        self._menu: Optional[QMenu] = None
        self._minimumMenuWidth: Optional[int] = None

    def isAccent(self) -> bool:
        return self._accent

    def setAccent(self, accent: bool) -> None:
        self.setProperty('isAccent', accent)
        self._accent = accent
        fTheme.update(self)

    def isTransparent(self) -> bool:
        return self._transparent

    def setTransparent(self, transparent: bool) -> None:
        self.setProperty('isTransparent', transparent)
        self._transparent = transparent
        fTheme.update(self)

    def isToggleable(self) -> bool:
        return self.isCheckable()

    def setToggleable(self, toggleable: bool) -> None:
        self.setCheckable(toggleable)
        self.repaint()

    def isToggled(self) -> bool:
        return self.isChecked()

    def setToggled(self, toggled: bool) -> None:
        self.setChecked(toggled)

    def icon(self) -> QIcon:
        if isinstance(self._icon, str) or isinstance(self._icon, QPixmap):
            return QIcon(self._icon)

        elif isinstance(self._icon, FIconBase):
            return self._icon.icon()

        return self._icon

    def getIcon(self) -> Optional[Union[QIcon, QPixmap, str, FIconBase]]:
        return self._icon

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]]) -> None:
        self._icon = icon

    def menu(self) -> Optional[QMenu]:
        return self._menu

    def setMenu(self, menu: Optional[QMenu]):
        self.setProperty('hasMenu', menu is not None)
        self._menu: QMenu = menu
        fTheme.update(self)
        self._hasBeenPressed = False
        if self._menu:
            self._menu.aboutToHide.connect(self._toggleOnHide)
            self._menu.triggered.connect(self._onMenuTriggered)

    def showMenu(self):
        if self._menu:
            self._hasBeenPressed = True

            menu: QMenu = self._menu

            if not self._minimumMenuWidth:
                self._minimumMenuWidth = menu.width()

            if self._minimumMenuWidth < self.width():
                menu.setFixedWidth(self.width())

            menu.adjustSize()

            # show menu
            x = -menu.width() / 2 + menu.contentsMargins().left() + self.width() / 2
            y = self.height() + 4
            menu.move(self.mapToGlobal(QPoint(x, y)))


            height = menu.height()

            self.total_height = menu.height()
            self.__menuHeight = 0

            ani = QPropertyAnimation(self, b'_menuHeight', self)
            ani.setDuration(25)
            ani.setEasingCurve(QEasingCurve.OutQuad)
            ani.valueChanged.connect(self._onValueChanged)
            ani.setStartValue(0)
            ani.setEndValue(height)
            ani.start()

            # menu.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
            menu.show()
            if isinstance(menu, FMenu):
                menu.set_acrylic()

    def menuHeight(self) -> int:
        return self.__menuHeight

    def setmenuHeight(self, opacity):
        self.__menuHeight = opacity

    _menuHeight = Property(float, menuHeight, setmenuHeight)

    def _onValueChanged(self):
        self._menu.resize(self._menu.width(), self.__menuHeight)
        self._menu.setContentsMargins(0, -self.total_height + self.__menuHeight, 0, 0)
        self._menu.update()

    def _toggleOnHide(self):
        if self.isToggleable():
            self.setToggled(False)

    def _onMenuTriggered(self):
        if not (type(self._menu.activeAction()) is FAction and self._menu.activeAction().keepMenuOpen()):
            self._hasBeenPressed = False

    def isUnderMouse(self) -> bool:
        return self.rect().contains(self.mapFromGlobal(QCursor().pos()))

    def _drawIcon(self, icon: Union[QIcon, QPixmap, str, FIconBase], painter: QPainter, rect: QRectF) -> None:

        if self.isChecked() or self.isAccent():
            alpha, color = FColors.TextOnAccentFillColorPrimary.getAlphaAndColor()
            if not self.isEnabled():
                alpha, color = FColors.TextOnAccentFillColorDisabled.getAlphaAndColor()
            elif self.isPressed:
                alpha, color = FColors.TextOnAccentFillColorSecondary.getAlphaAndColor()

        else:
            alpha, color = FColors.TextFillColorPrimary.getAlphaAndColor()
            if not self.isEnabled():
                alpha, color = FColors.TextFillColorDisabled.getAlphaAndColor()
            elif self.isPressed:
                alpha, color = FColors.TextFillColorSecondary.getAlphaAndColor()

        if not isinstance(icon, FIconBase) and not self.isEnabled():
            painter.setOpacity(alpha)

        drawIcon(icon, painter, rect, fill=color, opacity=alpha)

    def _drawDropDownIcon(self, painter: QPainter, rect: QRectF) -> None:

        if self.isChecked() or self.isAccent():
            alpha, color = FColors.TextOnAccentFillColorPrimary.getAlphaAndColor()
            if not self.isEnabled():
                alpha, color = FColors.TextOnAccentFillColorDisabled.getAlphaAndColor()
            elif self.isPressed:
                alpha, color = FColors.TextOnAccentFillColorSecondary.getAlphaAndColor()
            elif self.isHover and not self._menu.isVisible():
                alpha, color = FColors.TextOnAccentFillColorSecondary.getAlphaAndColor()
        else:
            alpha, color = FColors.TextFillColorSecondary.getAlphaAndColor()
            if not self.isEnabled():
                alpha, color = FColors.TextFillColorDisabled.getAlphaAndColor()
            elif self.isPressed:
                alpha, color = FColors.TextFillColorTertiary.getAlphaAndColor()
            elif self.isHover and not self._menu.isVisible():
                alpha, color = FColors.TextFillColorTertiary.getAlphaAndColor()

        FFontIcon("\uE96E").render(painter, rect, fill=color, opacity=alpha)


class FPushButton(ButtonBase, QPushButton):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, text: str, parent: Optional[QWidget] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], text: str, parent: Optional[QWidget] = None) -> None
    """

    @Overload
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        QPushButton.__init__(self, parent=parent)
        ButtonBase.__init__(self)

    @__init__.register
    def _(self, text: str, parent: Optional[QWidget] = None):
        QPushButton.__init__(self, parent=parent)
        ButtonBase.__init__(self)
        self.setText(text)

    @__init__.register
    def _(self, icon: Union[QIcon, QPixmap, str, FIconBase], text: str, parent: Optional[QWidget] = None):
        QPushButton.__init__(self, parent=parent)
        ButtonBase.__init__(self)
        self.setText(text)
        self.setIcon(icon)

    def icon(self) -> QIcon:
        return ButtonBase.icon(self)

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]]) -> None:
        if self._icon != icon:
            if not (icon and self._icon):
                self.setProperty('hasIcon', icon is not None)
                fTheme.update(self)
        ButtonBase.setIcon(self, icon)

    def menu(self) -> Optional[QMenu]:
        return ButtonBase.menu(self)

    def setMenu(self, menu: Optional[QMenu]) -> None:
        ButtonBase.setMenu(self, menu)

    def showMenu(self) -> None:
        ButtonBase.showMenu(self)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if not self._hasBeenPressed:
            self.arrowAni.onPress(e)
            super().mousePressEvent(e)
        else:
            self.widgetMouseEvent.cancelPressEvent()

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.arrowAni.onRelease(e)
        if not self._hasBeenPressed:
            super().mouseReleaseEvent(e)
            self.showMenu()
        else:
            self._hasBeenPressed = False

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        if not (self.menu() and self.menu().isVisible()):
            self._hasBeenPressed = False

    def paintEvent(self, e: QPaintEvent) -> None:
        if self.menu() and self.menu().isVisible():
            x = -self.menu().width() / 2 + self.menu().contentsMargins().left() + self.width() / 2
            y = self.height() + 4
            self.menu().move(self.mapToGlobal(QPoint(x, y)))

        super().paintEvent(e)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        mw = self.minimumSizeHint().width()
        if self._icon:
            w, h = self.iconSize().width(), self.iconSize().height()
            y = (self.height() - h) / 2
            if mw > 0:
                self._drawIcon(self._icon, painter, QRectF(12 + (self.width() - mw) / 2, y, w, h))
            else:
                self._drawIcon(self._icon, painter, QRectF(12, y, w, h))

        if self._menu:
            rect = QRectF(self.width() - (self.width() - mw) / 2 - 23, self.height() / 2 - 5 + self.arrowAni.offset, 10,
                          10)
            self._drawDropDownIcon(painter, rect)


class FToolButton(ButtonBase, QToolButton):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], parent: Optional[QWidget] = None) -> None
    """

    @Overload
    def __init__(self, parent: Optional[QWidget] = None):
        QToolButton.__init__(self, parent=parent)
        ButtonBase.__init__(self)
        self.setIconSize(QSize(18, 18))

    @__init__.register
    def _(self, icon: Union[QIcon, QPixmap, str, FIconBase], parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setIcon(icon)

    def icon(self) -> QIcon:
        return ButtonBase.icon(self)

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]]) -> None:
        ButtonBase.setIcon(self, icon)

    def menu(self) -> Optional[QMenu]:
        return ButtonBase.menu(self)

    def setMenu(self, menu: Optional[QMenu]) -> None:
        if menu:
            menu.installEventFilter(self)
        if self.menu():
            self._menu.removeEventFilter(self)
        ButtonBase.setMenu(self, menu)

    def showMenu(self) -> None:
        ButtonBase.showMenu(self)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if not self._hasBeenPressed:
            self.arrowAni.onPress(e)
            super().mousePressEvent(e)
        else:
            self.widgetMouseEvent.cancelPressEvent()

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.arrowAni.onRelease(e)
        if not self._hasBeenPressed:
            super().mouseReleaseEvent(e)
            self.showMenu()
        else:
            self._hasBeenPressed = False

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        if not (self.menu() and self.menu().isVisible()):
            self._hasBeenPressed = False

    def paintEvent(self, e: QPaintEvent) -> None:
        if self.menu() and self.menu().isVisible():
            x = -self.menu().width() / 2 + self.menu().contentsMargins().left() + self.width() / 2
            y = self.height() + 4
            self.menu().move(self.mapToGlobal(QPoint(x, y)))

        super().paintEvent(e)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        if self._icon:
            w, h = self.iconSize().width(), self.iconSize().height()
            y = (self.height() - h) / 2
            x = (self.width() - w) / 2
            if self._menu:
                x = (self.width() - w - 10) / 2 - 5
            self._drawIcon(self._icon, painter, QRectF(x, y, w, h))

        if self._menu:
            w, h = 10, 10
            y = (self.height() - h) / 2 + self.arrowAni.offset
            x = self.width() / 2 + (w + self.iconSize().width()) / 2 - 5
            self._drawDropDownIcon(painter, QRectF(x, y, w, h))

    def eventFilter(self, watched, event):
        if watched is self.menu():
            if event.type() == QEvent.Type.Hide:
                self._hasBeenPressed = False
        return super().eventFilter(watched, event)


class FHyperLinkButton(FPushButton):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, text: str, parent: Optional[QWidget] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], text: str, parent: Optional[QWidget] = None) -> None
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def isAccent(self) -> bool:
        return False

    def setAccent(self, accent: bool):
        pass

    def isTransparent(self) -> bool:
        return False

    def setTransparent(self, transparent: bool):
        pass

    def isToggleable(self):
        return False

    def setToggleable(self, toggleable: bool):
        pass

    def isToggled(self):
        return False

    def setToggled(self, toggled: bool):
        pass

    def menu(self) -> Optional[QMenu]:
        return None

    def setMenu(self, menu: Optional[QMenu]) -> None:
        pass

    def showMenu(self) -> None:
        pass

    def _drawIcon(self, icon: Union[QIcon, QPixmap, str, FIconBase], painter: QPainter, rect: QRectF) -> None:

        alpha, color = FColors.AccentTextFillColorPrimary.getAlphaAndColor()
        if not self.isEnabled():
            alpha, color = FColors.AccentTextFillColorDisabled.getAlphaAndColor()
        elif self.isPressed:
            alpha, color = FColors.AccentTextFillColorTertiary.getAlphaAndColor()
        elif self.isHover:
            alpha, color = FColors.AccentTextFillColorSecondary.getAlphaAndColor()

        if not isinstance(icon, FIconBase) and not self.isEnabled():
            alpha, color = FColors.TextFillColorDisabled.getAlphaAndColor()
            painter.setOpacity(alpha)

        drawIcon(icon, painter, rect, fill=color, opacity=alpha)


class FNavigationViewButton(FToolButton):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], parent: Optional[QWidget] = None) -> None
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(QSize(40, 36))
        self.setTransparent(True)


class FLineEditButton(FToolButton):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], parent: Optional[QWidget] = None) -> None
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(30)
        self.setIconSize(QSize(12, 12))
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._isButtonEnabled: bool = True
        self.setTransparent(True)

    def isButtonEnabled(self) -> bool:
        return self._isButtonEnabled

    def setButtonEnabled(self, enable: bool) -> None:
        self._isButtonEnabled = enable

    def _drawIcon(self, icon: Union[QIcon, QPixmap, str, FIconBase], painter: QPainter, rect: QRectF) -> None:

        if self.isChecked() or self.isAccent():
            alpha, color = FColors.TextOnAccentFillColorPrimary.getAlphaAndColor()
            if not self.isEnabled():
                alpha, color = FColors.TextOnAccentFillColorDisabled.getAlphaAndColor()
            elif self.isPressed:
                alpha, color = FColors.TextOnAccentFillColorSecondary.getAlphaAndColor()
        else:
            alpha, color = FColors.TextFillColorPrimary.getAlphaAndColor()
            if not self.isEnabled():
                alpha, color = FColors.TextFillColorDisabled.getAlphaAndColor()
            elif self.isPressed:
                alpha, color = FColors.TextFillColorSecondary.getAlphaAndColor()

        if not isinstance(icon, FIconBase) and not self.isEnabled():
            painter.setOpacity(alpha)

        drawIcon(icon, painter, rect, fill=color, opacity=alpha)


class FRadioButton(QRadioButton):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, text: str, parent: Optional[QWidget] = None) -> None
    """


class FSplitDropButton(FToolButton):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], parent: Optional[QWidget] = None) -> None
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arrowAni = TranslateAnimation(self, installEventFilter=False)
        self.setIconSize(QSize(10, 10))
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setIcon(FFontIcon("\uE96E"))

    def _drawIcon(self, icon: Union[QIcon, QPixmap, str, FIconBase], painter: QPainter, rect: QRectF) -> None:
        rect.translate(0, self.arrowAni.offset)

        if self.isChecked() or self.isAccent():
            alpha, color = FColors.TextOnAccentFillColorPrimary.getAlphaAndColor()
            if not self.isEnabled():
                alpha, color = FColors.TextOnAccentFillColorDisabled.getAlphaAndColor()
            elif self.isPressed:
                alpha, color = FColors.TextOnAccentFillColorSecondary.getAlphaAndColor()
        else:
            alpha, color = FColors.TextFillColorSecondary.getAlphaAndColor()
            if not self.isEnabled():
                alpha, color = FColors.TextFillColorDisabled.getAlphaAndColor()
            elif self.isPressed:
                alpha, color = FColors.TextFillColorTertiary.getAlphaAndColor()
            elif self.isHover and not (self.parent().menu() and self.parent().menu().isVisible()):
                alpha, color = FColors.TextFillColorPrimary.getAlphaAndColor()

        if not isinstance(icon, FIconBase) and not self.isEnabled():
            painter.setOpacity(alpha)

        drawIcon(icon, painter, rect, fill=color, opacity=alpha)

    def mouseReleaseEvent(self, e):
        self.arrowAni.onRelease(e)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        self.arrowAni.onPress(e)


class FSplitButtonBase(QWidget):
    """
    __init__(self, button: Union[QPushButton, QToolButton] parent: Optional[QWidget] = None) -> None
    """
    dropDownClicked = Signal()

    def __init__(self, button: Union[QPushButton, QToolButton], parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self._menu: Optional[QWidget] = None
        self._minimumFlyoutWidth = None

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.button: Union[QPushButton, QToolButton] = button

        self._toggleable = False
        self._toggled = False
        self._accent = False
        self._transparent = False
        self._hasBeenPressed = False

        self.dropButton = FSplitDropButton(self)
        self.dropButton.installEventFilter(self)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.dropButton)

        self.setButton(self.button)

    def setButton(self, button: Union[QPushButton, QToolButton]):
        self.button = button
        self.button.toggled.connect(lambda: self.setToggled(self.button.isChecked()))
        self.hBoxLayout.insertWidget(0, self.button)
        self.button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.button.installEventFilter(self)
        self.button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def menu(self) -> Optional[QWidget]:
        return self._menu

    def setMenu(self, menu: Optional[QWidget]):
        """ set the widget pops up when drop down button is clicked

        Parameters
        ----------
        menu: QWidget
            the widget pops up when drop down button is clicked.
            It should contain the `exec` method, whose first parameter type is `QPoint`
        """
        self._menu = menu
        if self._menu:
            self._menu.triggered.connect(self.onMenuTriggered)

    def showMenu(self):
        """ show flyout """
        if self._menu:
            self._hasBeenPressed = True

            w = self._menu

            if not self._minimumFlyoutWidth:
                self._minimumFlyoutWidth = w.width()

            if self._minimumFlyoutWidth < self.width():
                w.setFixedWidth(self.width())

            w.adjustSize()

            # show menu
            x = -w.width() / 2 + w.contentsMargins().left() + self.width() / 2
            y = self.height() + 4

            height = w.height()

            w.move(self.mapToGlobal(QPoint(x, y)))

            self.total_height = w.height()
            self.__menuHeight = 0

            ani = QPropertyAnimation(self, b'_menuHeight', self)
            ani.setDuration(25)
            ani.setEasingCurve(QEasingCurve.OutQuad)
            ani.valueChanged.connect(self._onValueChanged)
            ani.setStartValue(0)
            ani.setEndValue(height)
            ani.start()

            # ani_manager = WidgetAnimationManager.make(w, WidgetAnimationType.DROP_DOWN)
            # ani_manager.exec(self.mapToGlobal(QPoint(x, y)), int(w.width() / 2), mask=True, aniDuration=200)

            # w.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
            w.show()
            if isinstance(w, FMenu):
                w.set_acrylic()

    def menuHeight(self) -> int:
        return self.__menuHeight

    def setmenuHeight(self, opacity):
        self.__menuHeight = opacity

    _menuHeight = Property(float, menuHeight, setmenuHeight)

    def _onValueChanged(self):
        self._menu.resize(self._menu.width(), self.__menuHeight)
        self._menu.setContentsMargins(0, -self.total_height + self.__menuHeight, 0, 0)

    def icon(self):
        return self.button.icon()

    def setIcon(self, icon: Union[QIcon, FIconBase, str]):
        self.button.setIcon(icon)

    def setIconSize(self, size: QSize):
        self.button.setIconSize(size)

    def isAccent(self) -> bool:
        return self._accent

    def setAccent(self, accent: bool):
        self.button.setAccent(accent)
        self.dropButton.setAccent(accent)
        self._accent = accent

    def isTransparent(self) -> bool:
        return self._transparent

    def setTransparent(self, transparent: bool) -> None:
        self.button.setTransparent(transparent)
        self.dropButton.setTransparent(transparent)
        self._transparent = transparent

    def isToggleable(self):
        return self._toggleable

    def setToggleable(self, toggleable: bool):
        self.button.setToggleable(toggleable)
        self._toggleable = toggleable

    def isToggled(self):
        return self._toggled

    def setToggled(self, toggled: bool):
        self.button.setToggled(toggled)
        self.dropButton.setAccent(toggled)
        self._toggled = toggled

    def onMenuTriggered(self):
        self._hasBeenPressed = False

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        if not (self.menu() and self.menu().isVisible()):
            self._hasBeenPressed = False

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            if not self._hasBeenPressed:
                return super().eventFilter(watched, event)
            return True

        if event.type() == QEvent.Type.MouseButtonRelease:
            if watched == self.dropButton:
                self.dropButton.mouseReleaseEvent(event)
            if not self._hasBeenPressed:
                if watched == self.dropButton:
                    self.showMenu()
                    self.dropDownClicked.emit()
                return super().eventFilter(watched, event)
            self._hasBeenPressed = False
            return True

        return super().eventFilter(watched, event)


class FSplitPushButton(FSplitButtonBase):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, text: str, parent: Optional[QWidget] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], text: str, parent: Optional[QWidget] = None) -> None
    """

    clicked = Signal(bool)

    @Overload
    def __init__(self, parent: Optional[QWidget] = None):
        self.button = FPushButton()
        super().__init__(self.button, parent=parent)
        self.button.clicked.connect(self.clicked)
        self.button.setParent(self)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    @__init__.register
    def _(self, text: str, parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setText(text)

    @__init__.register
    def _(self, icon: Union[QIcon, QPixmap, str, FIconBase], text: str, parent: Optional[QWidget] = None):
        self.__init__(text=text, parent=parent)
        self.setIcon(icon)

    def text(self):
        return self.button.text()

    def setText(self, text: str):
        self.button.setText(text)
        self.adjustSize()


class FSplitToolButton(FSplitButtonBase):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], parent: Optional[QWidget] = None) -> None
    """

    clicked = Signal(bool)

    @Overload
    def __init__(self, parent: Optional[QWidget] = None):
        self.button = FToolButton()
        super().__init__(self.button, parent=parent)
        self.button.clicked.connect(self.clicked)
        self.button.setParent(self)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    @__init__.register
    def _(self, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]], parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setIcon(icon)
