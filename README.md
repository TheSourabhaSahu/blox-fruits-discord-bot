# Blox Fruits Pricing Bot Setup

This is a simple Discord bot that tells you the fixed Beli and Robux prices for Blox Fruits.

## 📂 Files
- `bot.py`: The main code for the bot.
- `fruits_data.py`: The database of prices.
- `requirements.txt`: List of python libraries needed.

## 🚀 How to Run Locally

1. **Install Python**: Make sure you have Python installed.
2. **Install Dependencies**:
   Open a terminal/command prompt in this folder and run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Get Discord Token**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications).
   - Create a New Application -> Bot -> Reset Token.
   - Copy that token.
4. **Run the Bot**:
   - Create a file named `.env` in this folder.
   - Add this line inside it: `DISCORD_TOKEN=your_token_here_paste_it`
   - Run command: `python bot.py`

## ✅ Slash Commands
- `/price <fruit>`
- `/list`

## 🔐 Optional Anti‑Abuse Settings (Environment Variables)
- `ALLOWED_GUILDS` (comma-separated IDs): only allow commands in these servers.
- `RATE_LIMIT_MAX` (default `5`): max requests per user in the window.
- `RATE_LIMIT_WINDOW_SECONDS` (default `10`): window size in seconds.
- `LOG_LEVEL` (default `INFO`)

## 🔗 Invite Scope
Make sure your bot invite uses the `applications.commands` scope so slash commands show up.

## 🔗 Source
Idea Source: [Blox fruits prices](https://bloxfruitscode.com/blox-fruits-values-trade/)
