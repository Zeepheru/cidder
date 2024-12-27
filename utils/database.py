import logging
import os

import psycopg
from log_config import LogConfig


class Database:
    def __init__(self, host:str = os.getenv("DB_HOST")) -> None:
        """Initialises a connection to the database.

        Args:
            host (str, optional): Host name override. Defaults to the host name supplied in the environment.
        """

        self._logger = logging.getLogger()
        self._conn = None

        # initiate connection
        dbhost = host
        dbname = os.getenv("DB_NAME")
        dbuser = os.getenv("DB_USER")
        dbpassword = os.getenv("DB_PASSWORD")

        DB_CONFIG = {
            "dbname": dbname,
            "user": dbuser,
            "password": dbpassword,
            "host": dbhost,  
            "port": 5432 # default PostgreSQL port
        }

        try:
            with psycopg.connect(**DB_CONFIG) as conn:
                self._logger.info("Connected to the database.")
                self._conn = conn

        except psycopg.Error as e:
            self._logger.error(f"Unable to connect to the database: {e}")



if __name__ == "__main__":
    LogConfig().setup(is_debug=True, filename="dev-log-database.txt")

    db = Database()