# coding: utf-8
from typing import Optional

from qtpy.QtWidgets import QCheckBox, QWidget

from ..common.overload import Overload


class FCheckBox(QCheckBox):
    @Overload
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

    @__init__.register
    def _(self, text: str, parent: Optional[QWidget] = None):
        self.__init__(parent=parent)
        self.setText(text)
