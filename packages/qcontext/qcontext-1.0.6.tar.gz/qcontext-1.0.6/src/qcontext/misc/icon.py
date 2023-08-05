from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtCore import QSize, QBuffer, QIODevice
# from loguru import logger
import base64
import site
import os

from .size import Size


class Icon:
    IconType = type[QIcon, str, bytes]
    SizeType = type[Size, QSize, tuple[int, int], Ellipsis, None]

    root = os.path.join(site.getsitepackages()[1], 'qcontext', '.assets')
    __icon: QIcon = None
    __size: QSize = None

    def __init__(self, instance: IconType, size: SizeType = None):
        self.icon = instance
        if size:
            self.size = size

    @property
    def icon(self) -> QIcon:
        return self.__icon

    @property
    def size(self) -> QSize:
        return self.__size

    @icon.setter
    def icon(self, instance: IconType) -> None:
        """

        :param instance: QIcon, string filename with already set Icon.root, icon bytes
        :return:
        """
        def from_bytes(icon_bytes: bytes):
            pixmap = QPixmap()
            png = base64.b64encode(icon_bytes).decode('utf-8')
            pixmap.loadFromData(base64.b64decode(png))
            self.__icon = QIcon(pixmap)

        if isinstance(instance, QIcon):  # directly set
            self.__icon = instance
        elif isinstance(instance, str):  # might be `paths` or `str(bytes)`
            if os.path.exists(filepath := os.path.join(os.path.abspath(self.root), instance)):
                self.__icon = QIcon(filepath)
            else:
                try:  # handle `eval(intance)` for case if instance is invalid `path`
                    if isinstance((icon_bytes := eval(instance)), bytes):
                        from_bytes(icon_bytes)
                except Exception:
                    self.__icon = QIcon()
                    # logger.warning(f'{instance=} is invalid path')
        elif isinstance(instance, bytes):
            from_bytes(instance)
        else:
            self.__icon = QIcon()
            # logger.warning(f'unknown type ({type(instance)}) of instance ({instance}), can not set Icon.icon')
        self.icon.addPixmap(self.__icon.pixmap(1000), mode=QIcon.Disabled)  # fix of `QPushButton.setDisabled()`

    @size.setter
    def size(self, size: SizeType) -> None:
        """

        :param size: QSize, qcontextapi.Size, tuple[int, int]
        :return:
        """
        if isinstance(size, tuple):
            self.__size = QSize(*size)
        elif isinstance(size, Size):
            self.__size = QSize(*size.size)
        elif isinstance(size, QSize):
            self.__size = size
        else:
            raise AttributeError(f'unknown type ({type(size)}) of size ({size}), can not set Icon.size')

    def adjusted(self, icon: IconType = None, size: SizeType = None) -> 'Icon':
        # if not icon and not size:
        #     logger.warning('Icon.adjusted() called without parameters. Redundant call.')
        if icon:
            self.icon = icon
        if size:
            self.size = size
        return self

    @staticmethod
    def bytes(icon: IconType, size: SizeType = None) -> bytes:
        icon = Icon(icon, size)
        # image = QImage(icon.icon.pixmap(icon.size).toImage())
        image = QImage(icon.icon.pixmap(QSize(512, 512)).toImage())
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, 'JPG')
        image_bytes = buffer.data()
        buffer.close()
        return image_bytes
