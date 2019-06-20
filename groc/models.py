import os
import sqlite3

from . import db, exceptions, utils


class Groc:
    def __init__(self):
        self.groc_dir = os.path.expanduser('~/.groc/')
        self.db_name = 'groc.db'
        self.db_url = self._get_db_url()
        # Set instance db connection
        self.connection = self._get_connection() if self.groc_dir_exists() else None

    def _get_db_url(self):
        """ Create the db_url attribute. """
        return os.path.join(self.groc_dir, self.db_name)

    def _get_connection(self):
        """
        Sets the connection attribute.

        Raises:
            exceptions.DatabaseError: Any error connecting to db
        """
        try:
            return db.create_connection(self.db_url)
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            raise exceptions.DatabaseError('Error connecting to database. Make sure database is initialized.')

    def _create_and_setup_db(self):
        """ Create database and tables. """
        self.connection = self.connection or self._get_connection()
        db.setup_db(self.connection)

    def groc_dir_exists(self):
        """
        Check if groc directory exists in user's home directory.

        Returns:
            True if successful, False otherwise.
        """
        return os.path.exists(self.groc_dir)

    def init_groc(self):
        """
        Initializes .groc directory and creates the database.

        Creates the groc directory if it doesn't exist.
        Raises an exception if the db exists. If not, creates the db.

        Raises:
            exceptions.DatabaseError: If database exists.
        """

        # If ~/.groc exists and is a directory
        if not os.path.isdir(self.groc_dir):
            os.mkdir(self.groc_dir)

        # Check ~/.groc/groc.db exists
        if os.path.isfile(self.db_url):
            raise exceptions.DatabaseError('Database already exists!')

        # Create groc.db here
        self._create_and_setup_db()

    def clear_db(self):
        """ Delete all data from tables. """
        self.connection = self.connection or self._get_connection()
        db.clear_db(self.connection)

    def select_by_id(self, ids):
        """
        Select purchases by ids.

        Args:
            ids (list/tuple): purchase ids.

        Returns:
            A SQLite cursor object.
        """
        self.connection = self.connection or self._get_connection()
        return db.select_by_id(self.connection, ids)

    def select_purchase_ids(self, ids):
        """
        Select purchase ids only by given ids.
        Used for checking existence of purchases.

        Args:
            ids (list/tuple): purchase ids.

        Returns:
            A SQLite cursor object.
        """
        self.connection = self.connection or self._get_connection()
        return db.select_purchase_ids(self.connection, ids)

    def breakdown(self, month, year):
        """
        Get purchase stats grouped by month and year.
        Purchase stats: year, month, sum, purchase count,
                        min purchase amount, max purchase amount,
                        average purchase amount,
                        distinct store count.

        Args:
            month (str): Two digit month.
            year (str): Four digit month.

        Returns:
            A SQLite cursor object.
        """
        self.connection = self.connection or self._get_connection()
        return db.select_count_total_per_month(
            self.connection, month, year)

    def select_purchase_count(self):
        """
        Get total number of purchases.

        Returns:
            int: total number of purchases.
        """
        self.connection = self.connection or self._get_connection()
        cur = db.select_purchase_count(self.connection)
        # indexing with SQLite Row
        return cur.fetchone()['purchase_count']

    def delete_purchase(self, ids):
        """
        Delete purchases by id.

        Args:
            ids (list/tuple): purchase ids.
        """
        self.connection = self.connection or self._get_connection()
        db.delete_from_db(self.connection, ids)

    def list_purchases_date(self, month, year):
        """
        Get all purchases for a month/year.

        Args:
            month (str): Two digit month.
            year (str): Four digit month.

        Returns:
            A SQLite cursor object.
        """
        self.connection = self.connection or self._get_connection()
        return db.get_purchases_date(self.connection, month, year)

    def list_purchases_limit(self, limit=50):
        """
        Get latest purchases limited by limit amount.

        Args:
            limit (int): limit amount.

        Returns:
            A SQLite cursor object.
        """
        self.connection = self.connection or self._get_connection()
        return db.get_purchases_limit(self.connection, limit)

    def list_purchases_date_limit(self, month, year, limit=50):
        """
        Get purchases for a month/year limited by limit amount.

        Args:
            month (str): Two digit month.
            year (str): Four digit month.
            limit (int): limit amount.

        Returns:
            A SQLite cursor object.
        """
        self.connection = self.connection or self._get_connection()
        return db.get_purchases_date_limit(self.connection, month, year, limit)

    def add_purchase_manual(self, row, ignore_duplicate):
        """
        Add a single purchase. If the data is invalid,
        an exception will be thrown from the db module.

        Args:
            row (dict): A dictionary of purchase data.
                        Keys should be date, total, store, description.
            ignore_duplicate (bool): Flag to ignore exceptions thrown
                                     for duplicate purchases.

        Returns:
            True if successful.

        Raises:
            exceptions.DuplicateRow: if purchase is duplicate.
            exceptions.DatabaseInsertError: if data invalid.
        """
        self.connection = self.connection or self._get_connection()
        return db.validate_insert_row(self.connection,
                                      row, ignore_duplicate)

    def add_purchase_path(self, path, ignore_duplicate):
        """
        Add a purchase via file or directory.
        If path is directory, compile all csv files in a list.
        If path is a file, store path in a list.

        Args:
            path (str): A path to file or directory.
            ignore_duplicate (bool): Flag to ignore exceptions thrown
                                     for duplicate purchases.

        Returns:
            int: count of how many purchases added.

        Raises:
            Exception: if path could not be found.
            exceptions.DuplicateRow: if purchase is duplicate.
            exceptions.DatabaseInsertError: if data invalid.
        """
        path = os.path.abspath(os.path.expanduser(path))

        csv_files = []

        if os.path.isdir(path):
            csv_files = utils.compile_csv_files(path)
        elif os.path.isfile(path):
            csv_files = [path]
        else:
            raise Exception(f'{path} could not be found!')

        self.connection = self.connection or self._get_connection()
        return db.insert_from_csv_dict(self.connection,
                                       csv_files, ignore_duplicate)
