import datetime
import sqlite3

from prettytable import from_db_cursor

from app.connection import SQLiteConnection
from app.db import *
from app.utils import *
from app.groc import Groc

# conn = SQLiteConnection().get_connection()

# csvs = get_all_csv()

# insert_from_csv_dict(conn, csvs)

g = Groc()
# conn = g._get_connection(g.db_url)
# cur = conn.cursor()
# cur.execute('SELECT * FROM purchase;')

# x = from_db_cursor(cur)

def datetime_worded_abbreviated(bytes_string):
    s = str(bytes_string, 'utf-8')
    d = datetime.datetime.strptime(s, '%Y-%m-%d')
    return datetime.date.strftime(d, '%b %d, %Y')

def datetime_worded_full(bytes_string):
    s = str(bytes_string, 'utf-8')
    d = datetime.datetime.strptime(s, '%Y-%m-%d')
    return datetime.date.strftime(d, '%B %d, %Y')

def datetime_month_full(bytes_string):
    s = str(bytes_string, 'utf-8')
    d = datetime.datetime.strptime(s, '%Y-%m-%d')
    return datetime.date.strftime(d, '%B')

def datetime_month_numeric(bytes_string):
    s = str(bytes_string, 'utf-8')
    d = datetime.datetime.strptime(s, '%Y-%m-%d')
    return datetime.date.strftime(d, '%m')

def total_to_float(bytes_string):
    s = int(str(bytes_string, 'utf-8'))
    return f'${s:,.2f}'


sqlite3.register_converter("purchase_date", datetime_worded_full)
sqlite3.register_converter("purchase_date_abbreviated",
                           datetime_worded_abbreviated)
sqlite3.register_converter("purchase_month", datetime_month_full)
sqlite3.register_converter("purchase_month_numeric", datetime_month_numeric)
sqlite3.register_converter("total_money", total_to_float)

# sqlite3.register_converter("default_description", description_none)


con = sqlite3.connect(g.db_url, detect_types=sqlite3.PARSE_COLNAMES)
# con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("create table IF NOT EXISTS test(d date, total integer, description text)")
# cur.execute("""CREATE TRIGGER desc_unique BEFORE INSERT ON test
# WHEN NEW.description
# IS NULL
# BEGIN
#     SELECT
#         CASE 
#             WHEN ((SELECT 1 FROM test WHERE d=NEW.d AND total=NEW.total AND NEW.description IS NULL) NOTNULL) 
#                 THEN RAISE (ABORT, 'Row already exists')
#         END;
# END;""")

today = datetime.date.today()
# now = datetime.datetime.now()

# cur.execute("insert into test(d) values (?)", (today))
# con.commit()
# cur.execute('select d as "d [purchase_date_abbreviated]" from test')


# cur.execute("select d, ts from test")
# row = cur.fetchall()

# cur.execute('select total as "total_money_spent [total_money]" from test;').fetchall()
# print(today, "=>", row[0], type(row[0]))
# print(now, "=>", row[1], type(row[1]))
