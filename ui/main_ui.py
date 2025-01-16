import os
import sys

from qtpy.QtCore import Property, Qt
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QFileDialog

import pywintypes

from FluentQt import fTheme, Theme
from FluentQt.common.overload import Overload
from FluentQt.widgets import FMainWindow, FPushButton
from FluentQt.widgets.expander import FExpander
from main import DataType


class FileWidget(FExpander):
    def __init__(self, file_data: dict, widget_id: int, parent: 'FileList', *args, **kwargs):
        super().__init__(*args, **kwargs, parent=parent)
        self.parent = parent

        self._file_name = ""
        self._file_size = ""
        self.update_data(file_data)
        self._widget_id = widget_id

        self.setExpandDirection(FExpander.ExpandDirection.NONE)

        button = FPushButton("Delete", self)
        self.headerLayout().addWidget(button)
        button.clicked.connect(self.delete_file)

        button = FPushButton("Download", self)
        self.headerLayout().addWidget(button)
        button.clicked.connect(self.download_file)

    def update_data(self, file_data: dict):
        self._file_name = file_data["file_name"]
        self.setTitle(self._file_name)

        self._file_size = file_data["file_size"]
        self.setSubtitle(f"{self._file_size} bytes")

    def delete_file(self):
        # TODO Send delete file command to server

        # TODO Testing code
        self.parent.delete_file(self._widget_id)

    def download_file(self):
        # TODO Send download file command to server

        file_save_url, _ = QFileDialog.getSaveFileName(self, "Save File", self._file_name)
        print(file_save_url)



    WidgetId = Property(int, lambda self: self._widget_id)

"""
files_data:

[
    {
        file_name: str,
        file_size: int
    }
]
"""

class FileList(QWidget):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self._files_data: list = []
        self._file_widgets: list[FileWidget] = []
        self._highest_file_id = 0

        self.setAcceptDrops(True)

        # Layout
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.scroll_content = QWidget(scroll_area)
        self.scroll_content.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed))
        scroll_area.setWidget(self.scroll_content)

        self.layout = QVBoxLayout(self.scroll_content)

        # TODO Testing code
        button = FPushButton("Add File", self)
        self.layout.addWidget(button)
        button.clicked.connect(lambda: self.add_file({
            "file_name": "test2.txt",
            "file_size": 300
        }))

    def set_files(self, files: list):
        self._files_data = files
        self.update_data()

    def update_data(self):
        for i, file_data in enumerate(self._files_data):
            if i > len(self._file_widgets)-1:
                self.add_widget(file_data)
            else:
                self._file_widgets[i].update_data(file_data)

        data_len = len(self._files_data)
        widget_num = len(self._file_widgets)
        for i in range(data_len, widget_num):
            self.delete_widget(i)

    def add_widget(self, file_data: dict):
        self._highest_file_id += 1
        file_widget = FileWidget(file_data, self._highest_file_id, self)
        self._file_widgets.append(file_widget)
        self.layout.addWidget(file_widget)
        self.scroll_content.adjustSize()

    def delete_widget(self, index: int):
        file_widget = self._file_widgets.pop(index)
        self.layout.removeWidget(file_widget)
        file_widget.deleteLater()
        self.scroll_content.adjustSize()

    def add_file(self, file_data: dict):
        self._files_data.append(file_data)
        self.update_data()

    @Overload
    def delete_file(self, file_name: str) -> None:
        if file_name is not None:
            for i, file_data in enumerate(self._files_data):
                if file_data["file_name"] == file_name:
                    self._files_data.pop(i)
                    self.update_data()
                    break

    @delete_file.register
    def _(self, widget_id: int) -> None:
        if widget_id is not None:
            for i, file_widget in enumerate(self._file_widgets):
                if file_widget.WidgetId == widget_id:
                    self._files_data.pop(i)
                    self.update_data()
                    break

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

            for url in event.mimeData().urls():
                if self.client is not None:
                    self.client.send(DataType.FILE, str(url.toLocalFile()))

                # TODO Testing code
                self.add_file({
                    "file_name": os.path.basename(str(url.toLocalFile())),
                    "file_size": os.path.getsize(str(url.toLocalFile()))
                })
        else:
            event.ignore()


class MainWindow(FMainWindow):
    def __init__(self, client) -> None:
        super().__init__()
        self.setWindowTitle("File Delivery Protocol")

        file_list = FileList(client, self)
        self.setCentralWidget(file_list)

        # TODO Testing code
        file_list.set_files([
            {
                "file_name": "test0.txt",
                "file_size": 100
            },
            {
                "file_name": "test1.txt",
                "file_size": 200
            }
        ])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fTheme.set_app(app, Theme.DARK, True)
    main_window = MainWindow(None)
    main_window.resize(600, 600)
    main_window.show()

    app.exec()
