class GrocException(Exception):
	""" Groc Base Exception """
	pass


class RowIntegrityError(GrocException):
	""" Input data did not have correct amount of values. """
	pass


class InvalidRowException(GrocException):
	""" There was an invalid row while parsing input data. """
	pass


class DatabaseError(GrocException):
    """ An error related to database operations. """
    pass


# class DatabaseInitError(DatabaseError):
#     """ An error occured while creating database """
#     pass


class DatabaseInsertException(DatabaseError):
	""" An error occured while writing to database. """
	pass

