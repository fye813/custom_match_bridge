# commands.py
import random
import discord
from discord.ext import commands
import config
from ui import TeamSelectView

# === intents を定義 ===
intents = discord.Intents.default()
intents.message_content = True
intents.guild_scheduled_events = True

# === Botインスタンスを作成 ===
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def team(ctx):
    """
    !team コマンドでチーム分けUIを起動します。
    """
    try:
        # Google Sheets から参加者リストを取得
        from core import get_data
        data = get_data(
            config.CREDENTIALS_FILE,
            config.SPREADSHEET_ID,
            config.WORKSHEET_NAME
        )
        player_names = data["参加者"].tolist()
        options = [discord.SelectOption(label=n, value=n) for n in player_names]
    except Exception as e:
        await ctx.send(f"プレイヤー名の取得に失敗しました: {e}")
        return

    view = TeamSelectView(options)
    await ctx.send("下記のメニューから基準とプレイヤーを選択してください。", view=view)

@bot.command()
async def side(ctx):
    random_side = random.choice(["Blue", "Red"])
    await ctx.send(random_side)