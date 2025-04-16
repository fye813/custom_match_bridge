# Custom Match Bridge

Custom Match Bridge は、Google スプレッドシートからゲームプレイヤーの戦績データを取得し、Discord 上のセレクトボックスによるインタラクティブな UI を通じて、指定されたプレイヤーと基準（勝率または KDA）に基づいてチーム分けを実行する Discord Bot です。

## 特徴

- **Google スプレッドシート連携**  
  サービスアカウントと Google Sheets API を用いて、スプレッドシートからプレイヤーデータを取得します。  
  `core.py` 内の `get_data` 関数により、対象カラムが空でない行のみを抽出して DataFrame を生成します。

- **チーム分けアルゴリズム**  
  ユーザーが選択したプレイヤーに対して、勝率または KDA を基準にソートした上で、スネークドラフト方式でバランスの取れたチーム分けを行います。  
  この処理は `divide_teams_by_criteria` 関数で実装されています。

- **Discord UI コンポーネント**  
  最新の discord.py UI コンポーネントを利用し、
  - セレクトボックスでチーム分けの基準（勝率 or KDA）を選択
  - セレクトボックスで参加するプレイヤーを選択  
    を実現。  
    「チーム分けを実行」ボタンで、選択内容に基づいたチーム分け結果をチャットに送信します。

## ファイル構成

- **config.py**  
  Discord Bot のトークン、Google Sheets の認証情報ファイル（credentials.json）、スプレッドシート ID、ワークシート名などの設定値を管理します。

- **core.py**

  - `get_data(credentials_file, spreadsheet_id, worksheet_name)`  
    Google Sheets からデータを取得し、対象カラム（例: "参加者", "ゲーム数", "勝率", "キル平均", "デス平均", "アシスト平均", "KDA"）が空でない行のみ抽出した DataFrame を返します。
  - `divide_teams_by_criteria(data, selected_names, criteria, team_count)`  
    DataFrame のデータから、ユーザーが選択したプレイヤーをもとに、指定した基準（1: 勝率、2: KDA）でソートし、スネークドラフト方式でチーム分けを実施します。

- **bot.py**  
  Discord Bot の本体となるファイルです。  
  UI コンポーネント（セレクトボックスやボタン）を用いて、ユーザーが基準や参加プレイヤーを選択し、チーム分け結果をチャットに表示する仕組みを実装しています。
