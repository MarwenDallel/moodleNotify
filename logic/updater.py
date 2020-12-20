#!python
import os
import sys

import requests
from PySide2.QtWidgets import (
    QApplication,
    QMessageBox
)
from keyring.errors import PasswordDeleteError

from ui.downloadProgress import DownloadProgress
from ui.updater import UpdaterUI
from .credentialManager import CredentialManager
from .setupLogger import logger
from .utils import get_version, get_release_url, get_app_name, get_app_icon


class Updater:
    def __init__(self, updater_ui):
        self.updater_ui = updater_ui
        self.update_dir = "./update"

        self.release_url = get_release_url()
        self.app_name = get_app_name()

        self.session = requests.Session()
        self.headers = {}

    def retrieve_latest_version(self):
        app_key = CredentialManager.get_app_key()
        if not app_key:
            app_key = self.updater_ui.input_app_key()
            CredentialManager.set_app_key(app_key)

        self.headers = {"Authorization": f"token {app_key}"}
        latest_release = self.session.get(
            self.release_url,
            headers=self.headers,
        )
        if latest_release.status_code != 200:
            try:
                CredentialManager.delete_app_key()
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
            logger.info(f"a new update has been found: moodleNotify {latest_release['tag_name']}")
            reply = self.updater_ui.update_confirm(latest_version)
            if reply == QMessageBox.Yes:
                self.update(latest_release)
                sys.exit()
        else:
            logger.info("no updates found")

    def download_file(self, url, filename):
        local_filename = f"{self.update_dir}/{filename}"
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
        try:
            os.startfile(os.path.abspath(file_path))
        except OSError as e:
            # Errno 1223: access control was canceled by the user.
            if e.errno != 1223:
                logger.error("unexpected error, shutting down")
                sys.exit()


def main():
    app = QApplication(sys.argv)
    app_icon = get_app_icon()
    updater_ui = UpdaterUI(app_icon)
    updater = Updater(updater_ui)
    updater.check_update()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
