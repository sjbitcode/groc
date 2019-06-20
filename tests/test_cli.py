import copy
import datetime
from unittest import mock

from click.testing import CliRunner
from prettytable import from_db_cursor

from groc.cli import groc_entrypoint as groc_cli
from groc.models import Groc


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
@mock.patch('groc.cli.Groc.groc_dir_exists', return_value=True, autospec=True)
@mock.patch('groc.cli.Groc.init_groc', autospec=True)
def test_init_groc_dir_exists(groc_init, groc_dir_exists, groc_connection,
                              groc_db_url):
    _ = Groc()
    runner = CliRunner()

    result = runner.invoke(groc_cli, ['init', '--verbose'])
    assert result.exit_code == 0
    assert result.output == ('Groc directory exists\n'
                             'Attempting to create database...\n')


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
@mock.patch('groc.cli.Groc.groc_dir_exists', return_value=False, autospec=True)
@mock.patch('groc.cli.Groc.init_groc', autospec=True)
def test_init(groc_init, groc_dir_exists, groc_connection, groc_db_url):
    _ = Groc()
    runner = CliRunner()

    result = runner.invoke(groc_cli, ['init', '--verbose'])
    assert result.exit_code == 0
    assert result.output == ('Creating groc directory\n'
                             'Attempting to create database...\n')


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
@mock.patch('groc.cli.Groc.select_purchase_count', return_value=10, autospec=True)
@mock.patch('groc.cli.Groc.clear_db')
def test_reset_dry_run(groc_clear, groc_purchase_count, groc_connection,
                       groc_db_url):
    _ = Groc()
    runner = CliRunner()
    result = runner.invoke(groc_cli, ['reset', '--dry-run'])
    assert result.exit_code == 0
    assert result.output == 'Database reset will delete 10 purchase entries.\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
@mock.patch('groc.cli.Groc.select_purchase_count', return_value=10, autospec=True)
@mock.patch('groc.cli.Groc.clear_db')
def test_reset(groc_clear, groc_purchase_count, groc_connection, groc_db_url):
    _ = Groc()
    runner = CliRunner()
    result = runner.invoke(groc_cli, ['reset'])
    assert result.exit_code == 0
    assert result.output == ('Database reset will delete 10 purchase entries.\n'
                             'Database reset successful.\n')


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
@mock.patch('groc.cli.Groc.select_purchase_count', return_value=0, autospec=True)
def test_list_limit_no_purchases(groc_purchase_count, groc_connection, 
                                 groc_db_url):
    _ = Groc()

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['list', '--verbose'])
    assert result.exit_code == 0
    assert result.output == 'No purchase entries available. You should add some!\nSee groc add --help to add purchases.\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_list_limit_more_than_100(groc_connection, groc_db_url, 
                                  connection_function_scope, 
                                  stores_and_purchases_function_scope):
    groc_connection.return_value = connection_function_scope
    g = Groc()

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


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_list_limit_default(groc_connection, groc_db_url, 
                            connection_function_scope, 
                            stores_and_purchases_function_scope):
    groc_connection.return_value = connection_function_scope
    g = Groc()

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


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_list_limit_default_no_verbose(groc_connection, groc_db_url,
                                       connection_function_scope,
                                       stores_and_purchases_function_scope):
    groc_connection.return_value = connection_function_scope
    g = Groc()

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


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_list_month_year_all_verbose(groc_connection, groc_db_url,
                                     connection_function_scope,
                                     stores_and_purchases_function_scope):

    groc_connection.return_value = connection_function_scope
    g = Groc()

    # Make table for Jan 2019 purchases (3 total)
    month, year = '01', '2019'
    purchases = g.list_purchases_date(month, year)
    table = from_db_cursor(purchases)
    table.title = f'All purchases from {month}/{year}'
    table.align['store'] = 'r'
    table.align['total'] = 'r'
    table.align['description'] = 'l'

    runner = CliRunner()
    result = runner.invoke(
        groc_cli, ['list', '-m', '01', '-y', '2019', '--all', '--verbose'])
    assert result.exit_code == 0
    assert result.output == f'{table.get_string()}\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_list_month_year_limit_verbose(groc_connection, groc_db_url,
                                       connection_function_scope,
                                       stores_and_purchases_function_scope):

    groc_connection.return_value = connection_function_scope
    g = Groc()

    # Make table for Jan 2019 purchases limit by 1
    month, year, limit = '01', '2019', 1
    purchases = g.list_purchases_date_limit(month, year, limit)
    table = from_db_cursor(purchases)
    table.title = f'Last {limit} purchase(s) from {month}/{year}'
    table.align['store'] = 'r'
    table.align['total'] = 'r'
    table.align['description'] = 'l'

    runner = CliRunner()
    result = runner.invoke(
        groc_cli, ['list', '-m', '01', '-y', '2019', '-l', 1, '--verbose'])
    assert result.exit_code == 0
    assert result.output == f'{table.get_string()}\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
