#!python
# -*- coding: utf-8 -*-

import os
import sys

import keyring
import requests
from PySide2.QtWidgets import (
    QApplication,
    QInputDialog,
    QMessageBox,
    QProgressBar,
    QLineEdit
)
from keyring.errors import PasswordDeleteError

from setupLogger import logger
from utils import get_icon, get_version


class DownloadProgress(QProgressBar):
    def __init__(self, file_size):
        super().__init__()
        self._value = 0
        self._percentage = 0
        self._max_value = file_size
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Downloading...")
        self.setWindowIcon(get_icon("assets/moodle.ico"))
        self.resize(350, 30)
        self.show()

    def increase_value(self, block_size):
        self._value += block_size
        self._percentage = (self._value / self._max_value) * 100
        self.setValue(self._percentage)
        QApplication.processEvents()

    def closeEvent(self, event):
        sys.exit()


class UpdaterUI(QMessageBox):
    def __init__(self, parent=None):
        super(UpdaterUI, self).__init__(parent)

    def update_confirm(self, version):
        self.setWindowTitle("moodleNotify Update")
        self.setWindowIcon(get_icon("assets/moodle.ico"))
        self.setStyleSheet("QLabel{min-width: 250px;}")
        self.setText("A new update is available")
        self.setInformativeText(f"Would you like to download v{version}")
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        return self.exec_()

    def input_app_key(self):
        app_key, ok = QInputDialog.getText(self, "Github App Key", "Enter App Key:", QLineEdit.EchoMode.Normal)
        if ok and app_key:
            return app_key

    @staticmethod
    def failed_update():
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setText("Invalid Application Key")
        error_msg.setInformativeText("Please restart the application to insert a new one.")
        error_msg.setWindowTitle("Error")
        error_msg.exec_()


class Updater:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {}
        self.update_dir = "./update"
        self.updater_ui = UpdaterUI()
        self.app_key_service_name = "GitHub App Key"

    def set_app_key(self, app_key):
        logger.info("saving github application key")
        keyring.set_password(self.app_key_service_name, "moodleNotify", app_key)

    def get_app_key(self):
        logger.info("retrieving github application key")
        app_key = keyring.get_password(self.app_key_service_name, "moodleNotify")
        return app_key

    @staticmethod
    def delete_app_key():
        keyring.delete_password("GitHub App Key", "moodleNotify")

    def retrieve_latest_version(self):
        app_key = self.get_app_key()
        if not app_key:
            app_key = self.updater_ui.input_app_key()
            self.set_app_key(app_key)

        self.headers = {"Authorization": f"token {app_key}"}
        latest_release = self.session.get(
            "https://api.github.com/repos/MarwenDallel/MoodleWrapper/releases/latest",
            headers=self.headers,
        )
        if latest_release.status_code != 200:
            try:
                self.delete_app_key()
            except PasswordDeleteError:
                pass
            self.updater_ui.failed_update()
            sys.exit()
        else:
            return latest_release.json()

    def check_update(self):
        latest_release = self.retrieve_latest_version()
        latest_version = float(latest_release["tag_name"][1:])
        if latest_version > get_version():
            reply = self.updater_ui.update_confirm(latest_version)
            if reply == QMessageBox.Yes:
                self.update(latest_release)
                sys.exit()

    def download_file(self, url, filename):
        local_filename = f"{self.update_dir}/{filename}"
        # NOTE the stream=True parameter below
        self.headers["Accept"] = "application/octet-stream"
        with self.session.get(url, stream=True, headers=self.headers) as r:
            file_size = int(r.headers.get("Content-Length", None))
            r.raise_for_status()
            download_progress = DownloadProgress(file_size)
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=4096):
                    download_progress.increase_value(4096)
                    f.write(chunk)
        return local_filename

    def update(self, latest_release):
        if not os.path.exists(self.update_dir):
            os.mkdir(self.update_dir)
        asset_url, asset_name = [
            (asset["url"], asset["name"])
            for asset in latest_release["assets"]
            if asset["name"].endswith("exe")
        ][0]
        file_path = self.download_file(asset_url, asset_name)
        os.startfile(os.path.abspath(file_path))


def main():
    app = QApplication(sys.argv)
    updater_service = Updater()
    updater_service.check_update()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
