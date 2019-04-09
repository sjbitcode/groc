import csv
import os
import sqlite3

from app.connection import SQLiteConnection
from app.settings import DB_URL
from app.utils import validate_row


# SQLite specific statements
sqlite_create_store_table = """ CREATE TABLE IF NOT EXISTS store (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						name VARCHAR(50) NOT NULL UNIQUE
						); """

sqlite_create_purchase_table = """ CREATE TABLE IF NOT EXISTS purchase (
							id INTEGER PRIMARY KEY AUTOINCREMENT,
							purchase_date TEXT NOT NULL,
							total INTEGER NOT NULL,
							description TEXT NOT NULL,
							store_id INTEGER NOT NULL,
							FOREIGN KEY (store_id) REFERENCES store(id),
							UNIQUE(purchase_date, total, description, store_id)
							); """

sqlite_list_tables = """ SELECT name FROM sqlite_master WHERE type='table'; """


# Postgres specific statements
postgres_create_store_table = """ CREATE TABLE store (
						id SERIAL PRIMARY KEY,
						name VARCHAR(50) NOT NULL UNIQUE
						); """

postgres_create_purchase_table = """ CREATE TABLE purchase (
							id SERIAL PRIMARY KEY,
							purchase_date DATE NOT NULL,
							total INT NOT NULL,
							description TEXT NOT NULL,
							store_id INTEGER NOT NULL REFERENCES store(id),
							UNIQUE(purchase_date, total, description, store_id)
							); """

postgres_list_tables = """ SELECT table_name FROM information_schema.tables
   						WHERE table_schema = 'public'; """


# SQL general statements
sql_clear_store_table = """ DELETE FROM store; """

sql_clear_purchase_table = """ DELETE FROM purchase; """

sql_delete_store_table = """ DROP TABLE store; """

sql_delete_purchase_table = """ DROP TABLE purchase; """


# Useful db methods
def execute_sql(conn, sql_statement_string):
    """ 
    Execute a sql statement via connection cursor.

    :param conn: Connection object
    :param sql_statement_string: a SQL statement
    :return:
    """
    with conn:
        cursor = conn.cursor()
        cursor.execute(sql_statement_string)


def setup_db(conn):
	"""
	Set up the sqlite database with store and puchase tables.

	:param conn: Connection object
	:return:
	"""
	with conn:
		execute_sql(conn, sqlite_create_store_table)
		execute_sql(conn, sqlite_create_purchase_table)


def list_tables(conn):
	"""
	Get list of all tables in the sqlite database.

	:param conn: Connection object
	:return: Comma separated list of all tables in database
	"""
	with conn:
		cursor = conn.cursor()
		tables = cursor.execute(sqlite_list_tables).fetchall()
		return ', '.join(t[0] for t in tables)


def clear_db(conn):
	"""
	Delete all data from the store and purchase tables.

	:param conn: Connection object
	:return:
	"""
	with conn:
		execute_sql(conn, sql_clear_purchase_table)
		execute_sql(conn, sql_clear_store_table)


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


def insert_csv_row_sqlite(cursor, row):
	"""
	Insert store and purchase data from a
	csv row into a SQLite db.

	:param cursor: A SQLite cursor object
	:param row: A csv row containing data about a purchase.
	            Format should be [
	            	purchase_date, store_name,
	            	total, description
	            ]
	:return:
	"""
	purchase_date, store, total, description = row

	# Insert store and get store_id
	cursor.execute('INSERT OR IGNORE INTO store(name) VALUES (?)', (store,))
	store_id = cursor.execute('SELECT id FROM store WHERE name = ?', (store,)).fetchone()[0]

	# Insert purchase details
	cursor.execute(""" INSERT INTO purchase(purchase_date, total, description, store_id)
		VALUES (?, ?, ?, ?); """,
		(purchase_date, total, description, store_id,))


def insert_csv_row_postgres(cursor, row):
	"""
	Insert store and purchase data from a
	csv row into a Postgres db.

	:param cursor: A Postgres cursor object
	:param row: A csv row containing data about a purchase.
	            Format should be [
	            	purchase_date, store_name,
	            	total, description
	            ]
	:return:
	"""
	purchase_date, store, total, description = row

	# Insert store and get store_id
	cursor.execute('INSERT INTO store(name) VALUES (%s) ON CONFLICT DO NOTHING;', (store,))
	cursor.execute('SELECT id FROM store WHERE name = %s', (store,))
	store_id = cursor.fetchone()[0]

	# Insert purchase details
	cursor.execute(
		""" INSERT INTO purchase(purchase_date, total, description, store_id) 
		VALUES (%s, %s, %s, %s); """,
		(purchase_date, total, description, store_id,))


def insert_from_csv(conn, file_paths, db='sqlite'):
    """
    Insert contents from list of csv files into database.

    :param conn: Connection object
    :param file_paths: List of path strings to csv files
    :param db: String either 'sqlite' or 'postgres'
    :return:
    """

    for file in file_paths:
        with open(file, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            # Ignore header row
            next(csv_reader)

            with conn:
                cursor = conn.cursor()

                for row in csv_reader:
                    row = validate_row(row)                   
                    print(row)

                    try:
                        # Insert into sqlite or postgres
                        if db == 'postgres':
                        	insert_csv_row_postgres(cursor, row)
                        else:
                        	insert_csv_row_sqlite(cursor, row)

                    except Exception as e:
                        print(f'Error inserting to database!', e)

