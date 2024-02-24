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
    cmd = [
        'pyinstaller', '__main__.py',
        '--name', 'LanguageDecoder',
        '--windowed',  # set ui.run(native=True)!!!
        '--icon', 'frontend/pages/icon/LD-icon.png',
        '--add-data', f'{pathlib.Path(nicegui.__file__).parent}{os.pathsep}nicegui',
        '--add-data', f'_data/config.yml{os.pathsep}backend/config/',
        '--add-data', f'backend/fonts/{os.pathsep}backend/fonts/',
        '--add-data', f'frontend/pages/icon/{os.pathsep}frontend/pages/icon/',
        '--add-data', f'frontend/pages/labels/{os.pathsep}frontend/pages/labels/',
        '-y'
    ]
    subprocess.run(cmd, shell = False, check = True)
    zip_directory(zip_file_path = 'LanguageDecoder.zip', source_directory = 'dist/LanguageDecoder/')
    print('Successfully build application')
except Exception as exception:
    print(f'Building application failed with:\n{exception}')
