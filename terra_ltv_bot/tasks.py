import asyncio
import logging
from functools import wraps
from typing import Callable

from aiogram.dispatcher import Dispatcher

from .models import Address
from .terra import Terra

log = logging.getLogger(__name__)


def every(frequency: int) -> Callable:
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        async def wrapper(self) -> None:
            while True:
                await f(self)
                await asyncio.sleep(frequency)

        return wrapper

    return decorator


def skip_exceptions(f: Callable) -> Callable:
    @wraps(f)
    async def wrapper(self) -> None:
        try:
            await f(self)
        except Exception as e:
            log.error(f"exception in task: {e}", stack_info=True)

    return wrapper


class Tasks:
    def __init__(self, dp: Dispatcher, terra: Terra) -> None:
        self.terra = terra
        dp._loop_create_task(self.check_loans_to_values())

    @every(60 * 5)
    @skip_exceptions
    async def check_loans_to_values(self) -> None:
        tasks = []
        addresses = await Address.find_all().to_list()
        for result in addresses:
            tasks.append(asyncio.create_task(self.terra.ltv(result.account_address)))
        ltvs = await asyncio.gather(*tasks)
        for index, ltv in enumerate(ltvs):
            if ltv >= 35:
                print(addresses[index].account_address, "alert")
            else:
                print(addresses[index].account_address, "ok")
