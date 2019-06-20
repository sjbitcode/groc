import csv
import datetime
import sqlite3

from . import exceptions, utils


""" SQLite specific statements """
sqlite_create_store_table = """CREATE TABLE IF NOT EXISTS store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE );"""

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

sqlite_count_tables = """SELECT COUNT(*) FROM sqlite_master WHERE type='table';"""

sqlite_delete_purchase_by_id = """DELETE FROM purchase WHERE id IN (%s);"""

sqlite_select_purchase_by_id = """SELECT
    p.id,
    p.purchase_date AS date,
    p.total AS "total [total_money]",
    s.name AS store,
    COALESCE(p.description, '--') description
FROM purchase p
INNER JOIN store s ON p.store_id = s.id
WHERE p.id IN (%s);"""

sqlite_select_purchase_ids = """SELECT
    id
FROM purchase
WHERE id IN (%s);"""

sqlite_select_purchase_ids_by_month = """SELECT
    id
FROM purchase
WHERE strftime('%%m', purchase_date) IN (%s);"""

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

# SQL general statements
sql_count_store_table = """SELECT COUNT(*) FROM store;"""

sql_count_purchase_table = """SELECT
    COUNT(*) as purchase_count
FROM purchase;"""

sql_clear_store_table = """DELETE FROM store;"""

sql_clear_purchase_table = """DELETE FROM purchase;"""

sql_delete_store_table = """DROP TABLE store;"""

sql_delete_purchase_table = """DROP TABLE purchase;"""


""" SQLite converter methods """


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
    return datetime.date.strftime(date, '%b %Y')


def total_to_float(bytes_string):
    s = float(str(bytes_string, 'utf-8'))/100
    return f'${s:,.2f}'


""" Db methods """


def execute_sql(conn, sql_stmt, values=()):
    """
    Execute a sql statement via connection cursor.

    Args:
        conn: SQLite connection object.
        sql_stmt (str): a SQL statement.
        values (list): values to use in sql statement.

    Returns:
        cursor: SQLite cursor object.

    Raises:
        exceptions.DatabaseError.
    """
    with conn:
        try:
            cursor = conn.cursor()
            return cursor.execute(sql_stmt, values)
        except sqlite3.DatabaseError:
            raise exceptions.DatabaseError('Something went wrong with the database!')


def create_connection(cnxn_str):
    """
    Create and return a SQLite connection.

    Args:
        cnxn_str (str): path to create db.

    Returns:
        connection: SQLite connection object.
    """
    # Register sqlite converters
    sqlite3.register_converter("purchase_date",
                               datetime_worded_full)
    sqlite3.register_converter("purchase_date_abbreviated",
                               datetime_worded_abbreviated)
    sqlite3.register_converter("purchase_month",
                               datetime_month_full)
    sqlite3.register_converter(
        "purchase_month_abbreviated", datetime_month_abbreviated)
    sqlite3.register_converter(
        "purchase_month_year", datetime_month_year_numeric)
    sqlite3.register_converter("total_money", total_to_float)

    connection = sqlite3.connect(
        cnxn_str, detect_types=sqlite3.PARSE_COLNAMES)

    # Set pragms and row_factory
    connection.execute('PRAGMA foreign_keys = ON;')
    connection.row_factory = sqlite3.Row

    return connection


def setup_db(conn):
    """
    Set up the sqlite database with store and puchase tables.

    Args:
        conn: SQLite connection object.

    Returns: None.
    """
    with conn:
        execute_sql(conn, sqlite_create_store_table)
        execute_sql(conn, sqlite_create_purchase_table)
        execute_sql(conn, sqlite_insert_purchase_trigger)


def select_by_id(conn, ids):
    """
    Select purchase details for multiple ids.

    Args:
        conn: SQLite connection object.
        ids (list/tuple): purchase ids.

    Returns:
        A SQLite cursor object (return value of execute_sql).
    """
    sql_select = multiple_parameter_substitution(
        sqlite_select_purchase_by_id,
        [len(ids)]
    )
    return execute_sql(conn, sql_select, values=ids)


def select_purchase_ids(conn, ids):
    """
    Select purchase ids where for multiple ids.

    Args:
        conn: SQLite connection object.
        ids (list/tuple): purchase ids.

    Returns:
        A SQLite cursor object (return value of execute_sql).
    """
    sql_select = multiple_parameter_substitution(
        sqlite_select_purchase_ids,
        [len(ids)]
    )
    return execute_sql(conn, sql_select, values=ids)


