from PySide2.QtWidgets import QMessageBox, QInputDialog, QLineEdit

from logic.utils import get_app_name


class UpdaterUI(QMessageBox):
    def __init__(self, icon, parent=None):
        super(UpdaterUI, self).__init__(parent)
        self.app_name = get_app_name()
        self.icon = icon

    def update_confirm(self, version):
        self.setWindowTitle(f"{self.app_name} Update")
        self.setWindowIcon(self.icon)
        self.setStyleSheet("QLabel{min-width: 250px;}")
        self.setText("A new update is available")
        self.setInformativeText(f"Would you like to download v{version}")
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        return self.exec_()

    def input_app_key(self):
        app_key, ok = QInputDialog.getText(
            self,
            "Github App Key",
            "Enter App Key:",
            QLineEdit.EchoMode.Normal
        )
        if ok and app_key:
            return app_key

    def failed_update(self):
        error_msg = QMessageBox()
        error_msg.setWindowIcon(self.icon)
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setText((
            "Invalid application key.\n"
            "Please restart the application to insert a new one."
        ))
        error_msg.setWindowTitle(self.app_name)
        error_msg.exec_()
