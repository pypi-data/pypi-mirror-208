from PyQt5.QtWidgets import QScrollArea, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QObject
from typing import Sequence, Iterable

from .frame import Frame
from .layout import Layout
from .extensions import ContextObjectExt


class ScrollArea(ContextObjectExt, QScrollArea):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, stylesheet: str = None):
        QScrollArea.__init__(self, parent)
        ContextObjectExt.__init__(self, parent, name, visible)
        if stylesheet:
            self.setStyleSheet(stylesheet)

    async def init(
            self, *,
            orientation: Qt.Orientation, horizontal: bool = True, vertical: bool = True,
            margins: tuple[int, ...] = (0, 0, 0, 0), spacing: int = 0, alignment: Qt.Alignment = None,
            items: Sequence[QObject] = (), policy: tuple[QSizePolicy, QSizePolicy] = None
    ) -> 'ScrollArea':
        if not horizontal:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        if not vertical:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        if policy:
            self.setSizePolicy(*policy)
        frame = Frame(self, f'{self.objectName()}Widget')
        self.setWidget(await frame.init(
            layout=await Layout.oriented(orientation, frame, f'{frame.objectName()}Layout').init(
                margins=margins, spacing=spacing, alignment=alignment, items=items
            )
        ))
        return self

    def clear(self, exceptions: Iterable[QObject] = ()):
        self.widget().layout().clear(exceptions)
