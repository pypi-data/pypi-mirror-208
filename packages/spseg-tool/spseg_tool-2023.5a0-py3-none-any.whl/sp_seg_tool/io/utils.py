from PyQt5.QtWidgets import QFileDialog

from ..state import State
from .task import Task


def is_path_valid(path):
    if not isinstance(path, str):
        return False
    if path.strip() == "":
        return False
    return True
