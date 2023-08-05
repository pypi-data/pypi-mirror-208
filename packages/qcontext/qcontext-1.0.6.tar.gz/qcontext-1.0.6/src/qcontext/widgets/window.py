from PyQt5.QtWidgets import QMainWindow


class Window(QMainWindow):

    def __init__(self, name: str, stylesheet: str = None):
        QMainWindow.__init__(self)
        self.setObjectName(name)
        if stylesheet:
            self.setStyleSheet(stylesheet)

    async def init(self) -> 'Window':
        return self
