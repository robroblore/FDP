# coding: utf-8
from typing import Sequence, Optional

from qtpy.QtCore import Qt, QRectF, Signal, QStringListModel, QMargins
from qtpy.QtGui import QPainter, QPainterPath, QFocusEvent, QResizeEvent
from qtpy.QtWidgets import QHBoxLayout, QLineEdit, QTextEdit, QPlainTextEdit, QWidget

from .button import FLineEditButton
from .completer import FCompleter
from .menu import FLineEditMenu, FTextEditMenu
from .scroll_bar import FSmoothScrollDelegate
from ..common import FColors
from ..common.icon import FFontIcon
from ..common.overload import Overload


class FLineEdit(QLineEdit):
    clearSignal = Signal()

    @Overload
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)

        self.hBoxLayout = QHBoxLayout(self)
        self.clearButton = FLineEditButton(FFontIcon("\uE711"), self)

        self.hBoxLayout.setSpacing(4)
        self.hBoxLayout.setContentsMargins(1, 5, 5, 5)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.clearButton.clicked.connect(self.clear)
        self.clearButton.clicked.connect(self.clearSignal)

        self.textChanged.connect(self.__onTextChanged)

        self._buttons = [self.clearButton]

        self._placeButtons()

        self.clearButton.hide()

    @__init__.register
    def _(self, text: str, parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setText(text)

    def buttons(self) -> Sequence[FLineEditButton]:
        return self._buttons

    def addButton(self, button: FLineEditButton):
        self._buttons.append(button)
        self._placeButtons()

    def addButtons(self, buttons: Sequence[FLineEditButton]):
        self._buttons.extend(buttons)
        self._placeButtons()

    def removeButton(self, button: FLineEditButton):
        self._buttons.remove(button)
        self._placeButtons()

    def insertButton(self, index: int, button: FLineEditButton):
        self._buttons.insert(index, button)
        self._placeButtons()

    def clearButtons(self):
        self._buttons.clear()
        self._placeButtons()

    def _placeButtons(self):
        for button in self._buttons:
            self.hBoxLayout.addWidget(button, 0, Qt.AlignmentFlag.AlignRight)
        self._setMargins()

    def _setMargins(self):
        buttons_visible = 0
        for button in self._buttons:
            if button.isVisible():
                buttons_visible += 1
        margins = QMargins(0, 0, max(31 * buttons_visible + 4 * (buttons_visible - 1), 0), 0)
        if self.textMargins() != margins:
            self.setTextMargins(margins)

    def setClearButtonEnabled(self, enable: bool):
        self.clearButton.setButtonEnabled(enable)

    def isClearButtonEnabled(self) -> bool:
        return self.clearButton.isButtonEnabled()

    def focusOutEvent(self, e: QFocusEvent):
        super().focusOutEvent(e)
        if not self.hasFocus() and e.reason() != Qt.FocusReason.ActiveWindowFocusReason:
            self.clearButton.hide()
            self._setMargins()

    def focusInEvent(self, e):
        super().focusInEvent(e)
        if self.isClearButtonEnabled():
            self.clearButton.setVisible(bool(self.text()))
            self._setMargins()

    def __onTextChanged(self, text):
        """ text changed slot """
        if self.isClearButtonEnabled():
            self.clearButton.setVisible(bool(text) and self.hasFocus())
            self._setMargins()

    def contextMenuEvent(self, e):
        menu = FLineEditMenu(self)
        if len(menu.actions()) != 0:
            menu.exec_(e.globalPos())

    def paintEvent(self, e):
        super().paintEvent(e)
        self._setMargins()

        if not self.hasFocus():
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        path = QPainterPath()
        w, h = self.contentsRect().width()-self.contentsRect().x(), self.contentsRect().height()+self.contentsRect().y()
        path.addRoundedRect(QRectF(0, h-10, w, 10), 4, 4)

        rect_path = QPainterPath()
        rect_path.addRect(0, h-10, w, 8)
        path = path.subtracted(rect_path)

        painter.fillPath(path, FColors.AccentFillColorDefault.getColor())


class FAutoSuggestLineEdit(FLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completer = FCompleter(self)
        self.completer.setCompletionMode(self.completer.CompletionMode.PopupCompletion)
        self.setCompleter(self.completer)

    def setCompletion(self, completion: Sequence[str]):
        model = QStringListModel(completion)
        self.completer.setModel(model)

    def completion(self) -> str:
        return self.completer.currentCompletion()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.completer.popup().resize(self.width(), self.completer.popup().height())


class FSearchLineEdit(FAutoSuggestLineEdit):
    """ Search line edit """

    searchSignal = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.searchButton = FLineEditButton(FFontIcon("\uF78B"), self)
        self.searchButton.clicked.connect(self.search)
        self.addButton(self.searchButton)

    def search(self):
        """ emit search signal """
        text = self.text().strip()
        self.searchSignal.emit(text)


class FPasswordLineEdit(FLineEdit):
    """ Search line edit """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEchoMode(self.EchoMode.Password)
        self.setClearButtonEnabled(False)

        self.showPasswordButton = FLineEditButton(FFontIcon("\uEd1A"), self)
        self.showPasswordButton.pressed.connect(lambda: self.setPasswordVisible(True))
        self.showPasswordButton.clicked.connect(self.setPasswordVisible)
        self.addButton(self.showPasswordButton)

    def setCheckable(self, checkable: bool):
        self.showPasswordButton.setCheckable(checkable)
        self.setPasswordVisible()

    def isCheckable(self) -> bool:
        return self.showPasswordButton.isCheckable()

    def setChecked(self, checked: bool):
        self.showPasswordButton.setChecked(checked)
        self.setPasswordVisible()

    def isChecked(self) -> bool:
        return self.showPasswordButton.isChecked()

    def setPasswordVisible(self, visible=False):
        if self.isCheckable():
            self.setEchoMode(self.EchoMode.Normal if self.isChecked() else self.EchoMode.Password)
            self.showPasswordButton.setIcon(FFontIcon("\uE890") if self.isChecked() else FFontIcon("\uEd1A"))
        else:
            self.setEchoMode(self.EchoMode.Normal if visible else self.EchoMode.Password)
            self.showPasswordButton.setIcon(FFontIcon("\uE890") if visible else FFontIcon("\uEd1A"))

    def focusOutEvent(self, e: QFocusEvent) -> None:
        super().focusOutEvent(e)
        self.setPasswordVisible()


class FTextEdit(QTextEdit):
    """ Text edit """

    @Overload
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollDelegate = FSmoothScrollDelegate(self)

    @__init__.register
    def _(self, text: str, parent=None):
        super().__init__(text=text, parent=parent)
        self.scrollDelegate = FSmoothScrollDelegate(self)

    def contextMenuEvent(self, e):
        menu = FTextEditMenu(self)
        if len(menu.actions()) != 0:
            menu.exec_(e.globalPos())


class FPlainTextEdit(QPlainTextEdit):
    """ Plain text edit """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollDelegate = FSmoothScrollDelegate(self)

    def contextMenuEvent(self, e):
        menu = FTextEditMenu(self)
        if len(menu.actions()) != 0:
            menu.exec_(e.globalPos())
