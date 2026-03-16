#!/usr/bin/env python3
"""
Build script for the LanguageDecoder application.

This script handles:
1. Updating version information
2. Cleaning previous builds
3. Building the application with PyInstaller
4. Signing the executable (if certificate is available)
5. Creating a zip distribution

Usage:
    python build.py

Certificate Creation Instructions:
    # Create certificate
    New-SelfSignedCertificate -Type Custom -Subject "CN=PumucklRandom" -KeyUsage DigitalSignature
        -FriendlyName "LanguageDecoder" -CertStoreLocation "Cert:/CurrentUser/My"
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
        -NotAfter (Get-Date).AddYears(10)

    # Get certificate
    Get-ChildItem 'Cert:/CurrentUser/My' | Format-Table FriendlyName, Thumbprint, Subject

    # Set password for certificate
    $password = ConvertTo-SecureString -String "password" -Force -AsPlainText

    # Export certificate with Thumbprint
    Export-PfxCertificate -cert "Cert:/CurrentUser/My/Thumbprint" -FilePath certificate.pfx -Password $password

    # In case a certificate has to be removed
    Remove-Item Cert:/CurrentUser/My/Thumbprint
"""

import re
import os
import sys
import shutil
import pathlib
import zipfile
import nicegui
import logging
import traceback
import subprocess
from PyInstaller.__main__ import run as pyinstaller_run

# Configure logging
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('build')

# Default configuration
VERSION = '0.13.2.0'
APP_NAME = 'LanguageDecoder'
VERSION_RC_PATH = './_data/version.rc'
DESKTOP_PATH = './_data/.desktop'
UNBLOCK_PATH = './_data/unblock.bat'
README_PATH = './_data/readme.txt'
PW_PATH = './_data/password.txt'
CERTIFICATE_PATH = './_data/certificate.pfx'
SOURCE_DIR = f'./dist/{APP_NAME}/'
NATIVE = False


def update_version() -> bool:
    """
    Update version information in the version.rc and .desktop file.

    return: True if update succeeded, False otherwise
    """
    try:
        with open(VERSION_RC_PATH, 'r+') as file:
            content = file.read()
            content = re.sub(r'(\d+\.\d+\.\d+\.\d+)', VERSION, content)
            content = re.sub(r'(\d+, \d+, \d+, \d+)', VERSION.replace('.', ', '), content)
            file.seek(0)
            file.truncate()
            file.write(content)

        with open(DESKTOP_PATH, 'r+') as file:
            content = file.read()
            content = re.sub(r'(?<=Version=).*$', VERSION, content, flags = re.MULTILINE)
            content = re.sub(r'(?<=Name=).*$', APP_NAME, content, flags = re.MULTILINE)
            content = re.sub(r'(?<=\./)[\w-]+', APP_NAME, content, flags = re.MULTILINE)
            file.seek(0)
            file.truncate()
            file.write(content)

        logger.info(f'Updated version to {VERSION}')
        return True
    except Exception:
        logger.error(f'Failed to update version:\n{traceback.format_exc()}')
        return False


def rm_app_build() -> bool:
    """
    Remove previous build artifacts.
    Removes: ./build directory, ./dist directory, ./app_name.spec file

    return: True if removal succeeded, False otherwise
    """
    paths_to_remove = ('./build', './dist', f'./{APP_NAME}.spec')
    try:
        for path in paths_to_remove:
            if os.path.isdir(path):
                logger.info(f'Removing directory: {path}')
                shutil.rmtree(path)
            elif os.path.islink(path) or os.path.isfile(path):
                logger.info(f'Removing file: {path}')
                os.remove(path)
        return True
    except Exception:
        logger.warning(f'Failed to remove previous build:\n{traceback.format_exc()}')
        return False


