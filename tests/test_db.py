import datetime
import pytest
import sqlite3

from app import db, exceptions


def test_multiple_parameter_substitution_1():
    """ Test parameter substitution with 1 group of values """
    expected_sql_stmt = "SELECT * FROM some_table WHERE id IN (?,?,?,?)"

    # will create string 4 ?'s
    sql_stmt = "SELECT * FROM some_table WHERE id IN (%s)"
    parameterized_stmt = db.multiple_parameter_substitution(sql_stmt, [4])

    assert parameterized_stmt == expected_sql_stmt


def test_multiple_parameter_substitution_2():
    """ Test parameter substitution with 2 groups of values """
    expected_sql_stmt = "SELECT * FROM some_table WHERE id IN (?,?,?,?) AND name IN (?,?,?)"

    # will create string 4 ?'s and 3 ?'s
    sql_stmt = "SELECT * FROM some_table WHERE id IN (%s) AND name IN (%s)"
    parameterized_stmt = db.multiple_parameter_substitution(sql_stmt, [4, 3])

    assert parameterized_stmt == expected_sql_stmt


def test_datetime_worded_abbreviated(date_bytes):
    """ Sqlite converter method """
    expected = db.datetime_worded_abbreviated(date_bytes)
    assert expected == 'Jan 01, 2019'


def test_datetime_worded_full(date_bytes):
    """ Sqlite converter method """
    expected = db.datetime_worded_full(date_bytes)
    assert expected == 'January 01, 2019'


def test_datetime_month_full(date_bytes):
    """ Sqlite converter method """
    expected = db.datetime_month_full(date_bytes)
    assert expected == 'January'


def test_datetime_month_abbreviated(date_bytes):
    """ Sqlite converter method """
    expected = db.datetime_month_abbreviated(date_bytes)
    assert expected == 'Jan'


def test_datetime_month_year_numeric(date_bytes):
    """ Sqlite converter method """
    expected = db.datetime_month_year_numeric(date_bytes)
    assert expected == 'Jan 2019'


@pytest.mark.parametrize('input, expected', [
    ('1200', '$12.00'),
    ('12000', '$120.00'),
    ('120000', '$1,200.00')
])
def test_total_to_float(input, expected):
    """ Sqlite converter method """
    input_to_bytes = input.encode('utf-8')
    assert db.total_to_float(input_to_bytes) == expected


def test_execute_sql(connection):
    sql_stmt = "SELECT 'hello';"
    res = db.execute_sql(connection, sql_stmt).fetchone()
    assert res[0] == 'hello'


def test_execute_sql_fail(connection):
    sql_stmt = "SELECT;"
    with pytest.raises(exceptions.DatabaseError):
        db.execute_sql(connection, sql_stmt)


def test_create_connection(tmp_path):
    # Create connection from path
    db_url = tmp_path / "groc_test.db"
    conn = db.create_connection(db_url)

    # Assert that row factory set
    assert conn.row_factory == sqlite3.Row


def test_setup_db():
    """ Test that setup created 3 tables """
    connection = db.create_connection(':memory:')
    cur = connection.cursor()

    # Select table names and count them before set up
    before_tables = cur.execute(db.sqlite_list_tables).fetchall()
    assert len(before_tables) == 0

    db.setup_db(connection)

    # Select table names and count them after set up
    after_tables = cur.execute(db.sqlite_list_tables).fetchall()
    assert len(after_tables) == 3

    cur.close()
    connection.close()


def test_store_table_exists(cursor):
    cursor.execute('SELECT id FROM store;')
    res = cursor.fetchall()
    assert len(res) == 0


def test_purchase_table_exists(cursor):
    cursor.execute('SELECT id FROM purchase;')
    res = cursor.fetchall()
    assert len(res) == 0


def test_clear_db(connection, cursor, stores_and_purchases):
    """ Test that clearing db clears all purchase and store records """

    # Count purchases & stores before clearing db
    purchase_count = cursor.execute('SELECT COUNT(*) FROM purchase;').fetchone()
    assert purchase_count[0] == 8
    store_count = cursor.execute('SELECT COUNT(*) FROM store;').fetchone()
    assert store_count[0] == 4

    db.clear_db(connection)

    # Count purchases & stores after clearing db
    purchase_count = cursor.execute('SELECT COUNT(*) FROM purchase;').fetchone()
    assert purchase_count[0] == 0
    store_count = cursor.execute('SELECT COUNT(*) FROM store;').fetchone()
    assert store_count[0] == 0


