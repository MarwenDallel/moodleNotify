#!python
# -*- coding: utf-8 -*-

from PySide2.QtCore import QSize, QTimer
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QWidget,
)

from moodleNotify import MoodleWrapper
from setupLogger import logger
from updater import Updater
from utils import get_icon, get_version


class Login(QDialog):
    def __init__(self, moodle_wrapper, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowTitle("Login")
        self.setMinimumSize(QSize(260, 120))
        self.setWindowIcon(get_icon("assets/moodle.ico"))

        self.label_name = QLabel("Username", self)
        self.label_password = QLabel("Password", self)

        self.text_name = QLineEdit(self)
        self.text_pass = QLineEdit(self)
        self.button_login = QPushButton("Login", self)

        self.text_name.setPlaceholderText("Please enter your username")
        self.text_pass.setPlaceholderText("Please enter your password")
        self.text_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.button_login.clicked.connect(self.handle_login)

        layout = QGridLayout(self)
        layout.addWidget(self.label_name, 0, 0)
        layout.addWidget(self.text_name, 0, 1)
        layout.addWidget(self.label_password, 1, 0)
        layout.addWidget(self.text_pass, 1, 1)
        layout.addWidget(self.button_login, 2, 0, 1, 2)

        self.moodleWrapper = moodle_wrapper

    def handle_login(self):
        is_logged = self.moodleWrapper.login(
            self.text_name.text(), self.text_pass.text()
        )
        if is_logged:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Bad user or password")


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent, moodle_wrapper, updater):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.version = get_version()
        self.setToolTip("moodleNotify v" + self.version)
        self.moodleWrapper = moodle_wrapper
        self.updater = updater
        self.monitor_status = True
        self.systray_ui()

    def systray_ui(self):
        # Init QSystemTrayIcon
        self.monitor_action = QAction("Disable Monitoring", self)
        self.update_action = QAction("Check for Updates", self)
        self.quit_action = QAction("Exit", self)
        self.timer = QTimer()

        self.monitor_action.triggered.connect(self.monitoring)
        self.update_action.triggered.connect(self.check_update)
        self.quit_action.triggered.connect(lambda: sys.exit())
        self.timer.timeout.connect(self.show_changes)

        tray_menu = QMenu()
        tray_menu.addAction(self.monitor_action)
        tray_menu.addAction(self.update_action)
        tray_menu.addAction(self.quit_action)

        self.monitor_action.setIcon(get_icon("assets/monitoring_on.ico"))

        logger.info("started monitoring Moodle")

        self.start_timer()

        self.setContextMenu(tray_menu)
        self.show()

        self.showMessage(
            "moodleNotify", "Monitoring enabled", QSystemTrayIcon.Information, 1000
        )
        logger.info("initializing scrapper")
        MoodleWrapper.init(self.moodleWrapper)

    def check_update(self):
        logger.info("checking updates")
        self.updater.check_update()

    def start_timer(self):
        self.timer.start(1800000)

    def end_timer(self):
        self.timer.stop()

    def get_monitoring_status(self):
        return "Disable Monitoring" if self.monitor_status else "Enable Monitoring"

    def get_monitoring_icon(self):
        return (
            get_icon("assets/monitoring_on.ico")
            if self.monitor_status
            else get_icon("assets/monitoring_off.ico")
        )

    def monitoring(self):
        logger.info(self.get_monitoring_status().lower())
        self.end_timer() if self.monitor_status else self.start_timer()
        self.monitor_status = not self.monitor_status
        self.monitor_action.setText(self.get_monitoring_status())
        self.monitor_action.setIcon(self.get_monitoring_icon())

    def show_changes(self):
        logger.info("checking for changes")
        new_grades = MoodleWrapper.check_grades(self.moodleWrapper)
        if new_grades:
            self.showMessage("moodleNotify", "New grades have been found!", msecs=1000)
            logger.info("found new grades")
            for course_name, grade_details in new_grades.items():
                log_message = f"course: {course_name}\n"
                for k, v in grade_details.items():
                    log_message += f"\t{k}: {v}\n"
                logger.info(log_message)


def main():
    app = QApplication(sys.argv)
    logger.info("updater initiated")
    updater = Updater()
    logger.info("checking updates")
    updater.check_update()
    moodle_wrapper = MoodleWrapper("https://moodle.medtech.tn/")

    is_logged = moodle_wrapper.is_logged()
    if not is_logged:
        login = Login(moodle_wrapper)
        if is_logged or login.exec_() == QDialog.Accepted:
            w = QWidget()
            icon = get_icon("assets/moodle.ico")
            tray_icon = SystemTrayIcon(icon, w, moodle_wrapper, updater)
            tray_icon.show()
            sys.exit(app.exec_())


if __name__ == "__main__":
    import sys
    main()
