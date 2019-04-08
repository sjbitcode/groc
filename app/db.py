import os
import sqlite3

from app.connection import SQLiteConnection
from app.tables import (
	sql_create_store_table, sql_create_transaction_table,
	sql_delete_store_table, sql_delete_transaction_table,
	sql_list_tables
)
from app.settings import DB_URL
from app.utils import execute_sql


def setup_db(conn):
	"""
	Set up the sqlite database with store and puchase tables.

	:param conn: Connection object
	:return:
	"""
	with conn:
		execute_sql(conn, sql_create_store_table)
		execute_sql(conn, sql_create_transaction_table)


def list_tables(conn):
	"""
	Get list of all tables in database.

	:param conn: Connection object
	:return: Comma separated list of all tables in database
	"""
	with conn:
		cursor = conn.cursor()
		tables = cursor.execute(sql_list_tables).fetchall()
		return ', '.join(t[0] for t in tables)


def clear_db(conn):
	"""
	Delete all data from the store and purchase tables.

	:param conn: Connection object
	:return:
	"""
	with conn:
		execute_sql(conn, sql_delete_transaction_table)
		execute_sql(conn, sql_delete_store_table)


def create_db():
	"""
	Create the sqlite database at file path specified in settings.

	:param:
	:return:
	"""
	try:
		SQLiteConnection().get_connection()
	except Exception as e:
		print('Error creating sqlite database!', e)


def delete_db():
	"""
	Delete the sqlite database at file path specified in settings.

	:param:
	:return:
	"""
	try:
		os.remove(DB_URL)
	except FileNotFoundError:
		print(f'Database file not found at {DB_URL}')
