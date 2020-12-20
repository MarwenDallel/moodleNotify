import sys

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import (
    QAction,
    QMenu,
    QSystemTrayIcon,
)

from logic.setupLogger import logger
from logic.utils import get_icon, get_version, get_app_name


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent, moodle_scrapper, comparator, updater):
        QSystemTrayIcon.__init__(self, icon, parent)
        self.app_name = get_app_name()
        self.version = get_version()
        self.monitor_on_icon = get_icon("assets/monitoring_on.ico")
        self.monitor_off_icon = get_icon("assets/monitoring_off.ico")

        self.setToolTip(f"moodleNotify v{str(self.version)}")

        self.timer = QTimer()
        self.tray_menu = QMenu()

        self.monitor_action = QAction("Disable Monitoring", self)
        self.update_action = QAction("Check for Updates", self)
        self.quit_action = QAction("Exit", self)

        self.moodle_scrapper = moodle_scrapper
        self.comparator = comparator
        self.updater = updater
        self.monitor_status = True

        self.init_ui()

    def init_ui(self):
        self.monitor_action.triggered.connect(self.monitoring)
        self.update_action.triggered.connect(self.check_update)
        self.quit_action.triggered.connect(lambda: sys.exit())
        self.timer.timeout.connect(self.show_changes)

        self.tray_menu.addAction(self.monitor_action)
        self.tray_menu.addAction(self.update_action)

        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)

        self.monitor_action.setIcon(self.monitor_on_icon)

        logger.info("started monitoring Moodle")

        self.start_timer()

        self.setContextMenu(self.tray_menu)
        self.show()

        self.showMessage(
            self.app_name, "Monitoring enabled", QSystemTrayIcon.Information, 1000
        )
        logger.info("initializing scrapper")
        self.moodle_scrapper.init()

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
            self.monitor_on_icon
            if self.monitor_status
            else self.monitor_off_icon
        )

    def monitoring(self):
        logger.info(self.get_monitoring_status().lower())
        self.end_timer() if self.monitor_status else self.start_timer()
        self.monitor_status = not self.monitor_status
        self.monitor_action.setText(self.get_monitoring_status())
        self.monitor_action.setIcon(self.get_monitoring_icon())

    def show_changes(self):
        logger.info("checking for changes")
        new_grades = self.moodle_scrapper.check_grades(self.comparator)
        if new_grades:
            self.showMessage(self.app_name, "New grades have been found!", msecs=1000)
            logger.info("found new grades")
            for course_name, grade_details in new_grades.items():
                log_message = f"course: {course_name}\n"
                for k, v in grade_details.items():
                    log_message += f"\t{k}: {v}\n"
                logger.info(log_message)
