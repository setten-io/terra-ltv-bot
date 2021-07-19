from aiogram import types
from aiogram.dispatcher import Dispatcher
from terra_sdk.client.lcd.lcdclient import AsyncLCDClient


class Handlers:
    def __init__(self, dp: Dispatcher, lcd: AsyncLCDClient) -> None:
        self.lcd = lcd
        dp.register_message_handler(self.start, commands=["start"])

    async def start(self, message: types.Message) -> None:
        await message.reply("...")
