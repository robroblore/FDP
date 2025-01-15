# coding=utf-8
from enum import Enum

from qtpy.QtGui import QPaintEvent
from qtpy.QtCore import QRectF, Qt, Property, QSize
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import QAbstractButton

from .. import FColors, FColor
from ..common.icon import drawIcon, FFontIcon
# noinspection PyUnresolvedReferences
from ..ressources import resource


class TitleBarButtonState(Enum):
    """ Title bar button state """
    NORMAL = 0
    HOVER = 1
    PRESSED = 2


class TitleBarButton(QAbstractButton):
    """ Title bar button """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setFixedHeight(30)
        self.setIconSize(QSize(10, 10))
        self._state = TitleBarButtonState.NORMAL

        # icon color
        self._normalColor = FColor("#FFFFFF", "#191919")
        self._hoverColor = FColor("#FFFFFF", "#191919")
        self._pressedColor = FColor("#CFCFCF", "#606060")
        self._inactiveColor = FColor("#717171", "#9b9b9b")

        # background color
        self._normalBgColor: FColor = FColors.SubtleFillColorTransparent
        self._hoverBgColor: FColor = FColors.SubtleFillColorSecondary
        self._pressedBgColor: FColor = FColors.SubtleFillColorTertiary

    def setState(self, state):
        """ set the state of button

        Parameters
        ----------
        state: TitleBarButtonState
            the state of button
        """
        self._state = state
        self.update()

    def isPressed(self):
        """ whether the button is pressed """
        return self._state == TitleBarButtonState.PRESSED

    def getNormalColor(self) -> FColor:
        """ get the icon color of the button in normal state """
        return self._normalColor

    def getHoverColor(self) -> FColor:
        """ get the icon color of the button in hover state """
        return self._hoverColor

    def getPressedColor(self) -> FColor:
        """ get the icon color of the button in pressed state """
        return self._pressedColor

    def getNormalBackgroundColor(self) -> FColor:
        """ get the background color of the button in normal state """
        return self._normalBgColor

    def getHoverBackgroundColor(self) -> FColor:
        """ get the background color of the button in hover state """
        return self._hoverBgColor

    def getPressedBackgroundColor(self) -> FColor:
        """ get the background color of the button in pressed state """
        return self._pressedBgColor

    def setNormalColor(self, color: FColor) -> None:
        """ set the icon color of the button in normal state

        Parameters
        ----------
        color: QColor
            icon color
        """
        self._normalColor = color
        self.update()

    def setHoverColor(self, color: FColor) -> None:
        """ set the icon color of the button in hover state

        Parameters
        ----------
        color: QColor
            icon color
        """
        self._hoverColor = color
        self.update()

    def setPressedColor(self, color: FColor) -> None:
        """ set the icon color of the button in pressed state

        Parameters
        ----------
        color: QColor
            icon color
        """
        self._pressedColor = color
        self.update()

    def setNormalBackgroundColor(self, color: FColor) -> None:
        """ set the background color of the button in normal state

        Parameters
        ----------
        color: QColor
            background color
        """
        self._normalBgColor = color
        self.update()

    def setHoverBackgroundColor(self, color: FColor) -> None:
        """ set the background color of the button in hover state

        Parameters
        ----------
        color: QColor
            background color
        """
        self._hoverBgColor = color
        self.update()

    def setPressedBackgroundColor(self, color: FColor) -> None:
        """ set the background color of the button in pressed state

        Parameters
        ----------
        color: QColor
            background color
        """
        self._pressedBgColor = color
        self.update()

    def enterEvent(self, e):
        self.setState(TitleBarButtonState.HOVER)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setState(TitleBarButtonState.NORMAL)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() != Qt.MouseButton.LeftButton:
            return

        self.setState(TitleBarButtonState.PRESSED)
        super().mousePressEvent(e)

    def _getColors(self):
        """ get the icon color and background color """
        if self._state == TitleBarButtonState.NORMAL and self.window().isActiveWindow():
            return self._normalColor.getColor(), self._normalBgColor.getColor()
        elif self._state == TitleBarButtonState.HOVER:
            return self._hoverColor.getColor(), self._hoverBgColor.getColor()
        elif not self.window().isActiveWindow():
            return self._inactiveColor.getColor(), self._normalBgColor.getColor()

        return self._pressedColor.getColor(), self._pressedBgColor.getColor()

    normalColor = Property(QColor, getNormalColor, setNormalColor)
    hoverColor = Property(QColor, getHoverColor, setHoverColor)
    pressedColor = Property(QColor, getPressedColor, setPressedColor)
    normalBackgroundColor = Property(QColor, getNormalBackgroundColor, setNormalBackgroundColor)
    hoverBackgroundColor = Property(QColor, getHoverBackgroundColor, setHoverBackgroundColor)
    pressedBackgroundColor = Property(QColor, getPressedBackgroundColor, setPressedBackgroundColor)

    def _drawIcon(self, painter: QPainter, rect: QRectF):
        pass

    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter(self)
        bg_color = self._getColors()[1]

        # draw background
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        x = (self.width() - w) / 2
        self._drawIcon(painter, QRectF(x, y, w, h))


class MinimizeButton(TitleBarButton):
    """ Minimize button """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(42)

    def _drawIcon(self, painter: QPainter, rect: QRectF):
        color = self._getColors()[0]
        rect.setY(rect.y() + 1)
        rect.setHeight(rect.height() + 1)
        drawIcon(FFontIcon("\uE921"), painter, rect, fill=color)


class MaximizeButton(TitleBarButton):
    """ Maximize button """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._isMax = False
        self.setFixedWidth(48)

    def setMaxState(self, isMax):
        """ update the maximized state and icon """
        if self._isMax == isMax:
            return

        self._isMax = isMax
        self.setState(TitleBarButtonState.NORMAL)

    def _drawIcon(self, painter: QPainter, rect: QRectF):
        color = self._getColors()[0]
        if not self._isMax:
            drawIcon(FFontIcon("\uE922"), painter, rect, fill=color)
        else:
            drawIcon(FFontIcon("\uE923"), painter, rect, fill=color)


class CloseButton(TitleBarButton):
    """ Close button """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHoverColor(FColor("#FFFFFF"))
        self.setPressedColor(FColor("#CFCFCF"))
        self.setHoverBackgroundColor(FColor("#C42B1C"))
        self.setPressedBackgroundColor(FColor("#AE2A1B"))
        self.setFixedWidth(45)
        self.xOffset = 1

    def _drawIcon(self, painter: QPainter, rect: QRectF):
        color = self._getColors()[0]
        rect.setX(rect.x() - self.xOffset)
        rect.setWidth(rect.width() - self.xOffset)
        drawIcon(FFontIcon("\uE8bb"), painter, rect, fill=color)
