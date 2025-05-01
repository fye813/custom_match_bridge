import datetime
import discord
import config
from discord.ext import tasks
from commands import bot  # commands.py で定義した bot をインポート

# -------------- 定期イベント作成タスク --------------

@tasks.loop(time=[datetime.time(9, 30, 0, tzinfo=datetime.timezone.utc)])
async def auto_create_event():
    """
    毎日UTC12:00（日本時間21:00）に起動し、木曜日のみボイスチャットイベントを作成します。
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    if now.weekday() != 3:  # 木曜日
        return

    guild = bot.get_guild(config.DISCORD_GUILD_ID)
    if not guild:
        print("ギルドが見つかりません。")
        return

    channel = bot.get_channel(config.DISCORD_VOICE_CHANNEL_ID)
    if not channel or not isinstance(channel, discord.VoiceChannel):
        print(f"指定されたボイスチャンネルID({config.DISCORD_VOICE_CHANNEL_ID})が見つかりません。")
        return

    # 「今」の木曜日から次の土曜日の日付を計算
    # weekday: 0=月,1=火,2=水,3=木,4=金,5=土,6=日
    days_until_saturday = (5 - now.weekday()) % 7
    saturday_date = now.date() + datetime.timedelta(days=days_until_saturday)

    # 日本時間21:00を開始日時に設定
    jst = datetime.timezone(datetime.timedelta(hours=9))
    start_time = datetime.datetime.combine(
        saturday_date,
        datetime.time(21, 0, tzinfo=jst)
    )

    try:
        with open("img.png", "rb") as f:
            cover_data = f.read()
    except FileNotFoundError:
        cover_data = None
        print("img.png が見つかりません。画像なしでイベントを作成します。")

    try:
        event = await guild.create_scheduled_event(
            name="【定期】土曜深夜LoLカスタム",
            description=(
                "祝：定期開催決定  毎週土曜21時開始予定\n\n"
                "参加できる人は「興味あり」ボタンを押してください。\n"
                "時間までに10人集まれば開催、集まらなければノーマルor解散で。"
            ),
            entity_type=discord.EntityType.voice,
            privacy_level=discord.PrivacyLevel.guild_only,
            start_time=start_time,
            channel=channel,
            image=cover_data
        )
        
        announce_channel = bot.get_channel(config.DISCORD_CHANNEL_ID)
        role_id = config.DISCORD_ROLE_ID
        event_url = f"https://discord.com/events/{guild.id}/{event.id}"

        if announce_channel:
            await announce_channel.send(
                f"<@&{role_id}>\n"
                f"{event.name}\n"
                "参加できる人は「興味あり」ボタンを押してください！\n"
                f"{event_url}"
            )
        else:
            print(f"指定チャンネルID({config.DISCORD_CHANNEL_ID})が見つかりません。")

    except Exception as e:
        print(f"定期イベント作成失敗: {e}")

# -------------- 動作確認用 1分ごと ping タスク --------------

# @tasks.loop(minutes=1)
# async def test_ping():
#     """
#     動作確認用に 1 分ごとに指定チャンネルへ 'ping' を送信します。
#     config.TEST_CHANNEL_ID にテスト用チャンネルのIDを設定してください。
#     """
#     channel = bot.get_channel(config.DISCORD_CHANNEL_ID)
#     if channel:
#         await channel.send("ping")
#     else:
#         print("テスト用チャンネルが見つかりません。")

# -------------- タスク起動関数 --------------

def start_tasks():
    auto_create_event.start()
    # test_ping.start()
