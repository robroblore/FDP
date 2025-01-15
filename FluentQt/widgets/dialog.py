# coding=utf-8
from typing import Union, Optional

import winsound
from qtpy.QtCore import QCoreApplication, QSize, Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QDialogButtonBox, QWidget, QHBoxLayout, QLabel, QDialog, QVBoxLayout, QLayout, QLayoutItem

from .button import FPushButton
from .frame import FFrame
from .. import fTheme


def warning_retrycancel(parent: QWidget, title: str, text: Optional[str] = None, icon: bool = True,
                        sound: Optional[int] = winsound.MB_OK, accent: Optional[Union[int, bool]] = None) -> int:
    """
    Shows a warning with a retry and a cancel button.

    :param parent: the window to display the dialog onto.
    :param title: the title the dialog should have.
    :param text: the text to display under the title.
    :param icon: if the dialog should have an icon or not.
    :param sound: the sound winsound id to use for the notification sound. If null no sound is played.
    :return: the integer referring to the role pressed. See list below.
    """

    dialog = FDialog(parent, title, text, [["msc.warning", None]] if icon else None,
                     (QCoreApplication.translate("Dialog", "Retry"), QDialogButtonBox.ButtonRole.AcceptRole, "accent" if accent == 1 or accent is True else None),
                     (QCoreApplication.translate("Dialog", "Cancel"), QDialogButtonBox.ButtonRole.RejectRole, "accent" if accent == 2 else None))
    dialog.show()
    if sound:
        winsound.MessageBeep(sound)
    return dialog.exec()


def ask_okcancel(parent: QWidget, title: str, text: Optional[str] = None, icon: bool = True,
                 sound: Optional[int] = winsound.MB_OK, accent: Optional[Union[int, bool]] = None) -> int:
    """
    Ask the user with an ok button and a cancel button.

    :param parent: the window to display the dialog onto.
    :param title: the title the dialog should have.
    :param text: the text to display under the title.
    :param icon: if the dialog should have an icon or not.
    :param sound: the sound winsound id to use for the notification sound. If null no sound is played.
    :return: the integer referring to the role pressed. See list below.
    """

    dialog = FDialog(parent, title, text, [["msc.question", None]] if icon else None,
                     (QCoreApplication.translate("Dialog", "OK"), QDialogButtonBox.ButtonRole.AcceptRole, "accent" if accent == 1 or accent is True else None),
                     (QCoreApplication.translate("Dialog", "Cancel"), QDialogButtonBox.ButtonRole.RejectRole, "accent" if accent == 2 else None))
    dialog.show()
    if sound:
        winsound.MessageBeep(sound)
    return dialog.exec()


def ask_yesno(parent: QWidget, title: str, text: Optional[str] = None, icon: bool = True,
              sound: Optional[int] = winsound.MB_OK, accent: Optional[Union[int, bool]] = None) -> int:
    """
    Ask the user with a yes button and a no button.

    :param parent: the window to display the dialog onto.
    :param title: the title the dialog should have.
    :param text: the text to display under the title.
    :param icon: if the dialog should have an icon or not.
    :param sound: the sound winsound id to use for the notification sound. If null no sound is played.
    :return: the integer referring to the role pressed. See list below.
    """

    dialog = FDialog(parent, title, text, [["msc.question", None]] if icon else None,
                     (QCoreApplication.translate("Dialog", "Yes"), QDialogButtonBox.ButtonRole.YesRole, "accent" if accent == 1 or accent is True else None),
                     (QCoreApplication.translate("Dialog", "No"), QDialogButtonBox.ButtonRole.NoRole, "accent" if accent == 2 else None))
    dialog.show()
    if sound:
        winsound.MessageBeep(sound)
    return dialog.exec()


