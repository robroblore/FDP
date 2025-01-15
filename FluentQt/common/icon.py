# coding:utf-8
from enum import Enum
from typing import Union

from qtpy.QtSvg import QSvgRenderer
from qtpy.QtXml import QDomDocument
from qtpy.QtCore import QRectF, QFile, QRect, QPoint, QSize, Qt, QObject
from qtpy.QtGui import QIcon, QFont, QPen, QColor, QPixmap, QPainter, QIconEngine, QAction

from .overload import Overload
from .theme import fTheme

from .. import FColors


class MenuIconEngine(QIconEngine):
    def __init__(self, icon):
        super().__init__()
        self.icon = icon

    def paint(self, painter, rect, mode, state):
        painter.save()

        if mode == QIcon.Disabled:
            painter.setOpacity(0.5)
        elif mode == QIcon.Selected:
            painter.setOpacity(0.7)

        # change icon color according to the theme
        icon = self.icon
        if isinstance(self.icon, Icon):
            icon = self.icon.fluentIcon.icon()

        # prevent the left side of the icon from being cropped
        rect.adjust(-1, 0, 0, 0)

        icon.paint(painter, rect, Qt.AlignHCenter, QIcon.Normal, state)
        painter.restore()


def getIconColor(reverse=False):
    """ get the color of icon based on theme """
    if not reverse:
        lc, dc = "black", "white"
    else:
        lc, dc = "white", "black"

    color = dc if fTheme.isDark() else lc

    return color


def drawSvgIcon(icon, painter, rect):
    """ draw svg icon

    Parameters
    ----------
    icon: str | bytes | QByteArray
        the path or code of svg icon

    painter: QPainter
        painter

    rect: QRect | QRectF
        the rect to render icon
    """
    renderer = QSvgRenderer(icon)
    renderer.render(painter, QRectF(rect))


def writeSvg(iconPath: str, indexes=None, **attributes):
    """ write svg with specified attributes

    Parameters
    ----------
    iconPath: str
        svg icon path

    indexes: List[int]
        the path to be filled

    **attributes:
        the attributes of path

    Returns
    -------
    svg: str
        svg code
    """
    if not iconPath.lower().endswith('.svg'):
        return ""

    f = QFile(iconPath)
    f.open(QFile.OpenModeFlag.ReadOnly)

    dom = QDomDocument()
    dom.setContent(f.readAll())

    f.close()

    # change the color of each path
    pathNodes = dom.elementsByTagName('path')
    indexes = range(pathNodes.length()) if not indexes else indexes
    for i in indexes:
        element = pathNodes.at(i).toElement()

        for k, v in attributes.items():
            element.setAttribute(k, v)

    return dom.toString()


def drawIcon(icon, painter, rect, **attributes):
    """ draw icon

    Parameters
    ----------
    icon: str | QIcon | FluentIconBaseBase
        the icon to be drawn

    painter: QPainter
        painter

    rect: QRect | QRectF
        the rect to render icon

    **attribute:
        the attribute of svg icon
    """
    if isinstance(icon, FIconBase):
        icon.render(painter, rect, **attributes)
    else:
        icon = QIcon(icon)
        rect = QRectF(rect).toRect()
        image = icon.pixmap(rect.width(), rect.height())
        painter.drawPixmap(rect, image)


class FIconBase:
    """ Fluent icon base class """

    def path(self):
        """ get the path of icon """
        raise NotImplementedError

    def icon(self):
        """ create an fluent icon """
        return QIcon(self.path())

    def render(self, painter, rect, indexes=None, **attributes):
        """ draw svg icon

        Parameters
        ----------
        painter: QPainter
            painter

        rect: QRect | QRectF
            the rect to render icon

        indexes: List[int]
            the svg path to be modified

        **attributes:
            the attributes of modified path
        """
        if attributes:
            svg = writeSvg(self.path(), indexes, **attributes).encode()
        else:
            svg = self.path()

        drawSvgIcon(svg, painter, rect)


