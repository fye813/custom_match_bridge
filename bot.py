# bot.py
from commands import bot
from tasks import start_tasks
import config

@bot.event
async def on_ready():
    print(f"Bot 起動: {bot.user}")
    start_tasks()

bot.run(config.DISCORD_BOT_TOKEN)