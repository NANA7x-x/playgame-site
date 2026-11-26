# PG ロゴ（2026-11 リニューアル）

角ばった線の P・G を、ピンクの光が走る斜めの切れ込みが切り裂く形。色は白とピンク（#FF3FD0）だけ。

| ファイル | 用途 |
|---|---|
| pg-logo.svg / .png | マーク＋PLAY GAME（透明） |
| pg-mark.svg / .png | マークだけ（透明） |
| pg-icon.png / pg-icon-512.png | Discord などのアイコン（黒地の正方形） |

作り直すとき：`python3 logo.py`（線の位置や太さは logo.py の先頭で変えられる）。concepts.py / concepts.png は検討したラフ3案。

## いまのロゴの「ピンク＋ラベンダー」版（採用）

結局、ロゴの形は今までのドット絵のまま、色だけを同系色に抑えた。
- `recolor.py`：img/original/*.png（元の4色）→ img/*.png（ピンク＋ラベンダー）に塗り替える
- `anim.py`：色がピンク↔ラベンダーで流れるGIF（pg-logo-anim.gif＝透明、pg-icon-anim.gif＝Discordアイコン用512px）
- HP のロゴの色の流れ（.rbw / glow）も同じ色の範囲にした
