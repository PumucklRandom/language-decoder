import os
import time
from backend.logger.logger import logger
from backend.config.config import CONFIG

file_dir = os.path.dirname(os.path.relpath(__file__))


def cleanup_files(directory: str, timeout: int = CONFIG.files_timeout) -> int:
    """
    Cleanup json files older than timeout in days.

    :param directory: directory of the json files
    :param timeout: timeout in days

    :return: number of removed files
    """
    files_removed = 0
    time_limit = time.time() - (timeout * 24 * 3600)
    files_path = os.path.join(file_dir, directory)
    try:
        if not os.path.isdir(files_path):
            logger.info(f'No json files to cleanup at "{files_path}"')
            return 0

        json_files = (file for file in os.listdir(files_path) if file.endswith('.json'))
        for json_file in json_files:
            json_path = os.path.join(files_path, json_file)
            if os.path.isfile(json_path) and os.path.getatime(json_path) < time_limit:
                try:
                    os.remove(json_path)
                    files_removed += 1
                except OSError as exception:
                    logger.error(f'Error removing json file "{json_path}" with exception: {exception}')
    except Exception as exception:
        logger.error(f'Error during json files cleanup with exception: {exception}')
    return files_removed


def main() -> None:
    try:
        logger.info('Cleanup user data:')
        logger.info(
            f'Removed: "{cleanup_files(directory = "dicts")}" dictionary files'
            f'Removed: "{cleanup_files(directory = "setts")}" settings files'
        )
    except Exception as exception:
        logger.error(f'Failed to cleanup user data with exception: {exception}")')


if __name__ == '__main__':
    main()
