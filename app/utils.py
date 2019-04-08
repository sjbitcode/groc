import csv
import os
import sqlite3

from app.settings import BASE_DIR


def execute_sql(conn, sql_statement_string):
    """ 
    Create a table from a sql create table statement.

    :param conn: Connection object
    :param sql_statement_string: a SQL statement
    :return:
    """
    with conn:
        cursor = conn.cursor()
        cursor.execute(sql_statement_string)


def dollar_to_cents(dollar):
    """
    Convert a dollar amount (float) to cents (integer).

    :param dollar: A string or float representing dollar amount
    :return: An integer representing amount as cents.
    """
    return round(float(dollar) * 100)


def get_all_csv(csv_dir, ignore_files=[]):
    """
    Gather all csv files and return as list, excludes any ignored files passed.
    Assumes that the csv files directory is within root project directory.

    :param csv_dir: csv directory name
    :param ignore_files: list of file names to ignore
    """
    csv_dir = os.path.join(BASE_DIR, csv_dir)
    csv_files = []

    # Walk all files in csv_dir
    for root, dirs, files in os.walk(csv_dir):
        for name in files:
            if name.endswith('.csv') and name not in ignore_files:
                # Get full path of file
                full_path = os.path.join(root, name)
                csv_files.append(full_path)

    return csv_files


def insert_from_csv(conn, file_paths):
    """
    Insert contents from list of csv files into database.

    :param conn: Connection object
    :param file_paths: List of path strings to csv files
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
                    print(row)

                    try:
                        # Insert store or ignore if exists
                        store = row[1]
                        cursor.execute('INSERT OR IGNORE INTO store(name) VALUES (?)', (store,))

                        # Insert purchase
                        store_id = cursor.execute('SELECT id FROM store WHERE name = ?', (store,)).fetchone()[0]
                        print(store_id)

                        date = row[0]
                        amount = dollar_to_cents(row[2])
                        description = row[3] or 'grocery'
                        insert = (date, amount, description, store_id)
                        print('Going to insert this {}'.format(insert))
                        cursor.execute('INSERT INTO purchase(purchase_date, total, description, store_id) VALUES (?, ?, ?, ?)', insert)
                    except Exception as e:
                        print(f'Error inserting to database!', e)
