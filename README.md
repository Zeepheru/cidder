# CIDDER

This is a Discord bot for the (private) Discord server _Countries in Dispute_. Hence the name.

## Development

### Python venv

```bash
python -m venv env
```

(Windows, cuz I'm a pleb)

```bash
env/Scripts/activate.bat // CMD
env/Scripts/activate.psl // PWSH
```

Install requirements

```bash
pip install -r requirements.txt
```

Create a file called `.env`

```text
# .env
DISCORD_TOKEN={your-bot-token}
# Disables extra logging messages
DEBUG_MODE=0

# DB
DB_HOST={}
DB_NAME={}
DB_USER={}
DB_PASSWORD={}
```

The Discord bot token is a Github secret (on Discord's page it can only be shown **once**)
