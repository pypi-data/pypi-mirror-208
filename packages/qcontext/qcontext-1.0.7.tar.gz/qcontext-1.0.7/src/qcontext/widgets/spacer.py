from PyQt5.QtWidgets import QSpacerItem, QSizePolicy


class Spacer(QSpacerItem):
    def __init__(self, horizontal: bool = False, vertical: bool = False):
        hpolicy = QSizePolicy.Expanding if horizontal else QSizePolicy.Minimum
        vpolicy = QSizePolicy.Expanding if vertical else QSizePolicy.Minimum
        super().__init__(0, 0, hpolicy, vpolicy)
