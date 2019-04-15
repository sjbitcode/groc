import pytest

from app import exceptions, utils


@pytest.mark.parametrize('dollar_amount, total_cents', [
	(12, 1200),
	(12.0, 1200),
	('12', 1200)
])
def test_dollar_to_cents(dollar_amount, total_cents):
	assert utils.dollar_to_cents(dollar_amount) == total_cents


@pytest.mark.parametrize('bad_input, raised_exception', [
	('foo', ValueError),
	(None, TypeError)
])
def test_dollar_to_cents_fail(bad_input, raised_exception):
	with pytest.raises(raised_exception):
		utils.dollar_to_cents(bad_input)


@pytest.mark.parametrize('row, expected', [
	([12], [12]),
	([12, '  foo'], [12, 'foo']),
	(['foo' + u"\u2019" + 'bar'], ["foo'bar"]),
	([' foo '], ['foo'])
])
def test_clean_row(row, expected):
	assert utils.clean_row(row) == expected


@pytest.mark.parametrize('row, expected', [
	(['foo', 'bar', 12, ''], ['foo', 'bar', 1200, 'grocery']),
	(['foo', 'bar', 12, 'baz'], ['foo', 'bar', 1200, 'baz']),
	(['foo', 'bar', 12, None], ['foo', 'bar', 1200, 'grocery'])
])
def test_update_row(row, expected):
	assert utils.update_row(row) == expected


@pytest.mark.parametrize('row, expected', [
	(['foo', 'bar', 'baz', 'qux'], None)
])
def test_check_row_integrity(row, expected):
	assert utils.check_row_integrity(row) == expected


@pytest.mark.parametrize('bad_row, raised_exception', [
	([], exceptions.RowIntegrityError),
	(['foo'], exceptions.RowIntegrityError),
	(['foo', 'bar', 'baz', 'qux', 'quux'], exceptions.RowIntegrityError)
])
def test_check_row_integrity(bad_row, raised_exception):
	with pytest.raises(raised_exception):
		utils.check_row_integrity(bad_row)
