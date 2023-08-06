import logging

from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import (
    QGridLayout,
    QDialog,
    QLabel,
)

from . import resources

log = logging.getLogger(__name__)


class Worker(QObject):
    finished = pyqtSignal(name="worker_finished")

    def __init__(self, func: callable, *args, **kwargs) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.res = self.func(*self.args, **self.kwargs)
        self.finished.emit()


def show_loading_dialog():
    dialog = QDialog()
    dialog.setAttribute(Qt.WA_TranslucentBackground)
    dialog.setStyleSheet("background:transparent;")
    dialog.setWindowFlags(Qt.FramelessWindowHint)
    dialog.setWindowTitle("Work in progress...")
    dialogGrid = QGridLayout()
    dialog.setLayout(dialogGrid)
    mainLabel = QLabel()
    mainLabel.setScaledContents(True)
    movie = QMovie(":/animations/loading.gif")
    mainLabel.setMovie(movie)
    movie.start()
    dialogGrid.addWidget(mainLabel, 0, 0)
    return dialog


class Task:
    __slots__ = ("worker", "callbacks", "is_loading_dialog_enabled", "thread")

    def __init__(self, func: callable, *args, **kwargs) -> None:
        self.worker = Worker(func, *args, **kwargs)
        self.callbacks = []
        self.is_loading_dialog_enabled = False

    def on_finished(self, callback: callable):
        self.callbacks.append(callback)
        return self

    def enable_loading_dialog(self):
        self.is_loading_dialog_enabled = True
        return self

    def run(self):
        log.debug("starting task...")
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        for callback in self.callbacks:
            self.worker.finished.connect(callback)
        self.thread.started.connect(self.worker.run)
        if self.is_loading_dialog_enabled:
            dialog = show_loading_dialog()
            self.thread.finished.connect(dialog.close)
        self.thread.start()
        if self.is_loading_dialog_enabled:
            dialog.exec_()
        return self

    def result(self):
        return self.worker.res
