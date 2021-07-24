import asyncio
import logging
from datetime import timedelta
from functools import wraps
from typing import Callable

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aioredis import Redis

from .models import Address, Subscription
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
        addresses: dict[str, Address] = {}
        async for address in Address.find_all():
            addresses[str(address.id)] = address
        tasks = []
        for address in addresses.values():
            tasks.append(asyncio.create_task(self.terra.ltv(address.account_address)))
        ltvs = await asyncio.gather(*tasks)
        addresses_id_to_ltv = dict(
            zip([address.id for address in addresses.values()], ltvs)
        )
        async for subscription in Subscription.find_all():
            address_id = str(subscription.address_id)
            account_address = addresses[address_id].account_address
            ltv = addresses_id_to_ltv[subscription.address_id]
            cache_key = f"{account_address}:anchor:{subscription.telegram_id}"
            if subscription.alert_threshold <= ltv and not await self.redis.get(
                cache_key
            ):
                await self.bot.send_message(
                    subscription.telegram_id,
                    f"🚨 anchor LTV ratio is at {ltv}%:\n<pre>{account_address}</pre>",
                )
                log.info(f"{account_address} {subscription.telegram_id} {ltv}")
                await self.redis.set(cache_key, 1, ex=timedelta(hours=1))
            elif subscription.alert_threshold <= ltv:
                log.debug(f"{account_address} {subscription.telegram_id} {ltv} muted")
            else:
                log.debug(f"{account_address} {ltv} ok")
