import os
from typing import Optional


class Config:
    def __init__(
        self,
        bot_token: str,
        lcd_url: str,
        chain_id: str,
        anchor_market_contract: str,
        anchor_overseer_contract: str,
        validator_address: Optional[str] = None,
    ) -> None:
        self.bot_token = bot_token
        self.lcd_url = lcd_url
        self.chain_id = chain_id
        self.anchor_market_contract = anchor_market_contract
        self.anchor_overseer_contract = anchor_overseer_contract
        self.validator_address = validator_address

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            os.environ["BOT_TOKEN"],
            os.environ["LCD_URL"],
            os.environ["CHAIN_ID"],
            os.environ["ANCHOR_MARKET_CONTRACT"],
            os.environ["ANCHOR_OVERSEER_CONTRACT"],
            os.getenv("VALIDATOR_ADDRESS"),
        )
