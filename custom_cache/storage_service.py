import logging
import sqlite3

from custom_cache.exceptions import *


class StorageService:
    def __init__(self, db_handler):
        self.db_handler = db_handler


class SqliteService(StorageService):
    def __init__(self, db_handler):
        super().__init__(db_handler)

    def create_cache_storage_table(self):
        try:

            self.db_handler.cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_storage (key TEXT PRIMARY KEY, value TEXT )
                ''')
            self.db_handler.connection.commit()

        except sqlite3.OperationalError as e:
            logging.error(f"Operational error creating cache table: {e}")
            raise StorageException("Failed to create table due to an operational error.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise StorageException("An unexpected error occurred while creating the table in storage.")

    def insert_entry_in_storage(self, key, value):
        try:

            self.db_handler.cursor.execute('INSERT OR REPLACE INTO cache_storage (key, value) VALUES (?, ?);', (key, value))
            self.db_handler.connection.commit()

        except Exception:
            raise StorageException(f"An unexpected error occurred while writing to the storage: {key}-{value}")

    def get_entry_from_storage(self, key):
        try:

            self.db_handler.cursor.execute("SELECT value FROM cache_storage WHERE KEY=?;", (key,))
            result = self.db_handler.cursor.fetchone()

            if result:
                return result[0]
            return None

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise StorageException(f"An unexpected error occurred while reading key '{key}' from storage.")

    def fetch_all_keys_from_storage(self):
        try:

            self.db_handler.cursor.execute('SELECT * FROM cache_storage;')
            result = self.db_handler.cursor.fetchall()

            if result is None:
                raise KeyNotFoundException(f"Data not found in the storage.")
            return result

        except KeyNotFoundException as e:
            logging.warning(e)
            return None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise StorageException(f"An unexpected error occurred while reading from storage.")

