import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_URL = os.path.join(BASE_DIR, 'grocery.db')