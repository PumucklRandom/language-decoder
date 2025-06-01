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


def cleanup_setts(timeout: int = 30, setts_path: str = 'setts') -> int:
    """
    Cleanup settings older than timeout in days.

    :param timeout: timeout in days
    :param setts_path: path to the settings directory
    :return: number of removed files
    """
    try:
        files_removed = 0
        time_now = time.time()
        time_limit = time_now - (timeout * 24 * 3600)
        setts_path = os.path.join(file_dir, setts_path)

        if not os.path.isdir(setts_path):
            logger.info(f'No settings to cleanup at "{setts_path}"')
            return 0

        json_files = [file for file in os.listdir(setts_path) if file.endswith('.json')]
        for json_file in json_files:
            json_path = os.path.join(setts_path, json_file)
            if os.path.isfile(json_path) and os.path.getmtime(json_path) < time_limit:
                try:
                    os.remove(json_path)
                    files_removed += 1
                except OSError as exception:
                    logger.error(f'Error removing file "{json_path}" with exception: {exception}')
        return files_removed
    except Exception as exception:
        logger.error(f'Error during settings cleanup with exception: {exception}')
        return 0


def main() -> None:
    try:
        logger.info('Cleanup user data:')
        logger.info(
            f'Removed: "{cleanup_dicts(timeout = CONFIG.files_timeout)}" dictionary files'
            f'Removed: "{cleanup_setts(timeout = CONFIG.files_timeout)}" settings files'
        )
    except Exception as exception:
        logger.error(f'Failed to cleanup user data with exception: {exception}")')


if __name__ == '__main__':
    main()
