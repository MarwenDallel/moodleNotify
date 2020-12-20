#!python
from PySide2.QtWidgets import QApplication, QDialog, QWidget

from logic.comparator import Comparator
from logic.credentialManager import CredentialManager
from logic.moodleScrapper import MoodleScrapper
from logic.setupLogger import logger
from logic.updater import Updater
from logic.utils import get_app_icon, get_moodle_url
from ui.login import Login
from ui.systemTray import SystemTrayIcon
from ui.updater import UpdaterUI


def main():
    app = QApplication(sys.argv)
    app_icon = get_app_icon()

    logger.info("updater initiated")
    updater_ui = UpdaterUI(app_icon)
    updater = Updater(updater_ui)

    logger.info("checking updates")
    updater.check_update()

    moodle_url = get_moodle_url()
    moodle_scrapper = MoodleScrapper(moodle_url)

    is_logged = moodle_scrapper.is_logged()
    if not is_logged:
        credential = CredentialManager.get_moodle_cred()
        if credential:
            is_logged = moodle_scrapper.login(credential.username, credential.password)
        else:
            login = Login(app_icon, moodle_scrapper)
            is_logged = login.exec_()
    if is_logged or is_logged == QDialog.Accepted:
        w = QWidget()
        comparator = Comparator()
        tray_icon = SystemTrayIcon(app_icon, w, moodle_scrapper, comparator, updater)
        tray_icon.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    import sys

    main()
