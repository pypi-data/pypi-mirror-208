from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt

from ..button import Button
from ..label import Label
from ..layout import Layout
from ...misc import Icon


class MenuButton(Button):
    def __init__(self, parent: QWidget, name: str = None, visible: bool = True):
        super().__init__(parent, name if name else self.__class__.__name__, visible)

    async def init(
            self, *,
            icon: Icon, text: str, total: int = 0, alignment: Qt.Alignment = None, slot: callable = None
    ) -> 'MenuButton':
        self.setLayout(await Layout.horizontal().init(
            margins=(10, 5, 10, 5), spacing=10,
            items=[
                icon_btn := await Button(self, f'{self.objectName()}IconBtn').init(
                    size=icon.size, icon=icon, disabled=True
                ), Layout.Left,
                text_lbl := await Label(self, f'{self.objectName()}TextLbl').init(
                    text=text, alignment=alignment, elided=True, policy=(QSizePolicy.Expanding, QSizePolicy.Minimum)
                ),
                total_lbl := await Label(self, f'{self.objectName()}TotalLbl').init(
                    text=str(total)
                ), Layout.Right
            ]
        ))
        self.icon_btn = icon_btn
        self.text_lbl = text_lbl
        self.total_lbl = total_lbl
        if slot:
            self.clicked.connect(slot)
        return self
