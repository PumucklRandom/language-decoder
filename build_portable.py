"""
create app folder
copy create_portable_env.py
run create_portable_env.py
delete create_portable_env.py
copy main, backend and frontend
copy .bat file
zip
"""

import os
import sys
import shutil
import pathlib
import subprocess
import zipfile
import traceback
import logging
from backend.config.config import load_config

# Configure logging
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('build')

APP_NAME = 'LanguageDecoder'
CONFIG = load_config('../../_data/config.yml')
SOURCES = (
    'backend', 'frontend', '__main__.py',
    '_data/create_portable_env.py', '_data/config.yml',
    '_data/run_main.bat', '_data/run_main.vbs'
)

APP_DIR = f'./{APP_NAME}'
CREATE_ENV_PATH = os.path.join(APP_DIR, 'create_portable_env.py')


def setup_app_dir() -> bool:
    try:
        if os.path.exists(APP_DIR):
            shutil.rmtree(APP_DIR)
        os.mkdir(APP_DIR)
        return True
    except Exception:
        logger.error(f'App directory setup failed with:\n{traceback.format_exc()}')
        return False


def copy_source() -> bool:
    try:
        for source in SOURCES:
            destin = os.path.join(APP_DIR, os.path.basename(source))
            if os.path.isfile(source):
                if destin.endswith('config.yml'):
                    destin = os.path.join(APP_DIR, 'backend/config/config.yml')
                elif destin.endswith('.bat'):
                    destin = os.path.join(os.path.dirname(destin), f'{APP_NAME}.bat')
                elif destin.endswith('.vbs'):
                    destin = os.path.join(os.path.dirname(destin), f'{APP_NAME}.vbs')
                shutil.copyfile(source, destin)
            if os.path.isdir(source):
                shutil.copytree(source, destin)
        config_path = os.path.join(APP_DIR, 'frontend/pages/ui/config.py')
        with open(config_path, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()
            for line in lines:
                if line.strip().startswith("os.environ['WEBVIEW2_USER_DATA_FOLDER']"):
                    file.write("os.environ['WEBVIEW2_USER_DATA_FOLDER'] = './Lib/site-packages/webview'\n")
                else:
                    file.write(line)
        logger.info(f'Copied source to {APP_DIR}')
        return True
    except Exception:
        logger.error(f'Copy of source failed with exception:\n{traceback.format_exc()}')
        return False


def create_env() -> bool:
    try:
        subprocess.run([sys.executable, CREATE_ENV_PATH], check = True)  # nosec
        os.remove(CREATE_ENV_PATH)
        logger.info(f'Created environment in {APP_DIR}')
        return True
    except Exception:
        logger.error(f'Creation of environment failed with exception:\n{traceback.format_exc()}')
        return False


def zip_app() -> bool:
    """
    Create a zip archive of the app.
    return: True if zipping succeeded, False otherwise
    """

    zip_file_path = f'./{APP_NAME}-portable.zip'

    if not os.path.isdir(APP_DIR):
        logger.error(f'App directory not found: {APP_DIR}')
        return False

    try:
        if os.path.isfile(zip_file_path):
            logger.info(f'Removing existing zip file: {zip_file_path}')
            os.remove(zip_file_path)

        source_path = pathlib.Path(APP_DIR).expanduser()  # .resolve(strict = True)

        logger.info(f'Creating zip archive: {zip_file_path}')
        with zipfile.ZipFile(file = zip_file_path, mode = 'w', compression = zipfile.ZIP_DEFLATED) as zf:
            file_count = 0
            for file_path in source_path.rglob('*'):
                zf.write(file_path, file_path.relative_to(source_path.parent))
                file_count += 1

        logger.info(f'Zip archive created with {file_count} files')
        return True
    except Exception:
        logger.error(f'Failed to create zip archive:\n{traceback.format_exc()}')
        return False


def main() -> int:
    """
    Main build process.

    return: Exit code (0 for success, non-zero for error)
    """
    try:

        # Step 1: Setup app directory
        if not setup_app_dir():
            return 1

        # Step 2: Copy source
        if not copy_source():
            return 2

        # Step 3: Create portable environment
        if not create_env():
            return 3

        # Step 4: Create zip archive
        if not zip_app():
            return 4

        logger.info('Build process completed successfully')
        return 0
    except Exception:
        logger.error(f'Build process failed with exception:\n{traceback.format_exc()}')
        return 5


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
