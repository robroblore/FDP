# coding=utf-8
from enum import Enum
from typing import Optional

from PySide6.QtWidgets import QLabel, QWidget

from .. import fTheme
from ..common.overload import Overload


class FLabel(QLabel):
    """
    __init__(self, parent: Optional[QWidget] = None, f: Qt.WindowType = Default(Qt.WindowFlags)) -> None

    __init__(self, text: str, parent: Optional[QWidget] = None, f: Qt.WindowType = Default(Qt.WindowFlags)) -> None

    __init__(self, textStyle: TextStyle, parent: Optional[QWidget] = None, f: Qt.WindowType = Default(Qt.WindowFlags)) -> None

    __init__(self, text: str, textStyle: TextStyle, parent: Optional[QWidget] = None, f: Qt.WindowType = Default(Qt.WindowFlags)) -> None
    """

    class TextStyle(Enum):
        Caption = "caption"
        Body = "body"
        BodyStrong = "bodyStrong"
        Subtitle = "subtitle"
        Title = "title"
        TitleLarge = "titleLarge"
        Display = "display"

    @Overload
    def __init__(self, parent: Optional[QWidget] = None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.setProperty("textStyle", FLabel.TextStyle.Body)

    @__init__.register
    def _(self, text: str, parent: Optional[QWidget] = None, *args, **kwargs) -> None:
        self.__init__(parent=parent, *args, **kwargs)
        self.setText(text)

    @__init__.register
    def _(self, textStyle: TextStyle, parent: Optional[QWidget] = None, *args, **kwargs) -> None:
        self.__init__(parent=parent, *args, **kwargs)
        self.setTextStyle(textStyle)

    @__init__.register
    def _(self, text: str, textStyle: TextStyle, parent: Optional[QWidget] = None, *args, **kwargs) -> None:
        self.__init__(text=text, parent=parent, *args, **kwargs)
        self.setTextStyle(textStyle)

    def textStyle(self) -> TextStyle:
        return self.property("textStyle")

    def setTextStyle(self, textStyle: TextStyle):
        self.setProperty("textStyle", textStyle.value)
        fTheme.update(self)