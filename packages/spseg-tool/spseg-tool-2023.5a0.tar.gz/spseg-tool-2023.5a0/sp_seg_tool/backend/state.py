import os
from enum import Enum
from collections import defaultdict

import numpy as np
from PIL import Image
from tqdm.auto import tqdm

from PyQt5.QtCore import Qt, QPointF

from .labels import LabelManager
from .openers import OpenerFactory
from .utils import cartesian_to_spherical, normalize
from ..config import Conf


class PointData:
    def __init__(self, height, width) -> None:
        self.height = height
        self.width = width
        self.coords = np.zeros((height, width, 3))
        self.color = np.zeros((height, width, 3))
        self.depth = np.zeros((height, width))
        self.idx = np.empty((height, width), dtype=object)
        for y in range(height):
            for x in range(width):
                self.idx[y, x] = []
        self.category_code = np.full((height, width), fill_value=-1)
        self.instance_code = np.full((height, width), fill_value=-1)
        self.category_instace_color = np.zeros((height, width, 3))
        self.mask = np.full((height, width), fill_value=False)

    def reset_mask(self):
        self.mask = np.full((self.height, self.width), fill_value=False)

    def roll_data(self, window, axis=0):
        self.mask = np.roll(self.mask, window, axis=axis)
        self.color = np.roll(self.color, window, axis=axis)
        self.category_instace_color = np.roll(
            self.category_instace_color, window, axis=axis
        )
        self.coords = np.roll(self.coords, window, axis=axis)
        self.category_code = np.roll(self.category_code, window, axis=axis)
        self.instance_code = np.roll(self.instance_code, window, axis=axis)
        self.idx = np.roll(self.idx, window, axis=axis)
        self.depth = np.roll(self.depth, window, axis=axis)


class DisplayMode(Enum):
    RGB = "rgb"
    DEPTH = "depth"


