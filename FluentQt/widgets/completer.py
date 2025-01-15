# coding=utf-8
from qtpy.QtWidgets import QCompleter

from ..common.theme import set_acrylic_round_corners
from .. import fTheme
from ..common import FColors


class FCompleter(QCompleter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init()

    def _init(self):
        self.popup().setStyleSheet("QAbstractItemView {background-color: transparent}")
        self.popup().setObjectName("CompleterPopup")
        fTheme.themeChangedSignal.connect(self.setAcrylic)
        self.setAcrylic()

    def setAcrylic(self):
        set_acrylic_round_corners(self.popup(), FColors.AcrylicFillColorDefault.get())
