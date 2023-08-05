from PyQt5.QtWidgets import QWidget, QLayout
from PyQt5.QtCore import Qt

from .extensions import ContextObjectExt


class Widget(ContextObjectExt, QWidget):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, stylesheet: str = None):
        QWidget.__init__(self, parent)
        ContextObjectExt.__init__(self, parent, name, visible)
        if stylesheet:
            self.setAttribute(Qt.WA_StyledBackground, True)
            self.setStyleSheet(stylesheet)

    async def init(
            self, *,
            layout: QLayout = None
    ) -> 'Widget':
        if layout:
            self.setLayout(layout)
        return self
