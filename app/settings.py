import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SQLITE_DB_NAME = 'grocery.db'
CSV_DIR_NAME = 'bills'

DB_URL = os.path.join(BASE_DIR, SQLITE_DB_NAME)
CSV_DIR = os.path.join(BASE_DIR, CSV_DIR_NAME)
