# core.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import pandas as pd

def get_data(credentials_file, spreadsheet_id, worksheet_name):
    """
    Google Sheetsからプレイヤー名を取得する関数です。
    ヘッダーを除いた1列目の内容をプレイヤー名として返します。
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(credentials)
    sheet = client.open_by_url(f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid=0").worksheet(worksheet_name)

    data = sheet.get_all_values()
    # 1行目をヘッダーとして DataFrame を作成（data[0]がヘッダー、data[1:]がデータ）
    df = pd.DataFrame(data[1:], columns=data[0])
    
    # 例として、特定のカラム（ここでは "対象列" とします）の内容が空欄になっている行を除外する
    # ※対象のカラム名に合わせて "対象列" の部分を変更してください。
    cols = ["参加者", "ゲーム数", "勝率", "キル平均", "デス平均", "アシスト平均", "KDA"]
    mask = df[cols].apply(lambda col: col.str.strip() != "").all(axis=1)
    return df.loc[mask, cols]

def divide_teams_by_criteria(data, selected_names, criteria=1, team_count=2):
    """
    DataFrame 'data' に含まれる15人ほどの戦績データから、
    ユーザーが選択したプレイヤー（selected_names）を抽出し、
    criteria に応じてソートした上で、スネークドラフト方式でチーム分けを行う関数です。
    
    引数:
      data: 戦績データを含む DataFrame（例: カラムに "名前", "勝率", "KDA" がある）
      selected_names: ユーザーが選択したプレイヤー名のリスト
      criteria: 1 を指定すると「勝率」でソート、2 を指定すると「KDA」でソートする
      team_count: 分割するチーム数（デフォルトは2）
    
    戻り値:
      チームごとの DataFrame のリスト
    """
    # ソート基準の列を決定
    if criteria == 1:
        sort_column = "勝率"
    elif criteria == 2:
        sort_column = "KDA"
    else:
        raise ValueError("criteria は 1（勝率）または 2（KDA）のいずれかで指定してください。")
    
    # 選択されたプレイヤーのみ抽出して DataFrame をリセット
    df_selected = data[data["参加者"].isin(selected_names)].reset_index(drop=True)
    # 指定した列で降順にソート
    sorted_df = df_selected.sort_values(by=sort_column, ascending=False).reset_index(drop=True)
    
    # スネークドラフト方式によるチーム分け
    teams = [[] for _ in range(team_count)]
    direction = 1  # 1: 正順, -1: 逆順
    i = 0
    n = len(sorted_df)
    
    while i < n:
        if direction == 1:
            for t in range(team_count):
                if i < n:
                    teams[t].append(sorted_df.iloc[i])
                    i += 1
        else:
            for t in range(team_count - 1, -1, -1):
                if i < n:
                    teams[t].append(sorted_df.iloc[i])
                    i += 1
        direction *= -1  # 方向転換
    
    # 各チームのリストを DataFrame に変換して返す
    team_dfs = [pd.DataFrame(team) for team in teams]
    return team_dfs

# 動作確認用（ローカルでの実行時にテストできます）
if __name__ == "__main__":
    import config
    data = get_data(config.CREDENTIALS_FILE, config.SPREADSHEET_ID, config.WORKSHEET_NAME)

    player_list = ['もち', 'たちゃ', 'シャンタ', 'かわぬ', 'ほのに', 'へりこ', 'UMA', 'ふかひれ', 'あき', 'まつだ']
    teams = divide_teams_by_criteria(data, player_list, criteria=2)
    for i, team in enumerate(teams, start=1):
        print(f"チーム{i}: {team}")