@mock.patch('groc.cli.Groc.select_purchase_count', return_value=0)
def test_breakdown_no_purchases(groc_purchase_count, groc_connection, 
                                groc_db_url):

    _ = Groc()

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['breakdown'])
    assert result.exit_code == 0
    assert result.output == f'No purchase entries available. You should add some!\nSee groc add --help to add purchases.\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_breakdown_default(groc_connection, groc_db_url,
                           connection_function_scope,
                           stores_and_purchases_function_scope):

    groc_connection.return_value = connection_function_scope
    g = Groc()
    today = datetime.date.today()
    month, year = [today.strftime('%m')], [today.strftime('%Y')]

    data = g.breakdown(month, year)
    table = from_db_cursor(data)
    field_names = [name for name in table.field_names]

    # No purchases exist for the current month.
    # Add a row with dashes if table empty
    temp_str = table.get_string()
    temp_table = copy.deepcopy(table)
    temp_table.clear_rows()
    if temp_str == temp_table.get_string():
        table.add_row(['--' for x in field_names])

    # Rmove columns used for db ordering
    field_names.remove('num_month')
    field_names.remove('min purchase')
    field_names.remove('max purchase')
    field_names.remove('avg purchase')
    field_names.remove('store count')
    output_msg = table.get_string(fields=field_names)

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['breakdown'])
    assert result.exit_code == 0
    assert result.output == f'{output_msg}\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_breakdown_year_no_month_verbose(groc_connection, groc_db_url,
                                         connection_function_scope,
                                         stores_and_purchases_function_scope):

    groc_connection.return_value = connection_function_scope
    g = Groc()
    month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', 
             '12']
    year = ['2019']

    data = g.breakdown(month, year)
    table = from_db_cursor(data)
    field_names = [name for name in table.field_names]

    # Rmove columns used for db ordering
    field_names.remove('num_month')
    output_msg = table.get_string(fields=field_names)

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['breakdown', '-y', '2019', '--verbose'])
    assert result.exit_code == 0
    assert result.output == f'{output_msg}\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_breakdown_year_month_year_verbose(groc_connection, groc_db_url,
                                           connection_function_scope,
                                           stores_and_purchases_function_scope):

    groc_connection.return_value = connection_function_scope
    g = Groc()
    month, year = ['01', '02'], ['2019']

    data = g.breakdown(month, year)
    table = from_db_cursor(data)
    field_names = [name for name in table.field_names]

    # Rmove columns used for db ordering
    field_names.remove('num_month')
    output_msg = table.get_string(fields=field_names)

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['breakdown', '-m', '01', '-m', '02',
                                      '-y', '2019', '--verbose'])
    assert result.exit_code == 0
    assert result.output == f'{output_msg}\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
