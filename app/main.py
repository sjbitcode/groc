import datetime
import sqlite3
import os

import click

from app.connection import SQLiteConnection, PostgresConnection
from app.settings import CSV_DIR, DB_URL
from app.groc import Groc
from app import exceptions

# Connect to sqlite database.
# connection = SQLiteConnection().get_connection()

# Connect to postgres database.
# pgconnection = PostgresConnection(params = {
#   'host': 'localhost',
#   'database': os.environ.get('POSTGRES_DB', 'postgres'),
#   'user': os.environ.get('POSTGRES_USER', 'postgres'),
#   'password': os.environ.get('POSTGRES_PASSWORD', 'postgres')}).get_connection()

def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


# Click CLI
@click.group()
@click.pass_context
def groc_entrypoint(ctx):
    """
    A simple bill tracking tool to help you review and analyze purchases.
    """
    ctx.obj = {}


@groc_entrypoint.command('init', short_help='Create database in groc directory')
@click.option('--verbose', is_flag=True)
def init(verbose):
    g = Groc()
    if verbose:
        click.echo('Groc directory exists') if g.groc_dir_exists() else click.echo('Creating groc directory')
        click.echo('Attempting create database...')
    g.init_groc()


@groc_entrypoint.command('reset', short_help='Reset database')
@click.option('--verbose', is_flag=True)
@click.option('--dry-run', is_flag=True)
def reset(verbose, dry_run):
    g = Groc()
    if verbose:
        click.echo('Attempting to delete all data from database')
    # g.clear_db()
    if dry_run:
        click.echo('You will be deleting some stuff!')
    else:
        g.clear_db()


@groc_entrypoint.command('list', short_help='List purchases')
@click.option('--limit', '-l',
    type=int,
    default=50,
    show_default=True,
    help='Number of last purchases'
)
@click.option('--verbose', is_flag=True)
def list(limit, verbose):
    if verbose:
        click.echo('Verbose mode')
    click.echo('List purchases')
    if limit:
        click.echo(limit)
        click.echo(type(limit))


@groc_entrypoint.command('delete', short_help='Delete purchases')
@click.option('--dry-run', is_flag=True)
@click.option('--id', '-i',
    type=int,
    multiple=True,
    help='Id of purchase',
    required=True
)
def delete(dry_run, id):
    if dry_run:
        click.echo('Dry run')
    click.echo('Deleting purchase {}'.format(id))


class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = kwargs.pop('mutually_exclusive', [])
        self.required_with = kwargs.pop('required_with', [])


        if self.mutually_exclusive:
            help_text = kwargs.get('help', '')
            mutex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help_text + (
                '\n-- NOTE: This argument is mutually exclusive with'
                ' arguments: [' + mutex_str +']'
            )

        if self.required_with:
            help_text = kwargs.get('help', '')
            req_opts_str = ', '.join(self.required_with)
            kwargs['help'] = help_text + (
                '\n-- NOTE: This argument is required with'
                ' arguments: [' + req_opts_str + ']'
            )

        super().__init__(*args, **kwargs)


    def handle_parse_result(self, ctx, opts, args):
        if set(self.mutually_exclusive).intersection(opts) and self.name in opts:
            raise click.UsageError(
                "Illegal usage: {} is mutually exclusive with "
                "arguments: [{}]".format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )
        
        if self.name in opts.keys():
            if set(self.required_with + [self.name]) != set(opts):
                raise click.UsageError(
                    "Illegal usage: {} requires arguments: [{}]".format(
                        self.name,
                        ', '.join(self.required_with)
                    )
                )

        return super().handle_parse_result(ctx, opts, args)


@groc_entrypoint.command('add', short_help='Add purchases')
@click.option('--total',
    type=float,
    help='Dollar amount of purchase',
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['source'],
    required_with=['date', 'store', 'description']
)
@click.option('--date',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help='The date of purchase',
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['source'],
    required_with=['total', 'store', 'description']
)
@click.option('--store',
    type=str,
    help='Store name where purchase was made',
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['source'],
    required_with=['date', 'total', 'description']
)
@click.option('--description',
    type=str,
    help='Brief description of purchase',
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['source'],
    required_with=['date', 'total', 'store']
)
@click.option('--source',
    type=click.Path(),
    help='File or directory',
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['date', 'total', 'store', 'description']
)
def add(date, total, store, description, source):
    """
    Add a purchase via command line, file, or directory
    """
    click.echo('Add a purchase manually or by file')
    if source:
        click.echo('Got a source')
    elif date:
        click.echo(date.strftime('%Y-%m-%d'))
        click.echo(total)
        click.echo(store)
        click.echo(description)
    else:
        raise click.UsageError('''
        Missing option "--source" OR
        options "--date", "store", "--total", "description" required together.
        ''')

@groc_entrypoint.command('breakdown', short_help='Show helpful stats for monthly purchases')
@click.option('--month', '-m',
    default=(datetime.date.today().strftime('%m'),),
    type=click.DateTime(formats=['%m']),
    multiple=True,
    show_default=True,
    help='month as a two digit number')
def breakdown(month):
    click.echo('Breakdown command')
    click.echo(type(month))
    for m in month:
        click.echo(m.strftime('%m'))

def safe_entry_point():
    try:
        click.secho('trying your command', fg='green')
        groc_entrypoint()
    except Exception as e:
        click.secho(str(e), fg='red')

if __name__ == '__main__':
    # groc_entrypoint()

    safe_entry_point()



