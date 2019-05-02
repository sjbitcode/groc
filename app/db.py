import csv
import datetime
import os
import sqlite3

from prettytable import from_db_cursor

from app.connection import SQLiteConnection
from app.exceptions import GrocException, DatabaseError, DatabaseInsertException, InvalidRowException
from app.settings import DB_URL
from app.utils import validate_row


# SQLite specific statements
sqlite_create_store_table = """CREATE TABLE IF NOT EXISTS store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE );"""

# sqlite_create_purchase_table = """CREATE TABLE IF NOT EXISTS purchase (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     purchase_date TEXT NOT NULL,
#     total INTEGER NOT NULL,
#     description TEXT NOT NULL,
#     store_id INTEGER NOT NULL,
#     FOREIGN KEY (store_id) REFERENCES store(id),
#     UNIQUE(purchase_date, total, description, store_id)
# );"""

# changing purchase_date type to date
sqlite_create_purchase_table = """CREATE TABLE IF NOT EXISTS purchase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_date date NOT NULL,
    total INTEGER NOT NULL,
    description TEXT,
    store_id INTEGER NOT NULL,
    FOREIGN KEY (store_id) REFERENCES store(id),
    UNIQUE(purchase_date, total, description, store_id)
);"""

sqlite_insert_purchase_trigger = """CREATE TRIGGER IF NOT EXISTS
unique_with_null_description
BEFORE INSERT 
ON purchase
WHEN NEW.description IS NULL
BEGIN
    SELECT CASE 
        WHEN (
            (SELECT 1 FROM purchase WHERE 
                purchase_date=NEW.purchase_date AND
                total=NEW.total AND
                store_id=NEW.store_id AND
                description IS NULL
            ) NOTNULL)
        THEN RAISE(ABORT, 'Purchase entry already exists!')
    END;
END;"""

sqlite_list_tables = """SELECT name FROM sqlite_master WHERE type='table';"""

sqlite_delete_purchase_by_id = """DELETE FROM purchase WHERE id IN (%s);"""

# sqlite_select_purchase_by_id = """SELECT * FROM purchase WHERE id IN (%s);"""
sqlite_select_purchase_by_id = """SELECT
    p.id,
    p.purchase_date AS date,
    p.total AS "total [total_money]",
    s.name AS store,
    COALESCE(p.description, '--') description
FROM purchase p
INNER JOIN store s ON p.store_id = s.id
WHERE p.id IN (%s);"""

sqlite_select_count_purchase_by_id = """SELECT id FROM purchase WHERE id IN (%s);"""
sqlite_select_count_purchase_by_month = """SELECT id FROM purchase WHERE strftime('%%m', purchase_date) IN (%s);"""

# sqlite_list_purchase_limit = """SELECT * FROM purchase LIMIT ?;"""
# sqlite_list_purchase_limit = """SELECT
#     id,
#     purchase_date as date,
#     total as "total [total_money]",
#     COALESCE(description, '--') description
# FROM purchase LIMIT ?;"""
sqlite_list_purchase_date_limit = """SELECT
    p.id,
    p.purchase_date AS date,
    p.total AS "total [total_money]",
    s.name AS store,
    COALESCE(p.description, '--') description
FROM purchase p
INNER JOIN store s ON p.store_id = s.id
WHERE 
    strftime ('%m', date) = ?
    AND strftime ('%Y', date) = ?
ORDER BY date DESC
LIMIT ?;"""

sqlite_list_purchase_limit = """SELECT
    p.id,
    p.purchase_date AS date,
    p.total AS "total [total_money]",
    s.name AS store,
    COALESCE(p.description, '--') description
FROM purchase p
INNER JOIN store s ON p.store_id = s.id
ORDER BY date DESC
LIMIT ?;"""

