import sqlite3
import os

from app.connection import SQLiteConnection, PostgresConnection
from app.settings import DB_URL


# Connect to sqlite database.
connection = SQLiteConnection().get_connection()

# Connect to postgres database.
pgconnection = PostgresConnection(params = {
	'host': 'localhost',
	'database': os.environ.get('POSTGRES_DB', 'postgres'),
	'user': os.environ.get('POSTGRES_USER', 'postgres'),
	'password': os.environ.get('POSTGRES_PASSWORD', 'postgres')}).get_connection()


with connection:
	print('SQLite Connection ready!')

