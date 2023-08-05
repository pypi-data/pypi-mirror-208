from PyQt5.QtWidgets import QComboBox, QWidget
from typing import Iterable, Any

from ..misc import Icon
from .extensions import ContextObjectExt


class Selector(ContextObjectExt, QComboBox):
    class Item:
        def __init__(self, text: str, icon: Icon = None, data: Any = None):
            self.params = []
            if icon:
                self.params.append(icon)
            self.params.append(str(text))
            if data:
                self.params.append(data)

    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QComboBox.__init__(self)
        ContextObjectExt.__init__(self, parent, name, visible)

    async def init(
            self, *,
            items: Iterable[Item | str] = (), indexchanged: callable = None, textchanged: callable = None
    ) -> 'Selector':
        for item in items:
            if isinstance(item, Selector.Item):
                self.addItem(*item.params)
            elif isinstance(item, str):
                self.addItem(item)
        if indexchanged:
            self.currentIndexChanged.connect(indexchanged)
        if textchanged:
            self.currentTextChanged.connect(textchanged)
        return self

    def setCurrentText(self, text: Any) -> None:
        super().setCurrentText(str(text))
