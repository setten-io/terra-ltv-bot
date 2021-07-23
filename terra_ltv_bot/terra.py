import asyncio

from terra_sdk.client.lcd.lcdclient import AsyncLCDClient
from terra_sdk.exceptions import LCDResponseError

FINDER_URL = "https://finder.terra.money/"


class Terra:
    def __init__(
        self,
        lcd: AsyncLCDClient,
        anchor_market_contract: str,
        anchor_overseer_contract: str,
    ) -> None:
        self.lcd = lcd
        self.anchor_market_contact = anchor_market_contract
        self.anchor_overseer_contact = anchor_overseer_contract

    async def ltv(self, account_address: str) -> float:
        borrower_info, borrow_limit = await asyncio.gather(
            self.lcd.wasm.contract_query(
                contract_address=self.anchor_market_contact,
                query=dict(borrower_info=dict(borrower=account_address)),
            ),
            self.lcd.wasm.contract_query(
                contract_address=self.anchor_overseer_contact,
                query=dict(borrow_limit=dict(borrower=account_address)),
            ),
        )
        borrowed = int(borrower_info["loan_amount"])
        limit = int(borrow_limit["borrow_limit"])
        if limit > 0:
            return round(((borrowed * 60) / limit), 2)
        else:
            return 0

    async def is_staking(self, account_address: str, validator_address: str) -> bool:
        try:
            delegations = await self.lcd.staking.delegations(
                account_address, validator_address
            )
            if delegations and delegations[0].balance.amount > 0:
                return True
            else:
                return False
        except LCDResponseError:
            return False
