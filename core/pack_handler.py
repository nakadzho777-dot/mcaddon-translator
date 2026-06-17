import zipfile
import os


def is_mcaddon(path):
    return path.endswith(".mcaddon")


def extract_mcaddon(path):
    temp_dir = path + "_extracted"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
    except:
        return None

    return temp_dir