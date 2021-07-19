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


class Bot:
    def __init__(self, config: Config) -> None:
        self.dp = Dispatcher(
            TelegramBot(token=config.bot_token, parse_mode=types.ParseMode.MARKDOWN_V2)
        )
        self.lcd = AsyncLCDClient(url=config.lcd_url, chain_id=config.chain_id)
        self.db = motor.motor_asyncio.AsyncIOMotorClient().ltv

    async def on_startup(self, dp: Dispatcher):
        await init_beanie(
            database=self.db,
            document_models=all_models,
        )
        Handlers(dp, self.lcd)
        Tasks(dp, self.lcd)

    async def on_shutdown(self, dp: Dispatcher):
        pass

    def run(self) -> None:
        executor.start_polling(
            self.dp,
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown,
        )
