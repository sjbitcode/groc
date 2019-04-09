# SQLite specific statements
sqlite_create_store_table = """ CREATE TABLE IF NOT EXISTS store (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						name VARCHAR(50) NOT NULL UNIQUE
						); """

sqlite_create_purchase_table = """ CREATE TABLE IF NOT EXISTS purchase (
							id INTEGER PRIMARY KEY AUTOINCREMENT,
							purchase_date TEXT NOT NULL,
							total INTEGER NOT NULL,
							description TEXT NOT NULL,
							store_id INTEGER NOT NULL,
							FOREIGN KEY (store_id) REFERENCES store(id),
							UNIQUE(purchase_date, total, description, store_id)
							); """

sqlite_list_tables = """ SELECT name FROM sqlite_master WHERE type='table'; """


# Postgres specific statements
postgres_create_store_table = """ CREATE TABLE store (
						id SERIAL PRIMARY KEY,
						name VARCHAR(50) NOT NULL UNIQUE
						); """

postgres_create_purchase_table = """ CREATE TABLE purchase (
							id SERIAL PRIMARY KEY,
							purchase_date DATE NOT NULL,
							total INT NOT NULL,
							description TEXT NOT NULL,
							store_id INTEGER NOT NULL REFERENCES store(id),
							UNIQUE(purchase_date, total, description, store_id)
							); """

postgres_list_tables = """ SELECT table_name FROM information_schema.tables
   						WHERE table_schema = 'public'; """


# SQL general statements
sql_clear_store_table = """ DELETE FROM store; """

sql_clear_purchase_table = """ DELETE FROM purchase; """

sql_delete_store_table = """ DROP TABLE store; """

sql_delete_purchase_table = """ DROP TABLE purchase; """



