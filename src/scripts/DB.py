from pathlib import Path
import sqlite3


class DB:
    def __init__(self):
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent

        self.db_connection = sqlite3.connect(project_root / 'data.db')
        self.cursor = self.db_connection.cursor()
        self.initializeDB()
    
    def initializeDB(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS BRAND (
                Brand_Full VARCHAR(255) PRIMARY KEY,
                Brand_Short CHAR(25) NOT NULL
            );
            """)
        
    def get_all_db_brands(self) -> list[any]:
        self.cursor.execute(''' 
            SELECT * FROM BRAND        
        ''')
        return self.cursor.fetchall()

    def insert_db_brand(self, brand_full: str, brand_short: str):
        self.cursor.execute(f'''
            INSERT INTO BRAND VALUES(?, ?)
        ''', (brand_full, brand_short))
        self.db_connection.commit()

    def update_db_brand(self, brand_full: str, brand_short: str):
        self.cursor.execute(f'''
            UPDATE BRAND SET Brand_Short = ? WHERE Brand_Full = ?
        ''', brand_short, brand_full)
        self.db_connection.commit()

    def update_db_brands(self, updated_brands):
        all_brands = self.get_all_db_brands()
        brands_dict = {b.brand_full: b for b in all_brands}

        for brand_data in updated_brands:
            full_name = brand_data.get("brandFull")
            short_name = brand_data.get("brandShort")

            if not full_name or not short_name:
                continue

            existing_brand = brands_dict.get(full_name)

            if existing_brand:
                if existing_brand.Brand_Short != short_name:
                    self.update_db_brand(full_name, short_name)
                    self.db_connection.commit()
            else:
                self.insert_db_brand(full_name, short_name)
                self.db_connection.commit()