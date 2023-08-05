from PyQt5.QtCore import QSettings as _QSettings
import socket as _socket
from typing import Any


class ContextAPI:
    __settings = _QSettings(_socket.gethostname(), __file__)
    debug: bool = False

    def __getitem__(self, key: str):
        return self.__settings.value(key)

    def __setitem__(self, key: str, value: Any):
        return self.__settings.setValue(key, value)


CONTEXT = ContextAPI()
