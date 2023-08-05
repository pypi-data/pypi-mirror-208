from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from contextlib import suppress
from qasync import asyncSlot

from ..button import Button
from ..popup import Popup
from ...misc import Icon


class ImageButton(Button):
    def __init__(self, parent: QWidget, name: str = None, visible: bool = True):
        super().__init__(parent, name if name else self.__class__.__name__, visible)
        self.image_bytes = None

    async def init(
            self, *,
            icon: Icon, slot: callable = lambda: None, directory: str = ''
    ) -> 'ImageButton':
        await super().init(icon=icon, slot=lambda: self.choose_image(slot, directory))
        self.RemoveImageBtn = await Button(self, f'{self.objectName()}RemoveImageBtn').init(
            icon=Icon('x-circle.svg', (30, 30)), size=QSize(30, 30),
            slot=lambda: Popup(self.core).display(
                message=f'Remove icon?',
                on_success=self.remove_icon
            )
        )
        self.RemoveImageBtn.move(self.width() - 30, 0)
        self.RemoveImageBtn.setStyleSheet(f'''
            #{self.objectName()}RemoveImageBtn {{background-color: transparent; border-radius: 14px;}}
            #{self.objectName()}RemoveImageBtn:hover {{background-color: rgba(255, 255, 255, 0.3);}}
        ''')
        return self

    @property
    def image_bytes_str(self) -> str | None:
        return str(self.image_bytes) if self.image_bytes else None

    def remove_icon(self):
        super().setIcon(QIcon())
        self.image_bytes = None
        with suppress(AttributeError):
            self.RemoveImageBtn.setVisible(False)

    def setIcon(self, icon: QIcon) -> None:
        self.image_bytes = Icon.bytes(icon, self.iconSize())
        super().setIcon(icon)
        with suppress(AttributeError):
            self.RemoveImageBtn.setVisible(True)

    def setDisabled(self, disabled: bool) -> None:
        with suppress(AttributeError):
            self.RemoveImageBtn.setVisible(not disabled)
        super().setDisabled(disabled)

    def setEnabled(self, enabled: bool) -> None:
        with suppress(AttributeError):
            self.RemoveImageBtn.setVisible(enabled)
        super().setEnabled(enabled)

    @asyncSlot()
    async def choose_image(self, slot: callable = lambda: None, directory: str = ''):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Choose image', directory, 'Images (*.jpg)')
        if filepath:
            with open(filepath, 'rb') as file:
                self.setIcon(Icon(file.read()).icon)
            slot()
