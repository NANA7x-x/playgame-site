# PLAY GAME 告知動画

全イベント共通の **OP（5秒）** と **ED（5.5秒）** に、イベントごとの **本編（9秒）** をはさんで1本にします。
ロゴは `../img` のPGロゴのパーツを使います。1920×1080・30fps・音なし。

## 作り方
```
python3 make.py op                          # out/op.mp4（共通OP）
python3 make.py ed                          # out/ed.mp4（共通ED）
python3 make.py event events/league01.json  # out/league01.mp4（OP＋本編＋ED）と out/league01_body.mp4
python3 make.py frames body events/league01.json 1.3 5.6   # 確認用の静止画
```
必要なもの：Python 3（Pillow）、ffmpeg、Noto Sans CJK フォント。

## イベントの設定（events/*.json）
| 項目 | 例 | |
|---|---|---|
| id | league01 | 出力ファイル名 |
| prefix / game_title / title | PGP / VALORANT / LEAGUE 01 | タイトルの3段 |
| sub | 8 TEAMS ROUND ROBIN | タイトル下の英字 |
| teams | 8 | 書くと総当たりの図。書かないと `games`（ゲーム名の配列）が輪の上を回る |
| info | [["DATE ","…"],["PRIZE","…"],["ENTRY","…"]] | メッセージ窓の3行 |
| cta / cta_sub / how | ENTRY OPEN / ひとりでも参加OK！ / Discord… | 最後の画面 |
| stage | STAGE 01 | 右上の表示 |
