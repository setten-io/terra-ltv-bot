def linkify(account_address: str) -> str:
    return (
        "<a href='https://finder.terra.money/columbus-4/address/{}'>{}...{}</a>".format(
            account_address, account_address[:13], account_address[-5:]
        )
    )
