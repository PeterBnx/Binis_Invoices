import sys
sys.dont_write_bytecode = True #testing
sys.path.insert(0, './backend')
from backend.pathResolver import PathResolver
from backend.db import DB

def main():
    print(PathResolver.get_db_path())
    db = DB()

if __name__ == '__main__':
    main()