import keyring

from .setupLogger import logger

keyring.core.set_keyring(keyring.core.load_keyring('keyring.backends.Windows.WinVaultKeyring'))


class CredentialManager:
    moodle_service_name = "moodleNotify/moodle.credentials"
    github_service_name = "moodleNotify/github.appkey"

    @staticmethod
    def set_moodle_cred(username, password):
        logger.info("saving moodle credentials")
        keyring.set_password(CredentialManager.moodle_service_name, username, password)

    @staticmethod
    def get_moodle_cred():
        logger.info("retrieving moodle credentials")
        # https://stackoverflow.com/a/54091770/4192044
        credential = keyring.get_credential(CredentialManager.moodle_service_name, None)
        return credential

    @staticmethod
    def delete_moodle_cred(username):
        logger.info("deleting moodle credentials")
        keyring.delete_password(CredentialManager.moodle_service_name, username)

    @staticmethod
    def set_app_key(app_key):
        logger.info("saving github application key")
        keyring.set_password(CredentialManager.github_service_name, "api_key", app_key)

    @staticmethod
    def get_app_key():
        logger.info("retrieving github application key")
        app_key = keyring.get_password(CredentialManager.github_service_name, "api_key")
        return app_key

    @staticmethod
    def delete_app_key():
        logger.info("deleting github application key")
        keyring.delete_password(CredentialManager.github_service_name, "api_key")
