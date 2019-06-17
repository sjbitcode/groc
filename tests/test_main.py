from unittest import mock

from click.testing import CliRunner
from prettytable import from_db_cursor

from app.main import groc_entrypoint as groc_cli
from app import db, exceptions, groc


def test_hi():
    runner = CliRunner()
    result = runner.invoke(groc_cli, ['hi', 'Sangeeta'])
    assert result.exit_code == 0
    assert result.output == 'Hello Sangeeta!\n'


@mock.patch('app.main.Groc._get_db_url')
@mock.patch('app.main.Groc._get_connection')
@mock.patch('app.main.Groc.groc_dir_exists', return_value=True, autospec=True)
@mock.patch('app.main.Groc.init_groc', autospec=True)
def test_init_groc_dir_exists(groc_init, groc_dir_exists, groc_connection, groc_db_url):
    groc.Groc()
    runner = CliRunner()

    result = runner.invoke(groc_cli, ['init', '--verbose'])
    assert result.exit_code == 0
    assert result.output == ('Groc directory exists\n'
                             'Attempting to create database...\n')


@mock.patch('app.main.Groc._get_db_url')
@mock.patch('app.main.Groc._get_connection')
@mock.patch('app.main.Groc.groc_dir_exists', return_value=False, autospec=True)
@mock.patch('app.main.Groc.init_groc', autospec=True)
def test_init(groc_init, groc_dir_exists, groc_connection, groc_db_url):
    groc.Groc()
    runner = CliRunner()

    result = runner.invoke(groc_cli, ['init', '--verbose'])
    assert result.exit_code == 0
    assert result.output == ('Creating groc directory\n'
                             'Attempting to create database...\n')


@mock.patch('app.main.Groc._get_db_url')
@mock.patch('app.main.Groc._get_connection')
@mock.patch('app.main.Groc.select_purchase_count', return_value=10, autospec=True)
@mock.patch('app.main.Groc.clear_db')
def test_reset_dry_run(groc_clear, groc_purchase_count, groc_connection, groc_db_url):
    groc.Groc()
    runner = CliRunner()
    result = runner.invoke(groc_cli, ['reset', '--dry-run'])
    assert result.exit_code == 0
    assert result.output == 'Database reset will delete 10 purchase entries.\n'


@mock.patch('app.main.Groc._get_db_url')
@mock.patch('app.main.Groc._get_connection')
@mock.patch('app.main.Groc.select_purchase_count', return_value=10, autospec=True)
@mock.patch('app.main.Groc.clear_db')
def test_reset(groc_clear, groc_purchase_count, groc_connection, groc_db_url):
    groc.Groc()
    runner = CliRunner()
    result = runner.invoke(groc_cli, ['reset'])
    assert result.exit_code == 0
    assert result.output == ('Database reset will delete 10 purchase entries.\n'
                             'Database reset successful.\n')


@mock.patch('app.main.Groc._get_db_url')
@mock.patch('app.main.Groc._get_connection')
@mock.patch('app.main.Groc.select_purchase_count', return_value=0, autospec=True)
def test_list_limit_no_purchases(
        groc_purchase_count, groc_connection, groc_db_url):
    groc.Groc()

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['list', '--verbose'])
    assert result.exit_code == 0
    assert result.output == 'No purchase entries available. You should add some!\nSee groc add --help to add purchases.\n'


@mock.patch('app.main.Groc._get_db_url')
@mock.patch('app.main.Groc._get_connection')
@mock.patch('app.main.Groc.select_purchase_count', return_value=9, autospec=True)
@mock.patch('app.main.Groc.list_purchases_limit', autospec=True)
def test_list_limit_more_than_100(
        groc_purchase_limit, groc_purchase_count, groc_connection,
        groc_db_url, connection_function_scope, stores_and_purchases_function_scope):
    groc_connection.return_value = connection_function_scope
    g = groc.Groc()

    # Make table
    table = from_db_cursor(g.list_purchases_limit(101))
    table.title = f'Last 50 purchase(s)'
    table.align['store'] = 'r'
    table.align['total'] = 'r'
    table.align['description'] = 'l'

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['list', '--verbose'])
    assert result.exit_code == 0
    assert result.output == f'{table.get_string()}\n'


@mock.patch('app.main.Groc._get_db_url')
@mock.patch('app.main.Groc._get_connection')
@mock.patch('app.main.Groc.select_purchase_count', return_value=9, autospec=True)
@mock.patch('app.main.Groc.list_purchases_limit', autospec=True)
def test_list_limit_default(
        groc_purchase_limit, groc_purchase_count, groc_connection, 
        groc_db_url, connection_function_scope, stores_and_purchases_function_scope):
    groc_connection.return_value = connection_function_scope
    g = groc.Groc()

    # Make table
    table = from_db_cursor(g.list_purchases_limit(50))
    table.title = f'Last 50 purchase(s)'
    table.align['store'] = 'r'
    table.align['total'] = 'r'
    table.align['description'] = 'l'

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['list', '--verbose'])
    assert result.exit_code == 0
    assert result.output == f'{table.get_string()}\n'


@mock.patch('app.main.Groc._get_db_url')
@mock.patch('app.main.Groc._get_connection')
@mock.patch('app.main.Groc.select_purchase_count', return_value=9, autospec=True)
def test_list_limit_default_no_verbose(
    groc_purchase_count, groc_connection,
    groc_db_url, connection_function_scope,
    stores_and_purchases_function_scope
):
    groc_connection.return_value = connection_function_scope
    g = groc.Groc()

    # Make table
    purchases = g.list_purchases_limit(50)
    table = from_db_cursor(purchases)
    table.title = f'Last 50 purchase(s)'
    table.align['store'] = 'r'
    table.align['total'] = 'r'
    table.align['description'] = 'l'
    field_names = [name for name in table.field_names]
    field_names.remove('id')

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['list'])
    assert result.exit_code == 0
    assert result.output == f'{table.get_string(fields=field_names)}\n'
