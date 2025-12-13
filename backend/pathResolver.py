import os
import sys

class PathResolver:
    @staticmethod
    def get_project_path():
        return os.path.dirname(os.path.abspath(sys.argv[0])) + '\\'

    @staticmethod
    def get_db_path():
        return PathResolver.get_project_path() + 'backend\\' + 'data.db'
    
    @staticmethod
    def get_creds_path():
        return PathResolver.get_project_path() + 'backend\\' + 'creds.txt'
    
    @staticmethod
    def get_styles_path():
        return PathResolver.get_project_path() + 'GUI\\' + 'styles\\'