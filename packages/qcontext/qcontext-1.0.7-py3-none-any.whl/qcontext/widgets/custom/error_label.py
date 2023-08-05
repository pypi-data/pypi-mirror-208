from PyQt5.QtCore import QPropertyAnimation, pyqtProperty
from PyQt5.QtWidgets import QWidget
from time import sleep
from qasync import asyncSlot

from ...misc import ConditionalThreadQueue
from ..label import Label
from ..button import Button


class ErrorLabel(Label):
    def __init__(self, parent: QWidget, name: str = None, visible: bool = True):
        super().__init__(parent, name if name else self.__class__.__name__, visible)
        self.__ctq = ConditionalThreadQueue()
        self.__opacity: float = 1
        self.__duration: float = 0.5

    async def init(self, *args, **kwargs) -> 'ErrorLabel':
        self.__emitter = await Button(self, 'EmitterBtn', False).init(
            slot=self.reduce
        )
        await super().init(*args, **kwargs)
        return self

    def setText(self, text: str, delay: float = 2, duration: int = 0.5) -> None:
        if not text:  # text == '' means instantly clear the text and hide label without `post` action
            self.setVisible(False)
            return Label.setText(self, '')

        def pre():
            self._set_opacity(1)
            Label.setText(self, text)
            self.setVisible(True)
            sleep(delay)

        def post():
            self.__emitter.click()

        self.__duration = duration
        self.__ctq.new(pre, post)

    @asyncSlot()
    async def reduce(self):
        self.animation = QPropertyAnimation(self, b"_opacity")
        self.animation.setDuration(int(self.__duration * 1000))
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()

    def _get_opacity(self):
        return self.__opacity

    def _set_opacity(self, opacity):
        self.__opacity = opacity
        self.setStyleSheet(f'color: rgba(255, 0, 0, {opacity});')

    _opacity = pyqtProperty(float, _get_opacity, _set_opacity)
