# coding: utf-8
from typing import Optional

from qtpy.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation, Property, Signal
from qtpy.QtGui import QMouseEvent, QEnterEvent
from qtpy.QtWidgets import QWidget


class AnimationBase(QObject):
    """ Animation base class """

    def __init__(self, parent: QWidget, installEventFilter=True):
        super().__init__(parent=parent)
        if installEventFilter:
            parent.installEventFilter(self)

    def onHover(self, e: QEnterEvent):
        pass

    def onLeave(self, e: QEvent):
        pass

    def onPress(self, e: QMouseEvent):
        pass

    def onRelease(self, e: QMouseEvent):
        pass

    def eventFilter(self, obj: QObject, e: QEvent):
        if obj is self.parent() and self.parent().isEnabled():
            match e.type():
                case QEvent.Type.MouseButtonPress:
                    self.onPress(e)
                case QEvent.Type.MouseButtonRelease:
                    self.onRelease(e)
                case QEvent.Type.Enter:
                    self.onHover(e)
                case QEvent.Type.Leave:
                    self.onLeave(e)

        return super().eventFilter(obj, e)


class TranslateAnimation(AnimationBase):

    valueChanged = Signal(float)

    def __init__(self, parent: QWidget, offset=3, installEventFilter=True):
        super().__init__(parent, installEventFilter)
        self._offset = 0
        self.maxOffset = offset
        self.ani = QPropertyAnimation(self, b'offset', self)

    def getOffset(self):
        return self._offset

    def setOffset(self, offset):
        self._offset = offset
        self.parent().update()
        self.valueChanged.emit(offset)

    def onPress(self, e: Optional[QMouseEvent] = None):
        """ arrow down """
        if self.ani.state() != self.ani.State.Running:
            self.ani.setEndValue(self.maxOffset)
            self.ani.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.ani.setDuration(75)
            self.ani.start()

    def onRelease(self, e: Optional[QMouseEvent] = None):
        """ arrow up """
        if self.ani.state() != self.ani.State.Running:
            if self._offset != 0:
                self.ani.setEndValue(0)
                # self.ani.setDuration(550)
                # curve = QEasingCurve(QEasingCurve.Type.OutBack)
                # # curve.setPeriod(10)
                # curve.setAmplitude(0.1)
                # self.ani.setEasingCurve(curve)
                self.ani.setDuration(100)
                self.ani.setEasingCurve(QEasingCurve.Type.OutBack)
                self.ani.start()
        else:
            self.ani.finished.connect(self._release)

    def _release(self):
        self.ani.finished.disconnect(self._release)
        self.onRelease()

    offset = Property(float, getOffset, setOffset)


class RotateAnimation(AnimationBase):

    valueChanged = Signal(float)

    def __init__(self, parent: QWidget, yOffset=2, angleOffset=180, installEventFilter=True):
        super().__init__(parent, installEventFilter)
        self._y = 0
        self._angle = 0
        self.maxYOffset = yOffset
        self.maxAngleOffset = angleOffset
        self.aniY = QPropertyAnimation(self, b'y', self)
        self.aniA = QPropertyAnimation(self, b'angle', self)

    def getY(self):
        return self._y

    def setY(self, y):
        self._y = y
        self.parent().update()
        self.valueChanged.emit(y)

    def getAngle(self):
        return self._angle

    def setAngle(self, angle):
        self._angle = angle
        self.parent().update()
        self.valueChanged.emit(angle)

    def onPress(self, e: Optional[QMouseEvent] = None):
        """ arrow down """
        if self.aniA.state() != self.aniY.State.Running:

            if self._angle != 0:
                self.aniY.setEndValue(-self.maxYOffset)
            else:
                self.aniY.setEndValue(self.maxYOffset)

            self.aniY.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.aniY.setDuration(250)
            self.aniY.start()

    def onRelease(self, e: Optional[QMouseEvent] = None, angle: Optional[int] = None):
        """ arrow up and 180 turn """
        if self.aniA.state() != self.aniA.State.Running:
            self._y = 0
            if self._angle != 0:
                self.aniA.setEndValue(0)
            else:
                self.aniA.setEndValue(self.maxAngleOffset)

            if angle is not None:
                self.aniA.setEndValue(angle)

            self.aniA.setDuration(125)
            self.aniA.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.aniA.start()
        else:
            self.aniY.finished.connect(self._release)

    def _release(self):
        self.aniY.finished.disconnect(self._release)
        self.onRelease()

    y = Property(float, getY, setY)
    angle = Property(float, getAngle, setAngle)
