# coding=utf-8
from enum import Enum
from typing import Optional, Union

from PySide6.QtCore import QRectF, QSize, QPoint, Signal, QObject, QEvent, Qt
from PySide6.QtGui import QPaintEvent, QIcon, QPixmap, QPainter, QPainterPath, QMouseEvent, QRegion, QResizeEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QBoxLayout

from ..common.overload import Overload
from ..common.widget_animations import WidgetAnimationManager, WidgetAnimationType

from .. import FColors
from ..common.icon_animation import RotateAnimation, TranslateAnimation
from ..common.icon import FIconBase, FFontIcon, drawIcon
from ..common.widget_mouse_event import WidgetMouseEvent
from ..widgets.frame import FFrame
from ..widgets.label import FLabel


class FExpanderHeader(QWidget):

    def __init__(self, parent):
        super().__init__(parent=parent)

        self._expandDirection: FExpander.ExpandDirection = FExpander.ExpandDirection.Expand_Down

        self.isPressed: bool = False
        self.isHover: bool = False
        WidgetMouseEvent(self)

        self.arrowAniYA = RotateAnimation(self, installEventFilter=False, yOffset=-1)
        self.arrowAniX = TranslateAnimation(self, installEventFilter=False, offset=1)

        self.headerhorizontalLayout = QHBoxLayout(self)

        self.frame = FFrame(self, opacity=FFrame.Opacity.TRANSPARENT)
        self._verticalLayout = QVBoxLayout(self.frame)

        self.title = FLabel(FLabel.TextStyle.Body, self)
        self.title.hide()
        self._verticalLayout.addWidget(self.title)

        self.subtitle = FLabel(FLabel.TextStyle.Caption, self)
        self.subtitle.hide()
        self._verticalLayout.addWidget(self.subtitle)

        self.headerhorizontalLayout.addWidget(self.frame)

        self.headerLayout = QHBoxLayout()
        self.headerLayout.setDirection(QBoxLayout.Direction.RightToLeft)
        self.headerLayout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.headerLayout.setSpacing(10)
        self.headerhorizontalLayout.addLayout(self.headerLayout)

        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._expandDirection in [FExpander.ExpandDirection.Expand_Down, FExpander.ExpandDirection.Expand_Up]:
            self.arrowAniYA.onPress()
        else:
            self.arrowAniX.onPress()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._expandDirection in [FExpander.ExpandDirection.Expand_Down, FExpander.ExpandDirection.Expand_Up]:
            self.parent().eventFilter(self, event)
            self.arrowAniYA.onRelease()
        else:
            self.arrowAniX.onRelease()
        super().mouseReleaseEvent(event)

    def expandDirection(self):
        return self._expandDirection

    def setExpandDirection(self, expandDirection) -> None:
        self.setContentsMargins(self.contentsMargins().left(), 0, 8 + 32 * (expandDirection != FExpander.ExpandDirection.NONE), 0)
        self._expandDirection = expandDirection
        self.update()

    def _getRoundedRectPath(self, rect, roundBottomCorners=True):
        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        path.addRoundedRect(rect, 4, 4)
        if not roundBottomCorners:
            square_size = rect.height() / 2
            path.addRect(QRectF(rect.left(), rect.top() + rect.height() - square_size, square_size, square_size))
            path.addRect(QRectF((rect.left() + rect.width()) - square_size, rect.top() + rect.height() - square_size, square_size, square_size))
        return path.simplified()

    def _drawIcon(self, icon: Union[QIcon, QPixmap, str, FIconBase], painter: QPainter, rect: QRectF) -> None:

        alpha, color = FColors.TextFillColorPrimary.getAlphaAndColor()
        if not self.isEnabled():
            alpha, color = FColors.TextFillColorDisabled.getAlphaAndColor()

        if not isinstance(icon, FIconBase) and not self.isEnabled():
            painter.setOpacity(alpha)

        drawIcon(icon, painter, rect, fill=color, opacity=alpha)

    def _drawDropDownIcon(self, painter: QPainter, rect: QRectF) -> None:

        alpha, color = FColors.TextFillColorPrimary.getAlphaAndColor()
        if not self.isEnabled():
            alpha, color = FColors.TextFillColorDisabled.getAlphaAndColor()

        FFontIcon("\uE96E").render(painter, rect, fill=color, opacity=alpha)

    def paintEvent(self, event: QPaintEvent) -> None:

        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect().x() + 1, self.rect().y() + 1, self.rect().width() - 2, self.rect().height() - 2)
        painter.fillPath(self._getRoundedRectPath(rect, not self.parent().isExpanded() and not (self.parent().ani_manager and self.parent().ani_manager.ani.state() == self.parent().ani_manager.ani.State.Running)), FColors.CardBackgroundFillColorDefault.getColor())

        rect = QRectF(self.rect().x()+0.5, self.rect().y()+0.5, self.rect().width()-1, self.rect().height()-1)
        painter.setPen(FColors.CardStrokeColorDefault.getColor())
        painter.drawPath(self._getRoundedRectPath(rect, not self.parent().isExpanded() and not (self.parent().ani_manager and self.parent().ani_manager.ani.state() == self.parent().ani_manager.ani.State.Running)))

        painter.end()

        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.VerticalSubpixelPositioning)

        if self.parent().getIcon():
            w, h = self.parent().iconSize().width(), self.parent().iconSize().height()
            y = (self.height() - h) / 2
            self._drawIcon(self.parent().getIcon(), painter, QRectF(19, y, w, h))

        if self._expandDirection != FExpander.ExpandDirection.NONE:
            path = QPainterPath()
            rect = QRectF(self.width() - 41, self.height() / 2 - 16, 32, 32)
            path.addRoundedRect(rect, 4, 4)

            if not self.isEnabled():
                color = FColors.SubtleFillColorDisabled
            elif self.isPressed:
                color = FColors.SubtleFillColorTertiary
            elif self.isHover:
                color = FColors.SubtleFillColorSecondary
            else:
                color = FColors.SubtleFillColorTransparent

            painter.fillPath(path, color.getColor())

            if self._expandDirection in [FExpander.ExpandDirection.Expand_Down, FExpander.ExpandDirection.Expand_Up]:
                rect = QRectF(self.width() - 30, self.height() / 2 - 5 + self.arrowAniYA.y, 10, 10)
                painter.translate(rect.center())
                painter.rotate(self.arrowAniYA.angle)
                self._drawDropDownIcon(painter, QRectF(-5, -5, 10, 10))

            elif self._expandDirection == FExpander.ExpandDirection.Open_Left:
                rect = QRectF(self.width() - 30 - self.arrowAniX.offset, self.height() / 2 - 5, 10, 10)
                painter.translate(rect.center())
                painter.rotate(-90)
                self._drawDropDownIcon(painter, QRectF(-5, -5, 10, 10))


