from prettytable import from_db_cursor

from app.connection import SQLiteConnection
from app.db import *
from app.utils import *
from app.groc import Groc

# conn = SQLiteConnection().get_connection()

# csvs = get_all_csv()

# insert_from_csv_dict(conn, csvs)

g = Groc()
conn = g._get_connection(g.db_url)
cur = conn.cursor()
cur.execute('SELECT * FROM purchase;')

x = from_db_cursor(cur)
