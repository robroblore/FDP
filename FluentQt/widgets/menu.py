# coding:utf-8
import time
from typing import Union, Optional

from qtpy.QtGui import QPaintEvent, QGuiApplication
from qtpy.QtCore import QObject, Qt, QRect, QPoint, QSize, QRectF, QEvent
from qtpy.QtGui import QAction, QIcon, QPixmap, QPainter, QCursor, QMouseEvent
from qtpy.QtWidgets import QApplication, QMenu, QWidget, QMainWindow

from ..common.widget_animations import WidgetAnimationManager, WidgetAnimationType
from ..common.icon import FFontIcon, FIconBase
from ..common import FColors
from ..common.theme import set_acrylic_round_corners, fTheme, remove_acrylic_round_corners
from ..common.overload import Overload


class FMenu(QMenu):
    """
    __init__(self, parent: Optional[QWidget] = None) -> None

    __init__(self, title: str, parent: Optional[QWidget] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], title: str, parent: Optional[QWidget] = None) -> None
    """
    @Overload
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        # TODO explain effect disappearing
        self.aboutToShow.connect(self.set_acrylic)
        self.isPressed = False
        self._pressLater = False
        self.isHover = False
        self._icon = None

        self.setWindowFlag(Qt.WindowType.ToolTip, True)
        self.setWindowFlag(Qt.WindowType.WindowDoesNotAcceptFocus, True)

        window = self.parent()
        if window is not None:
            while not isinstance(window, QMainWindow):
                parent = window.parent()
                if parent is not None:
                    window = parent
                else:
                    break

            window.installEventFilter(self)

    @__init__.register
    def _(self, title: str, parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setTitle(title)

    @__init__.register
    def _(self, icon: Union[QIcon, QPixmap, str, FIconBase], title: str, parent: Optional[QWidget] = None):
        self.__init__(title=title, parent=parent)
        self.setIcon(icon)

    def addMenu(self, title: str = None, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]] = None, menu=None) -> QMenu:
        if not menu:
            menu = FMenu(self)
            if title:
                menu.setTitle(title)
            if icon:
                menu.setIcon(icon)
        self.addAction(menu.menuAction())
        return menu

    def set_acrylic(self):
        set_acrylic_round_corners(self, FColors.AcrylicFillColorDefault.get())
        for action in self.actions():
            if isinstance(action, FAction):
                action.updateIcon()
        time.sleep(0.05)
        self.setStyleSheet(self.styleSheet() + "QMenu {background-color: transparent}")

    def isUnderMouse(self) -> bool:
        return self.rect().contains(self.mapFromGlobal(QCursor().pos()))

    def activeActionIsUnderMouse(self) -> bool:
        return self.actionGeometry(self.activeAction()).contains(self.mapFromGlobal(QCursor().pos()))

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]]) -> None:
        self._icon = icon

    def icon(self) -> QIcon:
        if isinstance(self._icon, str) or isinstance(self._icon, QPixmap):
            return QIcon(self._icon)
        if isinstance(self._icon, FIconBase):
            return self._icon.icon()

        return self._icon

    def menuAction(self):
        action = super().menuAction()
        f_action = FAction(action.text(), action.parent())
        f_action.setIcon(self._icon)
        f_action.setMenu(action.menu())
        return f_action

    def event(self, e: QEvent) -> bool:
        event = super().event(e)

        if e.type() in [QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease, QEvent.Type.MouseMove, QEvent.Type.HoverEnter, QEvent.Type.HoverLeave]:

            if e.type() in [QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease]:
                self.isPressed = self.isUnderMouse() and e.buttons() == Qt.MouseButton.LeftButton
                self._pressLater = False
            self.isHover = self.isUnderMouse()
            if self.isPressed and not self.isHover:
                self.isPressed = False
                self._pressLater = True
            elif not self.isPressed and self.isHover and self._pressLater:
                self.isPressed = True
                self._pressLater = False

            for action in self.actions():
                if isinstance(action, FAction):
                    old_pressed = action.isPressed
                    old_hover = action.isHover
                    action.isPressed = False
                    action.isHover = False
                    if (old_pressed != action.isPressed or old_hover != action.isHover) and action != self.activeAction():
                        action.updateIcon()

            if isinstance(self.activeAction(), FAction):
                old_pressed = self.activeAction().isPressed
                old_hover = self.activeAction().isHover
                self.activeAction().isHover = self.activeActionIsUnderMouse()
                self.activeAction().isPressed = self.activeActionIsUnderMouse() and self.isPressed
                if old_pressed != self.activeAction().isPressed or old_hover != self.activeAction().isHover:
                    self.activeAction().updateIcon()

        if e.type() is QEvent.Type.WindowDeactivate:
            self.hide()
            remove_acrylic_round_corners(self)

        if e.type() is QEvent.Type.MouseButtonRelease:
            if not (isinstance(self.activeAction(), FAction) and self.activeAction().keepMenuOpen()):
                self.hide()
                remove_acrylic_round_corners(self)

        return event

    def addAction(self, *args, **kwargs):
        super().addAction(*args, **kwargs)
        self._update()

    def addActions(self, *args, **kwargs):
        super().addActions(*args, **kwargs)
        self._update()

    def insertAction(self, *args, **kwargs):
        super().insertAction(*args, **kwargs)
        self._update()

    def insertActions(self, *args, **kwargs):
        super().insertActions(*args, **kwargs)
        self._update()

    def removeAction(self, *args, **kwargs):
        super().removeAction(*args, **kwargs)
        self._update()

    def _update(self):
        has_icon = self.property("hasIcon")
        self.setProperty("hasIcon", False)
        for action in self.actions():
            if action.icon():
                self.setProperty("hasIcon", True)
                break
        if has_icon != self.property("hasIcon"):
            fTheme.update(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Paint and not self.isUnderMouse() and QGuiApplication.mouseButtons() != Qt.MouseButton.NoButton and self.isVisible():
            self.hide()
            return False
        return super().eventFilter(obj, event)


class FAction(QAction):
    """
    __init__(self, parent: Optional[QObject] = None) -> None

    __init__(self, text: str, parent: Optional[QObject] = None) -> None

    __init__(self, icon: Union[QIcon, QPixmap], text: str, parent: Optional[QObject] = None) -> None
    """
    @Overload
    def __init__(self, parent: Optional[QObject] = None, **kwargs) -> None:
        super().__init__(parent=parent, **kwargs)
        self._icon: Optional[Union[QIcon, QPixmap, str, FIconBase]] = None
        self._keepMenuOpen = False
        self.enabledChanged.connect(self.updateIcon)
        self.hovered.connect(self.updateIcon)
        self.toggled.connect(self.updateIcon)
        self.triggered.connect(self.updateIcon)
        self.triggered.connect(self._triggered)
        self.isPressed = False
        self.isHover = False

    @__init__.register
    def _(self, text: str, parent: Optional[QObject] = None, **kwargs) -> None:
        self.__init__(parent=parent, **kwargs)
        self.setText(text)

    @__init__.register
    def _(self, icon: Union[QIcon, QPixmap, str, FIconBase], text: str, parent: Optional[QObject] = None, **kwargs) -> None:
        self.__init__(text=text, parent=parent, **kwargs)
        self.setIcon(icon)

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]]) -> None:
        self._icon = icon
        self.updateIcon()

    def icon(self) -> QIcon:
        if isinstance(self._icon, str) or isinstance(self._icon, QPixmap):
            return QIcon(self._icon)
        if isinstance(self._icon, FIconBase):
            return self._icon.icon()

        return self._icon

    def _triggered(self):
        if self.keepMenuOpen() and type(self.parent()) == FMenu:
            self.parent().show()
            self.parent().set_acrylic()

    def setKeepMenuOpen(self, keepMenuOpen: bool) -> None:
        self._keepMenuOpen = keepMenuOpen

    def keepMenuOpen(self) -> bool:
        return self._keepMenuOpen

    def updateIcon(self):
        if self._icon and self.isIconVisibleInMenu():
            pix = QPixmap(16, 16)
            pix.fill(Qt.GlobalColor.transparent)
            rect = QRect(QPoint(0, 0), QSize(16, 16))

            alpha, color = FColors.TextFillColorPrimary.getAlphaAndColor()
            if not self.isEnabled():
                alpha, color = FColors.TextFillColorDisabled.getAlphaAndColor()
            elif self.isPressed:
                alpha, color = FColors.TextFillColorSecondary.getAlphaAndColor()

            # painter.setOpacity(alpha)

            if isinstance(self._icon, FIconBase):
                self._icon.render(QPainter(pix), rect, fill=color, opacity=alpha)
            else:
                icon = QIcon(self._icon)
                rect = QRectF(rect).toRect()
                image = icon.pixmap(rect.width(), rect.height())
                QPainter(pix).drawPixmap(rect, image)

            QAction.setIcon(self, QIcon(pix))

