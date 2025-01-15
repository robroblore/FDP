from enum import Enum
from typing import Self

from qtpy.QtCore import QObject, QPropertyAnimation, QEasingCurve, QPoint, Property
from qtpy.QtGui import QCursor, QRegion
from qtpy.QtWidgets import QApplication, QWidget


class WidgetAnimationType(Enum):
    """ widget animation type """

    NONE = 0
    DROP_DOWN = 1
    PULL_BACK_UP = 2
    PULL_UP = 3
    DROP_BACK_DOWN = 4
    SLIDE_RIGHT = 5
    SLIDE_LEFT = 6
    SLIDE_UP = 7


class WidgetAnimationManager(QObject):
    """ widget animation manager """

    managers = {}

    def __init__(self, widget: QWidget):
        super().__init__()
        self._opacity = 1.0
        self._startPosOffset = QPoint(0, 0)

        self.widget = widget
        self.mask = True
        self.startOpacity = 1.0
        self.endOpacity = 1.0

        self.ani = QPropertyAnimation(widget, b'pos', widget)
        self.ani.setDuration(150)
        self.ani.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.ani.valueChanged.connect(self._onValueChanged)
        self.ani.valueChanged.connect(lambda: self.widget.update())

        self.opacityAni = QPropertyAnimation(self, b'opacity', self)
        self.opacityAni.setEasingCurve(QEasingCurve.Type.OutExpo)
        self.opacityAni.valueChanged.connect(self._onValueChanged)
        self.opacityAni.valueChanged.connect(lambda: self.widget.update())

    def _onValueChanged(self):
        self.widget.setWindowOpacity(self.opacity)

    def _endPosition(self, pos, globalPos=True):
        m = self.widget
        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        w, h = m.width(), m.height()
        x = min(pos.x(), rect.right() - w - 4) if globalPos else pos.x()
        y = min(pos.y(), rect.bottom() - h - 4) if globalPos else pos.y()
        return QPoint(x, y)

    def _widgetSize(self):
        m = self.widget.contentsMargins()
        w = self.widget.width() + m.left() + m.right()
        h = self.widget.height() + m.top() + m.bottom()
        return w, h

    def opacity(self):
        return self._opacity

    def setOpacity(self, opacity):
        self._opacity = opacity
        self.widget.setWindowOpacity(opacity)

    opacity = Property(float, opacity, setOpacity)

    def exec(self, pos: QPoint, offset: int, startOpacity: float = 0.0, endOpacity: float = 1.0, mask: bool = True, aniDuration: int = 150, globalPos=True):
        self.mask = mask
        pos = self._endPosition(pos, globalPos)

        self.ani.setDuration(aniDuration)
        self.ani.setStartValue(pos-self._startPosOffset)
        self.ani.setEndValue(pos)
        self.ani.start()

        self.opacityAni.setDuration(aniDuration)
        self.opacityAni.setStartValue(startOpacity)
        self.opacityAni.setEndValue(endOpacity)
        self.opacityAni.start()

    @classmethod
    def register(cls, name):
        """ register widget animation manager

        Parameters
        ----------
        name: Any
            the name of manager, it should be unique
        """
        def wrapper(Manager):
            if name not in cls.managers:
                cls.managers[name] = Manager

            return Manager

        return wrapper

    @classmethod
    def make(cls, widget: QWidget, aniType: WidgetAnimationType) -> Self:
        if aniType not in cls.managers:
            raise ValueError(f'`{aniType}` is an invalid widget animation type.')

        return cls.managers[aniType](widget)


@WidgetAnimationManager.register(WidgetAnimationType.NONE)
class DummyWidgetAnimationManager(WidgetAnimationManager):
    """ Dummy widget animation manager """
    def _onValueChanged(self):
        super()._onValueChanged()
        w, h = self._widgetSize()
        y = self.ani.endValue().y() - self.ani.currentValue().y()

        if self.mask:

            self.widget.setMask(QRegion(0, y, w, h))


@WidgetAnimationManager.register(WidgetAnimationType.DROP_DOWN)
class DropDownWidgetAnimationManager(WidgetAnimationManager):
    """ Drop down widget animation manager """

    def _onValueChanged(self):
        super()._onValueChanged()
        w, h = self._widgetSize()
        y = self.ani.endValue().y() - self.ani.currentValue().y()

        if self.mask:
            region = QRegion(0, y, w, h)
            # region -= QRegion(self.widget.rect())

            # effect = QGraphicsOpacityEffect(self.widget)
            # effect.rect = region.boundingRect()
            # effect.setOpacity(0)
            #
            # self.widget.setContentsMargins(0, y, 0, 0)

    def exec(self, pos: QPoint, offset: int, startOpacity: float = 0.0, endOpacity: float = 1.0, mask: bool = True, aniDuration: int = 200, globalPos=True):
        self._startPosOffset = QPoint(0, int(offset))
        super().exec(pos, offset, startOpacity, endOpacity, mask, aniDuration, globalPos)


@WidgetAnimationManager.register(WidgetAnimationType.PULL_BACK_UP)
class DropDownWidgetAnimationManager(WidgetAnimationManager):
    """ Drop down widget animation manager """

    def _onValueChanged(self):
        super()._onValueChanged()
        w, h = self._widgetSize()
        y = self.ani.startValue().y() - self.ani.currentValue().y()

        if self.mask:
            self.widget.setMask(QRegion(0, y, w, h))

    def exec(self, pos: QPoint, offset: int, startOpacity: float = 0.0, endOpacity: float = 1.0, mask: bool = True, aniDuration: int = 200, globalPos=True):
        self._startPosOffset = QPoint(0, int(offset))
        super().exec(pos, offset, startOpacity, endOpacity, mask, aniDuration, globalPos)
        pos = self.ani.endValue()
        self.ani.setStartValue(pos)
        self.ani.setEndValue(pos-self._startPosOffset)


