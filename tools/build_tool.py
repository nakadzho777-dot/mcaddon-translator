import os
import shutil


def build():

    print("BUILD START")

    os.system("pyinstaller --onefile --noconsole --icon assets/icon.ico app/gui.py")

    if not os.path.exists("release/app"):
        os.makedirs("release/app")

    shutil.copy("dist/gui.exe", "release/app/gui.exe")

    print("BUILD DONE")


if __name__ == "__main__":
    build()