class FExpander(QWidget):
    """
    __init__(self, parent: Optional[QWidget] = None)

    __init__(self, title: str, parent: Optional[QWidget] = None)

    __init__(self, title: str, subtitle: str, parent: Optional[QWidget] = None)

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], title: str, parent: Optional[QWidget] = None)

    __init__(self, icon: Union[QIcon, QPixmap, str, FIconBase], title: str, subtitle: str, parent: Optional[QWidget] = None)
    """

    Expanded = Signal(bool)

    class ExpandDirection(Enum):
        NONE = 0
        Open_Left = 1
        Expand_Down = 2
        Expand_Up = 3

    @Overload
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self._expanded: bool = False
        self.ani_manager = None

        self._header = FExpanderHeader(self)
        self._header.setFixedHeight(70)
        self.setMinimumHeight(self._header.height())

        self._contentFrame = FFrame(self)

        self._iconSize = QSize(22, 22)
        self._icon: Optional[Union[QIcon, QPixmap, str, FIconBase]] = None
        self.setIcon(self._icon)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setExpandDirection(self.ExpandDirection.Expand_Down)

        self._contentFrame.installEventFilter(self)

    @__init__.register
    def _(self, title: Optional[str], parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setTitle(title)

    @__init__.register
    def _(self, title: Optional[str], subtitle: Optional[str], parent: Optional[QWidget] = None):
        self.__init__(title=title, parent=parent)
        self.setSubtitle(subtitle)

    @__init__.register
    def _(self, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]], title: Optional[str], subtitle: Optional[str], parent: Optional[QWidget] = None):
        self.__init__(title=title, subtitle=subtitle, parent=parent)
        self.setIcon(icon)

    def iconSize(self) -> QSize:
        return self._iconSize

    def setIconSize(self, size: QSize) -> None:
        self._iconSize = size

    def icon(self) -> QIcon:
        if isinstance(self._icon, str) or isinstance(self._icon, QPixmap):
            return QIcon(self._icon)

        elif isinstance(self._icon, FIconBase):
            return self._icon.icon()

        return self._icon

    def getIcon(self) -> Optional[Union[QIcon, QPixmap, str, FIconBase]]:
        return self._icon

    def setIcon(self, icon: Optional[Union[QIcon, QPixmap, str, FIconBase]]) -> None:
        self._header.setContentsMargins(8 + 42 * (icon is not None), 0, self._header.contentsMargins().right(), 0)
        self._icon = icon
        self.update()
        self.updateGeometry()

    def expandDirection(self) -> ExpandDirection:
        return self._header.expandDirection()

    def setExpandDirection(self, expandDirection: ExpandDirection) -> None:
        self.updateGeometry()

        if expandDirection == self.ExpandDirection.Expand_Down:
            self._header.arrowAniYA.onRelease(angle=0)
        elif expandDirection == self.ExpandDirection.Expand_Up:
            self._header.arrowAniYA.onRelease(angle=180)

        was_expanded = self.isExpanded()
        if was_expanded:
            self._setExpanded(False)

        if self.ani_manager and expandDirection in [self.ExpandDirection.Expand_Down, self.ExpandDirection.Expand_Up] and was_expanded:
            self.ani_manager.ani.finished.connect(lambda: self._header.setExpandDirection(expandDirection))
            self.ani_manager.ani.finished.connect(self._updateHeaderPos)
        else:
            self._header.setExpandDirection(expandDirection)
            self._updateHeaderPos()

    def isExpanded(self) -> bool:
        return self._expanded

    def setExpanded(self, expanded: bool) -> None:
        if expanded != self.isExpanded():
            if self.expandDirection() in [self.ExpandDirection.Expand_Down, self.ExpandDirection.Expand_Up]:
                self._setExpanded(expanded)

    def _setExpanded(self, expanded: bool) -> None:
        if expanded != self.isExpanded():

            if self.expandDirection() in [self.ExpandDirection.Expand_Down, self.ExpandDirection.Expand_Up]:
                if self.isExpanded():
                    if self.expandDirection() == self.ExpandDirection.Expand_Down:
                        self.ani_manager = WidgetAnimationManager.make(self._contentFrame, WidgetAnimationType.PULL_BACK_UP)
                    else:
                        self.ani_manager = WidgetAnimationManager.make(self._contentFrame, WidgetAnimationType.DROP_BACK_DOWN)

                else:
                    if self.expandDirection() == self.ExpandDirection.Expand_Down:
                        self.ani_manager = WidgetAnimationManager.make(self._contentFrame, WidgetAnimationType.DROP_DOWN)
                    else:
                        self.ani_manager = WidgetAnimationManager.make(self._contentFrame, WidgetAnimationType.PULL_UP)
                    # self.ani_manager.ani.finished.connect(self._contentFrame.clearMask)

                if self.expandDirection() == self.ExpandDirection.Expand_Down:
                    self.ani_manager.exec(QPoint(0, self._header.height()), self._contentFrame.height(), globalPos=False, aniDuration=200)
                else:
                    self.ani_manager.exec(QPoint(0, 0), self._header.height(), globalPos=False, aniDuration=200, mask=False)
                self.ani_manager.ani.valueChanged.connect(self.updateGeometry)
                self.ani_manager.ani.valueChanged.connect(self._updateFrameMask)
                self.ani_manager.ani.finished.connect(self.update)

            self._expanded = expanded
            self.Expanded.emit(expanded)

    def title(self) -> str:
        return self._header.title.text()

    def setTitle(self, title: Optional[str]) -> None:
        self._header.title.setText(title)
        self._header.title.setVisible(title is not None)

    def subtitle(self) -> str:
        return self._header.subtitle.text()

    def setSubtitle(self, subtitle: Optional[str]) -> None:
        self._header.subtitle.setText(subtitle)
        self._header.subtitle.setVisible(subtitle is not None)

    def headerLayout(self) -> QBoxLayout:
        return self._header.headerLayout

    def setHeaderLayout(self, layout: QBoxLayout) -> None:
        self._header.headerhorizontalLayout.removeItem(self.headerLayout)
        self._header.headerLayout = layout
        self._header.headerhorizontalLayout.addLayout(self._header.headerLayout)

    def contentFrame(self) -> FFrame:
        return self._contentFrame

    def setContentFrame(self, frame: FFrame) -> None:
        self._contentFrame = frame
        self.resizeEvent(QResizeEvent(self.size(), self.size()))
        self.updateGeometry()

    def _get_content_frame_min_height(self) -> int:
        return max(min(self._contentFrame.minimumSizeHint().height(), self._contentFrame.maximumHeight()), self._contentFrame.minimumHeight())

    def _get_content_frame_height(self) -> int:
        return max(min(self._contentFrame.sizeHint().height(), self._contentFrame.maximumHeight()), self._contentFrame.minimumHeight())

    def _updateHeaderPos(self) -> None:
        if self.expandDirection() == self.ExpandDirection.Expand_Up:
            self._header.move(0, self.height()-self._header.height())
        else:
            self._header.move(0, 0)
        self._updateFramePos()
        self._updateFrameMask()

    def _updateFramePos(self) -> None:
        if self.expandDirection() == self.ExpandDirection.Expand_Up:
            self._contentFrame.move(0, self._header.height())
        else:
            self._contentFrame.move(0, self._header.height() - self._get_content_frame_height())
        self.updateGeometry()

    def _updateFrameMask(self) -> None:
        m = self._contentFrame.contentsMargins()
        w = self.width() + m.left() + m.right()
        h = self._get_content_frame_height() + m.top() + m.bottom()
        if self.expandDirection() == self.ExpandDirection.Expand_Up:
            self._contentFrame.setMask(QRegion(0, -2 * self._contentFrame.y(), w, h))
        else:
            self._contentFrame.setMask(QRegion(0, self._header.height() - self._contentFrame.y(), w, h))


    def minimumSizeHint(self) -> QSize:
        w = max(self._header.minimumSizeHint().width(), self._header.minimumWidth(), self._contentFrame.minimumSizeHint().width(), self._contentFrame.minimumWidth())
        h = self._header.height() + self._get_content_frame_min_height()

        if self.sizePolicy().verticalPolicy() in [QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding]:
            h = self._get_content_frame_min_height() + self._contentFrame.y()*(1-2*(self.expandDirection() == self.ExpandDirection.Expand_Up)) + self._header.height()*(self.expandDirection() == self.ExpandDirection.Expand_Up)
        return QSize(w, h)

    def setFixedHeight(self, h: int) -> None:
        super().setFixedHeight(h)
        self._contentFrame.setFixedHeight(h - self._header.height())
        if not self.isExpanded():
            self._updateFramePos()
            self._updateFrameMask()

    def sizeHint(self) -> QSize:
        w = max(self._header.sizeHint().width(), self._contentFrame.sizeHint().width())
        h = self._header.height() + self._get_content_frame_height()

        if self.sizePolicy().verticalPolicy() in [QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding]:
            h = self._get_content_frame_height() + self._contentFrame.y()*(1-2*(self.expandDirection() == self.ExpandDirection.Expand_Up)) + self._header.height()*(self.expandDirection() == self.ExpandDirection.Expand_Up)
        return QSize(w, h)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        self._header.resize(self.width(), self._header.height())
        self._contentFrame.resize(self.width(), self._contentFrame.sizeHint().height())

        if not (self.isExpanded() or self.ani_manager):
            self._updateFramePos()
        self._updateFrameMask()

        if self.expandDirection() == self.ExpandDirection.Expand_Up:
            self._header.move(0, self.height()-self._header.height())
        else:
            self._header.move(0, 0)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self._header and event.type() == QEvent.Type.MouseButtonRelease:
            self._setExpanded(not self.isExpanded())
        if watched == self._contentFrame and event.type() == QEvent.Type.LayoutRequest:
            self.updateGeometry()
        return super().eventFilter(watched, event)
