# main.py

import os
import base64
import discord
from discord.ext import commands
from commands import bot  # commands.py で bot を定義している前提
from tasks import start_tasks
import config

# credentials.json の復元（Railway用）
if "GOOGLE_CREDENTIALS_B64" in os.environ:
    with open("credentials.json", "wb") as f:
        f.write(base64.b64decode(os.environ["GOOGLE_CREDENTIALS_B64"]))

@bot.event
async def on_ready():
    print(f"Bot 起動: {bot.user}")
    start_tasks()

bot.run(config.DISCORD_BOT_TOKEN)