def select_ids_by_month(conn, months):
    """
    Select purchase ids where for given months.

    Args:
        conn: SQLite connection object.
        months (list/tuple): two digit month strings.

    Returns:
        A SQLite cursor object (return value of execute_sql).
    """
    sql_select = multiple_parameter_substitution(
        sqlite_select_purchase_ids_by_month,
        [len(months)]
    )
    return execute_sql(conn, sql_select, values=months)


def select_purchase_count(conn):
    """
    Get total number of purchases.

    Args:
        conn: SQLite connection object.

    Returns:
        A SQLite cursor object (return value of execute_sql).
    """
    return execute_sql(conn, sql_count_purchase_table)


def select_count_total_per_month(conn, months, years):
    """
    Select purchase stats grouped by month and years.

    Args:
        conn: SQLite connection object.
        months (list/tuple): two digit month strings.
        years (list/tuple): four digit year strings.

    Returns:
        A SQLite cursor object (return value of execute_sql).
    """
    sql_select = multiple_parameter_substitution(
        sqlite_select_purchase_count_and_total_per_month,
        [len(months), len(years)]
    )
    return execute_sql(conn, sql_select, values=tuple(months + years))


def delete_from_db(conn, ids):
    """
    Deletes rows from the purchase table given
    a list of purchase ids.

    Args:
        conn: SQLite connection object.
        ids (list/tuple): purchase ids.

    Returns:
        A SQLite cursor object (return value of execute_sql).
    """
    sql_delete = multiple_parameter_substitution(
        sqlite_delete_purchase_by_id,
        [len(ids)]
    )
    return execute_sql(conn, sql_delete, values=ids)


def get_purchases_date_limit(conn, month, year, limit):
    """
    Gets rows from the purchase table limited by amount specified.

    Args:
        conn: SQLite connection object.
        month (str): two digit month string.
        year (str): four digit year string.
        limit (int): Integer value for purchase limit.

    Returns:
        A SQLite cursor object (return value of execute_sql).
    """
    return execute_sql(conn, sqlite_list_purchase_date_limit,
                       values=(month, year, limit,))


def get_purchases_date(conn, month, year):
    """
    Gets all purchases for a month and year

    Args:
        conn: SQLite connection object.
        month (str): two digit month string.
        year (str): four digit year string.

    Returns:
        A SQLite cursor object (return value of execute_sql).
    """
    return execute_sql(conn, sqlite_list_purchase_date, values=(month, year,))


def get_purchases_limit(conn, limit):
    """
    Gets limited amount of purchases.

    Args:
        conn: SQLite connection object.
        limit (int): limit (int): Integer value for purchase limit.

    Returns:
        A SQLite cursor object (return value of execute_sql).
    """
    return execute_sql(conn, sqlite_list_purchase_limit, values=(limit,))


def clear_db(conn):
    """
    Delete all data from the store and purchase tables.

    Args:
        conn: SQLite connection object.

    Returns:
        A SQLite cursor object.

    Raises:
        exceptions.DatabaseError

    """
    with conn:
        try:
            cursor = conn.cursor()
            return cursor.executescript('{} {}'.format(
                sql_clear_purchase_table,
                sql_clear_store_table
            ))
        except sqlite3.DatabaseError as e:
            raise exceptions.DatabaseError(str(e))


def multiple_parameter_substitution(sql_stmt, lengths):
    """
    Parameterize a sqlite IN statement with correct number
    of '?' for arguments passed in and returns the sql
    statement string with correct number of string placeholders.

    source: https://stackoverflow.com/questions/1309989/parameter-substitution-for-a-sqlite-in-clause
    Example:
    ids = [1, 2, 3]
    cur.execute(
        'SELECT * FROM person WHERE id IN (%s)' % ','.join('?'*len(ids)), ids
    )
    'SELECT * FROM person WHERE id IN (?, ?, ?)'

    The code to generate placements has been modified to accept multiple
    lengths to generate different groups of string placements.

    Example:
    sql_stmt = 'SELECT * FROM person WHERE id IN (%s) AND age IN (%s)'
    lengths = [3, 2]
    multiple_parameter_substitution(sql_stmt, lengths) returns
        'SELECT * FROM person WHERE id IN (?, ?, ?) AND age IN (?, ?)'

    Args:
        sql_stmt (str): A SQL statement where string values denoted with %s
        lengths (list/tuple): Integers to determine number of ?'s per group

    Returns:
        str: Sql statement string with string placeholders
    """
    string_placements = tuple([','.join('?'*length) for length in lengths])
    return sql_stmt % string_placements


