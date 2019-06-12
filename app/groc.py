import os
import sqlite3

from app import db, exceptions, utils


class Groc:
    def _get_connection(self, db_url):
        try:
            self.connection = db.create_connection(db_url)
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            raise exceptions.DatabaseError('Error connecting to database')

    def __init__(self):
        self.groc_dir = os.path.expanduser('~/.groc/')
        self.db_name = 'groc.db'
        self.db_url = os.path.join(self.groc_dir, self.db_name)
        # Set instance db connection
        self._get_connection(self.db_url)

    def _create_and_setup_db(self):
        """Create database and tables."""
        db.setup_db(self.connection)

    def groc_dir_exists(self):
        return os.path.exists(self.groc_dir)

    def groc_db_exists(self):
        return os.path.exists(self.db_url)

    def init_groc(self):
        """
        Initializes .groc directory and creates the database.

        :raises DatabaseError if database exists
        """

        # If ~/.groc exists and is a directory
        if not os.path.isdir(self.groc_dir):
            print('creating .groc directory')
            os.mkdir(self.groc_dir)

        # Check ~/.groc/groc.db exists
        if os.path.isfile(self.db_url):
            raise exceptions.DatabaseError('Database already exists!')

        # Create groc.db here
        self._create_and_setup_db()

    def clear_db(self):
        """ Delete all data from tables. """
        db.clear_db(self.connection)

    def select_by_id(self, ids):
        return db.select_by_id(self.connection, ids)

    def select_purchase_ids(self, ids):
        return db.select_count_by_id(self.connection, ids)

    # Not used in CLI
    def select_ids_by_month(self, months):
        return db.select_ids_by_month(
            self.connection, months)

    def breakdown(self, month, year):
        return db.select_count_total_per_month(
            self.connection, month, year)

    # def select_purchase_count_per_month(self):
    #     return db.select_purchase_count_per_month(
    #         self.connection)

    def select_purchase_count(self):
        cur = db.select_purchase_count(self.connection)
        # indexing with Row
        return cur.fetchone()['purchase_count']

    def delete_purchase(self, ids):
        """
        Delete purchases by id.

        :param ids: A list of integers representing ids of purchase rows.
        """
        db.delete_from_db(self.connection, ids)

    def list_purchases_date(self, month, year):
        return db.get_purchases_date(self.connection, month, year)

    def list_purchases_limit(self, limit=50):
        return db.get_purchases_limit(self.connection, limit)

    def list_purchases_date_limit(self, month, year, limit=50):
        return db.get_purchases_date_limit(self.connection, month, year, limit)

    def add_purchase_manual(self, row, ignore_duplicate):
        """
        Add a single purchase.

        :param row: A dictionary of purchase data.
        """
        # this raises an exception if wrong
        return db.insert_from_commandline(self.connection,
                                          row, ignore_duplicate)

    def add_purchase_path(self, path, ignore_duplicate):
        """
        Add a purchase via file or directory.

        :param path: A string path to file or directory.
        """
        path = os.path.abspath(os.path.expanduser(path))

        csv_files = []

        if os.path.isdir(path):
            csv_files = utils.compile_csv_files(path)
        elif os.path.isfile(path):
            csv_files = [path]
        else:
            raise Exception(f'{path} could not be found!')

        # this raises an exception if wrong
        return db.insert_from_csv_dict(self.connection,
                                       csv_files, ignore_duplicate)
