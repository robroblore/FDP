import os
import sys

from qtpy.QtCore import Property, Qt
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QSizePolicy

import pywintypes

from FluentQt import fTheme, Theme
from FluentQt.widgets import FMainWindow, FPushButton
from FluentQt.widgets.expander import FExpander

class FileWidget(FExpander):
    def __init__(self, filename: str, parent: 'FileList', *args, **kwargs):
        super().__init__(*args, **kwargs, parent=parent)

        self._filename = filename
        self.FileName = filename

        self.setExpandDirection(FExpander.ExpandDirection.NONE)

        button = FPushButton("Remove", self)
        self.headerLayout().addWidget(button)
        button.clicked.connect(lambda: parent.RemoveFile(filename))

    def get_filename(self):
        return self._filename

    def set_filename(self, filename: str):
        self._filename = filename
        self.setTitle(filename)

    FileName = Property(str, get_filename, set_filename)


class FileList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.files = {}

        layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.scroll_content = QWidget(scroll_area)
        self.scroll_content.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed))
        scroll_area.setWidget(self.scroll_content)

        self.layout = QVBoxLayout(self.scroll_content)
        button = FPushButton("Add File", self)
        self.layout.addWidget(button)
        button.clicked.connect(lambda: self.AddFile(f"test{len(self.files)}.txt"))

    def AddFile(self, filename: str):
        if filename in self.files:
            return
        file_widget = FileWidget(filename, self)
        self.files[filename] = file_widget
        self.layout.addWidget(file_widget)
        self.scroll_content.adjustSize()

    def RemoveFile(self, filename: str):
        file_widget = self.files[filename]
        self.files.pop(filename)
        self.layout.removeWidget(file_widget)
        file_widget.deleteLater()
        self.scroll_content.adjustSize()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls and all([os.path.exists(url.toLocalFile()) for url in event.mimeData().urls()]):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls and all([os.path.exists(url.toLocalFile()) for url in event.mimeData().urls()]):
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls and all([os.path.exists(url.toLocalFile()) for url in event.mimeData().urls()]):
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
                self.AddFile(str(url.toLocalFile()))
            print(links)
            # self.fileDropped.emit(links)
        else:
            event.ignore()


class MainWindow(FMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("File Delivery Protocol")

        file_list = FileList(self)
        self.setCentralWidget(file_list)

        file_list.AddFile("test0.txt")
        file_list.AddFile("test1.txt")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fTheme.set_app(app, Theme.DARK, True)
    main_window = MainWindow()
    main_window.resize(600, 600)
    main_window.show()

    app.exec()