sqlite_list_purchase_date = """SELECT
    p.id,
    p.purchase_date AS date,
    p.total AS "total [total_money]",
    s.name AS store,
    COALESCE(p.description, '--') description
FROM purchase p
INNER JOIN store s ON p.store_id = s.id
WHERE 
    strftime ('%m', date) = ?
    AND strftime ('%Y', date) = ?
ORDER BY date DESC;"""

sqlite_select_purchase_count_per_month = """SELECT
    strftime ('%%m',p.purchase_date) AS num_month,
    p.purchase_date AS "month [purchase_month]",
    COUNT(p.id) AS number_of_purchases
FROM purchase p
GROUP BY num_month
ORDER BY num_month DESC;"""

sqlite_select_purchase_count_and_total_per_month = """SELECT
    strftime ('%%m',p.purchase_date) AS num_month,
    strftime('%%Y', p.purchase_date) AS year,
    p.purchase_date as "month [purchase_month_abbreviated]",
    SUM(p.total) as "total [total_money]",
    COUNT(p.id) AS "purchase count",
    MIN(p.total) as "min purchase [total_money]",
    MAX(p.total) as "max purchase [total_money]",
    round(avg(p.total)) as "avg purchase [total_money]",
    COUNT(DISTINCT p.store_id) as "store count"
FROM purchase p
WHERE num_month IN (%s) AND year IN (%s)
GROUP BY 
    num_month,
    year
ORDER BY year DESC, num_month DESC;"""


# Postgres specific statements
postgres_create_store_table = """CREATE TABLE store (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE );"""

postgres_create_purchase_table = """CREATE TABLE purchase (
    id SERIAL PRIMARY KEY,
    purchase_date DATE NOT NULL,
    total INT NOT NULL,
    description TEXT NOT NULL,
    store_id INTEGER NOT NULL REFERENCES store(id),
    UNIQUE(purchase_date, total, description, store_id)
);"""

postgres_list_tables = """SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';"""


# SQL general statements
sql_count_store_table = """SELECT COUNT(*) FROM store;"""

sql_count_purchase_table = """SELECT COUNT(*) as purchase_count FROM purchase;"""

sql_clear_store_table = """DELETE FROM store;"""

sql_clear_purchase_table = """DELETE FROM purchase;"""

sql_delete_store_table = """DROP TABLE store;"""

sql_delete_purchase_table = """DROP TABLE purchase;"""

# SQLite converter methods
def datetime_worded_abbreviated(bytes_string):
    s = str(bytes_string, 'utf-8')
    date = datetime.datetime.strptime(s, '%Y-%m-%d')
    return datetime.date.strftime(date, '%b %d, %Y')

def datetime_worded_full(bytes_string):
    s = str(bytes_string, 'utf-8')
    date = datetime.datetime.strptime(s, '%Y-%m-%d')
    return datetime.date.strftime(date, '%B %d, %Y')

def datetime_month_full(bytes_string):
    s = str(bytes_string, 'utf-8')
    date = datetime.datetime.strptime(s, '%Y-%m-%d')
    return datetime.date.strftime(date, '%B')

def datetime_month_abbreviated(bytes_string):
    s = str(bytes_string, 'utf-8')
    date = datetime.datetime.strptime(s, '%Y-%m-%d')
    return datetime.date.strftime(date, '%b')

def datetime_month_year_numeric(bytes_string):
    s = str(bytes_string, 'utf-8')
    date = datetime.datetime.strptime(s, '%Y-%m-%d')
    # return datetime.date.strftime(date, '%m/%Y')
    return datetime.date.strftime(date, '%b %Y')

def total_to_float(bytes_string):
    s = float(str(bytes_string, 'utf-8'))/100
    return f'${s:,.2f}'

# Useful db methods
def execute_sql(conn, sql_statement_string, values=()):
    """
    Execute a sql statement via connection cursor.

    :param conn: Connection object
    :param sql_statement_string: a SQL statement
    :param values: list of values to be execute with sql statement
    :returns: None
    """
    with conn:
        try:
            cursor = conn.cursor()
            return cursor.execute(sql_statement_string, values)
        except sqlite3.DatabaseError as e:
            raise DatabaseError(str(e))


