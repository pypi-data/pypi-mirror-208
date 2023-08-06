import os
import json
from typing import ClassVar

from pydantic import BaseModel, Field, validator
import numpy as np


def get_random_color():
    return tuple(np.random.randint(0, 256, size=3))


class LabelDefinition(BaseModel):
    label: str
    code: int
    color: None | tuple[int, int, int] = Field(
        default_factory=get_random_color
    )


class LabelManager(BaseModel):
    DEFAULT_LABEL: ClassVar[LabelDefinition] = LabelDefinition(
        label="undefined", code=-1
    )
    definitions: dict[int, LabelDefinition] | None = Field(
        default_factory=dict
    )

    @validator("definitions", pre=True)
    def match_definitions(cls, values):
        return {ld["code"]: ld for ld in values}

    @staticmethod
    def from_file(path: os.PathLike | str):
        assert os.path.exists(path), f"path: '{path}' does not exist!"
        with open(path, "rt") as file:
            load = json.load(file)
        return LabelManager(definitions=load)

    def get_all_labels(self) -> list[LabelDefinition]:
        return list(self.definitions.values())

    def get_color_for_code(self, code: int) -> tuple:
        return self.definitions.get(code, LabelManager.DEFAULT_LABEL).color
