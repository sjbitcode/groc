import csv
import os
import sqlite3

from app.settings import BASE_DIR, CSV_DIR


def dollar_to_cents(dollar):
    """
    Convert a dollar amount (float) to cents (integer).

    :param dollar: A string or float representing dollar amount
    :return: An integer representing amount as cents.
    """
    return round(float(dollar) * 100)


def clean_row(row):
    """
    Clean row of data from csv by removing trailing spaces
    and converting forward and backward apostrophe to single quote.

    :param row: List of strings read in from csv
    :return: List of cleaned strings
    """
    clean = lambda x: x.lstrip().rstrip().replace(u"\u2018", "'").replace(u"\u2019", "'")

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


def validate_row(row):
    """
    Wrapper function for clean_row and validate_row.
    Format should be [
                    purchase_date, store_name,
                    total, description]

    :param row: Row from csv file
    :return: Row with values cleaned and validated
    """
    row = clean_row(row)
    row = update_row(row)
    return row


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
