import logging
from asyncio import sleep
from functools import wraps
from typing import Callable

from aiogram.dispatcher import Dispatcher
from terra_sdk.client.lcd.lcdclient import AsyncLCDClient

log = logging.getLogger(__name__)


def every(frequency: int) -> Callable:
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        async def wrapper(self) -> None:
            while True:
                await f(self)
                await sleep(frequency)

        return wrapper

    return decorator


def skip_excpetions(f: Callable) -> Callable:
    @wraps(f)
    async def wrapper(self) -> None:
        try:
            await f(self)
        except Exception as e:
            log.error(f"exception in task: {e}", stack_info=True)

    return wrapper


class Tasks:
    def __init__(self, dp: Dispatcher, lcd: AsyncLCDClient) -> None:
        self.lcd = lcd
        dp._loop_create_task(self.check_loans_to_values())

    @every(5)
    @skip_excpetions
    async def check_loans_to_values(self) -> None:
        pass
