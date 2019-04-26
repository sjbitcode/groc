import csv
import os
import sqlite3

from unidecode import unidecode

from app.exceptions import InvalidRowException, RowIntegrityError
from app.settings import BASE_DIR, CSV_DIR


def dollar_to_cents(dollar):
    """
    Convert a dollar amount (float) to cents (integer).

    :param dollar: A string or float representing dollar amount
    :return: An integer representing amount as cents.
    :raises ValueError or TypeError if value cannot be casted to float.
    """
    # try:
    #     return round(float(dollar) * 100)
    # except (ValueError, TypeError):
    #     raise
    return round(float(dollar) * 100)


def clean_unicode_whitespace(val):
    return unidecode(val).strip()

def selector(x):
        if isinstance(x, str):
            if x == '':
                return None
            else:
                return clean_unicode_whitespace(x)
        return x

def clean_row(row):
    """
    Clean row of data from csv by converting unicode characters to ASCII
    and strip whitespaces.

    :param row: List of strings read in from csv
    :return: List of cleaned strings
    """
    # clean = lambda x: unidecode(x).lstrip().rstrip()
    # clean = lambda x: unidecode(x).strip()
    # return [clean(s) if isinstance(s, str) else s for s in row]
    
    return {key: selector(row[key]) for key in row.keys()}

    # return {
    #     key: clean_unicode_whitespace(row[key])
    #     if isinstance(row[key], str) else row[key] 
    #     for key in row.keys()
    # }


def clean_total(total):
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
    raise RowIntegrityError('Row does not have correct fieldnames')


def validate_row(row):
    """
    Wrapper function for clean_row and validate_row.
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
        row = clean_row(row)
        row['total'] = clean_total(row['total'])
        return row
    except (RowIntegrityError, ValueError, TypeError) as exc:
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
