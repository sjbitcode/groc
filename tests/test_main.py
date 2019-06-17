from unittest import mock

from click.testing import CliRunner

from app.main import groc_entrypoint as groc_cli
from app import exceptions, groc


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


