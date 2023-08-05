from PyQt5.QtWidgets import QTextEdit, QWidget, QSizePolicy

from .extensions import ContextObjectExt


class TextInput(ContextObjectExt, QTextEdit):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QTextEdit.__init__(self, parent)
        ContextObjectExt.__init__(self, parent, name, visible)

    async def init(
            self, *,
            placeholder: str = '', text: str = '', textchanged: callable = None,
            policy: tuple[QSizePolicy, QSizePolicy] = None
    ) -> 'TextInput':
        self.setText(text)
        self.setPlaceholderText(placeholder)
        if textchanged:
            self.textChanged.connect(textchanged)
        if policy:
            self.setSizePolicy(*policy)
        return self
