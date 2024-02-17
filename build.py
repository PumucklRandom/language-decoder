import os
import subprocess
from pathlib import Path
import nicegui

cmd = [
    'pyinstaller', '__main__.py',
    '--name', 'LanguageDecoder',
    '--windowed',  # set ui.run(native=True)!!!
    '--icon', 'frontend/pages/icon/LD-icon.png',
    '--add-data', f'{Path(nicegui.__file__).parent}{os.pathsep}nicegui',
    '--add-data', f'_data/config.yml{os.pathsep}backend/config/',
    '--add-data', f'backend/fonts/{os.pathsep}backend/fonts/',
    '--add-data', f'frontend/pages/icon/{os.pathsep}frontend/pages/icon/',
    '--add-data', f'frontend/pages/labels/{os.pathsep}frontend/pages/labels/',
    '-y'
]
subprocess.run(cmd, shell = False)
