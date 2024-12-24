import os
import subprocess
import urllib.request
import shutil
import glob
from pathlib import Path
import itertools
import threading
import time

GEP_DIR = Path.home() / ".gep"


def spinner_animation():
    spinner = itertools.cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
    while not spinner_animation.done:
        print(f"\r{next(spinner)}", end='')
        time.sleep(0.1)


def with_spinner(func):
    def wrapper(*args, **kwargs):
        spinner_animation.done = False
        spinner_thread = threading.Thread(target=spinner_animation)
        spinner_thread.start()
        try:
            result = func(*args, **kwargs)
            spinner_animation.done = True
            spinner_thread.join()
            print("\r", end='')  # Clear the spinner
            return result
        except Exception as e:
            spinner_animation.done = True
            spinner_thread.join()
            print("\r", end='')  # Clear the spinner
            raise e
    return wrapper


@with_spinner
def download_python():
    print("🔄 Downloading Python 3.12... Please wait...")
    python_url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    installer_path = "python_installer.exe"
    urllib.request.urlretrieve(python_url, installer_path)
    print("✅ Python 3.12 downloaded successfully!")

    print(Path.home() / "Python32" / "python.exe")
    return installer_path


@with_spinner
def install_python(installer_path: str):
    print("🔄 Installing Python 3.12, this may take a few moments...")
    subprocess.run([installer_path, "/quiet",
                   "InstallAllUsers=1", "PrependPath=1", "Include_test=0"], check=True)

    os.remove(installer_path)


@with_spinner
def create_virtual_env(venv_path: str):
    print("🔄 Creating virtual environment, this may take a few moments...")
    subprocess.run(["python", "-m", "venv", venv_path], check=True)
    print("✅ Virtual environment created successfully!")


@with_spinner
def install_requirements():
    print("🚀 Installing requirements, this may take a few moments...")
    pip_path = os.path.join("venv", "Scripts", "pip")

    requirements_path = os.path.join("..", "requirements.txt")

    subprocess.run([
        pip_path,
        "install",
        "-r",
        requirements_path
    ], check=True)

    subprocess.run([
        pip_path,
        "install",
        "pyinstaller"
    ], check=True)

    print("✅ Requirements installed successfully!")


@with_spinner
def create_executable():
    print("🛠️ Creating executable... This may take a few moments...")
    pyinstaller_path = os.path.join("venv", "Scripts", "pyinstaller")

    GEP_DIR.mkdir(parents=True, exist_ok=True)

    subprocess.run([
        pyinstaller_path,
        "--onefile",
        "--clean",
        "--name", "gep",
        "--distpath", str(GEP_DIR),
        os.path.join("..", "src", "main.py")
    ], check=True)

    print("✅ Executable created successfully! at ", GEP_DIR / "gep.exe")


@with_spinner
def cleanup_resources():
    print("\n🧹 Starting cleanup process...")

    cleanup_dirs = ['build', '__pycache__', 'venv']
    cleanup_files = ['*.spec', '*.pyc']

    try:
        for dir_name in cleanup_dirs:
            if os.path.exists(dir_name):
                print(f"📁 Removing {dir_name} directory...")
                shutil.rmtree(dir_name)

        for pattern in cleanup_files:
            for file_path in glob.glob(pattern):
                print(f"🗑️ Removing {file_path}...")
                os.remove(file_path)

        print("✨ Cleanup completed successfully!")

    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")


def main():

    process_complete = False
    try:
        print("🚀 Starting build process...")
        try:
            output = subprocess.check_output(["python", "--version"])
            if not output.decode().strip().startswith("Python 3.12"):
                print("🔄 Python 3.12 is not installed. Downloading...")
                installer_path = download_python()
                install_python(installer_path)
            else:
                print("✅ Python 3.12 is already installed.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            installer_path = download_python()
            install_python(installer_path)

        create_virtual_env("venv")
        install_requirements()
        create_executable()

        print("✅ Build completed successfully!")
        process_complete = True
    finally:
        cleanup_resources()

    if process_complete:
        print("🎉 Build completed successfully!")
        print("🚀 Executable created successfully! at ", GEP_DIR / "gep.exe")


if __name__ == "__main__":
    main()
