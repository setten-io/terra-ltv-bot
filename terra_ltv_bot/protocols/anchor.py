import asyncio

from terra_sdk.client.lcd import AsyncLCDClient
from terra_sdk.exceptions import LCDResponseError

from .protocol import Protocol


class Anchor(Protocol):
    SAFE_RATIO = 45
    SLUG = "anchor"
    EMOJI = "⚓"

    def __init__(
        self,
        lcd: AsyncLCDClient,
        market_contract: str,
        overseer_contract: str,
    ) -> None:
        self.lcd = lcd
        self.market_contract = market_contract
        self.overseer_contract = overseer_contract

    async def ltv(
        self,
        account_address: str,
    ) -> float:
        try:
            borrower_info, borrow_limit = await asyncio.gather(
                self.lcd.wasm.contract_query(
                    contract_address=self.market_contract,
                    query=dict(borrower_info=dict(borrower=account_address)),
                ),
                self.lcd.wasm.contract_query(
                    contract_address=self.overseer_contract,
                    query=dict(borrow_limit=dict(borrower=account_address)),
                ),
            )
            borrowed = int(borrower_info["loan_amount"])
            limit = int(borrow_limit["borrow_limit"])
            if limit > 0:
                return round(((borrowed * 60) / limit), 2)
        except LCDResponseError:
            pass
        return 0
