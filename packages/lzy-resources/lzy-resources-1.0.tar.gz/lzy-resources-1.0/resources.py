import os
import sys


def resources(resource):
    if getattr(sys, 'frozen', False):
        path = sys._MEIPASS
    else:
        path = os.path.abspath('.')
    return os.path.join(path, 'resources', resource)
