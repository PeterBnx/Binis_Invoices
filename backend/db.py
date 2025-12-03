import sqlite3
from pathResolver import PathResolver

class DB:
    def __init__(self):
        self.connection = self.get_connection()
        self.connection.row_factory = sqlite3.Row

    def get_connection(self):
        return sqlite3.connect(PathResolver.get_db_path(self))

    def execute(self, query, params=None, fetch=False):
        try:
            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            self.connection.commit()

            if fetch:
                return cursor.fetchall()

            return True

        except sqlite3.Error as error:
            print("Error occurred:", error)
            return None

    def createBrandsTable(self):
        query = """
        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_full TEXT,
            brand_short TEXT
        );
        """
        return self.execute(query)

    def insertNewBrand(self, brand_full, brand_short):
        query = "INSERT INTO brands (brand_full, brand_short) VALUES (?, ?)"
        return self.execute(query, (brand_full, brand_short))
