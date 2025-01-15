# coding=utf-8
from qtpy.QtGui import QPainter, QColor
from qtpy.QtWidgets import QStyledItemDelegate, QStyle, QTreeWidget, QTreeView, QAbstractItemView

from ..common import FColors
from .scroll_bar import FSmoothScrollDelegate

from qtpy.QtCore import Qt


class Tree:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scrollDelagate = FSmoothScrollDelegate(self)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(5)

    def drawBranches(self, painter, rect, index):
        rect.moveLeft(7)
        return QTreeView.drawBranches(self, painter, rect, index)


class TreeView(Tree, QTreeView):
    pass


class TreeWidget(Tree, QTreeWidget):
    pass


class FTreeView(TreeView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setItemDelegate(FTreeItemDelegate(self, FColors.SubtleFillColorTertiary, FColors.SubtleFillColorTertiary, FColors.SubtleFillColorSecondary, FColors.AccentFillColorDefault, FColors.TextFillColorDisabled))


class FCheckTreeView(TreeView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setItemDelegate(FTreeItemDelegate(self, FColors.SubtleFillColorTertiary, FColors.SubtleFillColorTertiary, FColors.SubtleFillColorSecondary, FColors.AccentFillColorDefault, FColors.TextFillColorDisabled, True))


class FTreeWidget(TreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setItemDelegate(FTreeItemDelegate(self, FColors.SubtleFillColorTertiary, FColors.SubtleFillColorTertiary, FColors.SubtleFillColorSecondary, FColors.AccentFillColorDefault, FColors.TextFillColorDisabled))


class FCheckTreeWidget(TreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setItemDelegate(FTreeItemDelegate(self, FColors.SubtleFillColorTertiary, FColors.SubtleFillColorTertiary, FColors.SubtleFillColorSecondary, FColors.AccentFillColorDefault, FColors.TextFillColorDisabled, True))


class FTreeItemDelegate(QStyledItemDelegate):
    """ Tree item delegate """
    def __init__(self, parent, hover_color, pressed_color, selected_color, accent_color, accent_color_disabled, multi_select=False):
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.selected_color = selected_color
        self.accent_color = accent_color
        self.accent_color_disabled = accent_color_disabled
        self.multi_select = multi_select
        super().__init__(parent=parent)

    def paint(self, painter, option, index):
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        super().paint(painter, option, index)

        if not (option.state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver)):
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
        w = self.parent().width() - (self.parent().leftSpacing + 12 if self.parent().verticalScrollBar().isVisible() else 8)
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
            painter.drawRoundedRect(0, option.rect.y() + 11, 3, 16, 2.5, 2.5)

        painter.restore()
