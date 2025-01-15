# coding=utf-8
import math
from enum import Enum
from typing import Optional

from qtpy.QtCore import QRectF, QTimer, Qt
from qtpy.QtGui import QPaintEvent, QPainter, QPainterPath, QPen
from qtpy.QtWidgets import QProgressBar, QWidget

from .. import fTheme, FColors, FColor


class FProgressBar(QProgressBar):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None
    """
    class ProgressState(Enum):
        Running = 0
        Paused = 1
        Error = 2

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self._progressState = self.ProgressState.Running
        self.setProperty("progressState", self._progressState.name.lower())
        self.setTextVisible(False)
        self.setOrientation(Qt.Orientation.Vertical)

        self.setMaximumHeight(3 if self.orientation() == Qt.Orientation.Horizontal else 16777215)
        self.setMaximumWidth(3 if self.orientation() != Qt.Orientation.Horizontal else 16777215)

    def setOrientation(self, orientation):
        super().setOrientation(orientation)
        self.setMaximumHeight(3 if orientation == Qt.Orientation.Horizontal else 16777215)
        self.setMaximumWidth(3 if orientation != Qt.Orientation.Horizontal else 16777215)

    def progressState(self) -> ProgressState:
        return self._progressState

    def setProgressState(self, state: ProgressState) -> None:
        self._progressState = state
        self.setProperty("progressState", state.name.lower())
        fTheme.update(self)

    def paintEvent(self, event):
        super().paintEvent(event)


class FProgressRing(QProgressBar):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None
    """

    class ProgressState(Enum):
        Running = 0
        Paused = 1
        Error = 2

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self._progressState = self.ProgressState.Running
        self.setProperty("progressState", self._progressState.name.lower())
        self._animStep = 0
        self._animTimer = QTimer(self)
        self._animTimer.timeout.connect(self._timerTimeout)
        self._backGroundColor: Optional[FColor] = None

    def _timerTimeout(self):
        self._animStep += 8
        self.update()

    def progressState(self) -> ProgressState:
        return self._progressState

    def setProgressState(self, state: ProgressState) -> None:
        self._progressState = state
        self.setProperty("progressState", state.name.lower())
        fTheme.update(self)

    def getSmallerLength(self):
        return min(self.width(), self.height()) - 6

    def setMaximum(self, maximum):
        if maximum == 0 and self.minimum() == 0:
            self._animTimer.start(16)
        else:
            self._animTimer.stop()
            self._animStep = 0
        super().setMaximum(maximum)

    def setMinimum(self, minimum):
        if self.maximum() == 0 and minimum == 0:
            self._animTimer.start(16)
        else:
            self._animTimer.stop()
            self._animStep = 0
        super().setMinimum(minimum)

    def backGroundColor(self) -> Optional[FColor]:
        return self._backGroundColor

    def setBackGroundColor(self, color: Optional[FColor]):
        self._backGroundColor = color
        self.update()

    def paintEvent(self, e: QPaintEvent) -> None:
        value = self.value()
        if value < 0:
            value = 0
        try:
            pd = value/(self.maximum() - self.minimum()) * 360
        except ZeroDivisionError:
            pd = 180

        painter = QPainter(self)
        painter.translate(3, 3)
        painter.setRenderHint(QPainter.Antialiasing)

        if self._backGroundColor:
            path = QPainterPath()
            path.moveTo(self.getSmallerLength()/2, 0)
            path.arcTo(QRectF(0, 0, self.getSmallerLength(), self.getSmallerLength()), 90, 360)
            pen = QPen()
            pen.setWidth(5)
            pen.setColor(self._backGroundColor.getColor())
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.strokePath(path, pen)

        path2 = QPainterPath()

        start_angle = 90
        end_angle = pd

        if self.maximum() == 0 and self.minimum() == 0:
            start_angle = -self._animStep
            end_angle = (math.sin(math.radians(self._animStep/2)) * 75 + 85) * -1

        if self.invertedAppearance():
            path2.moveTo(
                math.cos(math.radians(180+start_angle)) * self.getSmallerLength() / 2 + self.getSmallerLength() / 2,
                math.sin(math.radians(180+start_angle)) * self.getSmallerLength() / 2 + self.getSmallerLength() / 2)
            path2.arcTo(QRectF(0, 0, self.getSmallerLength(), self.getSmallerLength()), 180-start_angle, end_angle)
        else:
            path2.moveTo(
                math.cos(math.radians(-start_angle)) * self.getSmallerLength() / 2 + self.getSmallerLength() / 2,
                math.sin(math.radians(-start_angle)) * self.getSmallerLength() / 2 + self.getSmallerLength() / 2)
            path2.arcTo(QRectF(0, 0, self.getSmallerLength(), self.getSmallerLength()), start_angle, -end_angle)

        pen2 = QPen()
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)

        if not self.isEnabled():
            color = FColors.AccentFillColorDisabled.getColor()
        elif self.progressState() == self.ProgressState.Error:
            color = FColors.SystemFillColorCritical.getColor()
        elif self.progressState() == self.ProgressState.Paused:
            color = FColors.SystemFillColorCaution.getColor()
        else:
            color = FColors.AccentFillColorDefault.getColor()
        pen2.setColor(color)
        pen2.setWidth(5)
        painter.strokePath(path2, pen2)

        if self.isTextVisible():
            painter.drawText(0, 0, self.getSmallerLength(), self.getSmallerLength(), Qt.AlignmentFlag.AlignCenter, self.text())
