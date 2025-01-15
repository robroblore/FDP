# coding=utf-8
from enum import Enum
from typing import Optional

from qtpy.QtCore import Qt, QEvent, QObject, QPropertyAnimation, QEasingCurve, QSize, QRect, QPoint, Signal
from qtpy.QtGui import QResizeEvent, QMoveEvent, QFocusEvent
from qtpy.QtWidgets import QWidget

from .nav import Panel
from .navigation_panel import FNavigationPanel
from .. import fTheme
from ..common import FColors
from ..common.theme import set_acrylic_round_corners
from ..common.overload import Overload
from ..widgets.frame import FFrame


class FNavigationView(QWidget):
    """
    __init__(self, parent: Optional[QWidget] = None, displayMode: PaneDisplayMode = PaneDisplayMode.AUTO, paneState: PaneDisplayState = PaneDisplayState.COLLAPSED)

    __init__(self, paneDisplayMode: PaneDisplayMode, parent: Optional[QWidget] = None)

    __init__(self, paneDisplayState: PaneDisplayState, parent: Optional[QWidget] = None)

    __init__(self, paneDisplayMode: PaneDisplayMode, paneDisplayState: PaneDisplayState, parent: Optional[QWidget] = None)
    """

    class PaneDisplayMode(Enum):
        AUTO = 0
        LEFT = 1
        COMPACT = 2
        MINIMAL = 3
        TOP = 4

    class PaneDisplayState(Enum):
        COLLAPSED = 0
        LEFTEXPANDED = 1
        COMPACTEXPANDED = 2
        MINIMALEXPANDED = 3

    baseWidth: int = 48
    expandWidth: int = 320
    compactModeThresholdWidth: int = 640
    expandedModeThresholdWidth: int = 1007

    # Todo must be opposite
    autoCollapseMinimal: bool = True
    autoCollapseCompact: bool = True
    autoCollapseLeft: bool = False

    autoExpandMinimal: bool = False
    autoExpandCompact: bool = False
    autoExpandLeft: bool = True

    paneDisplayModeChangeSignal = Signal(PaneDisplayMode)
    paneSateChangeSignal = Signal(PaneDisplayState)
    paneModeChangeSignal = Signal(PaneDisplayMode)

    @Overload
    def __init__(self, parent: Optional[QWidget] = None, displayMode: PaneDisplayMode = PaneDisplayMode.AUTO, paneState: PaneDisplayState = PaneDisplayState.COLLAPSED):
        super().__init__(parent=parent)
        self._paneDisplayMode = displayMode
        self._paneState = paneState
        self._paneMode = None
        self.setPaneMode()
        self._changeDisplayMode = False
        self._expandMinimalLater: bool = False
        self._expandCompactLater: bool = False
        self._expandLeftLater: bool = False

        self.refFrame = FRefFrame(self)
        self.panel: Panel = Panel(self)
        self.panel.installEventFilter(self)

        self._navigationPanel: FNavigationPanel = FNavigationPanel(self, self)
        self.contentFrame: FFrame = FFrame(self)

        self._animationRefFrame: QPropertyAnimation = QPropertyAnimation(self.refFrame, b'size', self)
        self._animationRefFrame.finished.connect(self._hidePanel)
        self.refFrame.setAttribute(Qt.WidgetAttribute.WA_InputMethodTransparent)
        self.window().installEventFilter(self)

        self.setAnimationDuration(200)
        self.setAnimationEasingCurve(QEasingCurve.Type.OutQuart)

        fTheme.themeChangedSignal.connect(self._setPanelAcrylic)

    @__init__.register
    def _(self, displayMode: PaneDisplayMode, parent: Optional[QWidget] = None):
        self.__init__(parent=parent, displayMode=displayMode)

    @__init__.register
    def _(self, paneState: PaneDisplayState, parent: Optional[QWidget] = None):
        self.__init__(parent=parent, paneState=paneState)

    @__init__.register
    def _(self, displayMode: PaneDisplayMode, paneState: PaneDisplayState, parent: Optional[QWidget] = None):
        self.__init__(parent=parent, displayMode=displayMode, paneState=paneState)

    def setAnimationEasingCurve(self, easingCurve: QEasingCurve.Type):
        self._animationRefFrame.setEasingCurve(easingCurve)

    def setAnimationDuration(self, duration: int):
        self._animationRefFrame.setDuration(duration)

    def setBackButtonVisible(self, isVisible: bool):
        """ set whether the return button is visible """
        self._navigationPanel.setBackButtonVisible(isVisible)

    def setLineEditVisible(self, isVisible: bool):
        """ set whether the line edit is visible """
        self._navigationPanel.setLineEditVisible(isVisible)

    def isExpanded(self):
        return self.paneState() is not self.PaneDisplayState.COLLAPSED

    def paneState(self):
        return self._paneState

    def setPaneState(self, paneState: PaneDisplayState):
        if self.paneState() != paneState:
            self._setPaneState(paneState)
            self.updateSizes()

    def _setPaneState(self, paneState: PaneDisplayState):
        if self.paneState() != paneState:
            self._paneState = paneState
            self.paneSateChangeSignal.emit(paneState)

    def paneDisplayMode(self) -> PaneDisplayMode:
        return self._paneDisplayMode

    def setPaneDisplayMode(self, displayMode: PaneDisplayMode):
        if self.paneDisplayMode() != displayMode:
            self._setPaneDisplayMode(displayMode)
            if self.isExpanded():
                self.collapse()
                self._expandLeftLater = True
                self._expandCompactLater = True
                self._expandMinimalLater = True
                self._changeDisplayMode = True
            else:
                self.updateSizes()

    def _setPaneDisplayMode(self, displayMode: PaneDisplayMode):
        if self.paneDisplayMode() != displayMode:
            self._paneDisplayMode = displayMode
            self.paneDisplayModeChangeSignal.emit(displayMode)

    def paneMode(self) -> PaneDisplayMode:
        return self._paneMode

    def getSelectedIndex(self):
        return self._navigationPanel.treeWidget.selectedIndexes()

    def createItem(self, *args, bottom=False, **kwargs):
        return self._navigationPanel.createItem(*args, bottom=bottom, **kwargs)

    def getBaseWidth(self):
        return self.baseWidth

    def getAdjustedBaseWidth(self):
        if self.isMinial():
            return 0
        else:
            return self.getBaseWidth()

    def setBaseWidth(self, baseWidth: int):
        self.baseWidth = baseWidth
        self.updateSizes()

    def setExpandWidth(self, expandWidth: int):
        self.expandWidth = expandWidth
        self.updateSizes()

    def getExpandWidth(self) -> int:
        return self.expandWidth if self.contentsRect().width() >= self.expandWidth else self.contentsRect().width() + 1

    def setCompactModeThresholdWidth(self, compact_mode_threshold_width: int):
        self.compactModeThresholdWidth = compact_mode_threshold_width
        self.updateSizes()

    def setExpandedModeThresholdWidth(self, expanded_mode_threshold_width: int):
        self.expandedModeThresholdWidth = expanded_mode_threshold_width
        self.updateSizes()

    def isLeft(self):
        return (self.paneDisplayMode() == self.PaneDisplayMode.AUTO and self.contentsRect().width() > self.expandedModeThresholdWidth) or self.paneDisplayMode() is self.PaneDisplayMode.LEFT

    def isCompact(self):
        return (self.paneDisplayMode() == self.PaneDisplayMode.AUTO and self.contentsRect().width() > self.compactModeThresholdWidth) or self.paneDisplayMode() is self.PaneDisplayMode.COMPACT

    def isMinial(self):
        return (self.paneDisplayMode() == self.PaneDisplayMode.AUTO and self.contentsRect().width() <= self.compactModeThresholdWidth) or self.paneDisplayMode() is self.PaneDisplayMode.MINIMAL

    def setPaneMode(self):
        old_mode = self.paneMode()
        if self.isLeft():
            self._paneMode = self.PaneDisplayMode.LEFT
        elif self.isCompact():
            self._paneMode = self.PaneDisplayMode.COMPACT
        elif self.isMinial():
            self._paneMode = self.PaneDisplayMode.MINIMAL
        if old_mode != self.paneMode():
            self.paneModeChangeSignal.emit(self.paneMode())

    def expand(self):
        if self.paneDisplayMode() is not self.PaneDisplayMode.TOP:
            if self._animationRefFrame.state() == QPropertyAnimation.State.Running:
                return

            if self.isLeft():
                self._setPaneState(self.PaneDisplayState.LEFTEXPANDED)

            elif self.isCompact():
                self._showPanel()
                self._setPaneState(self.PaneDisplayState.COMPACTEXPANDED)

            elif self.isMinial():
                self._showPanel()
                self._setPaneState(self.PaneDisplayState.MINIMALEXPANDED)

            self._expandLeftLater = False
            self._expandCompactLater = False
            self._expandMinimalLater = False
            self._expandAni()

    def collapse(self):
        if self._animationRefFrame.state() != QPropertyAnimation.State.Running:
            self._setPaneState(self.PaneDisplayState.COLLAPSED)
            self._expandLeftLater = False
            self._expandCompactLater = False
            self._expandMinimalLater = False
            self._collapseAni()

    def toggle(self):
        """ switch the state of the pane"""
        if self.isExpanded():
            self.collapse()
        else:
            self.expand()

    def updateSizes(self):
        width = self.refFrame.width()
        if self._animationRefFrame.state() is not QPropertyAnimation.State.Running:
            width = self.getAdjustedBaseWidth() if self.paneState() is self.PaneDisplayState.COLLAPSED else self.getExpandWidth()
        self.refFrame.resize(self.getRefFrameSize(width))

        pos = self.mapToGlobal(QPoint(0, 0))
        pos.setX(pos.x() - 1)
        self.panel.move(pos)
        self.panel.resize(self.getPanelSize(self.refFrame.width() + 2))
        self._navigationPanel.resize(self.getNavigationPanelSize(self.refFrame.width()))

        if self.panel.isVisible():
            self.contentFrame.setGeometry(self.getContentFrameGeometry(self.getAdjustedBaseWidth()))
        else:
            self.contentFrame.setGeometry(self.getContentFrameGeometry(self.refFrame.width()))

        if (self.paneDisplayMode() == self.PaneDisplayMode.AUTO or self._changeDisplayMode) and self._animationRefFrame.state() != QPropertyAnimation.State.Running:
            
            self._changeDisplayMode = False

            if self.contentsRect().width() > self.expandedModeThresholdWidth or self.paneDisplayMode() == self.PaneDisplayMode.LEFT:
                if self.paneState() is self.PaneDisplayState.MINIMALEXPANDED:
                    self.collapse()
                    self._setExpandLater()

                elif self.paneState() is self.PaneDisplayState.COMPACTEXPANDED:
                    self.collapse()
                    self._setExpandLater()

                elif self._expandLeftLater:
                    self.expand()
                    self._expandLeftLater = False

            elif self.contentsRect().width() > self.compactModeThresholdWidth or self.paneDisplayMode() == self.PaneDisplayMode.COMPACT:
                if self.paneState() is self.PaneDisplayState.MINIMALEXPANDED:
                    self.collapse()
                    self._setExpandLater()

                elif self.paneState() is self.PaneDisplayState.LEFTEXPANDED:
                    self.collapse()
                    self._setExpandLater()

                elif self._expandCompactLater:
                    self.expand()
                    self._expandCompactLater = False

            elif self.contentsRect().width() <= self.compactModeThresholdWidth or self.paneDisplayMode() == self.PaneDisplayMode.MINIMAL:
                if self.paneState() is self.PaneDisplayState.COMPACTEXPANDED:
                    self.collapse()
                    self._setExpandLater()

                elif self.paneState() is self.PaneDisplayState.LEFTEXPANDED:
                    self.collapse()
                    self._setExpandLater()

                elif self._expandMinimalLater:
                    self.expand()
                    self._expandMinimalLater = False

        self.setPaneMode()

    def _setExpandLater(self):
        if self.autoExpandMinimal:
            self._expandMinimalLater = True
        if self.autoExpandCompact:
            self._expandCompactLater = True
        if self.autoExpandLeft:
            self._expandLeftLater = True

    def _showPanel(self):
        pos = self.mapToGlobal(QPoint(0, 0))
        pos.setX(pos.x() - 1)
        self.panel.move(pos)
        self.panel.setVisible(True)
        self._navigationPanel.showPanelFrame(self.panel)
        self._setPanelAcrylic()

    def _setPanelAcrylic(self):
        set_acrylic_round_corners(self.panel, FColors.AcrylicFillColorBase.get())

    def _hidePanel(self):
        if self.paneState() is self.PaneDisplayState.COLLAPSED:
            self.panel.hide()
            self._navigationPanel.hidePanelFrame(self)
        self.updateSizes()

    def _expandAni(self):
        if self.refFrame.width() == self.getExpandWidth():
            return
        self._animationRefFrame.setStartValue(self.getRefFrameSize(self.getAdjustedBaseWidth()))
        self._animationRefFrame.setEndValue(self.getRefFrameSize(self.getExpandWidth()))
        self._animationRefFrame.start()

    def _collapseAni(self):
        if self.refFrame.width() == self.getAdjustedBaseWidth():
            return
        self._animationRefFrame.setStartValue(self.getRefFrameSize(self.getExpandWidth()))
        self._animationRefFrame.setEndValue(self.getRefFrameSize(self.getAdjustedBaseWidth()))
        self._animationRefFrame.start()

    def getPanelSize(self, width) -> QSize:
        return QSize(width + 1, self.contentsRect().height() + 1)

    def getContentFrameGeometry(self, width) -> QRect:
        return QRect(QPoint(width, 49), QSize(self.contentsRect().width() - width, self.contentsRect().height() - 49))

    def getNavigationPanelSize(self, width) -> QSize:
        return QSize(width, self.contentsRect().height())

    def getRefFrameSize(self, width) -> QSize:
        return QSize(width, self.contentsRect().height())

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        # if watched in [self.panel, self.window()] and event.type() is QEvent.Type.ActivationChange and self.window().isActiveWindow():
        #     self.collapse()
        if watched == self.window() and isinstance(event, QMoveEvent) and event.type() is not QEvent.Type.Resize:
            pos = self.mapToGlobal(QPoint(0, 0))
            pos.setX(pos.x() - 1)
            self.panel.move(pos)
        return super().eventFilter(watched, event)

    def focusOutEvent(self, e: QFocusEvent):
        super().focusOutEvent(e)
        if e.reason() != Qt.FocusReason.ActiveWindowFocusReason:
            self.collapse()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self.paneState() is self.PaneDisplayState.LEFTEXPANDED and self.autoCollapseLeft:
            self.collapse()
            self._setExpandLater()
            if self.autoExpandLeft:
                self._expandLeftLater = False

        elif self.paneState() is self.PaneDisplayState.COMPACTEXPANDED and self.autoCollapseCompact:
            self.collapse()
            self._setExpandLater()
            if self.autoExpandCompact:
                self._expandCompactLater = False

        elif self.paneState() is self.PaneDisplayState.MINIMALEXPANDED and self.autoCollapseMinimal:
            self.collapse()
            self._setExpandLater()
            if self.autoExpandMinimal:
                self._expandMinimalLater = False
        self.updateSizes()

    def raiseButtons(self):
        self._navigationPanel.raiseButtons()


class FRefFrame(FFrame):
    def __init__(self, parent: FNavigationView):
        super().__init__(parent=parent, opacity=FFrame.Opacity.TRANSPARENT)
        self.parent = parent

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.parent.updateSizes()
