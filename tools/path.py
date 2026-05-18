# tools/path.py
import sys
import os

# Making sure the it's the right path depending on the OS (for assets loading)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        # PyInstaller stores files in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Project root is parent of logic/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)