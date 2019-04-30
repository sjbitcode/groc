import csv
import datetime
import os
import sqlite3

from unidecode import unidecode

from app.exceptions import GrocException, InvalidRowException, RowIntegrityError
from app.settings import BASE_DIR, CSV_DIR


def dollar_to_cents(dollar):
    """
    Convert a dollar amount (float) to cents (integer).

    :param dollar: A string or float representing dollar amount
    :return: An integer representing amount as cents.
    :raises ValueError or TypeError if value cannot be casted to float.
    """
    try:
        return int(round(float(dollar)*100))
    except Exception as e:
        raise Exception(f'Total value could not convert to float: \'{dollar}\'') from e
    # return round(float(dollar) * 100)


def convert_unicode_whitespace(val):
    return unidecode(val).strip()

def clean_row_value(x):
        if isinstance(x, str):
            if x == '':
                return None
            else:
                return convert_unicode_whitespace(x)
        return x

def clean_row_strings(row):
    """
    Clean row of data from csv by converting unicode characters to ASCII
    and strip whitespaces.

    :param row: List of strings read in from csv
    :return: List of cleaned strings
    """
    # clean = lambda x: unidecode(x).lstrip().rstrip()
    # clean = lambda x: unidecode(x).strip()
    # return [clean(s) if isinstance(s, str) else s for s in row]

    return {key: clean_row_value(row[key]) for key in row.keys()}

    # return {
    #     key: convert_unicode_whitespace(row[key])
    #     if isinstance(row[key], str) else row[key] 
    #     for key in row.keys()
    # }


def format_total(total):
    """
    Update the total and description values of csv row.
    Convert total to integer.
    Ensure that description value is nonempty.

    :param row: Row from csv file
    :return: Row with total and description validated
    """
    return dollar_to_cents(total)
    # row['description'] = row['description'] or 'grocery'
    # row[2] = dollar_to_cents(row[2])
    # row[3] = row[3] or 'grocery'
    # return row


def format_date(date):
    try:
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d')

        if isinstance(date, datetime.datetime):
            return datetime.date(date.year, date.month, date.day)
    except Exception as e:
        raise Exception(f'Date value should be able to convert to datetime: Got \'{date}\' instead') from e
    
    # if isinstance(date, datetime.datetime):
    #     print('instance is datetime.datetime')
    #     return datetime.date(date.year, date.month, date.day)
    # elif isinstance(date, str):
    #     print('instance is string')
    #     # can raise ValueError if string does not match format
    #     return datetime.datetime.strptime(date, '%Y-%m-%d')
    # else:
    #     # if value passed in is some other type
    #     raise ValueError("Date value should be string or datetime of the format '%Y-%m-%d'")


def check_row_integrity(row):
    """
    Make sure a row has correct fieldnames.

    :param row: Row read from csv files as ordered dict
    :return: None
    :raises RowIntegrityError if row does not have correct fieldnames
    """

    # Check ordered dict keys
    fieldnames = {'date', 'store', 'total', 'description'}
    if set(row.keys()) == fieldnames:
        return
    
    # Get fieldnames from row that are not in supported fieldnames
    incorrect_fieldnames = set(row.keys()) - fieldnames
    raise RowIntegrityError(
        f'Improperly formatted row: incorrect fieldnames: {incorrect_fieldnames}')

def check_required_row_values(row):
    required_values_keys = {'date', 'store', 'total'}
    for key in required_values_keys:
        if not row[key]:
            raise RowIntegrityError(f'{key.title()} value is required: Got \'{row[key]}\' instead')
    return


def validate_row(row):
    """
    Wrapper function for clean_row_strings and validate_row.
    Format should be [
                    purchase_date, store_name,
                    total, description]

    :param row: Row from csv file
    :return: Row with values cleaned and validated
    :raises InvalidRowException if row integrity failed or value error
    """
    try:
        # import pdb; pdb.set_trace()
        check_row_integrity(row)
        check_required_row_values(row)
        row = clean_row_strings(row)
        row['total'] = format_total(row['total'])
        row['date'] = format_date(row['date'])
        return row
    except (RowIntegrityError, ValueError, TypeError, Exception) as exc:
        raise InvalidRowException(str(exc))


def compile_csv_files(csv_dir, ignore_files=[]):
    """
    Gather all csv files and return as list, excludes any ignored files passed.
    Assumes that the csv files directory is within root project directory.

    :param csv_dir: csv directory name
    :param ignore_files: list of file names to ignore
    """
    csv_files = []

    # Walk all files in csv_dir
    for root, dirs, files in os.walk(csv_dir):
        for name in files:
            if name.endswith('.csv') and name not in ignore_files:
                # Get full path of file
                full_path = os.path.join(root, name)
                csv_files.append(full_path)

    return csv_files


def get_all_csv(csv_dir=None, ignore_files=[]):
    """
    Gather all csv files and return as list, excludes any ignored files passed.
    Assumes that the csv files directory is within root project directory.

    :param csv_dir: csv directory name
    :param ignore_files: list of file names to ignore
    """
    if not csv_dir:
        csv_dir = CSV_DIR
    csv_files = []

    # Walk all files in csv_dir
    for root, dirs, files in os.walk(csv_dir):
        for name in files:
            if name.endswith('.csv') and name not in ignore_files:
                # Get full path of file
                full_path = os.path.join(root, name)
                csv_files.append(full_path)

    return csv_files
