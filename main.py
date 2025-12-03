import sys
sys.dont_write_bytecode = True #testing
sys.path.insert(0, './backend')
from backend.pathResolver import PathResolver

def main(self):
    print(PathResolver.get_db_path(self))

if __name__ == '__main__':
    main(self)