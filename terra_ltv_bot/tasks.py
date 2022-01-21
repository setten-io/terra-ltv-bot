import asyncio
import logging
from functools import wraps
from typing import Callable

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from aioredis import Redis

from .models import Subscription
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

    @skip_exceptions
    async def check_ltv_ratio(self) -> None:
        log.debug("sending deprecation message")
        async for subscription in Subscription.find_all():
            try:
                await self.bot.send_message(
                    subscription.telegram_id,
                    (
                        "⚠️ We are deprecating and stoping our Terra LTV bot ⚠️\n"
                        "https://twitter.com/ArbieApp does what "
                        "our bot does and more.\n",
                        "Please switch to it right now.",
                    ),
                )
                log.info(f"{subscription.telegram_id} alerted")
            except TelegramAPIError as e:
                log.warning(f"Couldn't send alert to {subscription.telegram_id}: {e}")
