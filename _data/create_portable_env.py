import os
import sys
import shutil
import zipfile
import subprocess  # nosec
import urllib.request
from pathlib import Path

# PROXY = 'http://localhost:3128'
# os.environ['HTTP_PROXY'] = PROXY
# os.environ['HTTPS_PROXY'] = PROXY

FILE_DIR = os.path.dirname(os.path.relpath(__file__))
ENV_DIR = os.path.join(FILE_DIR, 'python')  # relative path to the portable Python environment
PYTHON_EXE = os.path.join(ENV_DIR, 'python.exe')
PYTHON_FTP_URL = 'https://www.python.org/ftp/python'
GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'

# Add any "save to remove" packages here
RM_PACKAGES = (
    'PyInstaller',
    'pyinstaller_hooks_contrib',
    'setuptools',
    'wheels',
    'altgraph',  # pyinstaller dependency
    'packaging',  # pyinstaller dependency
    'pefile',  # pyinstaller dependency
    'pywin32_ctypes',  # pyinstaller dependency
    'python_dotenv',  # load .env dependency 0.03MB
    'pillow',  # fpdf2 dependency 15.0MB
    # 'attrs',  # dependency not found 0.22MB
    # 'tqdm',  # openai dependency 0.16MB
    # 'soupsieve',  # deep-translator -> beautifulsoup dependency 0.14MB
    # 'defusedxml'  # dependency not found 0.03MB
)
# Add any "save to remove" Lib/site-packages/... here
RM_PATTERN = ()
os.makedirs(ENV_DIR, exist_ok = True)


