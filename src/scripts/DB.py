from pathlib import Path
import sqlite3


class DB:
    def __init__(self):
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent
        self.db_connection = sqlite3.connect(project_root / 'data.db')
        self.cursor = self.db_connection.cursor()
        self.credentials = []
        self.initializeDB()
    
    def initializeDB(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS BRAND (
                Brand_Full VARCHAR(255) PRIMARY KEY,
                Brand_Short CHAR(25) NOT NULL
            );
        """)
        self.db_connection.commit()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS CREDS (
                Emp_Name VARCHAR(255) NOT NULL,
                Emp_Password CHAR(25) NOT NULL,
                Cis_Name CHAR(25) PRIMARY KEY,
                Cis_Password CHAR(25) NOT NULL
            );
        """)
        self.db_connection.commit()

        self.cursor.execute("SELECT COUNT(*) FROM CREDS;")
        row_count = self.cursor.fetchone()[0]

        if row_count == 0:
            self.cursor.execute("""
                INSERT INTO CREDS ( Emp_Name, Emp_Password, Cis_Name, Cis_Password )
                VALUES (None, None, None, None);
            """)
            self.db_connection.commit()

    def check_creds(self):
        self.cursor.execute('SELECT * FROM CREDS')
        result = self.cursor.fetchall()
        if not result:
            return False
        self.credentials = [val for val in result[0]]
        for val in self.credentials:
            if val is None or val == "":
                return False
        return True

    def update_creds(self, emp_name, emp_pass, cis_name, cis_pass):
        try:
            print(emp_name, emp_pass)
            self.cursor.execute("SELECT rowid FROM CREDS LIMIT 1")
            row = self.cursor.fetchone()
            if row:
                row_id = row[0]
                self.cursor.execute('''
                    UPDATE CREDS 
                    SET Emp_Name = ?, Emp_Password = ?, Cis_Name = ?, Cis_Password = ?
                    WHERE rowid = ?
                ''', (emp_name, emp_pass, cis_name, cis_pass, row_id))
            else:
                self.cursor.execute('''
                    INSERT INTO CREDS (Emp_Name, Emp_Password, Cis_Name, Cis_Password)
                    VALUES (?, ?, ?, ?)
                ''', (emp_name, emp_pass, cis_name, cis_pass))
            self.db_connection.commit()
            return True
        except Exception as e:
            print(f"Error in updating creds: {e}")
            return False
        
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
        ''', (brand_short, brand_full))
        self.db_connection.commit()

    def update_db_brands(self, updated_brands):
        all_brands = self.get_all_db_brands()
        # all_brands returns tuples: (brand_full, brand_short)
        brands_dict = {b[0]: b for b in all_brands}

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