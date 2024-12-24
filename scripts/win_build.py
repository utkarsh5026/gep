import os
import subprocess
import urllib.request
import shutil
import glob


def download_python():
    print("🔄 Downloading Python 3.12... Please wait...")
    python_url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    installer_path = "python_installer.exe"
    urllib.request.urlretrieve(python_url, installer_path)
    return installer_path


def install_python(installer_path: str):
    subprocess.run([installer_path, "/quiet",
                   "InstallAllUsers=1", "PrependPath=1", "Include_test=0"], check=True)

    os.remove(installer_path)


def create_virtual_env(venv_path: str):
    subprocess.run(["python", "-m", "venv", venv_path], check=True)


def install_requirements():
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


def create_executable():
    print("🛠️ Creating executable... This may take a few moments...")
    pyinstaller_path = os.path.join("venv", "Scripts", "pyinstaller")

    subprocess.run([
        pyinstaller_path,
        "--onefile",
        "--clean",
        os.path.join("..", "src", "main.py")
    ], check=True)


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
    try:
        print("🚀 Starting build process...")
        try:
            output = subprocess.check_output(["python", "--version"])
            if not output.decode().strip().startswith("Python 3.12"):
                installer_path = download_python()
                install_python(installer_path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            installer_path = download_python()
            install_python(installer_path)

        create_virtual_env("venv")
        install_requirements()
        create_executable()

        print("✅ Build completed successfully!")

    finally:
        cleanup_resources()


if __name__ == "__main__":
    main()