class FIcon(FIconBase, Enum):
    """ Fluent icon """

    ADD = "Add"
    CUT = "Cut"
    PIN = "Pin"
    TAG = "Tag"
    CHAT = "Chat"
    COPY = "Copy"
    CODE = "Code"
    EDIT = "Edit"
    FONT = "Font"
    HELP = "Help"
    HIDE = "Hide"
    HOME = "Home"
    INFO = "Info"
    LINK = "Link"
    MAIL = "Mail"
    MENU = "Menu"
    MORE = "More"
    SAVE = "Save"
    SEND = "Send"
    SYNC = "Sync"
    VIEW = "View"
    ZOOM = "Zoom"
    ALBUM = "Album"
    BRUSH = "Brush"
    CLOSE = "Close"
    EMBED = "Embed"
    GLOBE = "Globe"
    HEART = "Heart"
    MEDIA = "Media"
    MOVIE = "Movie"
    MUSIC = "Music"
    PASTE = "Paste"
    PHOTO = "Photo"
    PHONE = "Phone"
    PRINT = "Print"
    SHARE = "Share"
    UNPIN = "Unpin"
    VIDEO = "Video"
    ACCEPT = "Accept"
    CAMERA = "Camera"
    CANCEL = "Cancel"
    DELETE = "Delete"
    FOLDER = "Folder"
    SCROLL = "Scroll"
    LAYOUT = "Layout"
    GITHUB = "GitHub"
    UPDATE = "Update"
    RETURN = "Return"
    RINGER = "Ringer"
    SEARCH = "Search"
    SAVE_AS = "SaveAs"
    ZOOM_IN = "ZoomIn"
    HISTORY = "History"
    SETTING = "Setting"
    PALETTE = "Palette"
    MESSAGE = "Message"
    ZOOM_OUT = "ZoomOut"
    FEEDBACK = "Feedback"
    MINIMIZE = "Minimize"
    CHECKBOX = "CheckBox"
    DOCUMENT = "Document"
    LANGUAGE = "Language"
    DOWNLOAD = "Download"
    QUESTION = "Question"
    DATE_TIME = "DateTime"
    SEND_FILL = "SendFill"
    COMPLETED = "Completed"
    CONSTRACT = "Constract"
    ALIGNMENT = "Alignment"
    BOOK_SHELF = "BookShelf"
    HIGHTLIGHT = "Highlight"
    FOLDER_ADD = "FolderAdd"
    PENCIL_INK = "PencilInk"
    ZIP_FOLDER = "ZipFolder"
    BASKETBALL = "Basketball"
    MICROPHONE = "Microphone"
    ARROW_DOWN = "ChevronDown"
    TRANSPARENT = "Transparent"
    MUSIC_FOLDER = "MusicFolder"
    CARE_UP_SOLID = "CareUpSolid"
    CHEVRON_RIGHT = "ChevronRight"
    CARE_DOWN_SOLID = "CareDownSolid"
    CARE_LEFT_SOLID = "CareLeftSolid"
    BACKGROUND_FILL = "BackgroundColor"
    CARE_RIGHT_SOLID = "CareRightSolid"

    def path(self):
        return f':/qfluentwidgets/images/icons/{self.value}_{getIconColor()}.svg'


class FFontIcon(FIconBase):
    def __init__(self, code: str, family: str = None):
        self.code = code
        self.family = family if family else fTheme.icon_font_family

    def path(self):
        pass

    def icon(self):
        pix = QPixmap(16, 16)
        pix.fill(Qt.GlobalColor.transparent)

        self.render(QPainter(pix), QRect(QPoint(0, 0), QSize(16, 16)))
        return QIcon(pix)

    def render(self, painter, rect, indexes=None, **attributes):
        font = QFont(self.family)
        font.setPixelSize(round(rect.height()))

        pen_color = FColors.SystemBaseHighColor.getColor()
        if "fill" in attributes:
            color = QColor(attributes["fill"])
            if "opacity" in attributes:
                color.setAlphaF(attributes["opacity"])
            pen_color = color

        painter.setPen(QPen(pen_color))
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self.code)


class Icon(QIcon):

    def __init__(self, fluentIcon: FIcon):
        super().__init__(fluentIcon.path())
        self.fluentIcon = fluentIcon


class Action(QAction):
    """ Fluent action """

    @Overload
    def __init__(self, parent: QObject = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.fluentIcon = None

    @__init__.register
    def _(self, text: str, parent: QObject = None, **kwargs):
        super().__init__(text, parent, **kwargs)
        self.fluentIcon = None

    @__init__.register
    def _(self, icon: QIcon, text: str, parent: QObject = None, **kwargs):
        super().__init__(icon, text, parent, **kwargs)
        self.fluentIcon = None

    @__init__.register
    def _(self, icon: FIcon, text: str, parent: QObject = None, **kwargs):
        super().__init__(icon.icon(), text, parent, **kwargs)
        self.fluentIcon = icon

    def icon(self) -> QIcon:
        if self.fluentIcon:
            return Icon(self.fluentIcon)

        return super().icon()

    def setIcon(self, icon: Union[FIcon, QIcon]):
        if isinstance(icon, FIcon):
            self.fluentIcon = icon
            icon = icon.icon()

        super().setIcon(icon)
