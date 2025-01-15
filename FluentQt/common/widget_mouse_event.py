# coding=utf-8
from qtpy.QtWidgets import QWidget
from qtpy.QtCore import QObject, QEvent
from qtpy.QtGui import QCursor


class WidgetMouseEvent(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self._pressLater: bool = False

        self.parent: QWidget = parent
        self.parent.installEventFilter(self)

    def isUnderMouse(self) -> bool:
        return self.parent.rect().contains(self.parent.mapFromGlobal(QCursor().pos()))

    def cancelPressEvent(self):
        self._pressLater = False
        self.parent.isPressed = False
        self.parent.repaint()

    def cancelHoverEvent(self):
        self.parent.isHover = False
        self.parent.repaint()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() in [QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease, QEvent.Type.MouseMove,
                            QEvent.Type.Enter, QEvent.Type.Leave]:
            try:
                old_hover = self.parent.isHover
                old_pressed = self.parent.isPressed

                if event.type() in [QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease]:
                    self.parent.isPressed = self.isUnderMouse() and event.type() == QEvent.Type.MouseButtonPress
                    self._pressLater = False

                self.parent.isHover = self.isUnderMouse() and self.parent.window().isActiveWindow()

                if self.parent.isPressed and not self.parent.isHover:
                    self.parent.isPressed = False
                    self._pressLater = True

                elif not self.parent.isPressed and self.parent.isHover and self._pressLater:
                    self.parent.isPressed = True
                    self._pressLater = False

                if old_hover != self.parent.isHover or old_pressed != self.parent.isPressed:
                    self.parent.repaint()
            except RuntimeError:
                pass

        return super().event(event)
