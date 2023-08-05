from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from typing import Union
from abc import ABC

from .extensions import ContextObjectExt, LayoutExt, AlignmentExt, PolicyExt, OrientationExt


class Layout(ABC, AlignmentExt, PolicyExt, OrientationExt):
    @classmethod
    def horizontal(cls, parent: QWidget = None, name: str = None) -> 'HLayout':
        return HLayout(parent, name)

    @classmethod
    def vertical(cls, parent: QWidget = None, name: str = None) -> 'VLayout':
        return VLayout(parent, name)

    @classmethod
    def oriented(cls, orientation: Qt.Orientation, parent: QWidget = None, name: str = None) -> Union['VLayout', 'HLayout']:
        return Layout.vertical(parent, name) if orientation is Layout.Vertical else Layout.horizontal(parent, name)


class VLayout(ContextObjectExt, LayoutExt, QVBoxLayout):
    def __init__(self, parent: QWidget = None, name: str = None):
        QVBoxLayout.__init__(self, parent)
        ContextObjectExt.__init__(self, parent, name, True)


class HLayout(ContextObjectExt, LayoutExt, QHBoxLayout):
    def __init__(self, parent: QWidget = None, name: str = None):
        QHBoxLayout.__init__(self, parent)
        ContextObjectExt.__init__(self, parent, name, True)
