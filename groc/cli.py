import copy
import datetime

import click
from prettytable import from_db_cursor

from .models import Groc


class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = kwargs.pop('mutually_exclusive', [])
        self.required_with = kwargs.pop('required_with', [])

        # Modify help texts
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


# Click CLI
@click.group()
@click.version_option()
@click.pass_context
def groc_entrypoint(ctx):
    """
    A simple bill tracking tool to help you review and analyze purchases.
    """
    ctx.obj = {}


@groc_entrypoint.command('init', short_help='Create database in groc directory')
@click.option('--verbose', is_flag=True)
def init(verbose):
    """
    Set up Groc!

    Creates the groc directory in User directory and
    creates the groc database inside groc directory.
    Use the verbose flag to see extra output statements.
    \f
    Args:
        verbose (bool): Flag to output extra output statements.
    """
    g = Groc()

    if verbose:
        if g.groc_dir_exists():
            click.echo('Groc directory exists')
        else:
            click.echo('Creating groc directory')
        click.echo('Attempting to create database...')
    g.init_groc()


@groc_entrypoint.command('reset', short_help='Reset database')
@click.option('--dry-run', is_flag=True)
def reset(dry_run):
    """
    Deletes all purchase entries.

    Use the dry-run flag to see how many purchase exists without
    actually deleting them.
    \f
    Args:
        dry_run (bool): flag to toggle real deletion of purchases.
    """
    g = Groc()
    purchase_count = g.select_purchase_count()

    click.echo(f'Database reset will delete {purchase_count} purchase entries.')

    if not dry_run:
        g.clear_db()
        click.echo('Database reset successful.')


def check_limit(ctx, param, value):
    return 100 if value > 100 else value


@groc_entrypoint.command('list', short_help='List purchases')
@click.option('--limit', '-l',
              type=int,
              default=50,
              show_default=True,
              help='Number of last purchases. Maximum 100 allowed.',
              cls=MutuallyExclusiveOption,
              mutually_exclusive=['all'],
              callback=check_limit)
@click.option('--month', '-m',
              type=click.DateTime(formats=['%m']),
              help='month as a two digit number')
@click.option('--year', '-y',
              type=click.DateTime(formats=['%Y']),
              default=(datetime.date.today().strftime('%Y')),
              show_default=True,
              help='year as a four digit number',
              cls=MutuallyExclusiveOption,
              required_with=['month'])
@click.option('--all', '-a', is_flag=True,
              cls=MutuallyExclusiveOption,
              mutually_exclusive=['limit'],
              required_with=['month'],
              help='list all entries')
@click.option('--verbose', is_flag=True)
def list(limit, month, year, all, verbose):
    """
    View a list of purchases. You have three options to do so:

    (1) You can see the latest purchases limited by an amount, OR
    (2) You can see all purchases for a month and year pair, OR
    (3) You can see purchases for a  month and year pair by limit.
    Limit maximum is 100.

    If a month is passed, the year is default to current year.
    A year cannot be passed without a month.
    Pass the all flag to get all purchases for that month/year.
    \f
    Args:
        limit (int): Limit number for purchases.
        month (str): Two digit month.
        year (str): Four digit year.
        all (bool): Flag to show all purchases for a month/year.
        verbose (bool): Flag to show purchase ids too.
    """
    g = Groc()

    num_purchases = g.select_purchase_count()
    output_msg = None

    # If there are purchases in db
    if num_purchases:
        purchases = None  # to hold cursor object
        table_title = None  # to hold table title depending on query

        # If month passed, get either all purchases for month/year
        # or limited purchases for month/year depending on if 'all' flag
        if month:
            month = datetime.datetime.strftime(month, '%m')
            year = datetime.datetime.strftime(year, '%Y')
            if all:
                table_title = f'All purchases from {month}/{year}'
                purchases = g.list_purchases_date(month, year)
            else:
                table_title = f'Last {limit} purchase(s) from {month}/{year}'
                purchases = g.list_purchases_date_limit(month, year, limit)
        # Get latest purchases by limit amount
        else:
            table_title = f'Last {limit} purchase(s)'
            purchases = g.list_purchases_limit(limit)

        # Format output table
        table = from_db_cursor(purchases)
        table.title = table_title
        table.align['store'] = 'r'
        table.align['total'] = 'r'
        table.align['description'] = 'l'

        # If verbose flag, show all table fields, else remove id field
        if verbose:
            output_msg = table.get_string()
        else:
            field_names = [name for name in table.field_names]
            field_names.remove('id')
            output_msg = table.get_string(fields=field_names)

    # If no purchases in db
    else:
        output_msg = 'No purchase entries available. You should add some!\nSee groc add --help to add purchases.'

    click.echo(output_msg)


def format_month_year(ctx, param, value):
    """
    If month or year arguments passed,
    format the datetime object into strings
    and return in a list.
    """
    if value:
        if param.name == 'month':
            value = [datetime.datetime.strftime(m, '%m') for m in value]
        if param.name == 'year':
            value = [datetime.datetime.strftime(y, '%Y') for y in value]
    return value


@groc_entrypoint.command('breakdown',
                         short_help='Show helpful stats for monthly purchases')
@click.option('--month', '-m',
              type=click.DateTime(formats=['%m']),
              multiple=True,
              help='month as a two digit number',
              callback=format_month_year)
@click.option('--year', '-y',
              type=click.DateTime(formats=['%Y']),
              multiple=True,
              help='year as a four digit number',
              callback=format_month_year)
