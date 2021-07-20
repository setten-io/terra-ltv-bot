from beanie import Document, Indexed
from pydantic import validator

from .utils import is_account_address


class Address(Document):
    account_address: Indexed(str, unique=True)  # type: ignore
    subscribers: list[int] = []  # telegram ids
    is_staker: bool = False

    @validator("account_address", always=True)
    def account_address_should_be_a_terra_address(cls, v: str):
        if not is_account_address(v):
            raise ValueError("invalid account address")
        return v

    @staticmethod
    async def get_or_create(account_address: str) -> "Address":
        address = await Address.find_one(Address.account_address == account_address)
        if not address:
            new_address = Address(account_address=account_address)
            await new_address.insert()
            return new_address
        else:
            return address


all_models = [Address]
