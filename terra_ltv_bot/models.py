from beanie import Document, Indexed
from pydantic import validator


class Account(Document):
    telegram_id: Indexed(int, unique=True)  # type: ignore
    balances: dict[str, int] = {}
    games: int = 0
    wins: int = 0

    @validator("telegram_id", always=True)
    def telegram_should_be_positive_and_not_null(cls, v: int):
        if 0 >= v:
            raise ValueError("should be positive")
        return v

    @staticmethod
    async def get_or_create(telegram_id: int) -> "Account":
        account = await Account.find_one(Account.telegram_id == telegram_id)
        if not account:
            new_account = Account(telegram_id=telegram_id)
            await new_account.insert()
            return new_account
        else:
            return account

    def get_active_balances(self) -> dict[str, int]:
        return {denom: amount for denom, amount in self.balances.items() if amount > 0}


class Crawler(Document):
    chain_id: Indexed(str, unique=True)  # type: ignore
    height: int

    @staticmethod
    async def get_or_create(chain_id: str, height: int) -> "Crawler":
        crawler = await Crawler.find_one(Crawler.chain_id == chain_id)
        if not crawler:
            new_crawler = Crawler(chain_id=chain_id, height=height)
            await new_crawler.insert()
            return new_crawler
        else:
            return crawler


all_models = [Account, Crawler]
