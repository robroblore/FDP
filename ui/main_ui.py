import os
import socket
import sys
import threading

from PySide6.QtWidgets import QStackedWidget
from qtpy.QtCore import Property, Qt
from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QFileDialog

from FluentQt import fTheme, Theme
from FluentQt.common.overload import Overload
from FluentQt.widgets import FMainWindow, FPushButton, FLineEdit
from FluentQt.widgets.expander import FExpander
from FluentQt.widgets.label import FLabel
from client import Client
from tools import DataType


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
        self.parent.client.send(DataType.DELETE_FILE, self._file_name)

    def download_file(self):
        file_save_url, _ = QFileDialog.getSaveFileName(self, "Save File", self._file_name)
        if file_save_url:
            self.parent.client.download_file(self._file_name, file_save_url)

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
    def __init__(self, client, parent: 'MainWindow'=None):
        super().__init__(parent)
        self.parent = parent
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
        button = FPushButton("Disconnect", self)
        button.clicked.connect(self.parent.disconnect_client)
        layout.addWidget(button)

        self.client.files_info_received.connect(self.set_files)

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
                    # TODO Use threading for file transfer so app doesnt freeze, make sure only one file at a time is sent
                    self.client.send(DataType.UPLOAD_FILE, str(url.toLocalFile()))
        else:
            event.ignore()

class ConnectingWidget(QWidget):
    def __init__(self, parent:'MainWindow'=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        connecting_label = FLabel("Connecting...", self)
        layout.addWidget(connecting_label, alignment=Qt.AlignmentFlag.AlignCenter)

class LoginWidget(QWidget):
    def __init__(self, parent:'MainWindow'=None):
        super().__init__(parent)

        self.parent = parent

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_label = FLabel("Enter your username", self)
        layout.addWidget(login_label, alignment=Qt.AlignmentFlag.AlignCenter)

        line_edit = FLineEdit(self)
        line_edit.setPlaceholderText("Username")
        line_edit.textChanged.connect(lambda text: setattr(self.parent, "login", text))
        layout.addWidget(line_edit, alignment=Qt.AlignmentFlag.AlignCenter)

        server_ip_label = FLabel("Enter the server IP", self)
        layout.addWidget(server_ip_label, alignment=Qt.AlignmentFlag.AlignCenter)

        server_ip_edit = FLineEdit(socket.gethostbyname(socket.gethostname()), self)
        server_ip_edit.setPlaceholderText("Server IP")
        server_ip_edit.textChanged.connect(lambda text: setattr(self.parent.client, "server_ip", text))
        layout.addWidget(server_ip_edit, alignment=Qt.AlignmentFlag.AlignCenter)

        login_button = FPushButton("Login", self)
        login_button.clicked.connect(lambda: threading.Thread(target=self.parent.connect_client).start())
        layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)

class MainWindow(FMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("File Delivery Protocol")
        self.login = ""
        self.server_ip = socket.gethostbyname(socket.gethostname())

        self.client = Client()

        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        self.connecting = ConnectingWidget(self)
        self.login_widget = LoginWidget(self)
        self.file_list = FileList(self.client, self)

        self.stacked_widget.addWidget(self.connecting)
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.file_list)

        self.stacked_widget.setCurrentIndex(1)


    def connect_client(self):

        self.stacked_widget.setCurrentIndex(0)

        result = self.client.connect_to_server(self.login, self.server_ip)
        if result:
            self.stacked_widget.setCurrentIndex(2)
            self.client.send(DataType.FILES_INFO)
        else:
            self.stacked_widget.setCurrentIndex(1)

    def disconnect_client(self):
        self.client.send(DataType.DISCONNECT)
        self.stacked_widget.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fTheme.set_app(app, Theme.DARK, True)
    main_window = MainWindow()
    main_window.resize(600, 600)
    main_window.show()

    app.exec()
