import os
import sys


def fix_import():
    current_dir = os.path.abspath('.')
    sys.path.insert(0, current_dir)
    return sys.path


fix_import()
