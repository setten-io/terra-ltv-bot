import motor
from aiogram import Bot as TelegramBot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from beanie import init_beanie
from terra_sdk.client.lcd.lcdclient import AsyncLCDClient

from .config import Config
from .handlers import Handlers
from .models import all_models
from .tasks import Tasks
from .terra import Terra


class Bot:
    def __init__(self, config: Config) -> None:
        self.dp = Dispatcher(
            TelegramBot(token=config.bot_token, parse_mode=types.ParseMode.MARKDOWN_V2)
        )

        self.terra = Terra(
            AsyncLCDClient(url=config.lcd_url, chain_id=config.chain_id),
            anchor_market_contract="terra1sepfj7s0aeg5967uxnfk4thzlerrsktkpelm5s",
            # anchor_market_contract="terra15dwd5mj8v59wpj0wvt233mf5efdff808c5tkal",
            anchor_overseer_contract="terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8",
            # anchor_overseer_contract="terra1qljxd0y3j3gk97025qvl3lgq8ygup4gsksvaxv",
        )
        self.db = motor.motor_asyncio.AsyncIOMotorClient().ltv

    async def on_startup(self, dp: Dispatcher):
        await init_beanie(
            database=self.db,
            document_models=all_models,
        )
        Handlers(dp, self.terra)
        Tasks(dp, self.terra)

    async def on_shutdown(self, dp: Dispatcher):
        pass

    def run(self) -> None:
        executor.start_polling(
            self.dp,
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown,
        )
