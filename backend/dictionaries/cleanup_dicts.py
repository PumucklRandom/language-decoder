import os
import time
from backend.config.config import CONFIG
from backend.logger.logger import logger


def cleanup_dicts(n_days: int = 30, dicts_path: str = 'dicts'):
    f = 0
    time_now = time.time()
    del_time = time_now - (n_days * 24 * 3600)
    dicts_path = f'{os.path.join(os.path.dirname(os.path.relpath(__file__)), dicts_path)}'
    for file in os.listdir(dicts_path):
        if file.endswith('.json'):
            file_path = os.path.join(dicts_path, file)
            if os.path.isfile(file_path):
                if os.path.getmtime(file_path) < del_time:
                    os.remove(file_path)
                    f += 1
    return f


logger.info('Cleanup dictionary files:')
logger.info(f'Removed "{cleanup_dicts(n_days = CONFIG.del_time)}" json files')