class State:
    __slots__ = (
        "conf",
        "WIDTH",
        "HEIGHT",
        "ROLL_X",
        "ROLL_Y",
        "xyz",
        "color",
        "labels",
        "base_dir",
        "point_data",
        "current_category_code",
        "_instance_counter",
        "_opacity_factor",
        "is_initialized",
        "is_selecting",
        "display_mode",
        "depth_gamma",
        "depth_gamma_factor",
    )

    def __init__(self, conf: Conf) -> None:
        self.conf = conf
        self.base_dir = conf.gui.base_dir
        self.labels = LabelManager()
        self.WIDTH = conf.gui.scene_width
        self.HEIGHT = conf.gui.scene_height
        self.ROLL_X = conf.gui.roll_x
        self.ROLL_Y = conf.gui.roll_y
        self.point_data = PointData(width=self.WIDTH, height=self.HEIGHT)
        self.current_category_code = None
        self._instance_counter = defaultdict(int)
        self._opacity_factor = None
        self.is_initialized = False
        self.is_selecting = True
        self.display_mode = DisplayMode.RGB
        self.depth_gamma = 1.0
        self.depth_gamma_factor = conf.gui.depth_gamma_factor

    def roll_data_x(self):
        self.point_data.roll_data(self.ROLL_X, 0)

    def roll_data_y(self):
        self.point_data.roll_data(self.ROLL_Y, 1)

    def increase_depth_gamma(self):
        self.depth_gamma *= self.depth_gamma_factor

    def decrease_depth_gamma(self):
        self.depth_gamma /= self.depth_gamma_factor

    def set_selecting(self):
        self.is_selecting = True
        print("[selecting] mode")

    def set_deselecting(self):
        self.is_selecting = False
        print("[deselecting] mode")

    def get_instance_idx(self, category: int):
        instance_idx = self._instance_counter[category]
        self._instance_counter[category] += 1
        return instance_idx

    def set_opacity_factor(self, factor):
        self._opacity_factor = factor

    def update_base_dir(self, path: os.PathLike | str):
        if os.path.isdir(path):
            self.base_dir = path
        elif os.path.isfile(path):
            self.base_dir = os.path.dirname(path)
        else:
            raise TypeError

    def load_labels_definitions(self, path: os.PathLike | str):
        self.labels = LabelManager.from_file(path)

    def load_point_cloud(self, path: os.PathLike | str):
        self.xyz, self.color = OpenerFactory(path).open(conf=self.conf.opener)
        self.preprocess_point_cloud()
        self.is_initialized = True

    def preprocess_point_cloud(self):
        spherical = cartesian_to_spherical(self.xyz)
        normalized_spherical = normalize(spherical)
        adjusted_spherical = (
            normalized_spherical[:, :2] * [self.HEIGHT, self.WIDTH]
        ).astype(int)

        normalized_depth = normalize(
            np.sqrt(normalized_spherical[:, -1])
        )  # * 255
        # TODO: maybe vectorize
        for point_id, (img_x, img_y) in tqdm(
            enumerate(adjusted_spherical), total=len(adjusted_spherical)
        ):
            self.point_data.idx[img_x, img_y].append(point_id)
            self.point_data.coords[img_x, img_y] = self.xyz[point_id]
            self.point_data.color[img_x, img_y] = self.color[point_id]
            self.point_data.depth[img_x, img_y] = normalized_depth[point_id]
            self.point_data.category_instace_color[img_x, img_y] = self.color[
                point_id
            ]

    def set_display_mode(self, mode: str | DisplayMode):
        self.display_mode = DisplayMode(mode)

    def get_img(self):
        match self.display_mode:
            case DisplayMode.RGB:
                background = Image.fromarray(
                    State.normalize_array(
                        self.point_data.category_instace_color
                    )
                ).convert("RGBA")
                mask_img = np.where(
                    self.point_data.mask[:, :, np.newaxis].repeat(3, axis=2),
                    self.labels.get_color_for_code(self.current_category_code),
                    self.point_data.category_instace_color,
                )
                mask_img = State.normalize_array(mask_img)
                mask = Image.fromarray(mask_img).convert("RGBA")
                mask.putalpha(self._opacity_factor)
                background.paste(mask, (0, 0), mask)
                return State.normalize_array(np.array(background)[:, :, :3])
            case DisplayMode.DEPTH:
                background = (
                    self.point_data.depth ** (1.0 / self.depth_gamma)
                ) * 255.0
                background = Image.fromarray(
                    State.normalize_array(background)
                ).convert("L")
                return State.normalize_array(np.array(background))

    def save_segmentation_result(self, path: os.PathLike | str):
        with open(os.path.join(path), "wt") as file:
            file.write(f"{len(self.xyz)}\n")
            for x in tqdm(range(self.WIDTH)):
                for y in range(self.HEIGHT):
                    category_code = self.point_data.category_code[y, x]
                    instance_idx = self.point_data.instance_code[y, x]
                    for pt_idx in self.point_data.idx[y, x]:
                        coords = self.xyz[pt_idx]
                        color = self.color[pt_idx].astype(np.uint8)
                        category_code = int(category_code)
                        instance_idx = int(instance_idx)
                        pt = (
                            str(coords[0]),
                            str(coords[1]),
                            str(coords[2]),
                            str(color[0]),
                            str(color[1]),
                            str(color[2]),
                            str(category_code),
                            str(instance_idx),
                        )
                        file.write(f"{' '.join(pt)}\n")

    def set_current_category_code(self, code: int):
        self.current_category_code = code

    def get_all_labels(self) -> list[str]:
        return self.labels.get_all_labels()

    def get_color_for_code(self, code: int):
        return self.labels.get_color_for_code(code)

    def remove_segmentation_point(self, x, y):
        x, y = int(x), int(y)
        self.point_data.mask[y, x] = ~self.is_selecting

    def accept_region(self):
        instance_idx = self.get_instance_idx(
            category=self.current_category_code
        )
        self.point_data.category_code = np.where(
            self.point_data.mask,
            self.current_category_code,
            self.point_data.category_code,
        )
        self.point_data.instance_code = np.where(
            self.point_data.mask, instance_idx, self.point_data.instance_code
        )
        print(
            f"added cat: {self.current_category_code}, instance={instance_idx}"
        )

        self.point_data.category_instace_color = np.where(
            self.point_data.mask[:, :, np.newaxis].repeat(3, axis=2),
            self.labels.get_color_for_code(self.current_category_code),
            self.point_data.category_instace_color,
        )
        self._reset_current_region()
        return self.current_category_code, instance_idx

    def _reset_current_region(self):
        self.point_data.reset_mask()

    @staticmethod
    def normalize_array(arr):
        return np.require(arr.astype(np.int32), np.uint8, "C")

    def close_polygon_callback(self, poly):
        mask = self._in_polygon_mask(poly)
        if self.is_selecting:
            self.point_data.mask |= mask
        else:
            # TODO:
            self.point_data.mask &= ~mask

    def _in_polygon_mask(self, poly):
        x_id, y_id = np.meshgrid(np.arange(self.WIDTH), np.arange(self.HEIGHT))
        mask = self._is_in_poly(x_id, y_id, Polygon(poly))
        return mask

    @np.vectorize
    @staticmethod
    def _is_in_poly(a, b, poly):
        return poly.contains(QPointF(a, b))


class Polygon:
    def __init__(self, polygon) -> None:
        self.polygon = polygon

    def contains(self, pt):
        return self.polygon.containsPoint(pt, Qt.OddEvenFill)
