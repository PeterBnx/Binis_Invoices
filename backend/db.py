import sqlite3
from pathResolver import PathResolver

class DB:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DB, cls).__new__(cls)
            cls._connection = cls._create_connection()
        return cls._instance
    
    def __init__(self):
        self.create_db_tables()

    @classmethod
    def _create_connection(cls):
        conn = sqlite3.connect(
            PathResolver.get_db_path(),
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        return conn

    @property
    def connection(self):
        return self._connection


    # Generic execution helper

    def execute(self, query, params=None):
        try:
            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print("Database error:", e)
            return None

    def fetch_all(self, query, params=None):
        try:
            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            return cursor.fetchall()

        except sqlite3.Error as e:
            print("Database error:", e)
            return None
        
    # CRUD Operations

    def create_db_tables(self):
        self.create_brands_table()

    def create_brands_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_full TEXT NOT NULL,
            brand_short TEXT NOT NULL
        );
        """
        return self.execute(query)

    def insert_brand(self, brand_full, brand_short):
        query = """
            INSERT INTO brands (brand_full, brand_short)
            VALUES (?, ?)
        """
        return self.execute(query, (brand_full, brand_short))

    def get_all_brands(self):
        return self.fetch_all("SELECT * FROM brands ORDER BY id")

    def get_brand_by_id(self, brand_id):
        rows = self.fetch_all("SELECT * FROM brands WHERE id = ?", (brand_id,))
        return rows[0] if rows else None
