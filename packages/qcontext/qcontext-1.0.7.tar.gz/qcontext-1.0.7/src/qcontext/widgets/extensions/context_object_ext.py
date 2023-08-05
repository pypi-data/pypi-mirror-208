from PyQt5.QtWidgets import QWidget
from loguru import logger as _logger
from contextlib import suppress as _suppress
import uuid

from ...contextapi import CONTEXT


# ToDo: for all objects add to init(min_size, min_width, max_width, min_height, max_height, policy, margins?, alignment?)
class ContextObjectExt:
    __blacklist: dict[str, list[str]] = {}

    def __init__(self, parent: QWidget = None, name: str = str(uuid.uuid4()), visible: bool = True):
        if parent and name:
            self.setObjectName(name)
            self.register(parent, name, self)
            self.register(self, parent.objectName(), parent)
            self.register(CONTEXT, name, self)

            self.core = parent
            while p := self.core.parent():
                self.core = p
        else:
            attributes = []
            if not parent:
                attributes.append('`parent`')
            if not name:
                attributes.append('`name`')
            if CONTEXT.debug:
                _logger.warning(f"{self.__class__.__name__} not registered in `ContextAPI` since {' and '.join(attributes)} not specified")

        with _suppress(Exception):
            self.setVisible(visible)

    def register(self, parent: QWidget, name: str, child: QWidget) -> None:
        """
        Check if object not in `blacklist`, then register, otherwise show warning
        Check if object already registered, push its name to `blacklist` unregister and show warning otherwise register
        :param parent:
        :param name:
        :param child:
        :return:
        """
        key = parent.__class__.__name__
        self.__blacklist[key] = self.__blacklist.get(key, [])
        if name not in self.__blacklist[key]:
            try:
                getattr(parent, name)
                delattr(parent, name)
                self.__blacklist[key].append(name)
                if CONTEXT.debug:
                    _logger.warning(f'{name} already registered in {key}')
            except AttributeError:
                setattr(parent, name, child)