class FEditMenu(FMenu):
    """ Edit menu """

    @Overload
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self.createActions()

        if QApplication.clipboard().mimeData().hasText():
            if self._parentText():
                if self._parentSelectedText():
                    self.addActions(self.action_list)
                else:
                    self.addActions(self.action_list[2:])
            else:
                self.addAction(self.pasteAct)
        else:
            if self._parentText():
                if self._parentSelectedText():
                    self.addActions(
                        self.action_list[:2] + self.action_list[3:])
                else:
                    self.addActions(self.action_list[3:])

    @__init__.register
    def _(self, title: str, parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setTitle(title)

    def createActions(self):
        self.cutAct = FAction(
            FFontIcon("\uE8C6"),
            "Cut     ",
            self,
            shortcut="Ctrl+X",
            triggered=self.parent().cut
        )
        self.copyAct = FAction(
            FFontIcon("\uE8C8"),
            "Copy     ",
            self,
            shortcut="Ctrl+C",
            triggered=self.parent().copy
        )
        self.pasteAct = FAction(
            FFontIcon("\uE77F"),
            "Paste     ",
            self,
            shortcut="Ctrl+V",
            triggered=self.parent().paste
        )
        self.cancelAct = FAction(
            FFontIcon("\uE7A7"),
            "Undo     ",
            self,
            shortcut="Ctrl+Z",
            triggered=self.parent().undo
        )
        self.selectAllAct = FAction(
            "Select All     ",
            self,
            shortcut="Ctrl+A",
            triggered=self.parent().selectAll
        )
        self.action_list = [
            self.cutAct, self.copyAct,
            self.pasteAct, self.cancelAct, self.selectAllAct
        ]

    def _parentText(self):
        raise NotImplementedError

    def _parentSelectedText(self):
        raise NotImplementedError


class FLineEditMenu(FEditMenu):
    """ Line edit menu """

    def _parentText(self):
        return self.parent().text()

    def _parentSelectedText(self):
        return self.parent().selectedText()

    def exec_(self, pos, ani=True, aniType=WidgetAnimationType.NONE):
        if self.isVisible():
            return

        self.resize(self.sizeHint())

        if ani:
            ani_manager = WidgetAnimationManager.make(self, aniType)
            ani_manager.exec(pos, 0)

        self.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
        self.show()
        self.set_acrylic()


class FTextEditMenu(FEditMenu):
    """ Text edit menu """

    def _parentText(self):
        return self.parent().toPlainText()

    def _parentSelectedText(self):
        return self.parent().textCursor().selectedText()

    def exec_(self, pos, ani=True, aniType=WidgetAnimationType.NONE):
        if self.isVisible():
            return

        self.adjustSize()

        if ani:
            ani_manager = WidgetAnimationManager.make(self, aniType)
            ani_manager.exec(pos, self.width())

        self.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
        self.show()
        self.set_acrylic()


class FDropDownMenu(FMenu):
    def exec_(self, pos, ani=True, aniType=WidgetAnimationType.SLIDE_RIGHT):
        if self.isVisible():
            return

        self.adjustSize()

        if ani:
            ani_manager = WidgetAnimationManager.make(self, aniType)
            ani_manager.exec(pos, int(self.width()/20), mask=False)

        self.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
        self.show()
        self.set_acrylic()

class FNavigationMenu(FMenu):
    def exec_(self, pos, ani=True, aniType=WidgetAnimationType.SLIDE_RIGHT):
        if self.isVisible():
            return

        self.adjustSize()

        if ani:
            ani_manager = WidgetAnimationManager.make(self, aniType)
            ani_manager.exec(pos, int(self.width()/20), mask=False)

        self.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
        self.show()
        self.set_acrylic()
