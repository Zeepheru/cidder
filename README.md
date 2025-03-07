# CIDDER

This is a Discord bot for the (private) Discord server _Countries in Dispute_. Hence the name.

## Usage

WIP :c

## Development

### Setting Up

Set up Python venv:

```bash
python -m venv venv
```

Activate:

```shell
source venv/bin/activate
# Windows
venv/Scripts/activate.bat # CMD
venv/Scripts/activate.psl # PWSH
```

Install requirements:

```bash
pip install -r requirements.txt
```

Create the `.env` file. Remember to use quotes `"` for strings.
This contains the environment variables that are required.

```text
DISCORD_TOKEN={your-bot-token}
DEBUG_MODE=0

# DB
DB_HOST={}
DB_NAME={}
DB_USER={}
DB_PASSWORD={}
```

To run:

```bash
python3 -m cidderbot.bot
```