def setup_db(conn):
    """
    Set up the sqlite database with store and puchase tables.

    :param conn: Connection object
    :returns: None
    """
    with conn:
        execute_sql(conn, sqlite_create_store_table)
        execute_sql(conn, sqlite_create_purchase_table)
        execute_sql(conn, sqlite_insert_purchase_trigger)

def list_tables(conn):
    """
    Get list of all tables in the sqlite database.

    :param conn: Connection object
    :returns: Comma separated list of all tables in database
    :rtype: list
    """
    with conn:
        cursor = conn.cursor()
        tables = cursor.execute(sqlite_list_tables).fetchall()
        return ', '.join(t[0] for t in tables)

def select_by_id(conn, ids):
    with conn:
        sql_select = multiple_parameter_substitution(
            sqlite_select_purchase_by_id,
            [len(ids)]
        )
        return execute_sql(conn, sql_select, values=ids)


def select_count_by_id(conn, ids):
    with conn:
        sql_select = multiple_parameter_substitution(
            sqlite_select_count_purchase_by_id,
            [len(ids)]
        )
        return execute_sql(conn, sql_select, values=ids)

def select_ids_by_month(conn, months):
    with conn:
        sql_select = multiple_parameter_substitution(
            sqlite_select_count_purchase_by_month,
            len(months)
        )
        return execute_sql(conn, sql_select, values=months)

def select_purchase_count_per_month(conn):
    with conn:
        return execute_sql(conn, sqlite_select_purchase_count_per_month)


def select_purchase_count(conn):
    with conn:
        return execute_sql(conn, sql_count_purchase_table)

def select_count_total_per_month(conn, months, years):
    with conn:
        sql_select = multiple_parameter_substitution(
            sqlite_select_purchase_count_and_total_per_month,
            [len(months), len(years)]
        )
        return execute_sql(conn, sql_select, values=tuple(months + years))

def delete_from_db(conn, ids):
    """
    Deletes rows from the purchase table given
    a list of purchase ids.

    :param conn: Connection object
    :returns: None
    """
    with conn:
        sql_delete = multiple_parameter_substitution(
            sqlite_delete_purchase_by_id,
            [len(ids)]
        )
        return execute_sql(conn, sql_delete, values=ids)


def get_purchases_date_limit(conn, month, year, limit):
    """
    Gets rows from the purchase table limited by amount specified.

    :param conn: Connection object.
    :param limit: Integer value for amount of rows to return.
    :returns: List of results.
    """
    with conn:
        return execute_sql(conn, sqlite_list_purchase_date_limit, values=(month, year, limit,))
    

def get_purchases_date(conn, month, year):
    with conn:
        return execute_sql(conn, sqlite_list_purchase_date, values=(month, year,))


def get_purchases_limit(conn, limit):
    with conn:
        return execute_sql(conn, sqlite_list_purchase_limit, values=(limit,))


def clear_db(conn):
    """
    Delete all data from the store and purchase tables.

    :param conn: Connection object
    :return:
    """
    with conn:
        # execute_sql(conn, sql_clear_purchase_table)
        # execute_sql(conn, sql_clear_store_table)
        try:
            cursor = conn.cursor()
            return cursor.executescript('{} {}'.format(
                sql_clear_purchase_table,
                sql_clear_store_table
            ))
        except sqlite3.DatabaseError as e:
            raise DatabaseError(str(e))


