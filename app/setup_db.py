from app.db import SQLiteConnection
from app.tables import sql_create_store_table, sql_create_transaction_table
from app.utils import create_table


def setup():
	"""
	Set up the sqlite database with the tables

	:param conn: Connection object
	:return:
	"""
	connection = SQLiteConnection().get_connection()

	with connection:
		create_table(connection, sql_create_store_table)
		create_table(connection, sql_create_transaction_table)


setup()
