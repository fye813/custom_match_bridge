# core.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import pandas as pd

def get_data(credentials_file, spreadsheet_id, worksheet_name):
    """
    Google Sheetsから戦績データを取得して、必要な列を持つ DataFrame を返します。
    空欄の行は除外されます。
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(credentials)
    
    # より安全な方法でスプレッドシートを開く（URLではなくkeyを使う）
    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)

    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])  # 1行目: ヘッダー、2行目以降: データ
    
    # 対象列の空白を除外
    cols = ["参加者", "ゲーム数", "勝率", "キル平均", "デス平均", "アシスト平均", "KDA"]
    mask = df[cols].apply(lambda col: col.astype(str).str.strip() != "").all(axis=1)
    return df.loc[mask, cols]

def divide_teams_by_criteria(data, selected_names, criteria=1, team_count=2):
    """
    プレイヤーリストから指定された人数を、基準値でソートしスネークドラフトで分けます。
    criteria: 1=勝率, 2=KDA
    """
    if criteria == 1:
        sort_column = "勝率"
    elif criteria == 2:
        sort_column = "KDA"
    else:
        raise ValueError("criteria は 1（勝率）または 2（KDA）を指定してください。")

    df_selected = data[data["参加者"].isin(selected_names)].reset_index(drop=True)
    sorted_df = df_selected.sort_values(by=sort_column, ascending=False).reset_index(drop=True)

    teams = [[] for _ in range(team_count)]
    direction = 1
    i = 0
    n = len(sorted_df)

    while i < n:
        if direction == 1:
            for t in range(team_count):
                if i < n:
                    teams[t].append(sorted_df.iloc[i])
                    i += 1
        else:
            for t in reversed(range(team_count)):
                if i < n:
                    teams[t].append(sorted_df.iloc[i])
                    i += 1
        direction *= -1

    return [pd.DataFrame(team) for team in teams]

# --- ローカル実行用テスト ---
if __name__ == "__main__":
    import config
    df = get_data(config.CREDENTIALS_FILE, config.SPREADSHEET_ID, config.WORKSHEET_NAME)

    # サンプル選手
    player_list = df["参加者"].sample(10).tolist() if len(df) >= 10 else df["参加者"].tolist()

    teams = divide_teams_by_criteria(df, player_list, criteria=2)
    for i, team in enumerate(teams, start=1):
        print(f"\n▼ チーム{i}")
        print(team)