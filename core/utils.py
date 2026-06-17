import os
import sys


def base_path():

    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


def data_path(file):

    return os.path.join(base_path(), "data", file)


def asset_path(file):

    return os.path.join(base_path(), "assets", file)