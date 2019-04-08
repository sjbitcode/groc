import sqlite3
import os

from app.connection import SQLiteConnection
from app.settings import DB_URL


# Connect to sqlite database.
connection = SQLiteConnection().get_connection()

with connection:
	print(connection)

