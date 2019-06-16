import sqlite3
from unittest import mock

import pytest

from app import exceptions, groc


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.Groc._get_db_url', return_value='some-db-url')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
def test_get_connection_called_with_db_url(
    mock_create_connection, mock_get_db_url, mock_os_path_expanduser
):
    groc.Groc()
    mock_create_connection.assert_called_with('some-db-url')


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.Groc._get_db_url', return_value='some-db-url')
@mock.patch('app.groc.db.create_connection', side_effect=sqlite3.OperationalError)
def test_get_connection_exception(mock_db_create_conn, mock_get_db_url, mock_os_path_expanduser):
    with pytest.raises(exceptions.DatabaseError):
        groc.Groc()._get_connection()


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection')
def test_get_db_url(mock_create_connection, mock_os_path_expanduser):
    g = groc.Groc()
    assert g._get_db_url() == 'my-groc-dir/groc.db'


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.setup_db')
def test_create_and_setup_db_called_with_connection(
    mock_setup_db, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g._create_and_setup_db()
    mock_setup_db.assert_called_with('some-connection')


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection')
@mock.patch('app.groc.os.path.exists')
def test_groc_dir_exists(mock_os_path_exists, mock_create_connection,
                         mock_os_path_expanduser):
    g = groc.Groc()
    g.groc_dir_exists()
    mock_os_path_exists.assert_called_with('my-groc-dir')


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection')
@mock.patch('app.groc.os.path.isfile', return_value=True)
@mock.patch('app.groc.Groc._create_and_setup_db')
def test_init_groc_raise_exception(
    mock_create_setup_db, mock_os_path_isfile,
    mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    with pytest.raises(exceptions.DatabaseError):
        g.init_groc()
    assert not mock_create_setup_db.called


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection')
@mock.patch('app.groc.Groc._create_and_setup_db')
@mock.patch('app.groc.os.path.isdir', return_value=True)
def test_init_groc(
    mock_os_path_isdir, mock_create_setup_db,
    mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.init_groc()
    assert mock_create_setup_db.called


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection')
@mock.patch('app.groc.Groc._create_and_setup_db')
@mock.patch('app.groc.os.path.isdir', return_value=False)
@mock.patch('app.groc.os.mkdir')
def test_init_groc_2(
    mock_os_mkdir, mock_os_path_isdir,
    mock_create_setup_db, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.init_groc()
    assert g.groc_dir == 'my-groc-dir'
    assert mock_os_mkdir.called
    mock_os_mkdir.assert_called_with('my-groc-dir')


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.clear_db', autospec=True)
def test_clear_db(
    mock_clear_db, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.clear_db()
    mock_clear_db.assert_called_with('some-connection')


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.select_by_id', return_value='some-cursor', autospec=True)
def test_select_by_id(
    mock_select_id, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.select_by_id((1, 2, 3))
    mock_select_id.assert_called_with('some-connection', (1, 2, 3))


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.select_purchase_ids', return_value='some-cursor', autospec=True)
def test_select_purchase_ids(
    mock_select_purchase_ids, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.select_purchase_ids((1, 2, 3))
    mock_select_purchase_ids.assert_called_with('some-connection', (1, 2, 3))


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.select_count_total_per_month', return_value='some-cursor', autospec=True)
def test_breakdown(
    mock_count_total, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.breakdown('01', '2019')
    mock_count_total.assert_called_with('some-connection', '01', '2019')


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.select_purchase_count', autospec=True)
def test_select_purchase_count(
    mock_purchase_count, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.select_purchase_count()
    mock_purchase_count.assert_called_with('some-connection')


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.delete_from_db', autospec=True)
def test_delete_purchase(
    mock_delete_from_db, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.delete_purchase((1, 2, 3))
    mock_delete_from_db.assert_called_with('some-connection', (1, 2, 3))


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.get_purchases_date', autospec=True)
def test_list_purchases_date(
    mock_list_purchases_date, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.list_purchases_date('01', '2019')
    mock_list_purchases_date.assert_called_with(
        'some-connection', '01', '2019')


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.get_purchases_limit', autospec=True)
def test_list_purchases_limit_default(
    mock_list_purchases_limit, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.list_purchases_limit()
    mock_list_purchases_limit.assert_called_with('some-connection', 50)


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.get_purchases_limit', autospec=True)
def test_list_purchases_limit(
    mock_list_purchases_limit, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.list_purchases_limit(20)
    mock_list_purchases_limit.assert_called_with('some-connection', 20)


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.get_purchases_date_limit', autospec=True)
def test_list_purchases_date_limit_default(
    mock_list_purchases_date_limit, mock_create_connection,
    mock_os_path_expanduser
):
    g = groc.Groc()
    g.list_purchases_date_limit('01', '2019')
    mock_list_purchases_date_limit.assert_called_with(
        'some-connection', '01', '2019', 50)


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.get_purchases_date_limit', autospec=True)
def test_list_purchases_date_limit(
    mock_list_purchases_date_limit, mock_create_connection,
    mock_os_path_expanduser
):
    g = groc.Groc()
    g.list_purchases_date_limit('01', '2019', 20)
    mock_list_purchases_date_limit.assert_called_with(
        'some-connection', '01', '2019', 20)


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.validate_insert_row', autospec=True)
def test_add_purchase_manual(
    mock_validate_insert_row, mock_create_connection,
    mock_os_path_expanduser
):
    g = groc.Groc()
    g.add_purchase_manual({'foo': 'bar'}, False)
    mock_validate_insert_row('some-connection', {'foo': 'bar'}, False)


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.os.path.abspath')
@mock.patch('app.groc.os.path.isdir', return_value=True)
@mock.patch('app.groc.utils.compile_csv_files', return_value=['foo.csv', 'bar.csv'])
@mock.patch('app.groc.db.insert_from_csv_dict', autospec=True)
def test_add_purchase_path_with_dir(
    mock_insert_csv, mock_compile_csvs, mock_os_path_is_dir, 
    mock_os_path_abspath, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.add_purchase_path('some-path', False)

    mock_insert_csv.assert_called_with(
        'some-connection', ['foo.csv', 'bar.csv'], False)


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.os.path.abspath', return_value='some-path-to-file')
@mock.patch('app.groc.os.path.isdir', return_value=False)
@mock.patch('app.groc.os.path.isfile', return_value=True)
@mock.patch('app.groc.db.insert_from_csv_dict', autospec=True)
def test_add_purchase_path_with_file(
    mock_insert_csv, mock_os_path_isfile, mock_os_path_is_dir,
    mock_os_path_abspath, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()
    g.add_purchase_path('foo.csv', False)

    mock_insert_csv.assert_called_with(
        'some-connection', ['some-path-to-file'], False)


@mock.patch('app.groc.os.path.expanduser', return_value='my-groc-dir')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.os.path.abspath', return_value='some-path-to-file')
@mock.patch('app.groc.os.path.isdir', return_value=False)
@mock.patch('app.groc.os.path.isfile', return_value=False)
@mock.patch('app.groc.db.insert_from_csv_dict', autospec=True)
def test_add_purchase_path_exception(
    mock_insert_csv, mock_os_path_isfile, mock_os_path_is_dir,
    mock_os_path_abspath, mock_create_connection, mock_os_path_expanduser
):
    g = groc.Groc()

    with pytest.raises(Exception) as e:
        g.add_purchase_path('foo', False)
    assert "some-path-to-file could not be found!" in str(e.value)
