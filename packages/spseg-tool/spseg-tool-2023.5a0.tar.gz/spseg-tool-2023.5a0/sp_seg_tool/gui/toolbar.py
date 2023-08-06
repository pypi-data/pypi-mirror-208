from functools import partial

from PyQt5.QtWidgets import (
    QToolBar,
    QButtonGroup,
    QAction,
    QRadioButton,
    QWidget,
    QVBoxLayout,
)

from PyQt5.QtGui import QIcon

from .. import resources

from ..config import ToolbarConf
from . import utils as ut


class Toolbar(QToolBar):
    DEFAULT_SELECTOR_BASE_DIR = "D:\\Projekty\Python\seg-tool"

    def __init__(self, conf: ToolbarConf) -> None:
        super().__init__()
        self._conf = conf
        self._define_save_action()
        self._define_open_action()
        self._define_load_labels_definitions_action()
        self.insertWidget(QAction(), self.add_select_deselect())

    def _define_open_action(self):
        self.open_point_cloud_action = QAction(
            QIcon(":/icons/open.png"), "&Open...", self
        )
        self.addAction(self.open_point_cloud_action)

    def _define_save_action(self):
        self.save_point_cloud_action = QAction(
            QIcon(":/icons/save.png"), "&Save...", self
        )
        self.addAction(self.save_point_cloud_action)

    def _define_load_labels_definitions_action(self):
        self.load_label_definitions_action = QAction(
            QIcon(":/icons/label.png"), "&Load...", self
        )
        self.addAction(self.load_label_definitions_action)

    def add_open_logic(self, func: callable):
        self.open_point_cloud_action.triggered.connect(func)

    def add_save_logic(self, func: callable):
        self.save_point_cloud_action.triggered.connect(func)

    def add_load_labels_logic(self, func: callable):
        self.load_label_definitions_action.triggered.connect(func)

    def add_select_deselect(self):
        self.select_deselect_group = QButtonGroup()
        self.select_deselect_group.buttonClicked.connect(
            partial(
                ut.exclusive_select, button_group=self.select_deselect_group
            )
        )
        select_deselect_widget = QWidget()
        select_deselect_layout = QVBoxLayout()
        self.select_radio_button = QRadioButton("Select")
        self.select_radio_button.setChecked(True)
        self.deselect_radio_button = QRadioButton("Deselect")
        self.select_deselect_group.addButton(self.select_radio_button)
        self.select_deselect_group.addButton(self.deselect_radio_button)
        select_deselect_layout.addWidget(self.select_radio_button)
        select_deselect_layout.addWidget(self.deselect_radio_button)
        select_deselect_widget.setLayout(select_deselect_layout)
        return select_deselect_widget
