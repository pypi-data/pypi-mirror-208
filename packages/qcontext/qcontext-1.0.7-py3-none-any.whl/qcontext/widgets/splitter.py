from PyQt5.QtWidgets import QWidget, QSplitter, QSizePolicy
from PyQt5.QtCore import Qt
from typing import Iterable

from .widget import Widget
from .extensions import ContextObjectExt, SplitterWidgetExt


class SplitterHandle(Widget):
    def __init__(self, parent: QWidget, name: str):
        super().__init__(parent, name, True)


class SplitterWidget(SplitterWidgetExt, Widget):
    def __init__(self, parent: QWidget, name: str,
                 expand_to: int, expand_min: int = None, expand_max: int = None, orientation: Qt.Orientation = None):
        Widget.__init__(self, parent, name, True)
        SplitterWidgetExt.__init__(self, expand_to, expand_min, expand_max, orientation)


class Splitter(ContextObjectExt, QSplitter):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, stylesheet: str = None,
                 orientation: Qt.Orientation = Qt.Horizontal, collapsible: bool = False,
                 policy: tuple[QSizePolicy, QSizePolicy] = (QSizePolicy.Expanding, QSizePolicy.Expanding)):
        QSplitter.__init__(self, orientation, parent)
        ContextObjectExt.__init__(self, parent, name, visible)
        if stylesheet:
            self.setStyleSheet(stylesheet)
            self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(*policy)

    async def init(
            self, *,
            items: Iterable[QWidget] = ()
    ) -> 'Splitter':
        for item in items:
            self.addWidget(item)
        return self

    def addWidget(self, widget: QWidget, collapsible: bool = True) -> None:
        super().addWidget(widget)
        self.setCollapsible(self.count() - 1, collapsible)
        widget.splitter = self
