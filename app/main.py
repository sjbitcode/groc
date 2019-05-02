import copy
import datetime
import sqlite3
import os

import click
from prettytable import from_db_cursor

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


class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = kwargs.pop('mutually_exclusive', [])
        self.required_with = kwargs.pop('required_with', [])

        if self.mutually_exclusive:
            help_text = kwargs.get('help', '')
            mutex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help_text + (
                '\n-- NOTE: This argument is mutually exclusive with'
                ' arguments: [' + mutex_str + ']'
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
            # import pdb; pdb.set_trace()
            # if set(self.required_with + [self.name]) != set(opts):

            # allows description option to be optional
            if not set(self.required_with + [self.name]).issubset(set(opts)):
                raise click.UsageError(
                    "Illegal usage: {} requires arguments: [{}]".format(
                        self.name,
                        ', '.join(self.required_with)
                    )
                )

        return super().handle_parse_result(ctx, opts, args)


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
        if g.groc_dir_exists():
            click.echo('groc directory exists')
        else:
            click.echo('Creating groc directory')
        click.echo('Attempting to create database...')
    g.init_groc()


@groc_entrypoint.command('reset', short_help='Reset database')
@click.option('--dry-run', is_flag=True)
def reset(dry_run):
    g = Groc()

    purchase_count = g.select_purchase_count()
    click.echo(f'Database reset will delete {purchase_count} purchase entries.')
    if not dry_run:
        g.clear_db()
        click.echo('Database reset successful.')


@groc_entrypoint.command('list', short_help='List purchases')
@click.option('--limit', '-l',
    type=int,
    default=50,
    show_default=True,
    help='Number of last purchases',
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['all']
)
@click.option('--month', '-m',
    type=click.DateTime(formats=['%m']),
    help='month as a two digit number'
)
@click.option('--year', '-y',
    type=click.DateTime(formats=['%Y']),
    default=(datetime.date.today().strftime('%Y')),
    show_default=True,
    help='year as a four digit number',
    cls=MutuallyExclusiveOption,
    required_with=['month']
)
@click.option('--all', '-a', is_flag=True,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['limit'],
    required_with=['month'],
    help='list all entries'
)
@click.option('--verbose', is_flag=True)
def list(limit, month, year, all, verbose):
    g = Groc()

    num_purchases = g.select_purchase_count()
    output_msg = None

    if num_purchases:
        purchases = None
        table_title = None

        if month:
            month = datetime.datetime.strftime(month, '%m')
            year = datetime.datetime.strftime(year, '%Y')
            if all:
                table_title = f'All purchases from {month}/{year}'
                purchases = g.list_purchases_date(month, year)
            else:
                table_title = f'Last {limit} purchase(s) from {month}/{year}'
                purchases = g.list_purchases_date_limit(month, year, limit)
        else:
            table_title = f'Last {limit} purchase(s)'
            purchases = g.list_purchases_limit(limit)

        table = from_db_cursor(purchases)
        table.title = table_title
        table.align['store'] = 'r'
        table.align['total'] = 'r'
        table.align['description'] = 'l'
        if verbose:
            output_msg = table.get_string()
        else:
            field_names = [name for name in table.field_names]
            field_names.remove('id')
            output_msg = table.get_string(fields=field_names)
    else:
        output_msg = 'No purchase entries available. You should add some!\nSee groc add --help to add purchases.'
    
    click.echo(output_msg)

def format_month_year(ctx, param, value):
    if value:
        if param.name == 'month':
            value = [datetime.datetime.strftime(m, '%m') for m in value]
        if param.name == 'year':
            value = [datetime.datetime.strftime(y, '%Y') for y in value]
    return value

@groc_entrypoint.command('breakdown', short_help='Show helpful stats for monthly purchases')
@click.option('--month', '-m',
    type=click.DateTime(formats=['%m']),
    multiple=True,
    show_default=True,
    help='month as a two digit number',
    callback=format_month_year
)
@click.option('--year', '-y',
    type=click.DateTime(formats=['%Y']),
    multiple=True,
    show_default=True,
    help='year as a four digit number',
    callback=format_month_year
)
@click.option('--verbose', is_flag=True)
def breakdown(month, year, verbose):
    g = Groc()

    num_purchases = g.select_purchase_count()
    output_msg = None

    if year and not month:
        month = ['0'+str(x) if len(str(x)) == 1 else str(x)
                for x in range(1, 12)]
    if not year:
        year = [datetime.date.today().strftime('%Y')]
    if not month:
        month = [datetime.date.today().strftime('%m')]

    if num_purchases:
        data = g.breakdown(month, year)
        table = from_db_cursor(data)
        field_names = [name for name in table.field_names]

        # Add a row with dashes if table empty
        temp_str = table.get_string()
        temp_table = copy.deepcopy(table)
        temp_table.clear_rows()
        if temp_str == temp_table.get_string():
            table.add_row(['--' for x in field_names])

        # Rmove columns used for db ordering
        field_names.remove('num_month')
        if not verbose:
            field_names.remove('min purchase')
            field_names.remove('max purchase')
            field_names.remove('avg purchase')
            field_names.remove('store count')
        output_msg = table.get_string(fields=field_names)
    else:
        output_msg = 'No purchase entries available. You should add some!\nSee groc add --help to add purchases.'
    
    click.echo(output_msg)

@groc_entrypoint.command('delete', short_help='Delete purchases')
@click.option('--dry-run', is_flag=True)
@click.option('--id', '-i',
    type=int,
    multiple=True,
    help='Id of purchase',
    required=True
)
@click.option('--verbose', is_flag=True)
def delete(dry_run, id, verbose):
    g = Groc()
    purchase_ids_exist = g.select_count_by_id(id).fetchall()

    if purchase_ids_exist:
        if verbose:
            purchases = g.select_by_id(id)
            table = from_db_cursor(purchases)
            table.align['store'] = 'r'
            table.align['total'] = 'r'
            table.align['description'] = 'l'
            click.echo(table)

        ids_str = ', '.join([str(row['id']) for row in purchase_ids_exist])
        click.echo(f'Deleting purchases with id(s) {ids_str}.')

        if not dry_run:
            g.delete_purchase(id)
            click.echo(f'Delete successful.')
        
    else:
        ids_str = ', '.join([str(i) for i in id])
        click.echo('No purchases with id(s) {} to be deleted.'.format(ids_str))


@groc_entrypoint.command('add', short_help='Add purchases')
@click.option('--total',
    type=float,
    help='Dollar amount of purchase',
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['source'],
    required_with=['date', 'store']
)
@click.option('--date',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help='The date of purchase',
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['source'],
    required_with=['total', 'store']
)
@click.option('--store',
    type=str,
    help='Store name where purchase was made',
    cls=MutuallyExclusiveOption,
    mutually_exclusive=['source'],
    required_with=['date', 'total']
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
    g = Groc()

    if source:
        # Get current purchase count.
        current_num_purchases = g.select_purchase_count()

        # Add purchases from path.
        g.add_purchase_path(source)

        # Get updated purchase count and calculate difference.
        updated_num_purchases = g.select_purchase_count()
        count = updated_num_purchases - current_num_purchases
        click.echo(f'Added {count} purchase(s) successfully.')
    elif date:
        g.add_purchase_manual({
            'date': date,
            'total': total,
            'store': store,
            'description': description})
        click.echo('Added 1 purchase successfully.')
    else:
        raise click.UsageError('''
        Missing option "--source" OR
        options "--date", "store", "--total", "description" required together.
        ''')

def safe_entry_point():
    try:
        groc_entrypoint()
    except Exception as e:
        click.secho(str(e), fg='red')

if __name__ == '__main__':
    safe_entry_point()



