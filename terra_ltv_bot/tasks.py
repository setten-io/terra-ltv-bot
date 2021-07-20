import asyncio
from datetime import timedelta
import logging
from functools import wraps
from typing import Callable

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aioredis import Redis

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
    def __init__(self, dp: Dispatcher, bot: Bot, terra: Terra, redis: Redis) -> None:
        self.bot = bot
        self.terra = terra
        self.redis = redis
        dp._loop_create_task(self.check_ltv_ratio())

    @every(5 * 60)
    @skip_exceptions
    async def check_ltv_ratio(self) -> None:
        log.debug("checking ltv ratios")
        tasks = []
        addresses = await Address.find_all().to_list()
        for result in addresses:
            tasks.append(asyncio.create_task(self.terra.ltv(result.account_address)))
        ltvs = await asyncio.gather(*tasks)
        for index, ltv in enumerate(ltvs):
            address = addresses[index]
            if ltv >= 35:
                log.debug(f"{address.account_address} {ltv}% alerting")
                await asyncio.gather(
                    *[
                        self.notify(address.account_address, subscriber, ltv)
                        for subscriber in address.subscribers
                    ]
                )
            else:
                log.debug(f"{address.account_address} {ltv}% not alerting")

    async def notify(self, account_address: str, telegram_id: int, ltv: float) -> None:
        key = f"{account_address}:{telegram_id}"
        if not await self.redis.get(key):
            await self.bot.send_message(
                telegram_id,
                f"🚨 {ltv}% LTV ratio:\n<pre>{account_address}</pre>",
            )
            await self.redis.set(key, int(True), ex=timedelta(hours=2))
            log.info(f"{account_address} {telegram_id} notified")
        else:
            log.debug(f"{account_address} {telegram_id} muted")