@WidgetAnimationManager.register(WidgetAnimationType.PULL_UP)
class PullUpWidgetAnimationManager(WidgetAnimationManager):
    """ Pull up widget animation manager """

    def _endPosition(self, pos, globalPos=True):
        m = self.widget
        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        w, h = m.width(), m.height()
        x = min(pos.x(), rect.right() - w - 4) if globalPos else pos.x()
        y = max(pos.y() - h, rect.top() + 4) if globalPos else pos.y()
        return QPoint(x, y)

    def _onValueChanged(self):
        super()._onValueChanged()
        w, h = self._widgetSize()
        y = self.ani.endValue().y() - self.ani.currentValue().y()

        if self.mask:
            self.widget.setMask(QRegion(0, y, w, h))

    def exec(self, pos: QPoint, offset: int, startOpacity: float = 0.0, endOpacity: float = 1.0, mask: bool = True, aniDuration: int = 250, globalPos=True):
        self._startPosOffset = QPoint(0, int(-offset))
        super().exec(pos, offset, startOpacity, endOpacity, mask, aniDuration, globalPos)


@WidgetAnimationManager.register(WidgetAnimationType.DROP_BACK_DOWN)
class PullUpWidgetAnimationManager(WidgetAnimationManager):
    """ Drop back down widget animation manager """

    def _endPosition(self, pos, globalPos=True):
        m = self.widget
        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        w, h = m.width(), m.height()
        x = min(pos.x(), rect.right() - w - 4) if globalPos else pos.x()
        y = max(pos.y() - h, rect.top() + 4) if globalPos else pos.y()
        return QPoint(x, y)

    def _onValueChanged(self):
        super()._onValueChanged()
        w, h = self._widgetSize()
        y = self.ani.startValue().y() - self.ani.currentValue().y()

        if self.mask:
            self.widget.setMask(QRegion(0, y, w, h))

    def exec(self, pos: QPoint, offset: int, startOpacity: float = 0.0, endOpacity: float = 1.0, mask: bool = True, aniDuration: int = 250, globalPos=True):
        self._startPosOffset = QPoint(0, int(-offset))
        super().exec(pos, offset, startOpacity, endOpacity, mask, aniDuration, globalPos)
        pos = self.ani.endValue()
        self.ani.setStartValue(pos)
        self.ani.setEndValue(pos-self._startPosOffset)


@WidgetAnimationManager.register(WidgetAnimationType.SLIDE_RIGHT)
class FadeRightWidgetAnimationManager(WidgetAnimationManager):
    """ Pull up widget animation manager """

    def _onValueChanged(self):
        super()._onValueChanged()
        w, h = self._widgetSize()
        x = self.ani.endValue().x() - self.ani.currentValue().x()

        if self.mask:
            self.widget.setMask(QRegion(x, 0, w, h))

    def exec(self, pos: QPoint, offset: int, startOpacity: float = 0.0, endOpacity: float = 1.0, mask: bool = True, aniDuration: int = 200, globalPos=True):
        self._startPosOffset = QPoint(int(offset), 0)
        super().exec(pos, offset, startOpacity, endOpacity, mask, aniDuration, globalPos)


@WidgetAnimationManager.register(WidgetAnimationType.SLIDE_LEFT)
class FadeRightWidgetAnimationManager(WidgetAnimationManager):
    """ Pull up widget animation manager """

    def _endPosition(self, pos, globalPos=True):
        m = self.widget
        rect = QApplication.screenAt(QCursor.pos()).availableGeometry()
        w, h = m.width(), m.height()
        x = max(pos.x() - w, rect.left() + 4) if globalPos else pos.x()
        y = min(pos.y(), rect.bottom() - h - 4) if globalPos else pos.y()
        return QPoint(x, y)

    def _onValueChanged(self):
        super()._onValueChanged()
        w, h = self._widgetSize()
        x = self.ani.endValue().x() - self.ani.currentValue().x()

        if self.mask:
            self.widget.setMask(QRegion(x, 0, w, h))

    def exec(self, pos: QPoint, offset: int, startOpacity: float = 0.0, endOpacity: float = 1.0, mask: bool = True, aniDuration: int = 200, globalPos=True):
        self._startPosOffset = QPoint(int(-offset), 0)
        super().exec(pos, offset, startOpacity, endOpacity, mask, aniDuration, globalPos)

@WidgetAnimationManager.register(WidgetAnimationType.SLIDE_UP)
class FadeUpWidgetAnimationManager(WidgetAnimationManager):
    """ Pull up widget animation manager """

    def _onValueChanged(self):
        super()._onValueChanged()
        w, h = self._widgetSize()
        y = self.ani.endValue().y() - self.ani.currentValue().y()

        if self.mask:
            self.widget.setMask(QRegion(0, y, w, h))

    def exec(self, pos: QPoint, offset: int, startOpacity: float = 0.0, endOpacity: float = 1.0, mask: bool = True, aniDuration: int = 250, globalPos=True):
        self._startPosOffset = QPoint(0, int(-offset))
        super().exec(pos, offset, startOpacity, endOpacity, mask, aniDuration, globalPos)
