import discord
from discord import app_commands
from discord.ext import commands
import os
import time
import logging
import fruits_data
from dotenv import load_dotenv
from keep_alive import keep_alive

# Load environment variables if .env exists (for local testing)
load_dotenv()

# Get token from environment
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup intents (no message content needed for slash-only)
intents = discord.Intents.default()

bot = commands.Bot(command_prefix='!', intents=intents)

# Basic logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("blox-bot")

# Anti-abuse settings (env-configurable)
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "5"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "10"))
ALLOWED_GUILDS = {
    int(g.strip())
    for g in os.getenv("ALLOWED_GUILDS", "").split(",")
    if g.strip().isdigit()
}

# Simple in-memory rate limiter per user
_rate_state = {}  # {user_id: [timestamps]}

def _rate_limit_ok(user_id: int) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    ts_list = _rate_state.get(user_id, [])
    ts_list = [ts for ts in ts_list if ts >= window_start]
    if len(ts_list) >= RATE_LIMIT_MAX:
        _rate_state[user_id] = ts_list
        return False
    ts_list.append(now)
    _rate_state[user_id] = ts_list
    return True

def _guild_allowed(guild: discord.Guild | None) -> bool:
    if not ALLOWED_GUILDS:
        return True
    if guild is None:
        return False
    return guild.id in ALLOWED_GUILDS

@bot.event
async def on_ready():
    log.info("Logged in as %s (ID: %s)", bot.user.name, bot.user.id)
    # Set status
    await bot.change_presence(activity=discord.Game(name="/price <fruit> | /list"))
    try:
        await bot.tree.sync()
        log.info("Slash commands synced.")
    except Exception as exc:
        log.exception("Failed to sync slash commands: %s", exc)

def _build_price_embed(fruit_name: str, info: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"🍎 {fruit_name.title()} Info",
        color=0x00ff00
    )
    embed.add_field(name="💰 Beli Price", value=f"${info['formatted_beli']}", inline=True)
    embed.add_field(name="💎 Robux Price", value=f"R$ {info['formatted_robux']}", inline=True)
    embed.set_footer(text="Blox Fruits Pricing Bot")
    return embed

@bot.tree.command(name="price", description="Check the Beli and Robux price of a fruit.")
@app_commands.describe(fruit_name="The fruit to look up")
async def price_slash(interaction: discord.Interaction, fruit_name: str):
    if not _guild_allowed(interaction.guild):
        await interaction.response.send_message("❌ This bot is not enabled in this server.", ephemeral=True)
        return
    if not _rate_limit_ok(interaction.user.id):
        await interaction.response.send_message("⏳ You're sending commands too fast. Try again shortly.", ephemeral=True)
        return

    info = fruits_data.get_fruit_info(fruit_name)

    if info:
        embed = _build_price_embed(fruit_name, info)
        await interaction.response.send_message(embed=embed)
    else:
        all_fruits = fruits_data.get_all_fruits()
        possible_matches = [f for f in all_fruits if fruit_name.lower() in f]

        msg = f"❌ could not find fruit **{fruit_name}**."
        if possible_matches:
            formatted_matches = ", ".join([f"`{m}`" for m in possible_matches[:3]])
            msg += f"\nDid you mean: {formatted_matches}?"
        else:
            msg += "\nUse `/list` to see all available fruits."

        await interaction.response.send_message(msg)

@bot.tree.command(name="list", description="List all available fruits.")
async def list_slash(interaction: discord.Interaction):
    if not _guild_allowed(interaction.guild):
        await interaction.response.send_message("❌ This bot is not enabled in this server.", ephemeral=True)
        return
    if not _rate_limit_ok(interaction.user.id):
        await interaction.response.send_message("⏳ You're sending commands too fast. Try again shortly.", ephemeral=True)
        return

    fruits = fruits_data.get_all_fruits()
    fruit_list = ", ".join([f"`{f.title()}`" for f in fruits])

    embed = discord.Embed(
        title="📜 All Blox Fruits",
        description=fruit_list,
        color=0x3498db
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    log.exception("App command error: %s", error)
    if interaction.response.is_done():
        await interaction.followup.send("❌ Something went wrong. Try again later.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Something went wrong. Try again later.", ephemeral=True)

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        print("Please set it in your Render environment variables or .env file.")
    else:
        keep_alive()  # Start the web server
        bot.run(TOKEN)
