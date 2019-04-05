import sqlite3
import os

from .settings import DB_URL
from .tables import sql_create_store_table, sql_create_transaction_table
from .utils import create_connection, create_table


# Connect to sqlite database.
conn = create_connection(DB_URL)

if conn is not None:
	# Create tables
	create_table(conn, sql_create_store_table)
	create_table(conn, sql_create_transaction_table)
	conn.close()
else:
	print('Error connecting to database!')