def insert_row_sqlite(cursor, row):
    """
    Insert purchase data from into SQLite db.

    Args:
        cursor: A SQLite cursor object.
        row (dict): A dictionary with keys (date, store, total, description).

    Returns: None

    Raises:
        exceptions.DatabaseInsertError: if required value missing or some other
                                        SQLite exception.
        exceptions.DuplicateRow: if attempting to insert a duplicate purchase.
    """
    purchase_date = row['date']
    store = row['store']
    total = row['total']
    description = row['description']

    try:
        # Insert store and get store_id
        cursor.execute('INSERT OR IGNORE INTO store(name) VALUES (?)',
                       (store,))
        store_id = cursor.execute('SELECT id FROM store WHERE name = ?',
                                  (store,)).fetchone()[0]

        # Insert purchase details
        cursor.execute(
            """
                INSERT INTO purchase
                    (purchase_date, total, description, store_id)
                VALUES (?, ?, ?, ?);
            """, (purchase_date, total, description, store_id,))

    except (sqlite3.IntegrityError, sqlite3.DatabaseError, Exception) as e:
        exc = exceptions.DatabaseInsertError
        msg = 'Error saving purchase to database.'

        if (('UNIQUE constraint' in e.__str__()) or
           ('Purchase entry already exists' in e.__str__())):
            exc = exceptions.DuplicateRow
            total = float(total)/100
            msg = f'Duplicate purchase detected -- (' \
                  f'date: {purchase_date}, ' \
                  f'store: {store}, ' \
                  f'total: {total:.2f}, ' \
                  f'description: {description})'

        if 'NOT NULL constraint' in e.__str__():
            msg = 'Received incorrect value for required field(s).'

        raise exc(msg)


def open_files(file_paths):
    """
    A generator function that opens and yields files
    from a list of file paths.

    Args:
        file_paths (list): File path strings.

    Yields:
        File object.

    Raises:
        This gets called in function that uses the generator object.

        FileNotFoundError: if file not found.
        Exception: if another error happens while opening file.

    """
    for file in file_paths:
        try:
            with open(file, mode='r', newline='') as csv_file:
                yield csv_file
        except (FileNotFoundError, Exception):
            raise exceptions.GrocException(f'Error reading file: {file}')


def validate_insert_row(conn, row, ignore_duplicate=False):
    """
    Adds a single purchase to database.

    Args:
        conn: A SQLite connection object.
        row (dict): Dictionary with purchase details
        ignore_duplicate (bool): Flag to indicate whether
            to ignore exceptions thrown when a duplicate
            purchase entered. Default is False.

    Returns:
        bool: True if successful

    Raises:
        exceptions.DuplicateRow: if duplicate row detected.
    """
    with conn:
        cursor = conn.cursor()
        try:
            row = utils.validate_row(row)
            insert_row_sqlite(cursor, row)
            return True

        except exceptions.DuplicateRow:
            if not ignore_duplicate:
                raise


def insert_from_csv_dict(conn, file_paths, ignore_duplicate=False):
    """
    Read contents of a csv file and insert purchase data to db.

    Args:
        conn: A SQLite connection object.
        file_paths (list): file path strings
        ignore_duplcate (bool): Flag to indicate whether
            to ignore exceptions thrown when a duplicate
            purchase entered. Default is False.

    Returns:
        int: Count of how many purchases were added.

    Raises:
        Any exceptions to opening the file will be thrown here.
        FileNotFoundError: if file not found.
        Exception: if another error happens while opening file.
    """
    files = open_files(file_paths)
    count = 0

    for file in files:
        print(f'Importing data from {file.name}')
        dict_reader = csv.DictReader(file)
        dict_reader.fieldnames = [name.lower()
                                  for name in dict_reader.fieldnames]

        row_count = 0
        for row in dict_reader:
            if validate_insert_row(conn, row, ignore_duplicate):
                row_count += 1
                count += 1
        print(f'{row_count} purchase(s) added')

    return count
