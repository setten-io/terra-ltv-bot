import os
from typing import Optional


class Config:
    def __init__(
        self,
        debug: bool,
        bot_token: str,
        db_host: str,
        db_port: int,
        redis_url: str,
        lcd_url: str,
        chain_id: str,
        anchor_market_contract: str,
        anchor_overseer_contract: str,
        validator_address: Optional[str],
    ) -> None:
        self.debug = debug
        self.bot_token = bot_token
        self.db_host = db_host
        self.db_port = db_port
        self.redis_url = redis_url
        self.lcd_url = lcd_url
        self.chain_id = chain_id
        self.anchor_market_contract = anchor_market_contract
        self.anchor_overseer_contract = anchor_overseer_contract
        self.validator_address = validator_address

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            bool(os.getenv("BOT_TOKEN")),
            os.environ["BOT_TOKEN"],
            os.getenv("DB_HOST", "localhost"),
            int(os.getenv("DB_PORT", "27017")),
            os.getenv("REDIS_URL", "redis://localhost"),
            os.environ["LCD_URL"],
            os.environ["CHAIN_ID"],
            os.environ["ANCHOR_MARKET_CONTRACT"],
            os.environ["ANCHOR_OVERSEER_CONTRACT"],
            os.getenv("VALIDATOR_ADDRESS"),
        )