@mock.patch('groc.cli.Groc.select_purchase_ids')
def test_delete_no_purchases(groc_select_purchase_ids, groc_connection, 
                             groc_db_url, cursor_function_scope):
    groc_select_purchase_ids.return_value = cursor_function_scope
    _ = Groc()
    id = 1

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['delete', '--id', 1])
    assert result.exit_code == 0
    assert result.output == f'No purchases with id(s) {id} to be deleted.\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_delete_purchases_verbose(groc_connection, groc_db_url,
                                  connection_function_scope,
                                  stores_and_purchases_function_scope):

    groc_connection.return_value = connection_function_scope

    # Get a purchase id
    cursor = groc_connection().cursor()
    res = cursor.execute('SELECT id FROM purchase LIMIT 1;').fetchone()
    id = (res['id'])

    g = Groc()

    purchases = g.select_by_id((id,))
    table = from_db_cursor(purchases)
    table.align['store'] = 'r'
    table.align['total'] = 'r'
    table.align['description'] = 'l'

    # Output this string regardless of dry-run or not
    delete_msg = f'Deleting purchases with id(s) {id}.'
    delete_conf = f'Delete successful.'

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['delete', '--id', id, '--verbose'])
    assert result.exit_code == 0
    assert result.output == f'{table}\n{delete_msg}\n{delete_conf}\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_delete_purchases_verbose_dry_run(groc_connection, groc_db_url,
                                          connection_function_scope,
                                          stores_and_purchases_function_scope):

    groc_connection.return_value = connection_function_scope

    # Get a purchase id
    cursor = groc_connection().cursor()
    res = cursor.execute('SELECT id FROM purchase LIMIT 1;').fetchone()
    id = (res['id'])

    g = Groc()

    purchases = g.select_by_id((id,))
    table = from_db_cursor(purchases)
    table.align['store'] = 'r'
    table.align['total'] = 'r'
    table.align['description'] = 'l'

    # Output this string regardless of dry-run or not
    delete_msg = f'Deleting purchases with id(s) {id}.'

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['delete', '--id', id, '--verbose', '--dry-run'])
    assert result.exit_code == 0
    assert result.output == f'{table}\n{delete_msg}\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_add_no_args(groc_connection, groc_db_url):

    runner = CliRunner()
    result = runner.invoke(groc_cli, ['add'])
    from click import UsageError
    assert result.exit_code == UsageError.exit_code


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_add_manual(groc_connection, groc_db_url, connection_function_scope):
    groc_connection.return_value = connection_function_scope
    _ = Groc()

    runner = CliRunner()
    result = runner.invoke(
        groc_cli, ['add',
                   '--date', '2019-01-01',
                   '--total', 20.00,
                   '--store', 'Whole Foods',
                   '--description', 'bread']
    )
    assert result.exit_code == 0
    assert result.output == f'Added 1 purchase successfully.\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_add_manual_ignore_duplicate(groc_connection, groc_db_url,
                                     connection_function_scope,
                                     stores_and_purchases_function_scope):
    groc_connection.return_value = connection_function_scope
    _ = Groc()

    runner = CliRunner()
    # Adding a duplicate purchase from pytest fixture
    result = runner.invoke(
        groc_cli, ['add',
                   '--date', '2019-01-01',
                   '--total', 100.00,
                   '--store', 'Whole Foods',
                   '--ignore-duplicate']
    )
    assert result.exit_code == 0
    assert result.output == f'Added 0 purchase successfully.\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_add_file(groc_connection, groc_db_url, connection_function_scope,
                  stores_and_purchases_function_scope,
                  create_purchase_csvs):

    groc_connection.return_value = connection_function_scope
    _ = Groc()
    file_path = create_purchase_csvs[0]

    output = (
        f'Importing data from {file_path}\n'
        f'2 purchase(s) added\n'
        f'Added 2 purchase(s) successfully.'
    )

    runner = CliRunner()
    result = runner.invoke(
        groc_cli, ['add', '--source', file_path]
    )
    assert result.exit_code == 0
    assert result.output == f'{output}\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_add_dir(groc_connection, groc_db_url, connection_function_scope,
                 purchase_csv_dir):

    groc_connection.return_value = connection_function_scope
    _ = Groc()
    dir_path = purchase_csv_dir
    files = purchase_csv_dir.listdir()

    output = (
        f'Importing data from {files[0]}\n'
        f'2 purchase(s) added\n'
        f'Importing data from {files[1]}\n'
        f'2 purchase(s) added\n'
        f'Added 4 purchase(s) successfully.'
    )

    runner = CliRunner()
    result = runner.invoke(
        groc_cli, ['add', '--source', dir_path]
    )
    assert result.exit_code == 0
    assert result.output == f'{output}\n'


@mock.patch('groc.cli.Groc._get_db_url')
@mock.patch('groc.cli.Groc._get_connection')
def test_add_dir_with_duplicate_purchase(groc_connection, groc_db_url,
                                         connection_function_scope,
                                         create_purchase_csvs,
                                         add_csv_file_with_duplicate,
                                         purchase_csv_dir):

    groc_connection.return_value = connection_function_scope
    _ = Groc()
    dir_path = purchase_csv_dir

    files = purchase_csv_dir.listdir()

    output = (
        f'Importing data from {files[0]}\n'
        f'2 purchase(s) added\n'
        f'Importing data from {files[1]}\n'
        f'2 purchase(s) added\n'
        f'Importing data from {files[2]}'
    )
    exc_str = 'Duplicate purchase detected -- '\
              '(date: 2019-01-03, store: Store Bar, ' \
              'total: 25.00, description: bars)'

    runner = CliRunner()
    result = runner.invoke(
        groc_cli, ['add', '--source', dir_path]
    )
    assert result.exit_code == 1
    assert result.output == f'{output}\n'
    assert result.exception.__str__() == exc_str


def test_add_manual_and_source():
    runner = CliRunner()
    result = runner.invoke(
        groc_cli, ['add', '--source', 'my_csvs', '--date', '2019-01-01']
    )
    assert result.exit_code == 2
    assert result.output == 'Error: Illegal usage: source is ' \
                            'mutually exclusive with arguments:' \
                            ' [date, total, store, description]\n'


def test_add_date_field_only():
    runner = CliRunner()
    result = runner.invoke(
        groc_cli, ['add', '--date', '2019-01-01']
    )
    assert result.exit_code == 2
    assert result.output == 'Error: Illegal usage: date ' \
                            'requires arguments:' \
                            ' [total, store]\n'