def test_clear_db_fail():
    """ Trying to clear db with no tables """
    connection = db.create_connection(':memory:')

    with pytest.raises(exceptions.DatabaseError):
        db.clear_db(connection)


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


def test_select_purchase_ids(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    """ Test selecting specific ids """
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
    """ Test ids per given months by counting total returned """
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
    # Single sqlite Row object with keys corresponding to columns from sql query
    jan_2019_purchases = db.select_count_total_per_month(
        connection_function_scope,
        ['01'], ['2019']).fetchone()
    assert jan_2019_purchases['month'] == 'Jan'
    assert jan_2019_purchases['year'] == '2019'
    assert jan_2019_purchases['purchase count'] == 3

    # List of four sqlite Row objects for each month/year combo
    jan_feb_2019_2018_purchases = db.select_count_total_per_month(
        connection_function_scope,
        ['01', '02'], ['2019', '2018']).fetchall()
    assert len(jan_feb_2019_2018_purchases) == 4


def test_select_purchase_count(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    """ Count all purchases """
    count = db.select_purchase_count(
            connection_function_scope).fetchone()['purchase_count']
    assert count == 9


def test_get_purchases_date(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    """ Get purchases for a month and year """
    count = db.get_purchases_date(
        connection_function_scope, '01', '2019').fetchall()
    assert len(count) == 3


def test_get_purchases_limit(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    """ Get purchases by limit """
    limit_3 = db.get_purchases_limit(
        connection_function_scope, 3).fetchall()
    assert len(limit_3) == 3

    # Only 9 purchases in db
    limit_10 = db.get_purchases_limit(
        connection_function_scope, 10).fetchall()
    assert len(limit_10) == 9


def test_get_purchases_date_limit(
    connection_function_scope,
    stores_and_purchases_function_scope
):
    """ Get purchases for a month and year, by limit """
    jan_2019_limit_2 = db.get_purchases_date_limit(
        connection_function_scope,
        '01', '2019', 2
    ).fetchall()
    assert len(jan_2019_limit_2) == 2

    mar_2019_limit_5 = db.get_purchases_date_limit(
        connection_function_scope,
        '03', '2019', 5
    ).fetchall()
    assert len(mar_2019_limit_5) == 2


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


def test_insert_row_sqlite(connection_function_scope):
    cursor = connection_function_scope.cursor()
    purchase = {
        'date': datetime.date.today(),
        'store': 'Whole Foods',
        'total': 3500,
        'description': 'cake'
    }

    # Assert no purchases
    purchase_count = cursor.execute('SELECT id FROM purchase;').fetchall()
    assert len(purchase_count) == 0

    # Add the purchase
    db.insert_row_sqlite(cursor, purchase)
    purchase_count_after = cursor.execute(
        'SELECT id FROM purchase;').fetchall()
    assert len(purchase_count_after) == 1


@pytest.mark.parametrize('purchase, raised_exception', [
    ({
        'date': None,
        'store': 'Whole Foods',
        'total': 3500,
        'description': None
    }, exceptions.DatabaseInsertError),
    ({
        'date': datetime.date.today(),
        'store': 'Whole Foods',
        'total': None,
        'description': 'cake'
    }, exceptions.DatabaseInsertError),
    ({
        'date': datetime.date.today(),
        'store': None,
        'total': 3500,
        'description': 'cake'
    }, exceptions.DatabaseInsertError)
])
def test_insert_row_sqlite_required(
    connection_function_scope,
    purchase, raised_exception
):
    """ Try adding a purchase when a required field is missing """
    cursor = connection_function_scope.cursor()

    with pytest.raises(raised_exception):
        db.insert_row_sqlite(cursor, purchase)


@pytest.mark.parametrize('purchase, raised_exception', [
    ({
        'date': datetime.date.today(),
        'store': 'Whole Foods',
        'total': 3500,
        'description': None
    }, exceptions.DuplicateRow),
    ({
        'date': datetime.date.today(),
        'store': 'Whole Foods',
        'total': 3500,
        'description': 'cake'
    }, exceptions.DuplicateRow)
])
def test_insert_row_sqlite_duplicate(
    connection_function_scope,
    purchase, raised_exception
):
    """
        Try adding a duplicate purchase.
        First parametrized tests the insert trigger
    """
    cursor = connection_function_scope.cursor()

    # Add the purchase
    db.insert_row_sqlite(cursor, purchase)
    purchase_count_after = cursor.execute(
        'SELECT id FROM purchase;').fetchall()
    assert len(purchase_count_after) == 1

    # Add the same purchase again
    with pytest.raises(raised_exception):
        db.insert_row_sqlite(cursor, purchase)


def test_validate_insert_row(connection_function_scope):
    """ Validate and insert a row """
    purchase = {
        'date': datetime.date.today(),
        'store': 'Whole Foods',
        'total': 3500,
        'description': 'cake'
    }

    # Assert no purchases
    cursor = connection_function_scope.cursor()
    purchase_count = cursor.execute('SELECT id FROM purchase;').fetchall()
    assert len(purchase_count) == 0

    # Add the purchase
    db.validate_insert_row(
        connection_function_scope, purchase
    )
    purchase_count_after = cursor.execute(
        'SELECT id FROM purchase;').fetchall()
    assert len(purchase_count_after) == 1


def test_validate_insert_row_duplicate_ignore(connection_function_scope):
    """ Test no exception is raised when ignore duplicate flag True """
    purchase = {
        'date': datetime.date.today(),
        'store': 'Whole Foods',
        'total': 3500,
        'description': 'cake'
    }

    # Add the purchase
    db.validate_insert_row(connection_function_scope, purchase)

    # Add the purchase again, ignoring duplicate row exception
    db.validate_insert_row(
        connection_function_scope, purchase, ignore_duplicate=True)

    # Assert only one purchase added
    cursor = connection_function_scope.cursor()
    purchase_count = cursor.execute('SELECT id FROM purchase;').fetchall()
    assert len(purchase_count) == 1


def test_validate_insert_row_duplicate_raise(connection_function_scope):
    """ Test exception is raised when ignore duplicate flag False """
    purchase = {
        'date': datetime.date.today(),
        'store': 'Whole Foods',
        'total': 3500,
        'description': 'cake'
    }

    # Add the purchase
    db.validate_insert_row(connection_function_scope, purchase)

    # Add the same purchase again. Ignore set to False by default
    with pytest.raises(exceptions.DuplicateRow):
        db.validate_insert_row(
            connection_function_scope, purchase)


def test_open_files(create_purchase_csvs):
    """ Open files from path. Test generator object length """
    filepath = create_purchase_csvs
    file_dicts = db.open_files(filepath)
    assert len(list(file_dicts)) == 2


def test_insert_from_csv_dict(connection_function_scope, create_purchase_csvs):
    """ Insert csv files from path """
    filepath = create_purchase_csvs

    # Check the count returned
    count = db.insert_from_csv_dict(connection_function_scope, filepath)
    assert count == 4

    # Use cursor to check count
    cursor = connection_function_scope.cursor()
    db_count = cursor.execute('SELECT COUNT(*) FROM purchase;').fetchone()
    assert db_count['COUNT(*)'] == 4


def test_insert_from_csv_dict_invalid(
    connection_function_scope,
    create_invalid_purchase_csvs
):
    """ Test invalid file content from file """
    filepath = create_invalid_purchase_csvs

    with pytest.raises(exceptions.InvalidRowException):
        db.insert_from_csv_dict(
            connection_function_scope, filepath)


def test_test_open_files_fail(connection_function_scope, tmp_path):
    """ Test opening a file that doesn't exist """
    filepath = tmp_path / "foo.csv"

    with pytest.raises(exceptions.GrocException) as e:
        db.insert_from_csv_dict(
            connection_function_scope, [filepath]
        )
    assert f'Error reading file: {filepath.resolve()}' in e.__str__()
