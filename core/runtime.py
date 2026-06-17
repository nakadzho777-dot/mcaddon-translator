import os
import sys

def get_base_dir():
    """
    exe / python 両対応のベースパス取得
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()