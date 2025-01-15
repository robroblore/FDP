# coding=utf-8
from enum import Enum

from qtpy.QtWidgets import QFrame, QApplication

from .. import fTheme


class FFrame(QFrame):
    class Opacity(Enum):
        TRANSPARENT = "0"
        TRANSLUCENT = "1"
        OPAQUE = "2"

    def __init__(self, parent=None, opacity: Opacity = Opacity.TRANSLUCENT):
        super().__init__(parent=parent)
        self.setProperty('opacity', opacity.value)
        self.opacity = self.Opacity(opacity)

    def setOpacity(self, opacity: Opacity):
        self.opacity = opacity
        self.setProperty('opacity', opacity.value)
        fTheme.update(self)
