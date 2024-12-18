# CIDDER

This is a Discord bot for the private RP Discord server _Countries in Dispute_. Hence the name.

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
```

The Discord bot token is a Github secret (on Discord's page it can only be shown **once**)
