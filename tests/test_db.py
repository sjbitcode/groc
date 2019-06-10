import pytest

from app import db, exceptions


def test_execute_sql(connection):
    sql_stmt = "SELECT 'hello';"
    res = db.execute_sql(connection, sql_stmt).fetchone()
    assert res[0] == 'hello'


def test_execute_sql_fail(connection):
    sql_stmt = "SELECT;"
    with pytest.raises(exceptions.DatabaseError):
        db.execute_sql(connection, sql_stmt)


def test_setup_db(connection):
    cur = connection.cursor()

    # Select table names and count them before set up
    before_tables = cur.execute(db.sqlite_list_tables).fetchall()
    assert len(before_tables) == 0

    db.setup_db(connection)

    # Select table names and count them after set up
    after_tables = cur.execute(db.sqlite_list_tables).fetchall()
    assert len(after_tables) == 3


def test_clear_db(connection, create_stores_and_purchases):
    cur = connection.cursor()

    # Count purchases & stores before clearing db
    purchase_count = cur.execute(db.sql_count_purchase_table).fetchone()
    assert purchase_count[0] == 8
    store_count = cur.execute(db.sql_count_store_table).fetchone()
    assert store_count[0] == 4

    db.clear_db(connection)

    # Count purchases & stores after clearing db
    purchase_count = cur.execute(db.sql_count_purchase_table).fetchone()
    assert purchase_count[0] == 0
    store_count = cur.execute(db.sql_count_store_table).fetchone()
    assert store_count[0] == 0
