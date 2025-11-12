import os

from dotenv import load_dotenv

# should move to a constants file
_TOKEN_STRING = "DISCORD_TOKEN"
_DEBUG_MODE_STRING = "DEBUG_MODE"
# INTENTS_INTEGER = 182272

load_dotenv()

IS_DEBUG: bool = os.getenv(_DEBUG_MODE_STRING) == 1
DISCORD_TOKEN = os.getenv(_TOKEN_STRING)

DATABASE_URL = os.getenv("DATABASE_URL")
IS_SQL_DEBUG_ECHO = os.getenv("IS_SQL_DEBUG_ECHO") == 1
