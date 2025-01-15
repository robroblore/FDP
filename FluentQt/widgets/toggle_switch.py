# coding=utf-8
from typing import Optional

from qtpy.QtCore import QRect, QPropertyAnimation, QEasingCurve, Qt
from qtpy.QtGui import QPaintEvent, QPainter, QCursor, QPainterPath
from qtpy.QtWidgets import QCheckBox, QWidget,QStyle, QStyleOption

from .. import FColors
from ..common.overload import Overload
from ..common.widget_mouse_event import WidgetMouseEvent


class FToggleSwitch(QCheckBox):
    """
    _init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, text: str, parent: Optional[QWidget] = None) -> None
    """

    @Overload
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self.isPressed: bool = False
        self.isHover: bool = False
        WidgetMouseEvent(self)

        self.ani = QPropertyAnimation(self)
        self.ani.setTargetObject(self)
        self.ani.valueChanged.connect(self.update)

        self.stateChanged.connect(self.checkEvent)

    @__init__.register
    def _(self, text: str, parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setText(text)

    def isUnderMouse(self) -> bool:
        return self.rect().contains(self.mapFromGlobal(QCursor().pos()))

    def checkEvent(self):
        if self.isChecked():
            self.ani.setStartValue(4)
            self.ani.setEndValue(24)
            self.ani.setDuration(120)
            self.ani.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.ani.start()
        else:
            self.ani.setStartValue(24)
            self.ani.setEndValue(4)
            self.ani.setDuration(120)
            self.ani.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.ani.start()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        if self.isChecked():
            if self.isEnabled():
                color = FColors.TextOnAccentFillColorPrimary.getColor()
            else:
                color = FColors.TextOnAccentFillColorDisabled.getColor()
            x = self.ani.currentValue()
            if self.isPressed:
                x -= 3
        else:
            if self.isEnabled():
                color = FColors.TextFillColorSecondary.getColor()
            else:
                color = FColors.TextFillColorDisabled.getColor()
            x = self.ani.currentValue()

        if not x:
            x = 4

        path = QPainterPath()

        if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            x += self.width() - self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, QStyleOption(), self).width()

        if self.isPressed:
            path.addRoundedRect(QRect(x - 1, self.height()/2 - 7, 17, 14), 7, 7)
        elif self.isHover:
            path.addRoundedRect(QRect(x - 1, self.height()/2 - 7, 14, 14), 7, 7)
        else:
            path.addRoundedRect(QRect(x, self.height()/2 - 6, 12, 12), 6, 6)

        painter.fillPath(path, color)
