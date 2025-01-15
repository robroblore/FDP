import sys

from PySide6.QtGui import QPainter, QImage
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

import pywintypes

from FluentQt import fTheme, Theme
from FluentQt.widgets import FMainWindow


class MainWindow(FMainWindow):
    """
    Main application window that holds the Canvas.
    """

    def __init__(self) -> None:
        super().__init__()
        # self.canvas = Canvas(self)
        # self.setCentralWidget(self.canvas)

        self.update_size = False
        self.maximized = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fTheme.set_app(app, Theme.DARK, True)
    main_window = MainWindow()
    main_window.resize(600, 600)
    main_window.show()
    # main_window.canvas.update_size()

    app.exec()
