import os


class EnvConfig:
    _instance = None

    def __init__(self):
        self.multi_database_host = os.getenv("MULTI_DATABASE_HOST", "localhost")
        self.multi_database_name = os.getenv("MULTI_DATABASE_NAME", "multibanco")
        self.multi_database_user = os.getenv("MULTI_DATABASE_USER", "multibanco")
        self.multi_database_password = os.getenv("MULTI_DATABASE_PASS", "mysecretpassword")
        self.multi_database_port = os.getenv("MULTI_DATABASE_PORT", "5432")
        self.default_external_database_user = os.getenv("DEFAULT_EXTERNAL_DATABASE_USER", "nsj_integratto_admin")
        self.default_external_database_password = os.getenv("DEFAULT_EXTERNAL_DATABASE_PASSWORD", "temp%24P4ssw0rd46281937%24")

    @staticmethod
    def instance():
        if (EnvConfig._instance == None):
            EnvConfig._instance = EnvConfig()

        return EnvConfig._instance