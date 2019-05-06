class GrocException(Exception):
    """Groc Base Exception"""
    pass


class RowIntegrityError(GrocException):
    """Input data did not have correct amount of values."""
    pass


class RowValueError(GrocException):
    """A row value was incorrect while validating."""
    pass


class InvalidRowException(GrocException):
    """There was an invalid row while parsing input data."""
    pass


class DatabaseError(GrocException):
    """An error related to database operations."""
    pass


class DatabaseInsertError(DatabaseError):
    """An error occured while writing to database."""
    pass


class DuplicateRow(DatabaseInsertError):
    """A duplicate row was detected."""
    pass
