sql_create_store_table = """ CREATE TABLE IF NOT EXISTS store (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						name VARCHAR(50) NOT NULL UNIQUE
						); """

sql_create_transaction_table = """ CREATE TABLE IF NOT EXISTS purchase (
							id INTEGER PRIMARY KEY AUTOINCREMENT,
							purchase_date TEXT NOT NULL,
							total INTEGER NOT NULL,
							description TEXT NOT NULL,
							store_id INTEGER NOT NULL,
							FOREIGN KEY (store_id) REFERENCES store(id),
							UNIQUE(purchase_date, total, description, store_id)
							); """

sql_delete_store_table = """ DELETE FROM store; """

sql_delete_transaction_table = """ DELETE FROM purchase; """

sql_list_tables = """ SELECT name FROM sqlite_master WHERE type='table'; """
