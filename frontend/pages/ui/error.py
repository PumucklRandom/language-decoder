import asyncio
import traceback
import functools
from nicegui import ui
from typing import Callable
from backend.logger.logger import logger
from frontend.pages.ui.config import UI_LABELS


def catch(func: Callable) -> Callable:
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AttributeError as exception:
                ui.navigate.reload()
                logger.warning(f'Warning in "{func.__name__}" with exception: {exception}\n{traceback.format_exc()}')
                ui.notify(UI_LABELS.GENERAL.Warning.timeout, type = 'warning', position = 'top')
            except Exception as exception:
                logger.error(f'Error in "{func.__name__}" with exception: {exception}\n{traceback.format_exc()}')
                ui.notify(UI_LABELS.GENERAL.Error.internal, type = 'negative', position = 'top')

        return async_wrapper

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError as exception:
            ui.navigate.reload()
            logger.warning(f'Warning in "{func.__name__}" with exception: {exception}\n{traceback.format_exc()}')
            ui.notify(UI_LABELS.GENERAL.Warning.timeout, type = 'warning', position = 'top')
        except Exception as exception:
            logger.error(f'Error in "{func.__name__}" with exception: {exception}\n{traceback.format_exc()}')
            ui.notify(UI_LABELS.GENERAL.Error.internal, type = 'negative', position = 'top')

    return sync_wrapper