def get_portable_python() -> bool:
    """
    Download and extract embeddable Python version of project environment.
    Enable site imports from ../
    """
    try:
        print()
        # Get version and architecture
        version = f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
        architecture = 'amd64' if sys.maxsize > 2 ** 32 else 'win32'
        # Check if already exists
        if os.path.exists(PYTHON_EXE):
            response = subprocess.run(  # nosec
                [PYTHON_EXE, '--version'],
                capture_output = True,
                check = True,
                text = True
            )
            available_version = response.stdout.strip().split()[-1]
            if available_version == version:
                print(f'Embeddable Python "{version}" already satisfied.\n')
                return True
            else:
                print(f'Found embeddable Python - version "{available_version}"\n'
                      f'But embeddable Python - version "{version}" required.')
                shutil.rmtree(ENV_DIR)
                os.makedirs(ENV_DIR, exist_ok = True)
                print('Recreating embeddable Python environment...')

        # Download and extract
        filename = f'python-{version}-embed-{architecture}.zip'
        python_url = f'{PYTHON_FTP_URL}/{version}/{filename}'
        zip_path = os.path.join(ENV_DIR, filename)
        print(f'Download embeddable Python from:\n"{python_url}"')
        urllib.request.urlretrieve(python_url, zip_path)  # nosec # nosemgrep
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(ENV_DIR)
        os.remove(zip_path)
        # Read the file and uncomment "import site"
        pth_file_path = list(Path(ENV_DIR).glob('python*._pth'))[0]
        with open(pth_file_path, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()
            for line in lines:
                if line.strip() == '.':
                    file.write('.\n..\n')  # fix import from parent directory
                elif line.strip().endswith('import site'):
                    file.write('import site\n')  # enable site imports
                else:
                    file.write(line)
        print(f'Enabled site imports in {pth_file_path}\n')
        return True
    except Exception as exception:
        print(f'Error in "get_portable_python":\n{exception}')
        return False


def install_pip() -> bool:
    """
    Download and install pip in the embeddable Python environment
    """
    try:
        # Check if pip is already installed
        if os.path.exists(os.path.join(ENV_DIR, 'Scripts', 'pip.exe')):
            response = subprocess.run(  # nosec
                [PYTHON_EXE, '-m', 'pip', '--version'],
                capture_output = True,
                check = True,
                text = True
            )
            pip_version = response.stdout.strip().split(' from ')[0]
            print(f'Pip already installed: "{pip_version}"\n')
            return True

        print('Download "get-pip.py"')
        get_pip_path = os.path.join(ENV_DIR, 'get-pip.py')
        urllib.request.urlretrieve(GET_PIP_URL, get_pip_path)  # nosec # nosemgrep
        subprocess.run(  # nosec
            [PYTHON_EXE, get_pip_path, '--no-warn-script-location'],
            check = True
        )
        os.remove(get_pip_path)
        print()
        return True
    except Exception as exception:
        print(f'Error in "install_pip":\n{exception}')
        return False


def install_dependencies() -> bool:
    """
    Install dependencies of project environment to embeddable Python environment
    """
    try:
        # Clear environment
        uninstall_path = os.path.join(ENV_DIR, 'uninstall.txt')
        with open(uninstall_path, 'w') as file:
            subprocess.run(  # nosec
                [PYTHON_EXE, '-m', 'pip', 'freeze'],
                stdout = file,
                check = True
            )
        if os.path.getsize(uninstall_path) > 0:
            print('Clearing environment...')
            subprocess.run(  # nosec
                [PYTHON_EXE, '-m', 'pip', 'uninstall', '-r', 'uninstall_path', '-y'],
                check = True
            )
        os.remove(uninstall_path)
        # Install dependencies
        dependencies_path = os.path.join(ENV_DIR, 'dependencies.txt')
        with open(dependencies_path, 'w') as file:
            print('Installing dependencies...')
            subprocess.run(  # nosec
                [sys.executable, '-m', 'pip', 'freeze'],
                stdout = file,
                check = True
            )
        subprocess.run(  # nosec
            [PYTHON_EXE, '-m', 'pip', 'install', '-r', dependencies_path, '--no-warn-script-location'],
            check = True
        )
        os.remove(dependencies_path)
        print('Successfully installed dependencies.\n')
        return True
    except Exception as exception:
        print(f'Error in "installing_dependencies":\n{exception}')
        return False


def rm_folder(base_dir: str, folder: str) -> bool:
    path = os.path.join(base_dir, folder)
    if not os.path.isdir(path):
        return False
    shutil.rmtree(path)
    return True


def rm_global(base_dir: str, pattern: str, exceptions: list[str] = None) -> bool:
    if exceptions is None: exceptions = []
    flag = False
    for item in Path(base_dir).rglob(pattern):
        if any(exception in item.name for exception in exceptions):
            continue
        if item.is_dir():
            shutil.rmtree(item)
            flag = True
        elif item.is_file():
            item.unlink()
            flag = True
    return flag


def rm_package(package: str) -> bool:
    response = subprocess.run(  # nosec
        [PYTHON_EXE, '-m', 'pip', 'uninstall', package, '-y'],
        capture_output = True,
        check = True,
        text = True
    )
    if response.stderr:
        return False
    return True


def rm_package_dir(base_dir: str, pattern: str) -> list[str]:
    removed = []
    for item in Path(base_dir).glob(pattern):
        if item.is_dir():
            shutil.rmtree(item)
            removed.append(item.name)
        elif item.is_file():
            item.unlink()
            removed.append(item.name)
    return removed


def clean_up_portable_python(rm_packages: bool = True, rm_pattern: bool = True,  # noqa: C901
                             rm_cache: bool = True, rm_share: bool = False,
                             rm_scripts: bool = False, rm_info: bool = False,
                             rm_pip: bool = False, exceptions: list[str] = None) -> bool:
    """
    Remove unnecessary files, folders and packages from the embeddable Python environment
    :param rm_packages: Remove specified packages
    :param rm_pattern: Remove specified files and folders from Lib/site-packages
    :param rm_cache: Remove __pycache__ folders and .pyc files
    :param rm_share: Remove share folder
    :param rm_scripts: Remove Scripts folder
    :param rm_info: Remove .dist-info folders
    :param rm_pip: Remove pip package
    :param exceptions: List of patterns to exclude from removal
    """
    try:
        print('Cleaning up embeddable Python environment...')
        removed_items = []
        packages_dir = os.path.join(ENV_DIR, 'Lib/site-packages')

        if rm_packages:
            for package in RM_PACKAGES:
                if rm_package(package):
                    removed_items.append(package)

        if rm_pattern:
            for pattern in RM_PATTERN:
                removed_items.extend(rm_package_dir(packages_dir, f'{pattern}*'))

        if rm_cache:
            if rm_global(ENV_DIR, '__pycache__'):
                removed_items.append('__pycache__')
            if rm_global(ENV_DIR, '*.pyc'):
                removed_items.append('*.pyc')

        if rm_share:
            if rm_folder(ENV_DIR, 'share'):
                removed_items.append('share')

        if rm_scripts:
            if rm_folder(ENV_DIR, 'Scripts'):
                removed_items.append('Scripts')

        if rm_info:
            if rm_global(ENV_DIR, '*.dist-info', exceptions):
                removed_items.append('*.dist-info')

        if rm_pip:
            removed_items.extend(rm_package_dir(packages_dir, 'pip'))
            removed_items.extend(rm_package_dir(packages_dir, 'pip-*.dist-info'))

        print('Removed items:', removed_items, '\n')
        return True

    except Exception as exception:
        print(f'Error in "clean_up_portable_python":\n{exception}')
        return False


def main():
    try:

        # Step 1: Download embeddable Python
        if not get_portable_python():
            return 1

        # Step 2: Install pip
        if not install_pip():
            return 2

        # Step 3: Install dependencies
        if not install_dependencies():
            return 3

        # Step 4: Clean up unnecessary files
        if not clean_up_portable_python(*[True] * 7, exceptions = ['nicegui']):
            return 4

        print(f'The portable Python environment is available in:\n{os.path.abspath(ENV_DIR)}\n')
        return 0

    except Exception as e:
        print(f'Error:\n{e}')
        return 5


if __name__ == "__main__":
    if sys.platform == 'linux':
        print('WARNING: The portable Python environment is only supported on Windows.\n')
    exit_code = main()
    sys.exit(exit_code)
