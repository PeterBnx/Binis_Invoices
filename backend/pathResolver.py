import sys
import os

class PathResolver:

    @staticmethod
    def get_base_path():
        # Works for dev AND PyInstaller
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_project_path():
        return PathResolver.get_base_path()

    @staticmethod
    def get_creds_path():
        return os.path.join(PathResolver.get_project_path(), "creds.txt")

    @staticmethod
    def get_db_path():
        return os.path.join(PathResolver.get_project_path(), "data.db")

    @staticmethod
    def get_styles_path():
        return os.path.join(PathResolver.get_project_path(), "GUI", "styles")