def create_db():
    """
    Create the sqlite database at file path specified in settings.

    :returns None:
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


def multiple_parameter_substitution(sql_statement_string, lengths):
    """
    Parameterize a sqlite IN statement with correct number
    of '?' for arguments passed in and returns the sql 
    statement string with correct number of string placeholders.

    source: https://stackoverflow.com/questions/1309989/parameter-substitution-for-a-sqlite-in-clause
    Example:
    ids = ["1", "2", "3"]
    cur.execute(
        'SELECT * FROM person WHERE id IN (%s)' % ','.join('?'*len(ids)), 
        ids
    )

    :param sql_statement_string: A SQLite query string
    :param length: Integer to generate '?' placeholder
    :param lengths: Array of integer values to generate '?' placeholder
    :return: Modified sql statement string with string placeholders of passed length
    """
    string_placements = tuple([','.join('?'*length) for length in lengths])
    return sql_statement_string % string_placements
    # return sql_statement_string % ','.join('?'*length)


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
    print('GOING TO INSERT ROW IN SQLITE NOW')
    print(row)
    purchase_date = row['date']
    store = row['store']
    total = row['total']
    description = row['description']
    # import pdb; pdb.set_trace()

    # Insert store and get store_id
    cursor.execute('INSERT OR IGNORE INTO store(name) VALUES (?)', (store,))
    store_id = cursor.execute('SELECT id FROM store WHERE name = ?', (store,)).fetchone()[0]
    print('going to insert purchase deets')
    # Insert purchase details
    cursor.execute("""INSERT INTO purchase(purchase_date, total, description, store_id)
        VALUES (?, ?, ?, ?);""",
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
        """INSERT INTO purchase(purchase_date, total, description, store_id) 
        VALUES (%s, %s, %s, %s);""",
        (purchase_date, total, description, store_id,))

def insert_from_commandline(conn, row):
    with conn:
        cursor = conn.cursor()
        try:
            print('going to insert this row')
            print(row)
            row = validate_row(row)
            insert_csv_row_sqlite(cursor, row)
            # conn.commit()

        except InvalidRowException as exc:
            # conn.rollback()
            # print(f'Invalid row occured - {str(exc)}')
            # print(str(exc))
            raise InvalidRowException(str(exc))

        except (sqlite3.IntegrityError, sqlite3.DatabaseError) as exc:
            raise DatabaseInsertException(str(exc))
        
        except:
            raise

def insert_from_csv_dict(conn, file_path, db='sqlite'):
    """ Insert contents from csv using DictReader """
    for file in file_path:
        with open(file, mode='r', newline='') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            dict_reader.fieldnames = [name.lower()
                                      for name in dict_reader.fieldnames]

            with conn:
                cursor = conn.cursor()
                # import pdb; pdb.set_trace()

                for row in dict_reader:
                    try:
                        # pass
                        print(row)
                        # import pdb; pdb.set_trace()
                        # VALIDATE ROW - clean
                        row = validate_row(row)
                        insert_csv_row_sqlite(cursor, row)

                    except InvalidRowException as exc:
                        # print('Invalid row occured')
                        # print(str(exc))
                        raise InvalidRowException(str(exc))
                        # break

                    except (sqlite3.IntegrityError, sqlite3.DatabaseError) as exc:
                        raise DatabaseInsertException(str(exc))
                        # break
                    
                    except:
                        raise
                        # break


def insert_from_csv_dict_2(conn, file_path, db='sqlite'):
    """ Insert contents from csv using DictReader """
    for file in file_path:
        with open(file, mode='r', newline='') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            dict_reader.fieldnames = [name.lower()
                                      for name in dict_reader.fieldnames]

            for row in dict_reader:
                insert_from_commandline(conn, row)


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
                    try:
                        row = validate_row(row)
                        # print(row)

                        # Insert into sqlite or postgres
                        if db == 'postgres':
                            insert_csv_row_postgres(cursor, row)
                        else:
                            insert_csv_row_sqlite(cursor, row)

                    except InvalidRowException as exc:
                        print('Invalid row occured', exc)

                    except DatabaseInsertException as exc:
                        print('Error inserting to database!', exc)

