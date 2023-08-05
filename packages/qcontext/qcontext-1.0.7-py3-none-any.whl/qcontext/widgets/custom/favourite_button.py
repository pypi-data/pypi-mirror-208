from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon
from typing import Callable
from qasync import asyncSlot

from ..button import Button
from ...misc import Icon


class FavouriteButton(Button):
    def __init__(self, parent: QWidget, name: str = None, visible: bool = True, is_favourite: bool = False):
        super().__init__(parent, name if name else self.__class__.__name__, visible)
        self.is_favourite: bool = is_favourite
        self.if_set_icon: Icon = Icon('star-fill.svg', (30, 30))
        self.if_unset_icon: Icon = Icon('star.svg', (30, 30))

    async def init(
            self, *,
            if_set_icon: Icon = None, if_unset_icon: Icon = None, pre_slot: Callable[..., bool],
            **kwargs
    ) -> 'Button':
        await super().init(**kwargs)
        self.clicked.connect(lambda: self.slot(pre_slot))
        if if_unset_icon:
            self.setIcon(QIcon(if_unset_icon.icon))
            self.setIconSize(if_unset_icon.size)
        if if_set_icon:
            self.if_set_icon = if_set_icon
        if if_unset_icon:
            self.if_unset_icon = if_unset_icon
        return self

    @asyncSlot()
    async def slot(self, pre_slot: Callable[..., bool]):
        # toggle to change state
        self.set(not self.is_favourite)
        if not await pre_slot():
            # toggle once more to come back to prev state if `pre_slot` returns `False`
            self.set(not self.is_favourite)

    def set_favourite(self):
        self.setIcon(self.if_set_icon.icon)
        self.setIconSize(self.if_set_icon.size)
        self.is_favourite = True

    def unset_favourite(self):
        self.setIcon(self.if_unset_icon.icon)
        self.setIconSize(self.if_unset_icon.size)
        self.is_favourite = False

    def set(self, is_favourite: bool):
        self.is_favourite = is_favourite
        if self.is_favourite:
            self.set_favourite()
        else:
            self.unset_favourite()
