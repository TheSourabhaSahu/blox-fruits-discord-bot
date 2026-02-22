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
_last_cleanup = 0.0  # Track last cleanup time
_CLEANUP_INTERVAL = 300  # Purge stale entries every 5 minutes

def _rate_limit_ok(user_id: int) -> bool:
    global _last_cleanup
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    # Periodic cleanup: remove users with no recent activity
    if now - _last_cleanup > _CLEANUP_INTERVAL:
        stale_keys = [uid for uid, ts_list in _rate_state.items() if not ts_list or ts_list[-1] < window_start]
        for uid in stale_keys:
            del _rate_state[uid]
        _last_cleanup = now

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
    await bot.change_presence(activity=discord.Game(name="/price | /trade | /roll"))
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
    # Rarity color mapping could be added here later
    rarity = info.get("rarity", "Unknown")
    embed.add_field(name="✨ Rarity", value=rarity, inline=True)
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

@bot.tree.command(name="compare", description="Compare two fruits side-by-side.")
@app_commands.describe(fruit1="First fruit", fruit2="Second fruit")
async def compare_slash(interaction: discord.Interaction, fruit1: str, fruit2: str):
    if not _guild_allowed(interaction.guild):
        await interaction.response.send_message("❌ Not enabled here.", ephemeral=True)
        return
    if not _rate_limit_ok(interaction.user.id):
        await interaction.response.send_message("⏳ You're sending commands too fast. Try again shortly.", ephemeral=True)
        return
    
    info1 = fruits_data.get_fruit_info(fruit1)
    info2 = fruits_data.get_fruit_info(fruit2)
    
    if not info1 or not info2:
        missing = []
        if not info1: missing.append(fruit1)
        if not info2: missing.append(fruit2)
        await interaction.response.send_message(f"❌ Could not find: {', '.join(missing)}", ephemeral=True)
        return

    embed = discord.Embed(title=f"⚖️ {fruit1.title()} vs {fruit2.title()}", color=0xf1c40f)
    
    # Compare Beli
    p1 = info1['beli']
    p2 = info2['beli']
    
    val_diff = abs(p1 - p2)
    diff_msg = f"Difference: ${val_diff:,}"
    
    if p1 > p2:
        embed.add_field(name=f"🏆 {fruit1.title()}", value=f"**${info1['formatted_beli']}**\n(More expensive)", inline=True)
        embed.add_field(name=f"{fruit2.title()}", value=f"${info2['formatted_beli']}", inline=True)
    elif p2 > p1:
        embed.add_field(name=f"{fruit1.title()}", value=f"${info1['formatted_beli']}", inline=True)
        embed.add_field(name=f"🏆 {fruit2.title()}", value=f"**${info2['formatted_beli']}**\n(More expensive)", inline=True)
    else:
        embed.add_field(name=f"{fruit1.title()}", value=f"${info1['formatted_beli']}", inline=True)
        embed.add_field(name=f"{fruit2.title()}", value=f"${info2['formatted_beli']}", inline=True)
        diff_msg = "Equal Value"
        
    embed.set_footer(text=diff_msg)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roll", description="Simulate a random fruit spin (Gacha).")
async def roll_slash(interaction: discord.Interaction):
    if not _guild_allowed(interaction.guild):
        await interaction.response.send_message("❌ Not enabled here.", ephemeral=True)
        return
    if not _rate_limit_ok(interaction.user.id):
        await interaction.response.send_message("⏳ Cooldown! Wait a bit.", ephemeral=True)
        return

    # Simulate "spinning" animation? Maybe just instant for now to respect rate limits
    fruit_name = fruits_data.get_random_fruit()
    info = fruits_data.get_fruit_info(fruit_name)
    
    rarity = info.get("rarity", "Common")
    # Color based on rarity
    colors = {
        "Common": 0x95a5a6,    # Gray
        "Uncommon": 0x3498db,  # Blue
        "Rare": 0x9b59b6,      # Purple
        "Legendary": 0xe74c3c, # Red
        "Mythical": 0xf1c40f   # Gold
    }
    color = colors.get(rarity, 0x00ff00)
    
    embed = discord.Embed(title="🎲 Blox Fruit Gacha", description=f"You rolled: **{fruit_name.title()}**!", color=color)
    embed.add_field(name="Rarity", value=rarity, inline=True)
    embed.add_field(name="Value", value=f"${info['formatted_beli']}", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="trade", description="Calculate trade value and check fair trade rules (40% diff).")
@app_commands.describe(your_offer="Your fruits (comma separated)", their_offer="Their fruits (comma separated)")
async def trade_slash(interaction: discord.Interaction, your_offer: str, their_offer: str):
    if not _guild_allowed(interaction.guild):
        await interaction.response.send_message("❌ Not enabled here.", ephemeral=True)
        return
    if not _rate_limit_ok(interaction.user.id):
        await interaction.response.send_message("⏳ You're sending commands too fast. Try again shortly.", ephemeral=True)
        return

    val1, fruits1, unk1 = fruits_data.calculate_trade_value(your_offer)
    val2, fruits2, unk2 = fruits_data.calculate_trade_value(their_offer)
    
    embed = discord.Embed(title="🤝 Trade Calculator", color=0x34495e)
    
    # Side 1
    f1_str = ", ".join(fruits1) if fruits1 else "None"
    embed.add_field(name="You Offer", value=f"{f1_str}\n**${val1:,}**", inline=True)
    
    # Side 2
    f2_str = ", ".join(fruits2) if fruits2 else "None"
    embed.add_field(name="They Offer", value=f"{f2_str}\n**${val2:,}**", inline=True)
    
    # Validation Logic
    if val1 == 0 and val2 == 0:
        await interaction.response.send_message("❌ No valid fruits found.", ephemeral=True)
        return

    # Avoid division by zero
    max_val = max(val1, val2)
    min_val = min(val1, val2)
    
    if max_val == 0: # Should be covered above but safety check
        diff_pct = 0
    else:
        diff_pct = ((max_val - min_val) / max_val) * 100
        
    # Blox Fruits Rule: Value difference must be <= 40%
    is_fair = diff_pct <= 40
    
    status_emoji = "✅" if is_fair else "⚠️"
    status_text = "Fair Trade (Possible)" if is_fair else "Value Difference Too High (Impossible in-game)"
    
    # Determining generic "Win/Loss" ignoring the 40% rule purely on value
    if val1 > val2:
        value_result = "You are overpaying."
    elif val2 > val1:
        value_result = "You are gaining value (W)."
    else:
        value_result = "Equal value."

    embed.add_field(name="Analysis", value=f"Difference: **{diff_pct:.1f}%**\n{status_emoji} {status_text}\n💡 {value_result}", inline=False)
    
    if unk1 or unk2:
        all_unk = unk1 + unk2
        embed.set_footer(text=f"Unknown items ignored: {', '.join(all_unk)}")
        
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
