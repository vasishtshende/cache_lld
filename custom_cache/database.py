import sqlite3

from custom_cache.db_config import DATABASE_CONFIG
from custom_cache.exceptions import StorageException


class DatabaseHandler:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class SQLiteHandler(DatabaseHandler):
    def connect(self):
        try:
            self.connection = sqlite3.connect(DATABASE_CONFIG['sqlite']['name'])
            self.cursor = self.connection.cursor()
            print("Connection established with sqlite")
        except Exception:
            raise StorageException("Unable to connect to the Storage.")

    def close(self):
        try:
            self.connection.close()
        except Exception:
            raise StorageException("Unable to close connection with the Storage.")


class DatabaseFactory:
    @staticmethod
    def get_database_handler(db_type=DATABASE_CONFIG['type']):

        if db_type == 'sqlite':
            return SQLiteHandler()
        else:
            raise StorageException(f"Unsupported database type: {db_type}")
