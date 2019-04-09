import sqlite3
import psycopg2

from app.settings import DB_URL


class SQLiteConnection:
	def __init__(self):
		try:
			conn = sqlite3.connect(DB_URL)
			self.conn = conn
		except Exception as e:
			print(e)

	def get_connection(self):
		self.conn.execute('PRAGMA foreign_keys = ON;')
		return self.conn


class PostgresConnection:
	def __init__(self, params={'host': 'localhost', 'database': 'postgres', 'user': 'postgres', 'password': 'postgres'}):
		try:
			conn = psycopg2.connect(**params)
			self.conn = conn
		except Exception as e:
			print(e)

	def get_connection(self):
		return self.conn

