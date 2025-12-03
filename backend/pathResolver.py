import os
import sys

class PathResolver:
    def __init__(self):
        self.script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

    def get_project_path(self):
        return self.script_directory + '\\'

    def get_db_path(self):
        return self.get_project_path() + 'data.db'