import os
import asyncio

import nextcord
from nextcord.ext import commands
from colorama import Fore

from config import BOT_TOKEN, BOT_PREFIX, BOT_STATUS_TEXT, BOT_STATUS_URL, FOOTER_TEXT

intents = nextcord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)


@bot.event
async def on_ready():
    guild_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)
    command_count = len(bot.commands)

    print(Fore.BLUE + f"""
▸ {bot.user.name} is now online ◂
› ID ‐ {bot.user.id}
› Guilds - {guild_count}
› Members - {member_count}
› Commands - {command_count}
› {FOOTER_TEXT}
""")

    await bot.change_presence(
        status=nextcord.Status.idle,
        activity=nextcord.Streaming(name=BOT_STATUS_TEXT, url=BOT_STATUS_URL),
    )


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
                print(Fore.GREEN + f"[OK] Loaded cog: {filename[:-3]}")
            except Exception as e:
                print(Fore.RED + f"[ERR] Failed to load {filename}: {e}")


asyncio.run(load_extensions())

if not BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set. Check your .env file.")

bot.run(BOT_TOKEN)
