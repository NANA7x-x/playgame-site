"""いまのPGロゴを「ピンク＋ラベンダー」に塗り替える。img/original/*.png → img/*.png
水色・ミントなど青緑系の色を、くすんだラベンダーに寄せる。ピンク・紫・白・黒はそのまま。"""
import colorsys, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(HERE, '..', 'img')
PINKH = 312 / 360
def tone(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if s >= .15:
        d = (h - PINKH) % 1
        if .25 < d < .85: h, s = 262 / 360, s * .55
        else: s = s * .85
    return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))
for f in ['en', 'gbot', 'gtop', 'heart', 'kana', 'mark2', 'p']:
    im = Image.open(os.path.join(IMG, 'original', f + '.png')).convert('RGBA'); px = im.load(); memo = {}
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a:
                if (r, g, b) not in memo: memo[(r, g, b)] = tone(r, g, b)
                px[x, y] = memo[(r, g, b)] + (a,)
    im.save(os.path.join(IMG, f + '.png'))
print('ok')