def app_as_native() -> None:
    """
    Modify config for native app.
    """
    try:
        with open(f'./dist/{APP_NAME}/_internal/backend/config/config.yml', 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()
            for line in lines:
                if line.startswith('native: false'):
                    file.write(line.replace('false', 'true', 1))
                elif line.startswith('window_size: null'):
                    file.write(line.replace('null', '[1600, 900]', 1))
                else:
                    file.write(line)

        shutil.copy(UNBLOCK_PATH, f'./dist/{APP_NAME}/{os.path.basename(UNBLOCK_PATH)}')
        shutil.copy(README_PATH, f'./dist/{APP_NAME}/{os.path.basename(README_PATH)}')
    except Exception:
        logger.warning(f'Failed to configure app as native:\n{traceback.format_exc()}')


def build_app() -> bool:
    """
    Build the application using PyInstaller.

    return: True if build succeeded, False otherwise
    """
    cmd = [
        '__main__.py',
        '--name', APP_NAME,
        '--icon', './frontend/pages/ui/icon/LD-icon.png',
        '--add-data', f'{pathlib.Path(nicegui.__file__).parent}{os.pathsep}nicegui',
        '--add-data', f'./_data/config.yml{os.pathsep}./backend/config/',
        '--add-data', f'./backend/decoder/prompt.txt{os.pathsep}./backend/decoder/',
        '--add-data', f'./backend/fonts/{os.pathsep}./backend/fonts/',
        '--add-data', f'./frontend/pages/ui/labels/{os.pathsep}./frontend/pages/ui/labels/',
        '--add-data', f'./frontend/pages/ui/icon/{os.pathsep}./frontend/pages/ui/icon/',
        '--clean', '-y',
    ]

    if sys.platform != 'linux':
        cmd.extend(['--version-file', VERSION_RC_PATH])
    if NATIVE:
        cmd.append('--windowed')
    else:
        cmd.extend(['--exclude-module', 'pywebview'])

    try:
        logger.info('Building application with PyInstaller...')
        pyinstaller_run(cmd)
        if sys.platform == 'linux':
            shutil.copy(DESKTOP_PATH, f'./dist/{APP_NAME}/{APP_NAME}.desktop')
        else:
            if NATIVE: app_as_native()
        logger.info('Build completed successfully')
        return True
    except Exception:
        logger.error(f'Build failed with exception:\n{traceback.format_exc()}')
        return False


def get_password() -> str:
    """
    Get certificate password from file.

    return: Password string or empty string if file not found or error occurs
    """
    try:
        if not os.path.isfile(PW_PATH):
            logger.warning(f'Password file not found: {PW_PATH}')
            return ''

        with open(file = PW_PATH, mode = 'r', encoding = 'utf-8') as file:
            password = file.read().strip()
            return password
    except Exception:
        logger.error(f'Could not load password from: {PW_PATH}\n{traceback.format_exc()}')
        return ''


def sign_app() -> bool:
    """
    Sign the executable with the certificate.

    return: True if signing succeeded, False otherwise
    """
    if sys.platform == 'linux':
        logger.info('Skipping signing on Linux OS.')
        return True

    password = get_password()
    if not password:
        logger.warning('No password provided, skipping signing')
        return True

    if not os.path.isfile(CERTIFICATE_PATH):
        logger.warning(f'Certificate not found: {CERTIFICATE_PATH}')
        return True

    exe_path = f'./dist/{APP_NAME}/{APP_NAME}.exe'
    if not os.path.isfile(exe_path):
        logger.error(f'Executable not found: {exe_path}')
        return False

    cmd = [
        'signtool', 'sign', '/debug',
        '/f', CERTIFICATE_PATH,
        '/fd', 'SHA256',
        '/td', 'SHA256',
        '/tr', 'http://timestamp.digicert.com',
        '/p', password,
        exe_path
    ]

    try:
        logger.info('Signing executable...')
        subprocess.run(cmd, check = True)
        logger.info('Signing completed successfully')
        return True
    except Exception:
        logger.error(f'Signing failed with exception:\n{traceback.format_exc()}')
        return False


def zip_app() -> bool:
    """
    Create a zip archive of the app directory.

    return: True if zipping succeeded, False otherwise
    """

    zip_file_path = f'./{APP_NAME}.zip'
    if sys.platform == 'linux':
        zip_file_path = f'./{APP_NAME}-lx.zip'
    else:
        if NATIVE:
            zip_file_path = f'./{APP_NAME}-native.zip'

    if not os.path.isdir(SOURCE_DIR):
        logger.error(f'Source directory not found: {SOURCE_DIR}')
        return False

    try:
        if os.path.isfile(zip_file_path):
            logger.info(f'Removing existing zip file: {zip_file_path}')
            os.remove(zip_file_path)

        source_path = pathlib.Path(SOURCE_DIR).expanduser()  # .resolve(strict = True)

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
        # Step 1: Update version
        if not update_version():
            return 1

        # Step 2: Remove previous build
        if not rm_app_build():
            return 2

        # Step 3: Build application
        if not build_app():
            return 3

        # Step 4: Sign executable
        if not sign_app():
            return 4

        # Step 5: Create zip archive
        if not zip_app():
            return 5

        logger.info('Build process completed successfully')
        return 0
    except Exception:
        logger.error(f'Build process failed with exception:\n{traceback.format_exc()}')
        return 6


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
