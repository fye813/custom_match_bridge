import discord
from discord.ext import commands
import pandas as pd
import config
from core import get_data, divide_teams_by_criteria  # core.py の関数群をインポート

# --- UI コンポーネントの定義 ---

class CriteriaSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="勝率", description="勝率ベースでチーム分け", value="1"),
            discord.SelectOption(label="KDA", description="KDAベースでチーム分け", value="2")
        ]
        super().__init__(
            placeholder="チーム分けの基準を選択してください",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        # 選択結果を数値に変換し、View に保持
        self.view.criteria = int(self.values[0])
        # 応答は defer して何もメッセージを送らない（静かに状態を更新）
        await interaction.response.defer(ephemeral=True)

class PlayerSelect(discord.ui.Select):
    def __init__(self, player_options):
        # ユーザーに1名以上、全体まで選択可能に設定
        super().__init__(
            placeholder="参加するプレイヤーを選択してください",
            min_values=1,
            max_values=10,
            options=player_options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_names = self.values
        # 応答を defer して、静かに選択状態を更新
        await interaction.response.defer(ephemeral=True)

class TeamSelectView(discord.ui.View):
    def __init__(self, player_options):
        super().__init__(timeout=180)
        self.add_item(CriteriaSelect())
        self.add_item(PlayerSelect(player_options))
        self.criteria = None
        self.selected_names = None

    @discord.ui.button(label="チーム分けを実行", style=discord.ButtonStyle.primary)
    async def execute(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 基準またはプレイヤー選択が完了しているかチェック
        if self.criteria is None or self.selected_names is None:
            await interaction.response.send_message("基準またはプレイヤー選択が完了していません。", ephemeral=True)
            return

        try:
            # core.py の get_data を用いて、Google Sheets からデータを取得
            data = get_data(config.CREDENTIALS_FILE, config.SPREADSHEET_ID, config.WORKSHEET_NAME)
        except Exception as e:
            await interaction.response.send_message(f"データ取得に失敗しました: {str(e)}", ephemeral=True)
            return

        # ユーザー選択されたプレイヤーに基づき、チーム分けを実行
        teams = divide_teams_by_criteria(data, self.selected_names, criteria=self.criteria, team_count=2)
        result_message = ""
        for i, team_df in enumerate(teams, start=1):
            result_message += f"【チーム{i}】\n"
            for _, row in team_df.iterrows():
                result_message += f"・{row['参加者']} (勝率: {row['勝率']}, KDA: {row['KDA']})\n"
            result_message += "\n"

        await interaction.response.send_message(result_message)

# --- Bot の設定 ---

intents = discord.Intents.default()
intents.message_content = True  # Developer Portal で有効にしてください
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def team(ctx):
    """
    !selectteam コマンドで、セレクトボックスを利用して
      ・チーム分けの基準（勝率またはKDA）を選択
      ・参加するプレイヤーを選択し、チーム分けの結果を返します。
    """
    try:
        # core.py の get_data を使ってシートからデータを取得
        data = get_data(config.CREDENTIALS_FILE, config.SPREADSHEET_ID, config.WORKSHEET_NAME)
        # '参加者' 列を使ってプレイヤー名の選択肢を作成
        player_names = data["参加者"].tolist()
        player_options = [discord.SelectOption(label=name, value=name) for name in player_names]
    except Exception as e:
        await ctx.send(f"プレイヤー名の取得に失敗しました: {str(e)}")
        return

    view = TeamSelectView(player_options)
    await ctx.send("下記のメニューからチーム分けの基準と参加プレイヤーを選択してください。", view=view)

@bot.event
async def on_ready():
    print(f"Botがログインしました: {bot.user}")

bot.run(config.DISCORD_BOT_TOKEN)
