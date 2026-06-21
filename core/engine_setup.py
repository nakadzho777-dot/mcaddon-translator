import sys
import shutil
import subprocess
import importlib.util


def is_argos_installed():
    return importlib.util.find_spec("argostranslate") is not None


def is_ollama_installed():
    return shutil.which("ollama") is not None


def install_argos_library():
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "argostranslate"
    ])


def install_argos_en_ja_model():
    import argostranslate.package

    argostranslate.package.update_package_index()
    packages = argostranslate.package.get_available_packages()

    target = None

    for package in packages:
        if package.from_code == "en" and package.to_code == "ja":
            target = package
            break

    if target is None:
        raise RuntimeError("英語→日本語モデルが見つかりませんでした")

    path = target.download()
    argostranslate.package.install_from_path(path)


def install_argos_full():
    if not is_argos_installed():
        install_argos_library()

    install_argos_en_ja_model()


def open_ollama_download():
    import webbrowser
    webbrowser.open("https://ollama.com/download")