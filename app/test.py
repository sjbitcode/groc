from app.connection import SQLiteConnection
from app.db import *
from app.utils import *

conn = SQLiteConnection().get_connection()

# csvs = get_all_csv()

# insert_from_csv_dict(conn, csvs)
