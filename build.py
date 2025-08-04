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
    Get-childitem 'Cert:/CurrentUser/My' | Format-Table FriendlyName, Thumbprint, Subject

    # Set password for certificate
    $password = ConvertTo-SecureString -String "password" -Force -AsPlainText

    # Export certificate with Thumbprint
    Export-PfxCertificate -cert "Cert:/CurrentUser/My/Thumbprint" -FilePath certificate.pfx -Password $password

    # In case a certificate has to be removed
    Remove-Item Cert:/CurrentUser/My/Thumbprint
"""

import os
import re
import sys
import shutil
import subprocess
import pathlib
import zipfile
import nicegui
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

# Default configuration
VERSION = '0.12.8.2'
APP_NAME = 'LanguageDecoder'
VERSION_RC_PATH = './_data/version.rc'
PW_PATH = './_data/password.txt'
CERTIFICATE_PATH = './_data/certificate.pfx'
OUT_ZIP_PATH = f'./{APP_NAME}.zip'
CONFIG = load_config('../../_data/config.yml')


def update_version(version: str) -> None:
    """
    Update version information in the version.rc file.

    :param version: Version string in format 'x.y.z.w'
    """
    if not re.match(r'^\d+\.\d+\.\d+\.\d+$', version):
        raise ValueError(f"Invalid version format: {version}. Expected format: x.y.z.w")

    try:
        with open(VERSION_RC_PATH, 'r+') as file:
            content = file.read()
            content = re.sub(r'(\d+\.\d+\.\d+\.\d+)', version, content)
            content = re.sub(r'(\d+, \d+, \d+, \d+)', version.replace('.', ', '), content)
            file.seek(0)
            file.write(content)
            file.truncate()
        logger.info(f"Updated version to {version}")
    except FileNotFoundError:
        logger.error(f"Version file not found: {VERSION_RC_PATH}")
        raise


def del_old_build() -> None:
    """
    Remove previous build artifacts.

    Removes: ./build directory, ./dist directory, ./app_name.spec file
    """
    paths_to_remove = ('./build', './dist', f'./{APP_NAME}.spec')

    for path in paths_to_remove:
        try:
            if os.path.isdir(path):
                logger.info(f"Removing directory: {path}")
                shutil.rmtree(path)
            elif os.path.isfile(path):
                logger.info(f"Removing file: {path}")
                os.remove(path)
        except Exception:
            logger.warning(f"Failed to remove {path}:\n{traceback.format_exc()}")


def get_password() -> str:
    """
    Get certificate password from file.

    return: Password string or empty string if file not found or error occurs
    """
    try:
        if not os.path.isfile(PW_PATH):
            logger.warning(f"Password file not found: {PW_PATH}")
            return ''

        with open(file = PW_PATH, mode = 'r', encoding = 'utf-8') as file:
            password = file.read().strip()
            return password
    except Exception:
        logger.error(f"Could not load password from: {PW_PATH}\n{traceback.format_exc()}")
        return ''


def build_app() -> bool:
    """
    Get certificate password from file.

    return: Password string or empty string if file not found or error occurs
    """
    cmd_build = [
        'pyinstaller', '__main__.py',
        '--name', APP_NAME,
        '--icon', './frontend/pages/ui/icon/LD-icon.png',
        '--version-file', VERSION_RC_PATH,
        '--add-data', f'{pathlib.Path(nicegui.__file__).parent}{os.pathsep}nicegui',
        '--add-data', f'./_data/config.yml{os.pathsep}./backend/config/',
        '--add-data', f'./backend/decoder/prompt.txt{os.pathsep}./backend/decoder/',
        '--add-data', f'./backend/fonts/{os.pathsep}./backend/fonts/',
        '--add-data', f'./frontend/pages/ui/labels/{os.pathsep}./frontend/pages/ui/labels/',
        '--add-data', f'./frontend/pages/ui/icon/{os.pathsep}./frontend/pages/ui/icon/',
        '--clean', '-y',
    ]

    if CONFIG.native:
        cmd_build.append('--windowed')

    try:
        logger.info("Building application with PyInstaller...")
        subprocess.run(cmd_build, shell = False, check = True)
        logger.info("Build completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Build failed with exit code {e.returncode}\n{traceback.format_exc()}")
        return False
    except Exception:
        logger.error(f"Build failed with exception:\n{traceback.format_exc()}")
        return False


def sign_app() -> bool:
    """
    Sign the executable with the certificate.

    return: True if signing succeeded, False otherwise
    """
    password = get_password()
    if not password:
        logger.warning("No password provided, skipping signing")
        return False

    if not os.path.isfile(CERTIFICATE_PATH):
        logger.warning(f"Certificate not found: {CERTIFICATE_PATH}")
        return False

    exe_path = f'./dist/{APP_NAME}/{APP_NAME}.exe'
    if not os.path.isfile(exe_path):
        logger.error(f"Executable not found: {exe_path}")
        return False

    cmd_sign = [
        'signtool', 'sign', '/debug',
        '/f', CERTIFICATE_PATH,
        '/fd', 'SHA256',
        '/td', 'SHA256',
        '/tr', 'http://timestamp.digicert.com',
        '/p', password,
        exe_path
    ]

    try:
        logger.info("Signing executable...")
        subprocess.run(cmd_sign, shell = False, check = True)
        logger.info("Signing completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Signing failed with exit code {e.returncode}\n{traceback.format_exc()}")
        return False
    except Exception:
        logger.error(f"Signing failed with exception:\n{traceback.format_exc()}")
        return False


def zip_directory(zip_file_path: str, source_directory: str) -> bool:
    """
    Create a zip archive of the directory.

    :param zip_file_path: Path to the output zip file
    :param source_directory: Directory to zip

    return: True if zipping succeeded, False otherwise
    """
    if not os.path.isdir(source_directory):
        logger.error(f"Source directory not found: {source_directory}")
        return False

    try:
        if os.path.isfile(zip_file_path):
            logger.info(f"Removing existing zip file: {zip_file_path}")
            os.remove(zip_file_path)

        source_path = pathlib.Path(source_directory).expanduser()  # .resolve(strict = True)

        logger.info(f"Creating zip archive: {zip_file_path}")
        with zipfile.ZipFile(file = zip_file_path, mode = 'w', compression = zipfile.ZIP_DEFLATED) as zf:
            file_count = 0
            for file_path in source_path.rglob('*'):
                zf.write(file_path, file_path.relative_to(source_path.parent))
                file_count += 1

        logger.info(f"Zip archive created with {file_count} files")
        return True
    except Exception:
        logger.error(f"Failed to create zip archive:\n{traceback.format_exc()}")
        return False


def main() -> int:
    """
    Main build process.

    return: Exit code (0 for success, non-zero for error)
    """
    try:
        # Step 1: Update version
        update_version(VERSION)

        # Step 2: Clean previous build
        del_old_build()

        # Step 3: Build application
        if not build_app():
            return 1

        # Step 4: Sign executable
        sign_app()

        # Step 5: Create zip archive
        if not zip_directory(OUT_ZIP_PATH, f'./dist/{APP_NAME}/'):
            return 1

        logger.info("Build process completed successfully")
        return 0
    except Exception:
        logger.error(f"Build process failed with exception:\n{traceback.format_exc()}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