def ask_yesnocancel(parent: QWidget, title: str, text: Optional[str] = None, icon: bool = True,
                    sound: Optional[int] = winsound.MB_OK, accent: Optional[Union[int, bool]] = None) -> int:
    """
    Ask the user with a yes button, a no button and a cancel button.

    :param parent: the window to display the dialog onto.
    :param title: the title the dialog should have.
    :param text: the text to display under the title.
    :param icon: if the dialog should have an icon or not.
    :param sound: the sound winsound id to use for the notification sound. If null no sound is played.
    :return: the integer referring to the role pressed. See list below.
    """

    dialog = FDialog(parent, title, text, [["msc.question", None]] if icon else None,
                     (QCoreApplication.translate("Dialog", "Yes"), QDialogButtonBox.ButtonRole.YesRole, "accent" if accent == 1 or accent is True else None),
                     (QCoreApplication.translate("Dialog", "No"), QDialogButtonBox.ButtonRole.NoRole, "accent" if accent == 2 else None),
                     (QCoreApplication.translate("Dialog", "Cancel"), QDialogButtonBox.ButtonRole.RejectRole, "accent" if accent == 3 else None))
    dialog.show()
    if sound:
        winsound.MessageBeep(sound)
    return dialog.exec()


def warning_yescancel(parent: QWidget, title: str, text: Optional[str] = None, icon: bool = True,
                      sound: Optional[int] = winsound.MB_OK, accent: Optional[Union[int, bool]] = None) -> int:
    """
    Ask the user with a yes button, a no button and a cancel button.

    :param parent: the window to display the dialog onto.
    :param title: the title the dialog should have.
    :param text: the text to display under the title.
    :param icon: if the dialog should have an icon or not.
    :param sound: the sound winsound id to use for the notification sound. If null no sound is played.
    :return: the integer referring to the role pressed. See list below.
    """

    dialog = FDialog(parent, title, text, [["msc.warning", None]] if icon else None,
                     (QCoreApplication.translate("Dialog", "Yes"), QDialogButtonBox.ButtonRole.YesRole, "accent" if accent == 1 or accent is True else None),
                     (QCoreApplication.translate("Dialog", "Cancel"), QDialogButtonBox.ButtonRole.RejectRole, "accent" if accent == 2 else None))
    dialog.show()
    if sound:
        winsound.MessageBeep(sound)
    return dialog.exec()


def show_error(parent: QWidget, title: str, text: Optional[str] = None, icon: bool = True,
               sound: Optional[int] = winsound.MB_ICONHAND, accent: Optional[Union[int, bool]] = None) -> int:
    """
    Shows an error with the ok button.

    :param parent: the window to display the dialog onto.
    :param title: the title the dialog should have.
    :param text: the text to display under the title.
    :param icon: if the dialog should have an icon or not.
    :param sound: the sound winsound id to use for the notification sound. If null no sound is played.
    :return: the integer referring to the role pressed. See list below.
    """

    dialog = FDialog(parent, title, text, [["msc.error", None]] if icon else None,
                     (QCoreApplication.translate("Dialog", "OK"), QDialogButtonBox.ButtonRole.AcceptRole, "accent" if accent == 1 or accent is True else None))
    dialog.show()
    if sound:
        winsound.MessageBeep(sound)
    return dialog.exec()


def show_warning(parent: QWidget, title: str, text: Optional[str] = None, icon: bool = True,
                 sound: Optional[int] = winsound.MB_OK, accent: Optional[Union[int, bool]] = None) -> int:
    """
    Shows a warning with the ok button.

    :param parent: the window to display the dialog onto.
    :param title: the title the dialog should have.
    :param text: the text to display under the title.
    :param icon: if the dialog should have an icon or not.
    :param sound: the sound winsound id to use for the notification sound. If null no sound is played.
    :return: the integer referring to the role pressed. See list below.
    """

    dialog = FDialog(parent, title, text, [["msc.warning", None]] if icon else None,
                     (QCoreApplication.translate("Dialog", "OK"), QDialogButtonBox.ButtonRole.AcceptRole, "accent" if accent == 1 or accent is True else None))
    dialog.show()
    if sound:
        winsound.MessageBeep(sound)
    return dialog.exec()


