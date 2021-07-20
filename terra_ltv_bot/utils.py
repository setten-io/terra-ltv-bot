def is_account_address(account_address: str) -> bool:
    if account_address.startswith("terra1") and len(account_address) == 44:
        return True
    else:
        return False
