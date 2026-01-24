import discord
from discord.ext import commands
import os
import fruits_data
from dotenv import load_dotenv
from keep_alive import keep_alive

# Load environment variables if .env exists (for local testing)
load_dotenv()

# Get token from environment
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup intents (Basic permissions needed to read messages)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    # Set status
    await bot.change_presence(activity=discord.Game(name="!price <fruit> | !list"))

@bot.command(name='price')
async def price(ctx, *, fruit_name: str = None):
    """Checks the price of a fruit. Usage: !price leopard"""
    if not fruit_name:
        await ctx.send("Please specify a fruit! Example: `!price leopard`")
        return

    info = fruits_data.get_fruit_info(fruit_name)

    if info:
        # Create a nice embed
        embed = discord.Embed(
            title=f"🍎 {fruit_name.title()} Info",
            color=0x00ff00  # Green color
        )
        embed.add_field(name="💰 Beli Price", value=f"${info['formatted_beli']}", inline=True)
        embed.add_field(name="💎 Robux Price", value=f"R$ {info['formatted_robux']}", inline=True)
        embed.set_footer(text="Blox Fruits Pricing Bot")
        
        await ctx.send(embed=embed)
    else:
        # Simple fuzzy search suggestion (optional but nice)
        all_fruits = fruits_data.get_all_fruits()
        # Initial primitive check: is it in the name?
        possible_matches = [f for f in all_fruits if fruit_name.lower() in f]
        
        msg = f"❌ could not find fruit **{fruit_name}**."
        if possible_matches:
            formatted_matches = ", ".join([f"`{m}`" for m in possible_matches[:3]])
            msg += f"\nDid you mean: {formatted_matches}?"
        else:
            msg += "\nUse `!list` to see all available fruits."
            
        await ctx.send(msg)

@bot.command(name='list')
async def list_fruits(ctx):
    """Lists all available fruits."""
    fruits = fruits_data.get_all_fruits()
    # Join nicely
    fruit_list = ", ".join([f"`{f.title()}`" for f in fruits])
    
    # Discord has a 2000 char limit, but this list is short enough for now.
    embed = discord.Embed(
        title="📜 All Blox Fruits",
        description=fruit_list,
        color=0x3498db
    )
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass # Ignore command not found errors
    else:
        print(f"Error: {error}")

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        print("Please set it in your Render environment variables or .env file.")
    else:
        keep_alive()  # Start the web server
        bot.run(TOKEN)
