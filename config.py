# config.py
from dotenv import load_dotenv
load_dotenv()

import os

# Discord Botのトークンを設定
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# Discord サーバーID
DISCORD_GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])

# イベントを開催するボイスチャンネルのID
DISCORD_VOICE_CHANNEL_ID = int(os.environ["DISCORD_VOICE_CHANNEL_ID"])

# イベントをアナウンスするテキストチャンネルのID
DISCORD_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

# イベントをメンションするロールのID
DISCORD_ROLE_ID = int(os.environ["DISCORD_ROLE_ID"])

# Google Sheets関連の設定
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
WORKSHEET_NAME = os.environ.get("WORKSHEET_NAME", "基本戦績")
CREDENTIALS_FILE = os.environ.get("CREDENTIALS_FILE", "credentials.json")