def show_info(parent: QWidget, title: str, text: Optional[str] = None, icon: bool = True,
              sound: Optional[int] = winsound.MB_OK, accent: Optional[Union[int, bool]] = None) -> int:
    """
    Shows an info with the ok button.

    :param parent: the window to display the dialog onto.
    :param title: the title the dialog should have.
    :param text: the text to display under the title.
    :param icon: if the dialog should have an icon or not.
    :param sound: the sound winsound id to use for the notification sound. If null no sound is played.
    :return: the integer referring to the role pressed. See list below.
    """

    dialog = FDialog(parent, title, text, [["msc.info", None]] if icon else None,
                     (QCoreApplication.translate("Dialog", "OK"), QDialogButtonBox.ButtonRole.AcceptRole, "accent" if accent == 1 or accent is True else None))
    dialog.show()
    if sound:
        winsound.MessageBeep(sound)
    return dialog.exec()


def _role_to_int(role: QDialogButtonBox.ButtonRole) -> int:
    match role:
        case QDialogButtonBox.ButtonRole.InvalidRole:
            return -1
        case QDialogButtonBox.ButtonRole.RejectRole:  #
            return 0                                  # AcceptRole and RejectRole inverted
        case QDialogButtonBox.ButtonRole.AcceptRole:  # to match QDialog output when pressing escape
            return 1                                  #
        case QDialogButtonBox.ButtonRole.DestructiveRole:
            return 2
        case QDialogButtonBox.ButtonRole.ActionRole:
            return 3
        case QDialogButtonBox.ButtonRole.HelpRole:
            return 4
        case QDialogButtonBox.ButtonRole.YesRole:
            return 5
        case QDialogButtonBox.ButtonRole.NoRole:
            return 6
        case QDialogButtonBox.ButtonRole.ResetRole:
            return 7
        case QDialogButtonBox.ButtonRole.ApplyRole:
            return 7


class _IconLabel(QWidget):
    IconSize = QSize(48, 48)
    HorizontalSpacing = 2

    def __init__(self, icon: list[list[str, Optional[str]]], text: Optional[str] = None, final_stretch: bool = True) -> None:
        import qtawesome
        super().__init__()

        self.icon = icon

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.icon_label = QLabel()
        self.change_theme()
        layout.addWidget(self.icon_label)

        fTheme.themeChangedSignal.connect(self.change_theme)

        if text:
            layout.addSpacing(self.HorizontalSpacing)
            label = QLabel(text)
            label.setObjectName("subtitle")
            layout.addWidget(label)

        if final_stretch:
            layout.addStretch()

    def change_theme(self):
        icon_names = []
        icon_options = []
        for icon in self.icon:
            options = icon[1]
            if not icon[1]:
                options = {"color": "white" if fTheme.isDark() else QColor(0, 0, 0, 227)}
            elif "color" not in icon[1]:
                options = {**icon[1], **{"color": "white" if fTheme.actual_dark_theme else QColor(0, 0, 0, 227)}}
            icon_names.append(icon[0])
            icon_options.append(options)
        self.icon_label.setPixmap(qtawesome.icon(*icon_names, options=icon_options).pixmap(self.IconSize))


