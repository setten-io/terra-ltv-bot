import os


class Config:
    def __init__(
        self,
        bot_token: str,
        lcd_url: str,
        chain_id: str,
    ) -> None:
        self.bot_token = bot_token
        self.lcd_url = lcd_url
        self.chain_id = chain_id

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            os.environ["BOT_TOKEN"],
            os.environ["LCD_URL"],
            os.environ["CHAIN_ID"],
        )