@click.option('--verbose', is_flag=True)
def breakdown(month, year, verbose):
    """
    View helpful stats for purchases grouped by month.

    Stats are defaulted for current month and current year.
    You can also pass a combination of multiple months and years using the
    month and year flags.

    If a single month is passed, you will view breakdown for
    the month for all years.
    If a single year is passed, you will view breakdown for
    all months for that year.
    Pass multiple months and multiple years to target those
    month and year pairs.

    Use the verbose flag to see extended stats.
    \f
    Args:
        month (str): Two digit month.
        year (str): Four digit year.
        verbose (bool): Flag to show extended stats.
    """
    g = Groc()

    num_purchases = g.select_purchase_count()
    output_msg = None

    # Format month and year params
    if year and not month:
        # click.echo('all months for all years')
        month = ['0'+str(x) if len(str(x)) == 1 else str(x)
                 for x in range(1, 13)]
        # click.echo(f'months --> {month}')
        # click.echo(f'year --> {year}')
    if not year:
        year = [datetime.date.today().strftime('%Y')]
    if not month:
        month = [datetime.date.today().strftime('%m')]

    # If there are purchases in db
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

    # If no purchases in db
    else:
        output_msg = 'No purchase entries available. You should add some!\nSee groc add --help to add purchases.'

    click.echo(output_msg)


@groc_entrypoint.command('delete', short_help='Delete purchases')
@click.option('--dry-run', is_flag=True)
@click.option('--id', '-i',
              type=int,
              multiple=True,
              help='Id of purchase',
              required=True)
@click.option('--verbose', is_flag=True)
def delete(dry_run, id, verbose):
    """
    Delete purchases based on id.

    Use the dry-run flag to see what purchases will be deleted.
    Use the verbose flag to see purchase details.
    \f
    Args:
        id (tuple): Purchase ids.
        dry_run (bool): See purchases that would be deleted.
        verbose (bool): See purchase details.
    """
    g = Groc()
    purchase_ids = g.select_purchase_ids(id).fetchall()

    # If any of the purchases exist
    if purchase_ids:

        # Format an output table with purchase details
        if verbose:
            purchases = g.select_by_id(id)
            table = from_db_cursor(purchases)
            table.align['store'] = 'r'
            table.align['total'] = 'r'
            table.align['description'] = 'l'
            click.echo(table)

        # Output this string regardless of dry-run or not
        ids_str = ', '.join([str(row['id']) for row in purchase_ids])
        click.echo(f'Deleting purchases with id(s) {ids_str}.')

        if not dry_run:
            g.delete_purchase(id)
            click.echo(f'Delete successful.')

    # None of purchase ids exist
    else:
        ids_str = ', '.join([str(i) for i in id])
        click.echo('No purchases with id(s) {} to be deleted.'.format(ids_str))


@groc_entrypoint.command('add', short_help='Add purchases')
@click.option('--total',
              type=float,
              help='Dollar amount of purchase',
              cls=MutuallyExclusiveOption,
              mutually_exclusive=['source'],
              required_with=['store'])
@click.option('--date',
              type=click.DateTime(formats=['%Y-%m-%d']),
              default=(datetime.date.today().strftime('%Y-%m-%d')),
              show_default=True,
              help='The date of purchase',
              cls=MutuallyExclusiveOption,
              mutually_exclusive=['source'],
              required_with=['total', 'store'])
@click.option('--store',
              type=str,
              help='Store name where purchase was made',
              cls=MutuallyExclusiveOption,
              mutually_exclusive=['source'],
              required_with=['total'])
@click.option('--description',
              type=str,
              help='Brief description of purchase',
              cls=MutuallyExclusiveOption,
              mutually_exclusive=['source'],
              required_with=['total', 'store'])
@click.option('--source',
              type=click.Path(),
              help='File or directory',
              cls=MutuallyExclusiveOption,
              mutually_exclusive=['date', 'total', 'store', 'description'])
@click.option('--ignore-duplicate', is_flag=True)
def add(date, total, store, description, source, ignore_duplicate):
    """
    Add purchases via command line, file, or directory.

    Via commandline, you can only add a single purchase.
    Commandline arguments are store, total, date, and description.
    Store and total fields required. If date not passed,
    its defaulted to current date. Description is
    optional.

    By file or directory, supply the path via source argument.
    If path points to directory, all csv files are read.
    \f
    Args:
        date (str): format 'Y-m-d'. Will default to today's date.
                   Gets processed as a datetime.datetime object.
        description (str): Purchase note. Optional.
        total (float): Purchase total.
        store (str): Purchase store.
    """
    g = Groc()

    if source:
        count = g.add_purchase_path(source, ignore_duplicate)
        click.echo(f'Added {count} purchase(s) successfully.')

    # if one of required fields from (store, total, description, date)
    elif store:
        success = g.add_purchase_manual({
            'date': date,
            'total': total,
            'store': store,
            'description': description}, ignore_duplicate)
        count = 1 if success else 0
        click.echo(f'Added {count} purchase successfully.')

    # either source 0R (store, total) required
    else:
        raise click.UsageError('''
        Missing option "--source" OR
        options "--date", "store", "--total", "description" required together.
        ''')


def safe_entry_point():
    try:
        groc_entrypoint()
    except Exception as e:
        # Echo the exception message
        click.secho(str(e), fg='red')


if __name__ == '__main__':
    safe_entry_point()
