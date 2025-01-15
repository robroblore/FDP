# coding=utf-8
import sys

from qtpy.QtCore import Qt, QEvent
from qtpy.QtGui import QIcon, QContextMenuEvent
from qtpy.QtWidgets import QLabel, QWidget

from .title_bar_buttons import MinimizeButton, CloseButton, MaximizeButton
from ..common.win32_utils import WindowsMoveResize


class TitleBar(QWidget):
    """ Title bar """

    def __init__(self, parent):
        super().__init__(parent)
        self.minBtn = MinimizeButton(parent=self.window())
        self.closeBtn = CloseButton(parent=self.window())
        self.maxBtn = MaximizeButton(parent=self.window())

        self.resize(200, 32)
        self.setFixedHeight(32)

        # connect signal to slot
        self.minBtn.clicked.connect(self.window().showMinimized)
        self.maxBtn.clicked.connect(self.__toggleMaxState)
        self.closeBtn.clicked.connect(self.window().close)

        self.window().installEventFilter(self)

    def eventFilter(self, obj, e):
        if obj is self.window():
            if e.type() == QEvent.Type.WindowStateChange:
                self.maxBtn.setMaxState(self.window().isMaximized())

        return super().eventFilter(obj, e)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        super().contextMenuEvent(event)

        from .main_window import FMainWindow
        if isinstance(self.window(), FMainWindow):
            pos = event.pos() + self.window().geometry().topLeft()
            self.window().showSystemMenu(pos)

    def mouseDoubleClickEvent(self, event):
        """ Toggles the maximization state of the window """
        super().mouseDoubleClickEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.__toggleMaxState()

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        WindowsMoveResize.startSystemMove(self.window(), e.globalPos())

    def __toggleMaxState(self):
        """ Toggles the maximization state of the window and change icon """
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def raise_(self) -> None:
        super().raise_()
        self.minBtn.raise_()
        self.maxBtn.raise_()
        self.closeBtn.raise_()

    def setHeight(self, height: int):
        self.resize(self.width(), height)
        self.setFixedHeight(height)

    def update(self) -> None:
        super().update()
        self.minBtn.update()
        self.maxBtn.update()
        self.closeBtn.update()


class StandardTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add window icon
        self.iconLabel = QLabel(self.window())
        self.iconLabel.setFixedSize(20, 20)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self.window())
        self.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px
            }
        """)
        self.window().windowTitleChanged.connect(self.setTitle)

        self._hasIcon = False
        self._titleMargin = 0
        self.setTitleMargin(self._titleMargin)

        self.setTitleMargin(self._titleMargin)

    def setTitle(self, title):
        """ set the title of title bar
        Parameters
        ----------
        title: str
            the title of title bar
        """
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        """ set the icon of title bar
        Parameters
        ----------
        icon: QIcon | QPixmap | str
            the icon of title bar
        """
        self.iconLabel.setPixmap(QIcon(icon).pixmap(20, 20))
        self._hasIcon = True
        self.setTitleMargin(self._titleMargin)

    def titleMargin(self):
        return self._titleMargin

    def setHeight(self, height: int):
        super().setHeight(height)
        self.setTitleMargin(self._titleMargin)

    def setTitleMargin(self, margin: int):
        self._titleMargin = margin
        self.iconLabel.move(16 + self._titleMargin, int(self.height()/4))
        self.titleLabel.move(16 + (20 + 16) * self._hasIcon + self._titleMargin, int(self.height()/4))
