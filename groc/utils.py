import datetime
import decimal as dc
import os

from unidecode import unidecode

from . import exceptions


def check_row_integrity(row):
    """
    Check that a dictionary contains a set of keys exactly.

    Args:
        row (dict/ordered dict): A dictionary of purchase data.

    Raises:
        exceptions.RowIntegrityError: If keys are not found in dict.
    """
    fieldnames = {'date', 'store', 'total', 'description'}

    if set(row.keys()) != fieldnames:
        # Get fieldnames that are not in supported fieldnames
        incorrect_fieldnames = set(row.keys()) - fieldnames
        raise exceptions.RowIntegrityError(
            f'Improperly formatted fieldnames: {incorrect_fieldnames}')


def check_required_row_values(row):
    """
    Check that required purchase values exist.

    Args:
        row (dict/ordered dict): A dictionary of purchase data.

    Raises:
        exceptions.RowIntegrityError: If a required value is falsey.
    """
    required_values_keys = ['date', 'store', 'total']

    # Required fields that are not in row.
    not_supplied = [
        key for key in required_values_keys if not row[key]]
    not_supplied_str = ", ".join(not_supplied)
    not_supplied_values = ", ".join([f"\'{row[key]}\'" for key in not_supplied])

    if not_supplied:
        raise exceptions.RowIntegrityError(
            f'{not_supplied_str} value(s) required: ({not_supplied_values})')


def convert_unicode_whitespace(value):
    """Converts all unicode characters to ascii and removes whitespace."""
    return unidecode(value).strip()


def clean_row_strings(row):
    """
    Clean string values in given dictionary.

    Args:
        row (dict): A dictionary of purchase data.

    Returns:
        dict: A dictionary with string values cleaned.
    """
    cleaned_row = {}

    for key, value in row.items():
        if isinstance(value, str):
            # Empty strings will be converted to None
            cleaned_row[key] = convert_unicode_whitespace(value) or None
        else:
            cleaned_row[key] = value

    return cleaned_row


def format_total(total):
    """
    Converts dollar amount to cents.

    Args:
        total (str/int): The purchase total value.

    Returns:
        int: Total cents.

    Raises:
        exceptions.RowValueError: If dollar could not be converted to cents.
    """
    try:
        # return int(round(float(total)*100))
        return int(
            dc.Decimal(str(total))
            .quantize(
                dc.Decimal('.01'), rounding=dc.ROUND_HALF_UP
            )
            * 100
        )
    except (dc.InvalidOperation, Exception):
        raise exceptions.RowValueError(
            f'Incorrect value for total: \'{total}\'. ' +
            f'(Format must be whole or decimal number like 10, 100.00, 1000.01).')


def format_date(date):
    """
    Formats a value to a datetime.date object.
    A string value is converted to a datetime.datetime object
    and/or a datetime.datetime object is converted to a datetime.date object.

    Args:
        date (str/datetime): The purchase date value.

    Returns:
        datetime.date: Given date formatted to datetime.date.

    Raises:
        exceptions.RowValueError: If given date is not a string or
                       datetime.datetime object.
    """
    try:
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
        if isinstance(date, datetime.date):
            return datetime.date(
                date.year, date.month, date.day
            )
        else:
            raise exceptions.RowValueError
    except Exception:
        raise exceptions.RowValueError(f'Incorrect value for date: \'{date}\'. ' +
                            f'(Format must be YYYY-MM-DD).')


def validate_row(row):
    """
    Validate and clean a dictionary.

    Args:
        row (dict/ordered dict): A dictionary of purchase data.

    Returns:
        dict: A dictionary with cleaned and formatted values.

    Raises:
        exceptions.InvalidRowException: If data is incorrectly formatted,
                             or has missing/incorrect values.
    """
    try:
        check_row_integrity(row)
        check_required_row_values(row)
        row = clean_row_strings(row)
        row['total'] = format_total(row['total'])
        row['date'] = format_date(row['date'])
        return row
    except (exceptions.RowIntegrityError, exceptions.RowValueError, Exception) as exc:
        raise exceptions.InvalidRowException(str(exc))


def compile_csv_files(dir_path, ignore_files=None):
    """
    Create a list of absolute file paths for csv files
    from a directory, excluding ignored.

    Args:
        dir_path (str): name or path of directory.
        ignore_files (list): list of file paths to ignore relative to dir_path.

    Returns:
        list: Absolute paths of files inside directory.
    """
    if ignore_files is None:
        ignore_files = []

    dir_path = os.path.abspath(dir_path)
    ignore_files = [os.path.abspath(path) for path in ignore_files]

    csv_files = []
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            if name.endswith('.csv'):
                # Get absolute path of file.
                full_path = os.path.abspath(os.path.join(root, name))

                # Check if it should be ignored.
                if full_path not in ignore_files:
                    csv_files.append(full_path)

    return csv_files
