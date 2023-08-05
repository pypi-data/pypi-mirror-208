from PyQt5.QtWidgets import QFrame, QWidget, QLayout, QSizePolicy

from .extensions import ContextObjectExt


class Frame(ContextObjectExt, QFrame):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, stylesheet: str = None):
        QFrame.__init__(self, parent)
        ContextObjectExt.__init__(self, parent, name, visible)
        if stylesheet:
            self.setStyleSheet(stylesheet)

    async def init(
            self, *,
            style: ... = None,
            layout: QLayout = None, policy: tuple[QSizePolicy, QSizePolicy] = (QSizePolicy.Minimum, QSizePolicy.Minimum)
    ) -> 'Frame':
        if style:
            self.setFrameStyle(style)
        if layout:
            self.setLayout(layout)
        return self
