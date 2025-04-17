import discord
import config
from core import get_data, divide_teams_by_criteria

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
        self.view.criteria = int(self.values[0])
        await interaction.response.defer(ephemeral=True)

class PlayerSelect(discord.ui.Select):
    def __init__(self, player_options):
        super().__init__(
            placeholder="参加するプレイヤーを選択してください",
            min_values=1,
            max_values=10,
            options=player_options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_names = self.values
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
        if self.criteria is None or self.selected_names is None:
            await interaction.response.send_message("基準またはプレイヤー選択が完了していません。", ephemeral=True)
            return

        try:
            data = get_data(
                config.CREDENTIALS_FILE,
                config.SPREADSHEET_ID,
                config.WORKSHEET_NAME
            )
        except Exception as e:
            await interaction.response.send_message(f"データ取得に失敗しました: {e}", ephemeral=True)
            return

        teams = divide_teams_by_criteria(data, self.selected_names, criteria=self.criteria, team_count=2)
        text = ""
        for i, df in enumerate(teams, start=1):
            text += f"【チーム{i}】\n"
            for _, row in df.iterrows():
                text += f"・{row['参加者']} (勝率: {row['勝率']}, KDA: {row['KDA']})\n"
            text += "\n"

        await interaction.response.send_message(text)
