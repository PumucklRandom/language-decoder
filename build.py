"""
How to create certificate for the application:

# Create certificate
New-SelfSignedCertificate -Type Custom -Subject "CN=PumucklRandom" -KeyUsage DigitalSignature
    -FriendlyName "LanguageDecoder" -CertStoreLocation "Cert:/CurrentUser/My"
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

# Get certificate
Get-childitem 'Cert:/CurrentUser/My' | Format-Table FriendlyName, Thumbprint, Subject
# Set password for certificate
$password = ConvertTo-SecureString -String "password" -Force -AsPlainText
# Export certificate with Thumbprint
Export-PfxCertificate -cert "Cert:/CurrentUser/My/Thumbprint" -FilePath certificate.pfx -Password $password
"""

import os
import shutil
import subprocess
import pathlib
import zipfile
import nicegui


def del_previous_build():
    if os.path.isdir('./build'):
        shutil.rmtree('./build')
    if os.path.isdir('./dist'):
        shutil.rmtree('./dist')
    if os.path.isfile('./LanguageDecoder.spec'):
        os.remove('./LanguageDecoder.spec')


def get_password() -> str:
    pw_path = './_data/password.txt'
    try:
        if not os.path.isfile(pw_path):
            return ''
        with open(file = './_data/password.txt', mode = 'r', encoding = 'utf-8') as file:
            return file.read()
    except Exception:
        print(f'Could not load password from: "{pw_path}"')


def zip_directory(zip_file_path: str, source_directory: str):
    if os.path.isfile(zip_file_path):
        os.remove(zip_file_path)
    source_path = pathlib.Path(source_directory).expanduser()  # .resolve(strict = True)
    with zipfile.ZipFile(file = zip_file_path, mode = 'w', compression = zipfile.ZIP_DEFLATED) as zf:
        print(f'Zip {source_directory} to {zip_file_path}')
        for file_path in source_path.rglob('*'):
            zf.write(file_path, file_path.relative_to(source_path.parent))


try:
    del_previous_build()
    cmd_build = [
        'pyinstaller', '__main__.py',
        '--name', 'LanguageDecoder',
        '--windowed',  # set ui.run(native=True)!!!
        '--icon', './frontend/pages/icon/LD-icon.png',
        '--version-file', '_data/version.rc',
        '--add-data', f'{pathlib.Path(nicegui.__file__).parent}{os.pathsep}nicegui',
        '--add-data', f'./_data/config.yml{os.pathsep}./backend/config/',
        '--add-data', f'./backend/fonts/{os.pathsep}./backend/fonts/',
        '--add-data', f'./backend/config/labels/{os.pathsep}./backend/config/labels/',
        '--add-data', f'./frontend/pages/icon/{os.pathsep}./frontend/pages/icon/',
        '--clean', '-y'
    ]
    subprocess.run(cmd_build, shell = False, check = True)
    password = get_password()
    if password and os.path.isfile('./_data/certificate.pfx'):
        cmd_sign = [
            'signtool', 'sign',
            '/f', './_data/certificate.pfx',
            '/fd', 'SHA256',
            '/td', 'SHA256',
            '/tr', 'http://timestamp.digicert.com',
            '/p', f'{password}',
            './dist/LanguageDecoder/LanguageDecoder.exe'
        ]
        subprocess.run(cmd_sign, shell = False, check = True)
    zip_directory(zip_file_path = './LanguageDecoder.zip', source_directory = './dist/LanguageDecoder/')
    print('Successfully build application')
except Exception as exception:
    print(f'Building application failed with:\n{exception}')
