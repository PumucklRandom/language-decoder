import asyncio
import traceback
import functools
from nicegui import ui
from backend.logger.logger import logger
from frontend.pages.ui.config import UI_LABELS


def catch(func: callable) -> callable:
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exception:
                logger.error(f'Error in "{func.__name__}" with exception: {exception}\n{traceback.format_exc()}')
                ui.notify(UI_LABELS.GENERAL.Error.internal, type = 'negative', position = 'top')
                return None

        return async_wrapper

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exception:
            logger.error(f'Error in "{func.__name__}" with exception: {exception}\n{traceback.format_exc()}')
            ui.notify(UI_LABELS.GENERAL.Error.internal, type = 'negative', position = 'top')
            return None

    return sync_wrapper
