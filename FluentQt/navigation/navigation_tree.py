# coding=utf-8
from typing import Union, Optional

from qtpy.QtCore import QRect, QRectF, QSize, Qt
from qtpy.QtGui import QPainter, QColor, QIcon, QPixmap, QMouseEvent
from qtpy.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem, QTreeWidgetItem

from .. import fTheme
from ..common import FColors
from ..common.icon import FIconBase, drawIcon, FFontIcon
from ..widgets import FTreeWidget, FTreeItemDelegate, FNavigationMenu
from ..widgets.menu import FAction


class FNavTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, widget, icon=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._icon = icon
        self.widget = widget

    def icon(self) -> QIcon:
        if isinstance(self._icon, str) or isinstance(self._icon, QPixmap):
            return QIcon(self._icon)
        if isinstance(self._icon, FIconBase):
            return self._icon.icon()

        return self._icon

    def getIcon(self):
        return self._icon

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]]) -> None:
        if self._icon != icon:
            self._icon = icon

    def hasIcon(self):
        return self._icon

    def posInTree(self):
        pos = 0
        parent = self.parent()
        if parent:
            pos = parent.posInTree() + 1
        return pos

    def addItem(self, parent_menu):
        if self.childCount() != 0:
            menu = FNavigationMenu(self.text(0), self.treeWidget())
            if self.getIcon():
                menu.setIcon(self._icon)
            for child_id in range(self.childCount()):
                child: FNavTreeWidgetItem = self.child(child_id)
                if child.getIcon():
                    child.addItem(menu)
                else:
                    child.addItem(menu)
            if self.getIcon():
                parent_menu.addMenu(menu=menu)
            else:
                parent_menu.addMenu(menu=menu)
        else:
            if self.getIcon():
                parent_menu.addAction(FAction(self.getIcon(), self.text(0), self.treeWidget()))
            else:
                parent_menu.addAction(FAction(self.text(0), self.treeWidget()))


class FNavTreeWidget(FTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setHeaderHidden(True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setViewportMargins(0, 0, 0, 0)
        self.leftSpacing = 0
        self.setRootIsDecorated(False)
        self.setIconSize(QSize(16, 16))
        self.setExpandsOnDoubleClick(False)

        self.setItemDelegate(FNavTreeItemDelegate(self, FColors.SubtleFillColorTertiary, FColors.SubtleFillColorSecondary, FColors.SubtleFillColorSecondary, FColors.AccentFillColorDefault, FColors.TextFillColorDisabled))

        self.itemClicked.connect(self.itemClick)

        self.setProperty("pressedItem", False)

        self.itemPressed = None

    def drawBranches(self, painter: QPainter, rect: QRect, index):
        newRect = rect
        newRect.moveLeft(10)
        painter.setBrush(QColor(0, 0, 0))
        super().drawBranches(painter, newRect, index)

    def itemClick(self, item: FNavTreeWidgetItem):
        if self.parent().navigationView.isExpanded():
            if item.isExpanded():
                self.collapseItem(item)
            else:
                self.expandItem(item)
        if not self.parent().navigationView.isExpanded():
            menu = FNavigationMenu(self)
            for child_id in range(item.childCount()):
                child: FNavTreeWidgetItem = item.child(child_id)
                child.addItem(menu)
            rect: QRect = self.visualItemRect(item)
            rect.moveLeft(self.parent().width())
            menu.exec_(self.mapToGlobal(rect.topLeft()))

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        self.itemPressed = self.itemAt(event.pos())
        self.repaint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        self.itemPressed = None
        self.repaint()


class FNavTreeItemDelegate(FTreeItemDelegate):
    """ Tree item delegate """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _drawIcon(self, icon: Union[QIcon, QPixmap, str, FIconBase], painter: QPainter, rect: QRectF, option: QStyleOptionViewItem = None, item: FNavTreeWidgetItem = "") -> None:

        alpha, color = FColors.TextFillColorPrimary.getAlphaAndColor()
        if option:
            if not (option.state & QStyle.StateFlag.State_Enabled):
                alpha, color = FColors.TextFillColorDisabled.getAlphaAndColor()
            elif item == self.parent().itemPressed:
                alpha, color = FColors.TextFillColorSecondary.getAlphaAndColor()
            if self.parent().itemPressed is None and self.parent().property("pressedItem"):
                self.parent().setProperty("pressedItem", False)
                fTheme.update(self.parent())
            elif self.parent().itemPressed and not self.parent().property("pressedItem"):
                self.parent().setProperty("pressedItem", True)
                fTheme.update(self.parent())

        if not isinstance(icon, FIconBase):
            painter.setOpacity(alpha)
        drawIcon(icon, painter, rect, fill=color, opacity=alpha)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        item: FNavTreeWidgetItem = self.parent().itemAt(option.rect.x(), option.rect.y())

        # draw icon
        w, h = self.parent().iconSize().width(), self.parent().iconSize().height()
        y = (option.rect.y() + 2 + (option.rect.height()-h)/2)
        if item.hasIcon():
            self._drawIcon(item.getIcon(), painter, QRectF(41 * item.posInTree() + 12*(item.posInTree() == 0), y, w, h), option, item)
        w, h = 12, 12
        y = (option.rect.y() + 2 + (option.rect.height()-h)/2)
        if item.childCount() > 0:
            icon = FFontIcon("\uE70D")
            if item.isExpanded():
                icon = FFontIcon("\uE70E")
            self._drawIcon(icon, painter, QRectF(option.rect.width()+(option.rect.x() if option.rect.x() > 0 else 0)-31+12*(self.parent().verticalScrollBar().isVisible()), y, w, h))

        if not (option.state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver)):
            self._originalStyle(item, painter, option, index)
            return

        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        # draw background
        h = option.rect.height() - 4
        if self.parent().itemPressed:
            c = QColor(self.pressed_color.get())
        elif option.state & QStyle.StateFlag.State_MouseOver and option.state & QStyle.StateFlag.State_Selected:
            c = QColor(self.hover_color.get())
        elif option.state & QStyle.StateFlag.State_Selected:
            c = QColor(self.selected_color.get())
        else:
            c = QColor(self.hover_color.get())
        painter.setBrush(c)
        w = self.parent().width() - self.parent().leftSpacing - 2 - 2*(not self.parent().parent().inPanel)
        painter.drawRoundedRect(0, option.rect.y() + 4, w, h, 4, 4)

        if option.state & QStyle.StateFlag.State_Selected and option.state & QStyle.StateFlag.State_MouseOver and self.multi_select:
            c = QColor(self.selected_color.get())
            painter.setBrush(c)
            painter.drawRoundedRect(0, option.rect.y() + 4, w, h, 4, 4)

        # draw indicator
        if option.state & QStyle.StateFlag.State_Selected:
            c = QColor(self.accent_color.get())
            if not (option.state & QStyle.StateFlag.State_Enabled):
                c = QColor(self.accent_color_disabled.get())
            painter.setBrush(c)
            painter.drawRoundedRect(0, option.rect.y() + 14, 3, 16, 2.5, 2.5)

        self._originalStyle(item, painter, option, index)

        painter.restore()

    def _originalStyle(self, item, painter: QPainter, option: QStyleOptionViewItem, index):
        pos = item.posInTree()
        if item.hasIcon():
            pos += 1
        option.rect.moveLeft(12 + 29 * pos)
        painter.setBrush(QColor("red"))
        QStyledItemDelegate.paint(self, painter, option, index)
