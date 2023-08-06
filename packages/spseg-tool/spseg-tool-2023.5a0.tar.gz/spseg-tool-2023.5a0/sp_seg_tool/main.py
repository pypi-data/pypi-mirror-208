import os
from functools import partial
from time import sleep
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QMainWindow,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QFileDialog,
    QWidget,
    QScrollArea,
    QPushButton,
    QMessageBox,
    QRadioButton,
    QButtonGroup,
    QSlider,
)

from ._version import VERSION
from .gui.toolbar import Toolbar
from .task import Task
from .gui.scene import Scene
from .config import Conf
from .gui.utils import exclusive_select
from .backend import State

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    __slots__ = ("_conf", "_state", "_toolbar")

    def __init__(self, conf: Conf):
        super().__init__()
        self.acceptDrops()
        self._conf = conf

        self._state = State(self._conf)
        self._adjust_window()
        self._define_toolbar()
        self._toolbar.select_radio_button.toggled.connect(
            lambda: self._state.set_selecting()
        )
        self._toolbar.deselect_radio_button.toggled.connect(
            lambda: self._state.set_deselecting()
        )

        self._scene = self.create_scene()
        self._scene.add_close_polygon_callback(
            self._state.close_polygon_callback
        )
        self._add_polygon_color_logic()
        self._slider = self.create_opacity_slider()

        self.left_panel, self.left_panel_layout = (
            self.create_left_panel_and_layout()
        )
        central_layout = QGridLayout()
        central_layout.addWidget(self.left_panel, 0, 0)
        central_layout.addWidget(self._scene.view, 0, 2)
        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        parent_layout = QVBoxLayout()
        parent_widget = QWidget()
        parent_widget.setLayout(parent_layout)
        parent_layout.addWidget(self._slider)
        parent_layout.addWidget(central_widget)
        self.setCentralWidget(parent_widget)

    def _adjust_window(self):
        self.resize(self._conf.gui.width, self._conf.gui.height)
        self.setWindowTitle(f"SP-SEG | v{VERSION}")

    def _define_toolbar(self):
        self._toolbar = Toolbar(self._conf.toolbar)
        self.addToolBar(self._toolbar)

        def _open_point_cloud():
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open point cloud",
                self._state.base_dir,
                "Point cloud (*.pts)",
            )
            if self.is_path_valid(path):
                Task(
                    self._state.load_point_cloud, path=path
                ).enable_loading_dialog().run()
                self._state.update_base_dir(path)
                self._scene.refresh()

        def _save_segmentation():
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save labeled point cloud",
                self._state.base_dir,
                "Point cloud (*.pts)",
            )
            if self.is_path_valid(path):
                Task(
                    self._state.save_segmentation_result, path=path
                ).enable_loading_dialog().run()
                self._state.update_base_dir(path)

        def _load_labels():
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Open labels definition",
                self._state.base_dir,
                "JSON File (*.json)",
            )
            if self.is_path_valid(path):
                Task(
                    self._state.load_labels_definitions, path=path
                ).enable_loading_dialog().run()
                self._state.update_base_dir(path)
                self.populate_labels()

        self._toolbar.add_open_logic(_open_point_cloud)
        self._toolbar.add_save_logic(_save_segmentation)
        self._toolbar.add_load_labels_logic(_load_labels)

    def create_left_panel_and_layout(self):
        scroll_left_panel_area = QScrollArea()
        scroll_left_panel_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_left_panel_area.setWidgetResizable(True)
        scroll_left_panel_area.setFixedWidth(320)

        left_panel = QWidget()
        left_panel_layout = QGridLayout()
        left_panel_layout.setAlignment(Qt.AlignTop)
        self.labels_group = QButtonGroup()
        self.labels_group.buttonClicked.connect(
            partial(exclusive_select, button_group=self.labels_group)
        )
        self.labels_group.setExclusive(True)
        left_panel.setLayout(left_panel_layout)
        scroll_left_panel_area.setWidget(left_panel)
        return scroll_left_panel_area, left_panel_layout

    def _add_polygon_color_logic(self):
        def _get_color():
            return QColor(
                *self._state.labels.get_color_for_code(
                    self._state.current_category_code
                ),
                self._state._opacity_factor,
            )

        self._scene.get_color = _get_color

    def is_path_valid(self, path):
        if not isinstance(path, str):
            return False
        if path.strip() == "":
            return False
        return True

    def create_opacity_slider(self):
        def callback():
            self._state.set_opacity_factor(slider.value())
            self._scene.refresh()

        opacity_slider_widget = QWidget()
        layout = QFormLayout()
        label = QLabel("Category mask opacity", self)
        slider = QSlider(Qt.Horizontal)
        slider.setMaximum(200)
        slider.setMinimum(30)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(10)
        slider.valueChanged.connect(callback)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(3)
        slider.setValue(80)
        layout.addRow(label)
        layout.addRow(slider)
        opacity_slider_widget.setLayout(layout)
        return opacity_slider_widget

    def populate_labels(self):
        def _define_single_label_widget(label_definition, button_group):
            def _set_category_code_and_refresh():
                self._state.set_current_category_code(label_definition.code)
                self._scene.refresh()

            label_row = QWidget()
            label_row_layout = QHBoxLayout()
            label_radio_button = QRadioButton(label_definition.label)
            label_radio_button.toggled.connect(_set_category_code_and_refresh)
            button_group.addButton(label_radio_button)
            color_button = QPushButton("  ")
            color_button.setFixedWidth(20)
            color = QColor(
                *self._state.get_color_for_code(label_definition.code)
            )
            color_button.setStyleSheet(
                f"background-color: rgb{color.getRgb()};"
            )
            label_row_layout.addWidget(label_radio_button)
            label_row_layout.addWidget(color_button)

            label_row.setLayout(label_row_layout)
            return label_row

        for label in self._state.get_all_labels():
            self.left_panel_layout.addWidget(
                _define_single_label_widget(label, self.labels_group)
            )

    def create_scene(self):
        return Scene(
            self,
            left_button_logic=lambda x, y: self._state.add_segmentation_seed(
                x, y
            ),
            right_button_logic=lambda x, y: self._state.remove_segmentation_point(
                x, y
            ),
            get_img=self._state.get_img,
        )

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if not self._state.is_initialized:
            pass
        else:
            match event.key():
                case Qt.Key_F1:
                    category_id, instance_id = self._state.accept_region()
                    self.show_accept_msg(
                        category=category_id, instance=instance_id
                    )
                case Qt.Key_Q:
                    self._state.roll_data_x()
                case Qt.Key_W:
                    self._state.roll_data_y()
                case Qt.Key_Alt:
                    self._state.set_display_mode("depth")
                case Qt.Key_Plus:
                    self._state.increase_depth_gamma()
                case Qt.Key_Minus:
                    self._state.decrease_depth_gamma()
        match event.key():
            case Qt.Key_CapsLock:
                select_flag = self._toolbar.select_radio_button.isChecked()
                self._toolbar.select_radio_button.setChecked(~select_flag)
                self._toolbar.deselect_radio_button.setChecked(select_flag)
        self._scene.refresh()

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        if not self._state.is_initialized:
            return
        match event.key():
            case Qt.Key_Alt:
                self._state.set_display_mode("rgb")
        self._scene.refresh()

    def show_accept_msg(self, category, instance):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(
            f"Accepted object number #{instance} of the category with the"
            f" code: {category}!"
        )
        msgBox.setWindowTitle("Object accepted")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
