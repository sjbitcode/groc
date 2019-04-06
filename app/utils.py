import sqlite3


def create_connection(db_url):
	"""
	Create a database connection to the SQLite database
    specified by db_url.

    :param db_url: database path
    :return: Connection object or None
    """
	try:
		conn = sqlite3.connect(db_url)
		return conn
	except Exception as e:
		print(e)
	return None


def create_table(conn, create_table_sql_string):
	""" 
	Create a table from a sql create table statement.

    :param conn: Connection object
    :param create_table_sql_string: a CREATE TABLE statement
    :return:
    """
	try:
		c = conn.cursor()
		c.execute(create_table_sql_string)
	except Exception as e:
		print(e)


def enable_foreign_keys(conn):
	"""
	Enable foreign keys on database for each connection.
	"""
	try:
		c = conn.cursor()
		c.execute('PRAGMA foreign_keys = ON;')
	except Exception as e:
		print(e)


def insert_from_csv(conn, file_paths):
	pass
