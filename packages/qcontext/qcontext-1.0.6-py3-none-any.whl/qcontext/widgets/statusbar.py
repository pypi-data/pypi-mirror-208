from PyQt5.QtWidgets import QStatusBar, QWidget

from .extensions import ContextObjectExt


class StatusBar(ContextObjectExt, QStatusBar):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QStatusBar.__init__(self, parent)
        ContextObjectExt.__init__(self, parent, name, visible)

    async def init(self) -> 'StatusBar':
        return self
