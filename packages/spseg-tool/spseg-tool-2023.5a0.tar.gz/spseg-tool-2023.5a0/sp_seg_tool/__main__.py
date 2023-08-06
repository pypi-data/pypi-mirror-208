import os
import sys

from PyQt5.QtWidgets import QApplication

from .main import MainWindow
from .config import Conf


def run():
    conf_filename = os.path.join(
        os.path.dirname(__file__), "..", "resources", "conf.toml"
    )
    conf = Conf.load_from(conf_filename)

    app = QApplication(sys.argv)
    window = MainWindow(conf)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