# Todo explain "accent" and icon
class FDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, text: Optional[str] = None, icon: list[list[str, Optional[str]]] = None,
                 *buttons: Union[tuple[Union[FPushButton,  str], QDialogButtonBox.ButtonRole], tuple[Union[FPushButton,  str], QDialogButtonBox.ButtonRole, Optional[str]]]) -> None:
        """
        Make a dialog with the fluent theme.

        :param parent: the window to display the dialog onto.
        :param title: the title the dialog should have.
        :param icon: the icon used in the title. Must be an icon from qtawesome. If null, no icon will be used.
        :param text: the text to display under the title.
        :param buttons: the buttons for the dialog. Must be a tuple with a QPushButton or the text of it,
        a QDialogButtonBox.ButtonRole and the ObjectName the button should have (can be null).
        """
        super().__init__(parent)
        self.reject_on_esc = True

        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._dialog_frame = FDialogFrame(self, FFrame.Opacity.TRANSPARENT)
        self.set_size_limit()
        self._dialog_frame.setBaseSize(QSize(320, 160))

        self._layout_2 = QVBoxLayout(self._dialog_frame)
        self._layout_2.setSpacing(0)
        self._layout_2.setContentsMargins(0, 0, 0, 0)

        self._dialog_groupBox = FDialogContentFrame(self._dialog_frame, FFrame.Opacity.TRANSPARENT)

        self._layout_3 = QVBoxLayout(self._dialog_groupBox)
        self._layout_3.setSpacing(0)
        self._layout_3.setContentsMargins(24, 28, 24, 25)

        # User modifiable widgets
        #########################################################

        self.title_frame = FFrame(self._dialog_groupBox, FFrame.Opacity.TRANSPARENT)

        self.dialog_title_widgets = QVBoxLayout(self.title_frame)
        self.dialog_title_widgets.setSpacing(0)
        self.dialog_title_widgets.setContentsMargins(0, 0, 0, 0)

        if icon:
            self.dialog_title = _IconLabel(icon, title)
            self.dialog_title_widgets.addWidget(self.dialog_title)
        else:
            self.dialog_title = QLabel(self.title_frame)
            self.dialog_title.setText(title)
            self.dialog_title.setObjectName("subtitle")
            self.dialog_title_widgets.addWidget(self.dialog_title)


        self.widgets_frame = FFrame(self._dialog_groupBox, FFrame.Opacity.TRANSPARENT)

        self.dialog_content_widgets = None

        if text:
            self.dialog_text = QLabel(self.widgets_frame)
            self.dialog_text.setText(text)
            self.dialog_text.setWordWrap(True)
            self.add_content_widgets(self.dialog_text)

        ############################################################

        self._button_frame = FDialogButtonFrame(self._dialog_frame, FFrame.Opacity.TRANSPARENT)
        self._button_frame.setMaximumSize(QSize(16777215, 80))

        self._layout_4 = QHBoxLayout(self._button_frame)
        self._layout_4.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self._layout_4.setContentsMargins(24, 24, 22, 24)

        def press(_button):
            _button.press = True

        self.buttons = []
        for button in buttons:
            widget = button[0]
            if isinstance(widget, str):
                widget = FPushButton(text=widget)

            self._layout_4.addWidget(widget)

            if len(button) > 2 and button[2]:
                widget.setObjectName(button[2])
                if button[2] == "accent":
                    widget.setFocus()

            # memory leak
            # widget.clicked.connect(lambda state=None, b=button[1]: self.done(_role_to_int(b)))

            # to prevent the leak
            widget.press = False
            widget.role = button[1]

            widget.clicked.connect(lambda state=None, b=widget: press(b))
            widget.clicked.connect(self.clicked)

            self.buttons.append(widget)

        self._layout_3.addWidget(self.title_frame)
        self._layout_3.addWidget(self.widgets_frame)
        self._layout_2.addWidget(self._dialog_groupBox)
        self._layout_2.addWidget(self._button_frame)
        self._layout.addWidget(self._dialog_frame)

        self.setLayout(self._layout)
        print("made")

    def __del__(self):
        print("del")

    def clicked(self):
        for button in self.buttons:
            if button.press:
                button.press = False
                self.done(_role_to_int(button.role))

    def add_content_widgets(self, *widgets: QWidget | QLayoutItem) -> None:
        if not self.dialog_content_widgets:
            self.dialog_content_widgets = QVBoxLayout(self.widgets_frame)
            self.dialog_content_widgets.setSpacing(7)
            self.dialog_content_widgets.setContentsMargins(0, 16, 0, 0)

        for widget in widgets:
            try:
                widget.setParent(self.widgets_frame)
                self.dialog_content_widgets.addWidget(widget)
            except AttributeError:
                self.dialog_content_widgets.addItem(widget)

    def set_size_limit(self, min_size: QSize | None = QSize(320, 160), max_size: QSize | None = QSize(548, 756)):
        self._dialog_frame.setMinimumSize(min_size if min_size else QSize(0, 0))
        self._dialog_frame.setMaximumSize(max_size if max_size else QSize(16777215, 16777215))

    def reject(self) -> None:
        if self.reject_on_esc:
            super().reject()

    def show(self) -> None:
        self.activateWindow()
        super().show()


class FDialogFrame(FFrame):
    pass


class FDialogContentFrame(FFrame):
    pass


class FDialogButtonFrame(FFrame):
    pass
