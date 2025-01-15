# coding=utf-8
from enum import Enum
from math import ceil
from typing import Optional

from qtpy.QtCore import Qt, QEvent, QPoint
from qtpy.QtGui import QPaintEvent
from qtpy.QtWidgets import QStylePainter, QSlider, QToolTip, QStyle, QWidget

from ..common import FColors, fTheme
from ..common.overload import Overload


class FSlider(QSlider):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None) -> None
    """

    class TickPosition(Enum):

        NoTicks = 0
        TicksAbove = 1
        TicksLeft = 1
        TicksBelow = 2
        TicksRight = 2
        TicksBothSides = 3
        TicksInline = 4

    @Overload
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self._snapToTick = False
        self._stepFrequency = 1
        self._tickPosition = FSlider.TickPosition.NoTicks
        self._showValueToolTip = False
        self._toolTipPrefix = ""
        self._toolTipSuffix = ""

    @__init__.register
    def _(self, orientation: Qt.Orientation, parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setOrientation(orientation)

    def snapToTick(self) -> bool:
        return self._snapToTick

    def setSnapToTick(self, snap: bool) -> None:
        self._snapToTick = snap

    def stepFrequency(self) -> int:
        return self._stepFrequency

    def setStepFrequency(self, step: int) -> None:
        self._stepFrequency = step

    def tickPosition(self) -> TickPosition:
        return self._tickPosition

    def setTickPosition(self, position: TickPosition) -> None:
        self._tickPosition = position

    def setInvertedAppearance(self, appearance: bool) -> None:
        super().setInvertedAppearance(appearance)
        fTheme.update(self)

    def showValueToolTip(self) -> bool:
        return self._showValueToolTip

    def setShowValueToolTip(self, showValueToolTip: bool) -> None:
        self._showValueToolTip = showValueToolTip

    def toolTipPrefix(self) -> str:
        return self._toolTipPrefix

    def setToolTipPrefix(self, prefix: any) -> None:
        self._toolTipPrefix = str(prefix)

    def toolTipSuffix(self) -> str:
        return self._toolTipSuffix

    def setToolTipSuffix(self, suffix: any) -> None:
        self._toolTipSuffix = str(suffix)

    def event(self, event: QEvent) -> bool:
        slider_position = self.sliderPosition()
        return_value = super().event(event)

        interval = self.tickInterval()
        if interval == 0:
            interval = self.pageStep()

        if event.type() == QEvent.Type.MouseMove:
            if self.stepFrequency() != 0:
                self.setValue(round(self.sliderPosition() / self.stepFrequency()) * self.stepFrequency())
            else:
                self.setValue(slider_position)

        if self.snapToTick() and event.type() == QEvent.Type.MouseButtonRelease and interval != 0 and self.sliderPosition() % interval != 0:
            self.setValue(round(self.sliderPosition() / interval) * interval)

        if slider_position != self.sliderPosition():

            if self.orientation() == Qt.Orientation.Horizontal:
                x = QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), self.sliderPosition(), self.width() - 22)
                y = self.rect().bottom()/2 - 68
                if self.invertedAppearance():
                    x = self.width() - 22 - x
                pos = QPoint(x, y)
            else:
                x = self.rect().right()/2 - 68
                y = QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), self.sliderPosition(), self.height() - 22)
                if not self.invertedAppearance():
                    y = self.height() - 22 - y
                pos = QPoint(x, y)

            if self.showValueToolTip():
                if self.snapToTick() and event.type() == QEvent.Type.MouseMove and interval != 0:
                    QToolTip.showText(self.mapToGlobal(pos), f"{self.toolTipPrefix()}{round(self.sliderPosition() / interval) * interval}{self.toolTipSuffix()}")
                else:
                    QToolTip.showText(self.mapToGlobal(pos), f"{self.toolTipPrefix()}{self.sliderPosition()}{self.toolTipSuffix()}")
        return return_value

    def paintEvent(self, event: QPaintEvent) -> None:

        interval = self.tickInterval()
        if interval == 0:
            interval = self.pageStep()

        if self.tickPosition() != self.TickPosition.NoTicks and self.maximum() != self.minimum() and interval != 0:

            painter = QStylePainter(self)

            handle_width = 22
            handle_half_width = handle_width / 2
            slider_value_range = self.maximum() - self.minimum()
            if self.orientation() == Qt.Orientation.Horizontal:
                drawing_range = self.width() - handle_width
            else:
                drawing_range = self.height() - handle_width

            factor = drawing_range / slider_value_range

            for i in range(self.minimum(), self.maximum() + 1, interval):
                tick_height = 3

                offset_value_space = i - self.minimum()
                offset_drawing_space = factor * offset_value_space + handle_half_width
                if self.orientation() == Qt.Orientation.Horizontal:
                    x = int(offset_drawing_space)
                    y = ceil(self.rect().bottom() / 2)
                    if self.invertedAppearance():
                        x = self.width() - x
                else:
                    x = ceil(self.rect().right() / 2)
                    y = int(offset_drawing_space)
                    if not self.invertedAppearance():
                        y = self.height() - y

                if not self.isEnabled():
                    painter.setPen(FColors.ControlStrongFillColorDisabled.getColor())
                elif self.tickPosition() == self.TickPosition.TicksInline:
                    painter.setPen(FColors.ControlFillColorInputActive.getColor())
                else:
                    painter.setPen(FColors.ControlStrongFillColorDefault.getColor())

                if self.tickPosition() == self.TickPosition.TicksBothSides or self.tickPosition() == self.TickPosition.TicksAbove or self.tickPosition() == self.TickPosition.TicksLeft:
                    if self.orientation() == Qt.Orientation.Horizontal:
                        painter.drawLine(x, y - 10, x, y - 10 + tick_height)
                    else:
                        painter.drawLine(x - 10, y, x - 10 + tick_height, y)

                if self.tickPosition() == self.TickPosition.TicksBothSides or self.tickPosition() == self.TickPosition.TicksBelow or self.tickPosition() == self.TickPosition.TicksRight:
                    if self.orientation() == Qt.Orientation.Horizontal:
                        painter.drawLine(x, y + 9, x, y + 9 - tick_height)
                    else:
                        painter.drawLine(x + 9, y, x + 9 - tick_height, y)
            painter.end()
            super().paintEvent(event)
            if self.tickPosition() == self.TickPosition.TicksInline:
                painter = QStylePainter(self)
                for i in range(self.minimum(), self.maximum() + 1, interval):
                    offset_value_space = i - self.minimum()
                    offset_drawing_space = factor * offset_value_space + handle_half_width

                    if self.orientation() == Qt.Orientation.Horizontal:
                        x = int(offset_drawing_space)
                        slider_pos = round(self.sliderPosition()/self.maximum() * (self.width() - handle_width) + handle_half_width)

                        if self.invertedAppearance():
                            x = self.width() - x
                            slider_pos = self.width() - slider_pos

                        if x - slider_pos >= handle_half_width or x - slider_pos < - handle_half_width:
                            y = ceil(self.rect().bottom() / 2)
                            painter.drawLine(x, y - 2, x, y + 1)
                    else:
                        y = int(offset_drawing_space)
                        slider_pos = round(self.sliderPosition()/self.maximum() * (self.height() - handle_width) + handle_half_width)

                        if not self.invertedAppearance():
                            y = self.height() - y
                            slider_pos = int(self.height() - slider_pos)

                        if y - slider_pos >= handle_half_width or y - slider_pos < - handle_half_width:
                            x = ceil(self.rect().right() / 2)
                            painter.drawLine(x - 2, y, x + 1, y)
            return
        super().paintEvent(event)
