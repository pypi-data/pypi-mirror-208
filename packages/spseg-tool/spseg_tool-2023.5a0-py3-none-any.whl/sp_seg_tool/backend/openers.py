import os
import sys
from abc import ABC, abstractmethod
import inspect

import numpy as np

from ..config import OpenerConf


class OpenerFactory:
    @abstractmethod
    def get_expected_opener_name(path: os.PathLike | str):
        _, extension = os.path.splitext(path)
        # NOTE: we skip dot in the `extension`
        return f"{extension[1:].title()}Opener"

    def __init__(self, path: os.PathLike | str):
        self.path = path
        opener_name = OpenerFactory.get_expected_opener_name(path)
        opener_classes = inspect.getmembers(
            sys.modules[__name__], inspect.isclass
        )
        for cls_name, clzz in opener_classes:
            if cls_name == opener_name:
                self.chosen_opener_class = clzz
                break
        else:
            raise KeyError(f"no opener found for the path: {path}")

    def open(self, conf: OpenerConf):
        return self.chosen_opener_class.open(self.path, conf)


class Opener(ABC):
    METADATA_LINES = None

    @staticmethod
    @abstractmethod
    def open(path: os.PathLike | str):
        raise NotImplementedError


class PtsOpener(Opener):
    METADATA_LINES = 1

    @staticmethod
    def open(path: os.PathLike | str, conf: OpenerConf):
        assert path is not None, "'path' cannot be `None`"
        assert path.endswith(".pts"), "Required PTS file"
        pts = np.loadtxt(path, skiprows=PtsOpener.METADATA_LINES)
        return pts[:, conf.coords_ids], pts[:, conf.rgb_ids]
