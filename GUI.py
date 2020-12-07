#!python
# -*- coding: utf-8 -*-

from PySide2.QtWidgets import QAction, QApplication, QCheckBox, QDialog, QGridLayout, QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox, QPushButton, QSizePolicy, QSpacerItem, QStyle, QSystemTrayIcon, QVBoxLayout, QWidget
from PySide2.QtCore import QSize, QTimer
from PySide2 import QtGui
from setupLogger import logger
from moodleWrapper import MoodleWrapper
import os

def get_icon(path):
    return QtGui.QIcon(path)

class Login(QDialog):
    def __init__(self, moodleWrapper, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowTitle('Login')
        self.setMinimumSize(QSize(260, 120))
        self.setWindowIcon(get_icon("assets/moodle.ico"))
        
        self.label_name = QLabel('Username', self)
        self.label_password = QLabel('Password', self)
        
        self.text_name = QLineEdit(self)
        self.text_pass = QLineEdit(self)
        self.button_login = QPushButton('Login', self)
        
        self.text_name.setPlaceholderText("Please enter your username")
        self.text_pass.setPlaceholderText('Please enter your password')
        self.text_pass.setEchoMode(QLineEdit.EchoMode.Password)
    
        self.button_login.clicked.connect(self.handleLogin)
        
        layout = QGridLayout(self)
        layout.addWidget(self.label_name, 0, 0)
        layout.addWidget(self.text_name, 0, 1)
        layout.addWidget(self.label_password, 1, 0)
        layout.addWidget(self.text_pass, 1, 1)
        layout.addWidget(self.button_login, 2, 0, 1, 2)
        
        self.moodleWrapper = moodleWrapper

    def handleLogin(self):
        is_logged = self.moodleWrapper.login(self.text_name.text(), self.text_pass.text())
        if is_logged:
            logger.info('initializing scrapper')
            MoodleWrapper.init(self.moodleWrapper)
            self.accept()
        else:
            QMessageBox.warning(
                self, 'Error', 'Bad user or password')

class SystemTrayIcon(QSystemTrayIcon):    
    # Override the class constructor
    def __init__(self, icon, parent, moodleWrapper):
        # Be sure to call the super class method
        QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip('MoodleScrapper v2.2')
        self.moodleWrapper = moodleWrapper
        self.monitor_status = True
        self.systray_ui()

    def systray_ui(self):
        # Init QSystemTrayIcon
        '''
            Define and add steps to work with the system tray icon
            disable monitoring - disable monitoring
            open calculator - open calculator
            exit - exit from application
        '''
        self.monitor_action = QAction("Disable Monitoring", self)
        self.calc_action = QAction("Open Calculator", self)
        self.quit_action = QAction("Exit", self)
        self.timer = QTimer()
        
        self.monitor_action.triggered.connect(self.monitoring)
        self.calc_action.triggered.connect(self.open_calc)
        self.quit_action.triggered.connect(lambda: sys.exit())
        self.timer.timeout.connect(self.show_changes)

        tray_menu = QMenu()
        tray_menu.addAction(self.monitor_action)
        tray_menu.addAction(self.calc_action)
        tray_menu.addAction(self.quit_action)
        
        self.monitor_action.setIcon(get_icon("assets/monitoring_on.ico"))
        
        logger.info('started monitoring Moodle')
                
        self.start_timer()

        self.setContextMenu(tray_menu)
        self.show()
        
        self.showMessage(
            "MoodleScrapper",
            "Monitoring enabled",
            QSystemTrayIcon.Information,
            1000
        )

    def open_calc(self):
        os.system('calc')
        
    def start_timer(self):
        self.timer.start(1800000)

    def end_timer(self):
        self.timer.stop()

    def get_monitoring_status(self):
        return "Disable Monitoring" if self.monitor_status else "Enable Monitoring"
    
    def get_monitoring_icon(self):
        return get_icon("assets/monitoring_on.ico") if self.monitor_status else get_icon("assets/monitoring_off.ico")

    def monitoring(self):
        logger.info(self.get_monitoring_status().lower())
        self.end_timer() if self.monitor_status else self.start_timer()
        self.monitor_status = not self.monitor_status
        self.monitor_action.setText(self.get_monitoring_status())
        self.monitor_action.setIcon(self.get_monitoring_icon())

    def show_changes(self):
        logger.info('checking for changes')
        new_grades = MoodleWrapper.check_grades(self.moodleWrapper)
        if new_grades:
            self.showMessage('MoodleScrapper', 'New grades have been found!', msecs=1000)
            logger.info('found new grades')
            for course_name, grade_details in new_grades.items():
                log_message = f"course: {course_name}\n"
                for k, v in grade_details.items():
                    log_message += f"\t{k}: {v}\n"
                logger.info(log_message)

if __name__ == "__main__":
    import sys
    moodleWrapper = MoodleWrapper("https://moodle.medtech.tn/")
    is_logged = moodleWrapper.is_logged()
    app = QApplication(sys.argv)
    if not is_logged:
        login = Login(moodleWrapper)
    if is_logged or login.exec_() == QDialog.Accepted:
        w = QWidget()
        icon = get_icon("assets/moodle.ico")
        tray_icon = SystemTrayIcon(icon, w, moodleWrapper)
        tray_icon.show()
        sys.exit(app.exec_())
