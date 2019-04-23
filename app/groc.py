import os
import sqlite3

from app import db, exceptions, utils


class SQLiteConnection:
    def __init__(self, db_url):
        try:
            conn = sqlite3.connect(db_url)
            self.conn = conn
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            raise exceptions.DatabaseError('Error connecting to database')

    def get_connection(self):
        self.conn.execute('PRAGMA foreign_keys = ON;')
        return self.conn


class Groc:
    def __init__(self):
        self.groc_dir = os.path.expanduser('~/.groc/')
        self.db_name = 'groc.db'
        self.db_url = os.path.join(self.groc_dir, self.db_name)
    
    @staticmethod
    def _get_connection(db_url):
        try:
            connection = sqlite3.connect(db_url)
            connection = connection.execute('PRAGMA foreign_keys = ON;')
            return connection
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            raise exceptions.DatabaseError('Error connecting to database')

    def _create_and_setup_db(self):
        """ Create database and tables. """
        db.setup_db(self._get_connection(self.db_url))
    
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
        print('Creating db now! Didnt have one')
        self._create_and_setup_db()

    def clear_db(self):
        """ Delete all data from tables. """
        print('Resetting the db!')
        db.clear_db(self._get_connection(self.db_url))
    
    def select_by_id(self, ids):
        return db.select_by_id(self._get_connection(self.db_url), ids)

    def delete_purchase(self, ids):
        """
        Delete purchases by id.
        
        :param ids: A list of integers representing ids of purchase rows.
        """
        db.delete_from_db(self._get_connection(self.db_url), ids)
    
    def list_purchases(self, limit=50):
        """
        List purchases limited by amount.

        :param limit: Integer amount to limit purchases. Defaults to 50.
        """
        return db.get_purchases_limit(self._get_connection(self.db_url), limit)
    
    def add_purchase_manual(self, row):
        """
        Add a single purchase.

        :param row: A dictionary of purchase data.
        """
        # this raises an exception if wrong
        db.insert_a_row(self._get_connection(self.db_url), row)
    
    def add_purchase_path(self, path):
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

        # this raises an exception if wrong
        db.insert_from_csv_dict(self._get_connection(self.db_url), csv_files)
        









