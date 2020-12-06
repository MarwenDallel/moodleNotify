#!python
# -*- coding: utf-8 -*-

import os
import sys
import time
import moodleWrapper
from PySide2 import QtWidgets, QtGui
from PySide2.QtCore import QTimer
from resourcePath import resource_path
from setupLogger import logger

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'MoodleScrapper v0.1')
        menu = QtWidgets.QMenu(parent)
        
        self.monitor_status = True
        self.monitor = menu.addAction("Disable Monitoring")
        self.monitor.triggered.connect(self.monitoring)
        self.monitor.setIcon(QtGui.QIcon(resource_path("assets/monitoring_on.ico")))
        
        self.timer= QTimer()
        self.timer.timeout.connect(self.show_changes)
        logger.info('started monitoring Moodle')
        self.start_timer()

        open_cal = menu.addAction("Open Calculator")
        open_cal.triggered.connect(self.open_calc)
        open_cal.setIcon(QtGui.QIcon(resource_path("assets/moodle.ico")))
        
        menu.addSeparator()

        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(lambda: sys.exit())

        self.setContextMenu(menu)
        self.activated.connect(self.onTrayIconActivated)

    def onTrayIconActivated(self, reason):
        if reason == self.DoubleClick:
            self.open_calc()

    def open_calc(self):
        os.system('calc')
        
    def get_monitoring_status(self):
        return "Disable Monitoring" if self.monitor_status else "Enable Monitoring"
    
    def get_monitoring_icon(self):
        return QtGui.QIcon(resource_path("assets/monitoring_on.ico")) if self.monitor_status else QtGui.QIcon(resource_path("assets/monitoring_off.ico"))
        
    def monitoring(self):
        logger.info(self.get_monitoring_status().lower())
        self.end_timer() if self.monitor_status else self.start_timer()
        self.monitor_status = not self.monitor_status
        self.monitor.setText(self.get_monitoring_status())
        self.monitor.setIcon(self.get_monitoring_icon())

    def show_changes(self):
        new_grades = moodleWrapper.run()
        if new_grades:
            self.showMessage('MoodleScrapper', 'New grades have been found!', msecs=1000)
            log_message = ""
            for course_name, grade_details in new_grades.items():
                log_message += f"Course: {course_name}\n"
                for k, v in grade_details.items():
                    log_message += f"\t{k}:{v}\n"
            logger.info(log_message.lower())

    def start_timer(self):
        self.timer.start(3600000)

    def end_timer(self):
        self.timer.stop()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon(resource_path("assets/moodle.ico")), w)
    tray_icon.show()
    tray_icon.showMessage('MoodleScrapper', 'Monitoring enabled', msecs=1000)
    sys.exit(app.exec_())