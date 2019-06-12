import sqlite3
import textwrap

import pytest

from app import db


@pytest.fixture
def create_csvs(tmp_path):
    # Create two directories.
    csv_dir = tmp_path / "csv_files"
    csv_dir.mkdir()
    csv_dir_sub = csv_dir / "nested"
    csv_dir_sub.mkdir()

    # Create some test csv files.
    file1 = csv_dir / "foo.csv"
    file2 = csv_dir / "bar.csv"
    file3 = csv_dir_sub / "foo.csv"
    file1.touch()
    file2.touch()
    file3.touch()

    return (csv_dir, [file1, file2, file3])


@pytest.fixture(scope='module')
def connection():
    conn = db.create_connection(':memory:')
    yield conn
    conn.close()


@pytest.fixture()
def cursor(connection):
    cursor = connection.cursor()
    yield cursor
    connection.rollback()


@pytest.fixture()
def stores_and_purchases(cursor):
    # Insert stores
    sql_stmt_stores = textwrap.dedent("""
    INSERT INTO store (name)
    VALUES ("Whole Foods"),
           ("Trader Joe's"),
           ("Key Food"),
           ("Fairway Market")
    """)

    cursor.execute(sql_stmt_stores)

    # [(1, 'Whole Foods'), (2, "Trader Joe's"), (3, 'Key Food'), (4, 'Fairway Market')]
    store_ids = cursor.execute("SELECT * FROM store;")

    # {'Whole Foods': 1, "Trader Joe's": 2, 'Key Food': 3, 'Fairway Market': 4}
    stores = {store[1]: store[0] for store in store_ids}

    # Insert purchases
    purchases = [
        ('2019-01-01', 10000, None, stores.get('Whole Foods')),
        ('2019-01-05', 1050, 'fruits', stores.get("Trader Joe's")),
        ('2019-01-10', 530, 'milk and cheese', stores.get('Fairway Market')),
        ('2019-02-01', 5000, None, stores.get('Key Food')),
        ('2019-03-05', 8000, None, stores.get("Trader Joe's")),
        ('2019-03-15', 4300, 'veggies for dinner', stores.get('Key Food')),
        ('2018-01-10', 15000, 'orange juice', stores.get('Key Food')),
        ('2018-02-10', 2000, None, stores.get('Fairway Market'))
    ]

    sql_stmt_purchases = textwrap.dedent("""
    INSERT INTO purchase (purchase_date, total, description, store_id)
    VALUES (?, ?, ?, ?)
    """)

    cursor.executemany(sql_stmt_purchases, purchases)


""" For db functions using a connection parameter """
@pytest.fixture()
def connection_function_scope():
    conn = db.create_connection(':memory:')
    db.setup_db(conn)
    yield conn
    conn.close()


@pytest.fixture()
def stores_and_purchases_function_scope(connection_function_scope):
    # Insert stores
    sql_stmt_stores = textwrap.dedent("""
    INSERT INTO store (name)
    VALUES ("Whole Foods"),
           ("Trader Joe's"),
           ("Key Food"),
           ("Fairway Market")
    """)

    cursor = connection_function_scope.cursor()
    cursor.execute(sql_stmt_stores)

    # [(1, 'Whole Foods'), (2, "Trader Joe's"), (3, 'Key Food'), (4, 'Fairway Market')]
    store_ids = cursor.execute("SELECT * FROM store;")

    # {'Whole Foods': 1, "Trader Joe's": 2, 'Key Food': 3, 'Fairway Market': 4}
    stores = {store[1]: store[0] for store in store_ids}

    # Insert purchases
    purchases = [
        ('2019-01-01', 10000, None, stores.get('Whole Foods')),
        ('2019-01-05', 1050, 'fruits', stores.get("Trader Joe's")),
        ('2019-01-10', 530, 'milk and cheese', stores.get('Fairway Market')),
        ('2019-02-01', 5000, None, stores.get('Key Food')),
        ('2019-03-05', 8000, None, stores.get("Trader Joe's")),
        ('2019-03-15', 4300, 'veggies for dinner', stores.get('Key Food')),
        ('2018-01-10', 15000, 'orange juice', stores.get('Key Food')),
        ('2018-01-11', 14000, 'apple juice', stores.get('Key Food')),
        ('2018-02-10', 2000, None, stores.get('Fairway Market'))
    ]

    sql_stmt_purchases = textwrap.dedent("""
    INSERT INTO purchase (purchase_date, total, description, store_id)
    VALUES (?, ?, ?, ?)
    """)

    cursor.executemany(sql_stmt_purchases, purchases)
