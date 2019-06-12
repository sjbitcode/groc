import pytest
import textwrap

from app import db, exceptions


def test_multiple_parameter_substitution_1():
    expected_sql_stmt = "SELECT * FROM some_table WHERE id IN (?,?,?,?)"

    sql_stmt = "SELECT * FROM some_table WHERE id IN (%s)"
    parameterized_stmt = db.multiple_parameter_substitution(sql_stmt, [4])

    assert parameterized_stmt == expected_sql_stmt


def test_multiple_parameter_substitution_2():
    expected_sql_stmt = "SELECT * FROM some_table WHERE id IN (?,?,?,?) AND name IN (?,?,?)"

    sql_stmt = "SELECT * FROM some_table WHERE id IN (%s) AND name IN (%s)"
    parameterized_stmt = db.multiple_parameter_substitution(sql_stmt, [4, 3])

    assert parameterized_stmt == expected_sql_stmt


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


def test_store_table_exists(cursor):
    cursor.execute('SELECT id FROM store;')
    res = cursor.fetchall()
    assert len(res) == 0


def test_purchase_table_exists(cursor):
    cursor.execute('SELECT id FROM purchase;')
    res = cursor.fetchall()
    assert len(res) == 0


def test_clear_db(connection, cursor, stores_and_purchases):
    # cur = connection.cursor()

    # Count purchases & stores before clearing db
    purchase_count = cursor.execute(db.sql_count_purchase_table).fetchone()
    assert purchase_count[0] == 8
    store_count = cursor.execute(db.sql_count_store_table).fetchone()
    assert store_count[0] == 4

    db.clear_db(connection)

    # Count purchases & stores after clearing db
    purchase_count = cursor.execute(db.sql_count_purchase_table).fetchone()
    assert purchase_count[0] == 0
    store_count = cursor.execute(db.sql_count_store_table).fetchone()
    assert store_count[0] == 0


# @pytest.mark.skip
def test_purchase_table_count(cursor):
    cursor.execute('SELECT COUNT(*) FROM purchase;')
    res = cursor.fetchone()
    assert res[0] == 0


@pytest.mark.skip
def test_add_a_purchase(cursor, stores_and_purchases):
    cursor.execute('SELECT id FROM store LIMIT 1;')
    store_id = cursor.fetchone()[0]

    sql_stmt = textwrap.dedent("""
    INSERT INTO purchase (purchase_date, total, description, store_id)
    VALUES ('2019-09-02', 2000, 'candy', {})
    """.format(store_id))

    cursor.execute(sql_stmt)

    cursor.execute('SELECT COUNT(*) FROM purchase;')
    purchase_count = cursor.fetchone()
    assert purchase_count[0] == 9


@pytest.mark.skip
def test_purchase_table_count_2(cursor):
    cursor.execute('SELECT COUNT(*) FROM purchase;')
    res = cursor.fetchone()
    assert res[0] == 0


# @pytest.mark.skip
def test_select_by_id(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    # Get single purchase and save id
    cursor = connection_function_scope.cursor()
    purchase = cursor.execute('SELECT * FROM purchase LIMIT 1;').fetchone()
    id = purchase['id']

    # Use id to select by id
    purchase_selected_by_id = db.select_by_id(
        connection_function_scope, [id]).fetchone()

    # Compare id to check if same purchase
    assert purchase_selected_by_id['id'] == id


@pytest.mark.skip
def test_purchases_count(cursor, stores_and_purchases):
    count = cursor.execute('SELECT COUNT(*) FROM purchase').fetchone()['COUNT(*)']
    assert count == 8


@pytest.mark.skip
def test_purchase_table_count_3(cursor):
    cursor.execute('SELECT COUNT(*) FROM purchase;')
    res = cursor.fetchone()
    assert res[0] == 0


def test_select_purchase_ids(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    cursor = connection_function_scope.cursor()

    # Manually select purchase ids and store in a list
    res = cursor.execute('SELECT id FROM purchase;').fetchall()
    purchase_ids = [row['id'] for row in res]
    assert len(purchase_ids) == 9

    # Select purchase ids with the db function
    selected_ids = db.select_purchase_ids(
        connection_function_scope, purchase_ids).fetchall()
    assert len(selected_ids) == 9
    assert res == selected_ids

    # Delete a purchase, select original group of ids with db function
    cursor.execute('DELETE FROM purchase WHERE id=?', (purchase_ids[0],))
    selected_ids_after = db.select_purchase_ids(
        connection_function_scope, purchase_ids).fetchall()

    # Check that it returns 1 less id
    assert len(selected_ids_after) == 8


def test_select_ids_by_month(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    jan_purchases = db.select_ids_by_month(
        connection_function_scope, ['01']).fetchall()
    assert len(jan_purchases) == 5

    jan_feb_purchases = db.select_ids_by_month(
        connection_function_scope, ['01', '02']).fetchall()
    assert len(jan_feb_purchases) == 7


def test_select_count_total_per_month(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    jan_2019_purchases = db.select_count_total_per_month(
        connection_function_scope,
        ['01'], ['2019']).fetchone()
    assert jan_2019_purchases['month'] == 'Jan'
    assert jan_2019_purchases['year'] == '2019'
    assert jan_2019_purchases['purchase count'] == 3

    jan_feb_2019_2018_purchases = db.select_count_total_per_month(
        connection_function_scope,
        ['01', '02'], ['2019', '2018']).fetchall()
    assert len(jan_feb_2019_2018_purchases) == 4


def test_select_purchase_count(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    count = db.select_purchase_count(
                connection_function_scope).fetchone()['purchase_count']
    assert count == 9


def test_get_purchases_date(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    pass


def test_delete_from_db(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    cursor = connection_function_scope.cursor()

    # Manually select purchase ids and store in a list
    res = cursor.execute('SELECT id FROM purchase;').fetchall()
    purchase_ids = [row['id'] for row in res]
    assert len(purchase_ids) == 9

    id_to_delete = purchase_ids[0]
    db.delete_from_db(connection_function_scope, [id_to_delete])

    