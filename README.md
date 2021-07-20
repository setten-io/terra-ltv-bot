# terra-ltv-bot
Telegram Terra LTV alerts bot

## Running in production

Requires:

- running mongodb
- running redis
- python ^3.9 and poetry or docker

### Configuration

| envvar                   | type | default               | description                     |
|--------------------------|------|-----------------------|---------------------------------|
| BOT_TOKEN                | str  | -                     | Telegram bot token              |
| DB_HOST                  | str  | `"localhost"`         | Mongo database host             |
| DB_PORT                  | int  | `27017`               | Mongo port host                 |
| REDIS_URL                | str  | `"redis://localhost"` | Redis url connexion string      |
| LCD_URL                  | str  | -                     | Terra lcd url                   |
| CHAIN_ID                 | str  | -                     | Terra chaind id                 |
| ANCHOR_MARKET_CONTRACT   | str  | -                     | Anchor market contract address  |
| ANCHOR_OVERSEER_CONTRACT | str  | -                     | Anchor overseer contact address |

### Run

With docker

```bash
docker build -t terra-ltv-bot .

docker run \
    --name terra-ltv-bot \
    -e BOT_TOKEN="${BOT_TOKEN}" \
    -e LCD_URL="https://lcd.terra.dev" \
    -e CHAIN_ID="columbus-4" \
    -e ANCHOR_MARKET_CONTRACT="terra1sepfj7s0aeg5967uxnfk4thzlerrsktkpelm5s" \
    -e ANCHOR_OVERSEER_CONTRACT="terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8" \
    # + additional config
    terra-ltv-bot
```

## Development

We will take into consideration any pull requests.

Please try to respect [conventional commit messages](https://www.conventionalcommits.org/en/v1.0.0/) and ensure your code passes basic code style and typing tests by running `make all`.

### Setup

With poetry installed:

```bash
poetry install
```

Start redis and mongodb:

```bash
docker compose up -d  # or docker-compose up -d
```

Run the bot from source:

```bash
poetry run terra-ltv-bot
```

## Commands list

```
help - Display an help message
subscribe - Subscribe to an address LTV alerts
list - List all subscribed addresses and their current LTV
unsubscribe - Unsubscribe to an address LTV alerts
ltv - Retreive LTV for an arbitrary address
```
