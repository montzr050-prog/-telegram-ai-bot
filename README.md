# Telegram AI Bot

## Files
- `main.py` — Telegram bot using OpenAI API
- `requirements.txt` — Python dependencies

## Required environment variables
Set these in your hosting provider's service settings (do not put secrets in GitHub files):
- `TELEGRAM_BOT_TOKEN` — token from BotFather
- `OPENAI_API_KEY` — secret API key from OpenAI Platform
- Optional: `OPENAI_MODEL` — defaults to `gpt-4o-mini`

## Render setup
Create a **Background Worker** from this GitHub repository:
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `python main.py`

Add the environment variables above in Render's Environment section, then deploy.
