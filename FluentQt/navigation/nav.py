# coding=utf-8
from typing import Union

from qtpy.QtCore import Qt, QByteArray
from qtpy.QtGui import QFocusEvent
from qtpy.QtWidgets import QDialog, QWidget, QApplication
from ..widgets import FMainWindow
import ctypes, win32con, win32gui


class Panel(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("QDialog{background: transparent}")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        # def nativeEvent(self, eventType: Union[QByteArray, bytes], message: int) -> object:
    #     if isinstance(self.parent().window(), FMainWindow):
    #         result = self.parent().window().nativeEvent(eventType, message)
    #         if not result[0]:
    #             return result
    #     return super().nativeEvent(eventType, message)
