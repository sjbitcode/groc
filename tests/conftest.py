# import sqlite3
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


@pytest.fixture
def create_purchase_csvs(tmpdir):
    jan_purchases = tmpdir.join('jan_2019.csv')
    feb_purchases = tmpdir.join('feb_2019.csv')

    fieldnames = "Date,Store,Total,Description"
    jan_entries = [
        "2019-01-01,Store Foo,20.00,fruits",
        "2019-01-03,Store Bar,25.00,bars"
    ]
    jan_purchases.write(f"{fieldnames}\n{jan_entries[0]}\n{jan_entries[1]}")

    feb_entries = [
        "2019-02-04,Store Baz,12.00,milk",
        "2019-02-04,Store Foo,30.00,eggs"
    ]
    feb_purchases.write(f"{fieldnames}\n{feb_entries[0]}\n{feb_entries[1]}")

    return [str(jan_purchases), str(feb_purchases)]


@pytest.fixture
def create_invalid_purchase_csvs(tmpdir):
    jan_purchases = tmpdir.join('jan_2019_2.csv')
    feb_purchases = tmpdir.join('feb_2019_2.csv')

    fieldnames = "Date,Store,Total,Description"
    jan_entries = [
        "2019-01-01,Store Foo,20.00,fruits",
        "2019-01-03,Store Bar,25.00,bars",
        "2019-01-04,Store Foo Bar,23.00,apples"
    ]
    jan_purchases.write(f"{fieldnames}\n{jan_entries[0]}\n{jan_entries[1]}")

    feb_entries = [
        "2019-02-04,Store Baz,12.00,milk",
        "2019-02-04,Store Foo,,eggs"
    ]
    feb_purchases.write(f"{fieldnames}\n{feb_entries[0]}\n{feb_entries[1]}")

    return [str(jan_purchases), str(feb_purchases)]


@pytest.fixture
def date_bytes():
    # Fixed date string to bytes
    return '2019-01-01'.encode('utf-8')


@pytest.fixture(scope='module')
def connection():
    conn = db.create_connection(':memory:')
    db.setup_db(conn)
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


"""
    Fixtures with a function scope for testing db
    functions using a connection parameter
"""
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
