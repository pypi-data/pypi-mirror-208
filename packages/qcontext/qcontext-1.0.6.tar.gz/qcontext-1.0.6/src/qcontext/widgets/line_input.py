from PyQt5.QtWidgets import QLineEdit, QWidget
from PyQt5.QtCore import Qt

from .extensions import ContextObjectExt


class LineInput(ContextObjectExt, QLineEdit):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QLineEdit.__init__(self, parent)
        ContextObjectExt.__init__(self, parent, name, visible)

    async def init(
            self, *,
            placeholder: str = '', text: str = '', hidden: bool = False,
            textchanged: callable = None, alignment: Qt.Alignment = None
    ) -> 'LineInput':
        self.setText(text)
        self.setPlaceholderText(placeholder)
        if hidden:
            self.hide_echo()
        if textchanged:
            self.textChanged.connect(textchanged)
        if alignment:
            self.setAlignment(alignment)
        return self

    def hide_echo(self):
        self.setEchoMode(QLineEdit.Password)

    def show_echo(self):
        self.setEchoMode(QLineEdit.Normal)

    def toggle_echo(self):
        self.hide_echo() if self.echoMode() == QLineEdit.Normal else self.show_echo()
