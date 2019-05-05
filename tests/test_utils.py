import datetime
import os
import pytest

from app import exceptions, utils


@pytest.mark.parametrize('dollar_amount, total_cents', [
    (12, 1200),
    (12.0, 1200),
    ('12', 1200),
    (12.009, 1201),
    ('12.009', 1201),
])
def test_format_total(dollar_amount, total_cents):
    assert utils.format_total(dollar_amount) == total_cents


@pytest.mark.parametrize('bad_input, raised_exception', [
    ('foo', exceptions.RowValueError),
    (None, exceptions.RowValueError)
])
def test_format_total_fail(bad_input, raised_exception):
    with pytest.raises(raised_exception):
        utils.format_total(bad_input)


@pytest.mark.parametrize('date, expected', [
    ('2019-01-01', datetime.date(2019, 1, 1)),
    (datetime.datetime(2019, 1, 1), datetime.date(2019, 1, 1)),
    (datetime.date(2019, 1, 1), datetime.date(2019, 1, 1))
])
def test_format_date(date, expected):
    assert utils.format_date(date) == expected


@pytest.mark.parametrize('bad_input, raised_exception', [
    ('2019', exceptions.RowValueError),
    ('foo', exceptions.RowValueError),
    (1, exceptions.RowValueError),
    (None, exceptions.RowValueError)
])
def test_format_date_fail(bad_input, raised_exception):
    with pytest.raises(raised_exception):
        utils.format_date(bad_input)


@pytest.mark.parametrize('row, expected', [
    ({'num': 1, 'age': None}, {'num': 1, 'age': None}),
    ({'foo': '  bar'}, {'foo': 'bar'}),
    ({'foo': 'bar' + u"\u2019" + 'baz'}, {'foo': "bar'baz"})
])
def test_clean_row_strings(row, expected):
    assert utils.clean_row_strings(row) == expected


@pytest.mark.parametrize('row, expected', [
    ({'date': '', 'store': '', 'total': '', 'description': ''}, None)
])
def test_check_row_integrity(row, expected):
    assert utils.check_row_integrity(row) == expected


@pytest.mark.parametrize('bad_input, raised_exception', [
    ({}, exceptions.RowIntegrityError),
    ({'foo': 'bar'}, exceptions.RowIntegrityError),
    ({'date': ''}, exceptions.RowIntegrityError),
    (
        {'Date': '', 'Store': '', 'Total': '', 'Description': ''},
        exceptions.RowIntegrityError
    ),
    (
        {'  date': '', ' store ': '', 'total': '', ' description': ''},
        exceptions.RowIntegrityError
    )
])
def test_check_row_integrity_fail(bad_input, raised_exception):
    with pytest.raises(raised_exception):
        utils.check_row_integrity(bad_input)


@pytest.mark.parametrize('row, expected', [
    ({'date': 'foo', 'store': 'bar', 'total': 'baz'}, None),
    (
        {'date': 'foo', 'store': 'bar', 'total': 'baz', 'random': 'something'},
        None
    )
])
def test_check_required_row_values(row, expected):
    assert utils.check_required_row_values(row) == expected


@pytest.mark.parametrize('bad_input, raised_exception', [
    ({'date': '', 'store': '', 'total': ''}, exceptions.RowIntegrityError),
    ({'date': 0, 'store': 0, 'total': 0}, exceptions.RowIntegrityError),
    (
        {'date': None, 'store': None, 'total': None},
        exceptions.RowIntegrityError
    ),
    (
        {'date': False, 'store': False, 'total': False},
        exceptions.RowIntegrityError
    ),
    (
        {'date': 'foo', 'store': None, 'total': None},
        exceptions.RowIntegrityError
    ),
    (
        {'date': None, 'store': 'foo', 'total': None},
        exceptions.RowIntegrityError
    ),
    (
        {'date': None, 'store': None, 'total': 'foo'},
        exceptions.RowIntegrityError
    )
])
def test_check_required_row_values_fail(bad_input, raised_exception):
    with pytest.raises(raised_exception):
        utils.check_required_row_values(bad_input)


@pytest.mark.parametrize('row, expected', [
    (
        {'date': '2019-01-01', 'total': '1.00', 'store': ' Foo ',
            'description': 'foo' + u"\u2019" + 'bar'},
        {'date': datetime.date(2019, 1, 1), 'total': 100, 'store': 'Foo',
            'description': "foo'bar"}
    ),
    (
        {'date': datetime.datetime(2019, 1, 1), 'total': '1.00',
            'store': 'foo', 'description': ''},
        {'date': datetime.date(2019, 1, 1), 'total': 100, 'store': 'foo',
            'description': None},
    )
])
def test_validate_row(row, expected):
    assert utils.validate_row(row) == expected


@pytest.mark.parametrize('bad_input, raised_exception', [
    ({}, exceptions.InvalidRowException),
    (
        {'date': '2019-01-01', 'total': '1.00', 'store': 'Foo',
            'description': '', 'foo': 'bar'},
        exceptions.InvalidRowException
    ),
    (
        {'date': 'invalid_date', 'total': 'invalid_total', 'store': 'Foo',
            'description': 'foobar'},
        exceptions.InvalidRowException
    ),
    (
        {'date': datetime.datetime(2019, 1, 1),
            'total': datetime.datetime(2019, 1, 1), 'store': 'Foo',
            'description': datetime.datetime(2019, 1, 1)},
        exceptions.InvalidRowException
    )
])
def test_validate_row_fail(bad_input, raised_exception):
    with pytest.raises(raised_exception):
        utils.validate_row(bad_input)


def test_compile_csv_files(create_csvs):
    csv_dir_path, files = create_csvs
    expected = [os.path.abspath(os.path.join(csv_dir_path, file))
                for file in files]
    assert set(utils.compile_csv_files(csv_dir_path)) == set(expected)


def test_compile_csv_files_ignore(create_csvs):
    csv_dir_path, files = create_csvs
    # Ignore the last file.
    ignore_file = files.pop()
    expected = [os.path.abspath(os.path.join(csv_dir_path, file))
                for file in files]
    assert set(utils.compile_csv_files(
                csv_dir_path, ignore_files=[ignore_file])) == set(expected)
