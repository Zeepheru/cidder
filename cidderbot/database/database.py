import logging
import os

import psycopg

from cidderbot.utils.logging_utils.log_config import LogConfig


class Database:
    """Class that handles communication with the PostgreSQL database.
    """
    def __init__(self, host: str = os.getenv("DB_HOST")) -> None:
        """Initialises a connection to the database.

        Args:
            host (str): Host name override. Defaults to the host name supplied in the environment.
        """

        self._logger = logging.getLogger()
        self._conn = None

        # initiate connection
        dbhost = host
        dbname = os.getenv("DB_NAME")
        dbuser = os.getenv("DB_USER")
        dbpassword = os.getenv("DB_PASSWORD")

        db_config = {
            "dbname": dbname,
            "user": dbuser,
            "password": dbpassword,
            "host": dbhost,  
            "port": 5432 # default PostgreSQL port
        }

        try:
            conn = psycopg.connect(**db_config)
            self._logger.info("Connected to the database.")
            self._conn = conn

        except psycopg.Error as e:
            self._logger.error("Unable to connect to the database: %s", e)



if __name__ == "__main__":
    LogConfig().setup(is_debug=True, filename="_DEV-database-log.txt")

    db = Database()
