from abc import ABC, abstractmethod
from typing import Optional

from terra_ltv_bot.models import Address, Subscription


class Protocol(ABC):
    SAFE_RATIO: float
    SLUG: str
    EMOJI: str

    @abstractmethod
    async def ltv(self, account_address: str) -> Optional[float]:
        """get ltv for an account"""

    async def subscribe(
        self, account_address: str, alert_threshold: Optional[float], telegram_id: int
    ) -> Subscription:
        """subscribe to an address"""
        threshold = alert_threshold or self.SAFE_RATIO
        address = await Address.find_one(Address.account_address == account_address)
        if not address:
            address = Address(account_address)
            await address.insert()
        subscription = await Subscription.find_one(
            Subscription.address_id == address.id,
            Subscription.protocol == self.SLUG,
            Subscription.telegram_id == telegram_id,
        )
        if subscription:
            if threshold != subscription.alert_threshold:
                subscription.alert_threshold = threshold
        await subscription.save()
        return subscription
