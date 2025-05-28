import os
import time
from backend.config.config import CONFIG
from backend.logger.logger import logger

file_dir = os.path.dirname(os.path.relpath(__file__))


def cleanup_dicts(timeout: int = 30, dicts_path: str = 'dicts') -> int:
    """
    Cleanup dictionaries older than timeout in days.

    :param timeout: timeout in days
    :param dicts_path: path to the dictionaries directory
    :return: number of removed files
    """
    try:
        files_removed = 0
        time_now = time.time()
        time_limit = time_now - (timeout * 24 * 3600)
        dicts_path = os.path.join(file_dir, dicts_path)

        if not os.path.isdir(dicts_path):
            logger.info(f'No dictionaries to cleanup at "{dicts_path}"')
            return 0

        json_files = [file for file in os.listdir(dicts_path) if file.endswith('.json')]
        for json_file in json_files:
            json_path = os.path.join(dicts_path, json_file)
            if os.path.isfile(json_path) and os.path.getmtime(json_path) < time_limit:
                try:
                    os.remove(json_path)
                    files_removed += 1
                except OSError as exception:
                    logger.error(f'Error removing file "{json_path}" with exception: {exception}')
        return files_removed
    except Exception as exception:
        logger.error(f'Error during dictionary cleanup with exception: {exception}')
        return 0


def main() -> None:
    try:
        logger.info('Cleanup dictionary files:')
        logger.info(f'Removed "{cleanup_dicts(timeout = CONFIG.dicts_timeout)}" dictionary files')
    except Exception as exception:
        logger.error(f'Failed to cleanup dictionaries with exception: {exception}")')


if __name__ == '__main__':
    main()
