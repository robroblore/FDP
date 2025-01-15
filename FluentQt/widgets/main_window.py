# coding=utf-8
import sys
from ctypes import cast
from ctypes.wintypes import MSG, LPRECT

import win32con
import win32gui
import win32gui_struct
from qtpy.QtCore import Qt, QEvent, QPoint
from qtpy.QtGui import QCursor, QMouseEvent, QResizeEvent
from qtpy.QtWidgets import QMainWindow, QApplication

from .. import fTheme
from ..common import windows_effects
from ..common import win32_utils
from .title_bar import TitleBar, StandardTitleBar
from .title_bar_buttons import TitleBarButtonState
from ..common.win32_utils import Taskbar
from ..common.windows_effects import LPNCCALCSIZE_PARAMS


class FMainWindow(QMainWindow):
    """ Frameless window base class for Windows system """

    BORDER_WIDTH = 5

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.titleBar = StandardTitleBar(self)
        self._isResizeEnabled = True

        fTheme.themeChangedSignal.connect(self.set_mica)
        fTheme.micaChangedSignal.connect(self.set_mica)
        self.set_mica()
        windows_effects.setRoundedCorners(self.winId())

        windows_effects.addWindowAnimation(self.winId())

        self.setContentsMargins(0, 32, 0, 0)

        # solve issue #5
        self.windowHandle().screenChanged.connect(self.__onScreenChanged)

        # self.setContentsMargins(0, 0, 16, 8)
        self.titleBar.raise_()

        self._hmenu = win32gui.GetSystemMenu(self.winId(), False)

    def showSystemMenu(self, pos):
        item_info = win32gui_struct.PackMENUITEMINFO(fState=0 if self.isMaximized() else 3)
        win32gui.SetMenuItemInfo(self._hmenu, 61728, 0, item_info[0])

        item_info = win32gui_struct.PackMENUITEMINFO(fState=3 if self.isMaximized() else 0)
        win32gui.SetMenuItemInfo(self._hmenu, 61488, 0, item_info[0])

        action = win32gui.TrackPopupMenu(self._hmenu, 256, pos.x(), pos.y(), 0, self.winId(), None)

        match action:
            case 61728:
                self.showNormal()
            case 61472:
                self.showMinimized()
            case 61488:
                self.showMaximized()
            case 61536:
                self.close()

    def set_mica(self):
        if fTheme.mica and sys.getwindowsversion().build >= 22000:
            windows_effects.setMicaEffect(self.winId(), fTheme.isDark())
        else:
            windows_effects.SetImmersiveTitleBar(self.winId(), fTheme.isDark())

    def setTitleBar(self, titleBar):
        """ set custom title bar

        Parameters
        ----------
        titleBar: TitleBar
            title bar
        """
        self.titleBar.deleteLater()
        self.titleBar.hide()
        self.titleBar = titleBar
        self.titleBar.setParent(self)
        self.titleBar.raise_()

    def setTitleBarHeight(self, height):
        if height >= 32:
            self.titleBar.setHeight(height)
            self.setContentsMargins(0, height, 0, 0)

    def titleBarHeight(self):
        return self.titleBar.height()

    def expandContentIntoTitleBar(self, expandInTitleBar):
        self.setContentsMargins(0, self.titleBarHeight()*(not expandInTitleBar), 0, 0)

    def isContentIntoTitleBar(self):
        return self.contentsMargins().top() == 0

    def setResizeEnabled(self, isEnabled: bool):
        """ set whether resizing is enabled """
        self._isResizeEnabled = isEnabled

    def nativeEvent(self, eventType, message):
        """ Handle the Windows message """
        msg = MSG.from_address(message.__int__())
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)

        if msg.message == win32con.WM_NCHITTEST:
            pos = QCursor.pos()
            yPos = pos.y() - self.y()
            if yPos < self.BORDER_WIDTH:
                return True, win32con.HTTOP

            elif self.window().childAt(pos - self.geometry().topLeft()) is self.titleBar.maxBtn:
                self.titleBar.maxBtn.setState(TitleBarButtonState.HOVER)
                return True, win32con.HTMAXBUTTON

        elif msg.message in [0x2A2, win32con.WM_MOUSELEAVE]:
            self.titleBar.maxBtn.setState(TitleBarButtonState.NORMAL)

        elif msg.message in [win32con.WM_NCLBUTTONDOWN, win32con.WM_NCLBUTTONDBLCLK]:
            if self.window().childAt(QCursor.pos() - self.geometry().topLeft()) is self.titleBar.maxBtn:
                QApplication.sendEvent(self.titleBar.maxBtn, QMouseEvent(
                    QEvent.Type.MouseButtonPress, QPoint(), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))
                return True, 0

        elif msg.message in [win32con.WM_NCLBUTTONUP, win32con.WM_NCRBUTTONUP]:
            if self.window().childAt(QCursor.pos() - self.geometry().topLeft()) is self.titleBar.maxBtn:
                QApplication.sendEvent(self.titleBar.maxBtn, QMouseEvent(
                    QEvent.Type.MouseButtonRelease, QPoint(), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier))

        elif msg.message == win32con.WM_NCCALCSIZE:
            if msg.wParam:
                rect = cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
            else:
                rect = cast(msg.lParam, LPRECT).contents

            top = rect.top

            # make window resizable
            ret = win32gui.DefWindowProc(msg.hWnd, win32con.WM_NCCALCSIZE, msg.wParam, msg.lParam)
            if ret != 0:
                return True, ret

            # restore top to remove title bar
            rect.top = top

            isMax = win32_utils.isMaximized(msg.hWnd)
            isFull = win32_utils.isFullScreen(msg.hWnd)

            # adjust the size of client rect
            if isMax and not isFull:

                ty = win32_utils.getResizeBorderThickness(msg.hWnd, False)
                rect.top += ty

            # handle the situation that an auto-hide taskbar is enabled
            if (isMax or isFull) and Taskbar.isAutoHide():
                position = Taskbar.getPosition(msg.hWnd)
                if position == Taskbar.LEFT:
                    rect.top += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.BOTTOM:
                    rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.LEFT:
                    rect.left += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.RIGHT:
                    rect.right -= Taskbar.AUTO_HIDE_THICKNESS

            # result = 0 if not msg.wParam else win32con.WVR_REDRAW
            return True, 0

        return super().nativeEvent(eventType, message)

    def __onScreenChanged(self):
        hWnd = int(self.windowHandle().winId())
        win32gui.SetWindowPos(hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.ActivationChange:
            self.titleBar.update()
        return super().event(event)

    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)
        self.titleBar.resize(self.width(), self.titleBar.height())

        if win32_utils.isMaximized(self.winId()):
            self.titleBar.closeBtn.setFixedWidth(47)
            closeBtnPos = QPoint(self.width() - self.titleBar.closeBtn.width(), -1)
            self.titleBar.closeBtn.xOffset = 1
        else:
            self.titleBar.closeBtn.setFixedWidth(45)
            closeBtnPos = QPoint(self.width() - self.titleBar.closeBtn.width(), 0)
            self.titleBar.closeBtn.xOffset = 0

        maxBtnPos = QPoint(closeBtnPos.x() - self.titleBar.maxBtn.width(), 0)
        minBtnPos = QPoint(maxBtnPos.x() - self.titleBar.minBtn.width(), 0)

        if win32_utils.isMaximized(self.winId()):
            maxBtnPos.setY(-1)
            minBtnPos.setY(-1)

        self.titleBar.closeBtn.move(closeBtnPos)
        self.titleBar.maxBtn.move(maxBtnPos)
        self.titleBar.minBtn.move(minBtnPos)
