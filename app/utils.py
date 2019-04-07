import csv
import sqlite3


def create_table(conn, create_table_sql_string):
	""" 
	Create a table from a sql create table statement.

    :param conn: Connection object
    :param create_table_sql_string: a CREATE TABLE statement
    :return:
    """
	with conn:
		cursor = conn.cursor()
		cursor.execute(create_table_sql_string)


def dollar_to_cents(dollar):
	"""
	Convert a dollar amount (float) to cents (integer).

	:param dollar: A string or float representing dollar amount
	:return: An integer representing amount as cents.
	"""
	return round(float(dollar) * 100)


def insert_from_csv(conn, file_paths):
	files = file_paths.split(',')

	for file in files:
		with open(file, mode='r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')

			# Ignore header row
			next(csv_reader)

			with conn:
				cursor = conn.cursor()

				for row in csv_reader:
					print(row)

					# Insert store or ignore if exists
					store = row[1]
					cursor.execute('INSERT OR IGNORE INTO store(name) VALUES (?)', (store,))

					# Insert purchase
					store_id = cursor.execute('SELECT id FROM store WHERE name = ?', (store,)).fetchone()[0]
					print(store_id)

					date = row[0]
					amount = dollar_to_cents(row[2])
					insert = (date, amount, 'grocery', store_id)
					print('Going to insert this {}'.format(insert))
					cursor.execute('INSERT INTO purchase(purchase_date, total, description, store_id) VALUES (?, ?, ?, ?)', insert)
