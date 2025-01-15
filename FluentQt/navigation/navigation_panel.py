# coding=utf-8
from qtpy.QtCore import Qt, QSize, QPoint, QObject, QEvent, Signal
from qtpy.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy

from .navigation_tree import FNavTreeWidget, FNavTreeWidgetItem
from ..common.icon import FFontIcon
from ..widgets import FSearchLineEdit, FNavigationViewButton
from ..widgets.frame import FFrame


class FNavigationPanel(QWidget):
    _isBackButtonVisible: bool = True
    _isLineEditVisible: bool = True
    _previousSelectedIndex = None
    _items = []
    _bottomItems = []

    selectionChanged = Signal(int)

    def __init__(self, parent, navigation_view):
        super().__init__(parent=parent)
        self.navigationView = navigation_view

        self.setStyleSheet("FNavigationPanel{background: transparent}")

        self.setLayout(QVBoxLayout(self))
        self.layout().setSpacing(0)

        # Top Buttons
        self.topFrame = FFrame(self.window(), FFrame.Opacity.TRANSPARENT)
        self.window().installEventFilter(self)
        self.topLayout = QHBoxLayout(self.topFrame)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.setSpacing(0)
        self.topLayout.setSizeConstraint(self.topLayout.SizeConstraint.SetFixedSize)

        self.topBackButton = FNavigationViewButton(FFontIcon("\uE72B"), self.window())
        self.topBackButton.setIconSize(QSize(12, 12))
        self.topLayout.addWidget(self.topBackButton, Qt.AlignmentFlag.AlignLeft)

        self.topMenuButton = FNavigationViewButton(FFontIcon("\ue700"), self.window())
        self.topMenuButton.setIconSize(QSize(14, 14))
        self.topMenuButton.clicked.connect(navigation_view.toggle)
        self.topLayout.addWidget(self.topMenuButton, Qt.AlignmentFlag.AlignLeft)

        # Menu Button
        self.menuButton = FNavigationViewButton(FFontIcon("\ue700"), self.window())
        self.menuButton.setIconSize(QSize(14, 14))
        self.menuButton.clicked.connect(navigation_view.toggle)

        # Panel Buttons
        self.panelFrame = FFrame(None, FFrame.Opacity.TRANSPARENT)
        self.panelLayout = QHBoxLayout(self.panelFrame)
        self.panelLayout.setContentsMargins(0, 0, 0, 0)
        self.panelLayout.setSpacing(0)
        self.panelLayout.setSizeConstraint(self.topLayout.SizeConstraint.SetFixedSize)

        self.panelBackButton = FNavigationViewButton(FFontIcon("\uE72B"))
        self.panelBackButton.setIconSize(QSize(12, 12))
        self.panelLayout.addWidget(self.panelBackButton)

        self.panelMenuButton = FNavigationViewButton(FFontIcon("\ue700"))
        self.panelMenuButton.setIconSize(QSize(14, 14))
        self.panelMenuButton.clicked.connect(navigation_view.toggle)
        self.panelLayout.addWidget(self.panelMenuButton)

        # LineEdit
        self.lineEditFrame = FFrame(None, FFrame.Opacity.TRANSPARENT)
        self.lineEditLayout1 = QVBoxLayout(self.lineEditFrame)
        self.lineEditLayout1.setContentsMargins(0, 0, 0, 0)

        self.lineEditFrame2 = FFrame(None, FFrame.Opacity.TRANSPARENT)
        self.lineEditLayout2 = QHBoxLayout(self.lineEditFrame2)
        self.lineEdit = FSearchLineEdit(self)
        self.lineEditLayout2.addWidget(self.lineEdit)
        self.lineEditLayout1.addWidget(self.lineEditFrame2)

        self.lineEditIconButton = FNavigationViewButton(FFontIcon("\uF78B"))
        self.lineEditIconButton.setIconSize(QSize(14, 14))
        self.lineEditIconButton.clicked.connect(self.navigationView.expand)
        self.lineEditIconButton.clicked.connect(self.lineEdit.setFocus)
        self.lineEditLayout1.addWidget(self.lineEditIconButton)

        # TreeWidget
        self.treeWidget = FNavTreeWidget(self)
        self.treeWidget.itemSelectionChanged.connect(self.treeWidgetSelectionChanged)

        self.bottomTreeWidget = FNavTreeWidget(self)
        self.bottomTreeWidget.setFixedHeight(40)
        self.bottomTreeWidget.itemSelectionChanged.connect(self.bottomTreeWidgetSelectionChanged)

        # item = FNavTreeWidgetItem(self, FFontIcon("\uE80A"), self.bottomTreeWidget)
        # # item.setIcon(0, FFontIcon("\uF78B").icon())
        # item.setText(0, "BJoJo 1 - Phantom Blood")
        # item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsAutoTristate)
        self._bottomItemCount = 1

        # for i in range(10):
        #     item = FNavTreeWidgetItem(self, FFontIcon("\uE80A"), self.treeWidget)
        #     # item.setIcon(0, FFontIcon("\uF78B").icon())
        #     item.setText(0, "BJoJo 1 - Phantom Blood")
        #     item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsAutoTristate)
        #
        #     for j in range(10):
        #         item1 = FNavTreeWidgetItem(self, FFontIcon("\uE80A"), item)
        #         item1.setText(0, "BJoJo 1 - Phantom Blood")
        #         item1.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsAutoTristate)
        #
        #         for k in range(10):
        #             item2 = FNavTreeWidgetItem(None, None, item1)
        #             item2.setText(0, "BJoJo 1 - Phantom Blood")
        #             item2.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsAutoTristate)

        self.menuButtonSpacer = QSpacerItem(0, 0)
        self.topSpacer = QSpacerItem(0, 0)
        self.spacer = QWidget()
        self.spacer.setStyleSheet("background: red")
        self.spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.inPanel = False
        self.setBackButtonVisible(True)
        self.layout().addItem(self.topSpacer)
        self.layout().addWidget(self.panelFrame)
        self.layout().addItem(self.menuButtonSpacer)
        self.layout().addWidget(self.menuButton)
        self.layout().addWidget(self.lineEditFrame)
        self.layout().addWidget(self.treeWidget)
        self.layout().addWidget(self.bottomTreeWidget)

        self.navigationView.paneModeChangeSignal.connect(self._setBaseContentMargins)
        self.navigationView.paneModeChangeSignal.connect(self._setVisibility)
        self.navigationView.paneSateChangeSignal.connect(lambda: self._setVisibility())

        self._setBaseContentMargins()
        self._setVisibility()

    def setBackButtonVisible(self, isVisible: bool):
        """ set whether the return button is visible """
        self._isBackButtonVisible = isVisible
        self.topBackButton.setVisible(isVisible)
        self._setBaseContentMargins()

    def setLineEditVisible(self, isVisible: bool):
        """ set whether the line edit is visible """
        self._isLineEditVisible = isVisible
        self.lineEditFrame.setVisible(isVisible)
        self._setBaseContentMargins()

    def _setVisibility(self, mode=None):
        if not mode:
            mode = self.navigationView.paneMode()

        self.topSpacer.changeSize(0, 4 * (not self._isBackButtonVisible))

        self.panelBackButton.setVisible(self.inPanel and self._isBackButtonVisible)
        self.panelMenuButton.setVisible(self.inPanel and mode == self.navigationView.PaneDisplayMode.MINIMAL)

        self.menuButton.setVisible(not self.inPanel and self._isBackButtonVisible or self.inPanel and mode != self.navigationView.PaneDisplayMode.MINIMAL)
        self.menuButtonSpacer.changeSize(0, 3 * ((not self.inPanel or self.inPanel and mode != self.navigationView.PaneDisplayMode.MINIMAL) and self._isBackButtonVisible))

        self.topBackButton.setVisible(self._isBackButtonVisible)
        self.topMenuButton.setVisible(not self._isBackButtonVisible or mode == self.navigationView.PaneDisplayMode.MINIMAL)

        self.lineEditFrame2.setVisible(self._expandedOrMinimal(mode))
        self.lineEditIconButton.setVisible(not self.lineEditFrame2.isVisible())

        self.lineEditLayout2.setContentsMargins(12, 2, 14 + 2*(not self.inPanel), 2)
        self.lineEditFrame.setContentsMargins(0, 4, 0, 8)

        self.treeWidget.collapseAll()

    def showPanelFrame(self, parent):
        self.setParent(parent)
        self.setVisible(True)
        self._setPanelContentMargins()
        self.inPanel = True
        self._setVisibility()

    def hidePanelFrame(self, parent):
        self.setParent(parent)
        self.setVisible(True)
        self._setBaseContentMargins()
        self.inPanel = False
        self._setVisibility()

    def _setBaseContentMargins(self):
        self.layout().setContentsMargins(4, 39 + 4*self._isBackButtonVisible, 0, 6)

    def _setPanelContentMargins(self):
        self.layout().setContentsMargins(5, 3 + 4*self._isBackButtonVisible, 0, 6)

    def _expandedOrMinimal(self, mode):
        return self.navigationView.isExpanded() or mode == self.navigationView.PaneDisplayMode.MINIMAL

    def raiseButtons(self):
        self.topFrame.raise_()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Resize:
            self.topFrame.move(QPoint(4, 7))
            self.repaint()
        return super().eventFilter(watched, event)

    def treeWidgetSelectionChanged(self):
        if len(self.treeWidget.selectedItems()) > 0:
            self._previousSelectedIndex = self.treeWidget.currentIndex().row()
            self.selectionChanged.emit(self._previousSelectedIndex)
        else:
            self.selectItem(self._previousSelectedIndex)
        self.bottomTreeWidgetDeselectAll()

    def bottomTreeWidgetSelectionChanged(self):
        if len(self.bottomTreeWidget.selectedItems()) > 0:
            self._previousSelectedIndex = self.bottomTreeWidget.currentIndex().row() * -1 - 1
            self.selectionChanged.emit(self._previousSelectedIndex)
        else:
            self.selectItem(self._previousSelectedIndex)
        self.treeWidgetDeselectAll()

    def treeWidgetDeselectAll(self):
        for item in self.treeWidget.selectedItems():
            item.setSelected(False)

    def bottomTreeWidgetDeselectAll(self):
        for item in self.bottomTreeWidget.selectedItems():
            item.setSelected(False)

    def deselectAll(self):
        self.treeWidgetDeselectAll()
        self.bottomTreeWidgetDeselectAll()

    def selectItem(self, index):
        self._previousSelectedIndex = index
        if self._previousSelectedIndex > -1:
            self._items[self._previousSelectedIndex].setSelected(True)
        else:
            self._bottomItems[abs(self._previousSelectedIndex) - len(self._bottomItems)].setSelected(True)

    def createItem(self, *args, bottom=False, **kwargs):
        item = FNavTreeWidgetItem(*args, self.bottomTreeWidget if bottom else self.treeWidget, **kwargs)
        self._items.append(item) if not bottom else self._bottomItems.append(item)
        return item