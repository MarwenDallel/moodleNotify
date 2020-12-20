import sys

from PySide2.QtWidgets import QProgressBar, QApplication

from logic.utils import get_app_icon


class DownloadProgress(QProgressBar):
    def __init__(self, file_size):
        super().__init__()
        self._value = 0
        self._percentage = 0
        self._max_value = file_size
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Downloading...")
        self.setWindowIcon(get_app_icon())
        self.resize(350, 30)
        self.show()

    def increase_value(self, block_size):
        self._value += block_size
        self._percentage = (self._value / self._max_value) * 100
        self.setValue(self._percentage)
        QApplication.processEvents()

    def closeEvent(self, event):
        sys.exit()
