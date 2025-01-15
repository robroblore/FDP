# coding=utf-8
from qtpy.QtCore import QEvent, Qt
from qtpy.QtGui import QFocusEvent
from qtpy.QtWidgets import QComboBox, QAbstractItemView

from ..common import FColors, theme
from .scroll_bar import FSmoothScrollDelegate


class FComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setSizeAdjustPolicy(self.SizeAdjustPolicy.AdjustToContents)

        self.scrollDelegate = FSmoothScrollDelegate(self.view())
        self.view().setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.view().verticalScrollBar().setSingleStep(5)

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.FocusOut and QFocusEvent.reason(event) == Qt.FocusReason.PopupFocusReason:
            self.view().window().setStyleSheet("QFrame {background-color: transparent}")
            theme.set_acrylic_round_corners(self.view().window(), FColors.AcrylicFillColorDefault.get())
        if event.type() == QEvent.Type.FocusIn and QFocusEvent.reason(event) == Qt.FocusReason.PopupFocusReason:
            self.view().window().setStyleSheet("")
        return super().event(event)

    # def addItems(self, texts: Sequence[str]) -> None:
    #     super().addItems(texts)
    #     # self.setStyleSheet(self.styleSheet())
    #     self.adjustSize()