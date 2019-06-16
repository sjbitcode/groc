from unittest import mock

from app import groc


@mock.patch('app.groc.Groc._get_db_url', return_value='some-db-url')
@mock.patch('app.groc.db.create_connection', return_value='some-connection')
def test_get_connection_called_with_db_url(mock_create_connection, mock_get_db_url):
    groc.Groc()
    mock_create_connection.assert_called_with('some-db-url')


@mock.patch('app.groc.db.create_connection')
@mock.patch('app.groc.os.path.expanduser', return_value='/my/groc/dir')
def test_get_db_url(mock_os_path_expanduser, mock_create_connection):
    g = groc.Groc()
    assert g._get_db_url() == '/my/groc/dir/groc.db'


@mock.patch('app.groc.db.create_connection', return_value='some-connection')
@mock.patch('app.groc.db.setup_db')
def test_create_and_setup_db_called_with_connection(mock_setup_db, mock_create_connection):
    g = groc.Groc()
    g._create_and_setup_db()
    mock_setup_db.assert_called_with('some-connection')


@mock.patch('app.groc.db.create_connection')
@mock.patch('app.groc.os.path.expanduser', return_value='/my/groc/dir')
@mock.patch('app.groc.os.path.exists')
def test_groc_dir_exists(mock_os_path_exists, mock_os_path_expanduser, mock_create_connection):
    g = groc.Groc()
    g.groc_dir_exists()
    mock_os_path_exists.assert_called_with('/my/groc/dir')




