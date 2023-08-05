from PyQt5.QtWidgets import QWidget, QCompleter, QStyledItemDelegate
from PyQt5.QtCore import Qt
from typing import Iterable

from ..line_input import LineInput


class SearchBar(LineInput):
    def __init__(self, parent: QWidget, name: str = None, visible: bool = True):
        LineInput.__init__(self, parent, name if name else self.__class__.__name__, visible)

    async def init(self, *,
             items: Iterable[str] = (), textchanged: callable = None, placeholder: str = '',
             stylesheet: str = ''
             ) -> 'SearchBar':
        completer = QCompleter(set(items))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.popup().setObjectName(f'{self.objectName()}Popup')
        completer.popup().setItemDelegate(QStyledItemDelegate(completer))
        completer.popup().setStyleSheet(stylesheet)
        self.setCompleter(completer)
        await super().init(textchanged=textchanged, placeholder=placeholder)
        return self
