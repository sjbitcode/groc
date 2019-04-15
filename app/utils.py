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
    try:
        return round(float(dollar) * 100)
    except (ValueError, TypeError):
        raise


def clean_row(row):
    """
    Clean row of data from csv by converting unicode characters to ASCII
    and strip whitespaces.

    :param row: List of strings read in from csv
    :return: List of cleaned strings
    """
    clean = lambda x: unidecode(x).lstrip().rstrip()
    return [clean(s) if isinstance(s, str) else s for s in row]


def update_row(row):
    """
    Update the total and description values of csv row.
    Convert total to integer.
    Ensure that description value is nonempty.

    :param row: Row from csv file
    :return: Row with total and description validated
    """
    row[2] = dollar_to_cents(row[2])
    row[3] = row[3] or 'grocery'
    return row


def check_row_integrity(row):
    """
    Make sure a row has 4 fields.

    :param row: Row read from csv files as list of values
    :return: None
    :raises RowIntegrityError if row does not have four values
    """
    if len(row) == 4:
        return
    raise RowIntegrityError('Row does not have four values')


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
        check_row_integrity(row)
        row = clean_row(row)
        row = update_row(row)
        return row
    except (RowIntegrityError, ValueError, TypeError):
        raise InvalidRowException


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
