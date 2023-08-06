import os

import toml
from pydantic import BaseModel


class GUIConf(BaseModel):
    width: int
    height: int
    roll_x: int | None = 30
    roll_y: int | None = 30
    base_dir: str
    transparency_factor: int
    scene_width: int
    scene_height: int
    depth_gamma_factor: float | None = 0.5


class OpenerConf(BaseModel):
    columns: str

    @property
    def coords_ids(self) -> list:
        x_id = self.columns.find("X")
        y_id = self.columns.find("Y")
        z_id = self.columns.find("Z")
        return [x_id, y_id, z_id]

    @property
    def rgb_ids(self) -> list:
        r_id = self.columns.find("R")
        g_id = self.columns.find("G")
        b_id = self.columns.find("B")
        return [r_id, g_id, b_id]


class ToolbarConf(BaseModel):
    pass


class Conf(BaseModel):
    gui: GUIConf
    toolbar: ToolbarConf
    opener: OpenerConf

    @staticmethod
    def load_from(path: os.PathLike | str):
        with open(path, "rt") as file:
            load = toml.load(file)
        return Conf(**load)
