sql_create_store_table = """ CREATE TABLE IF NOT EXISTS store (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						name VARCHAR(50) NOT NULL UNIQUE
						); """

sql_create_transaction_table = """ CREATE TABLE IF NOT EXISTS purchase (
							id INTEGER PRIMARY KEY AUTOINCREMENT,
							purchase_date TEXT NOT NULL,
							total INTEGER NOT NULL,
							description TEXT,
							store_id INTEGER NOT NULL,
							FOREIGN KEY (store_id) REFERENCES store(id)
							); """
