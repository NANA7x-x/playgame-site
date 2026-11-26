"""PG ロゴ（案A：角ばった線＋ななめの切れ込み）を書き出す。python3 logo.py
  pg-mark.svg/png   … PG のマークだけ（透明）
  pg-logo.svg/png   … マーク＋PLAY GAME（透明）
  pg-icon.svg/png   … Discord などのアイコン用（黒地の正方形）
"""
import subprocess
INK, PINK, BG = '#F6F6F8', '#FF3FD0', '#0A0A0D'
W = 58  # 線の太さ
P = 'M180 600 V200 H320 L370 250 V350 L320 400 H180'
G = 'M690 250 L640 200 H540 L490 250 V550 L540 600 H640 L690 550 V420 H590'
CUT = 'M110 572 L770 308'          # 文字を切る斜めの線
LINE = 'M96 578 L784 302'           # 切れ込みの中を走るピンクの線
HEART = ''.join(f'<rect x="{x*9}" y="{y*9}" width="9.4" height="9.4"/>' for y, row in enumerate([".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]) for x, c in enumerate(row) if c == 'X')

def s(d, col, w, cap='square'):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="miter" stroke-linecap="{cap}"/>'

def mark(ink=INK):
    return (f'<defs><mask id="cut" maskUnits="userSpaceOnUse" x="0" y="0" width="900" height="800">'
            f'<rect x="0" y="0" width="900" height="800" fill="#fff"/>{s(CUT, "#000", 30, "butt")}</mask></defs>'
            f'<g mask="url(#cut)">{s(P, ink, W)}{s(G, ink, W)}</g>'
            f'{s(LINE, PINK, 8, "butt")}'
            f'<g fill="{PINK}" transform="translate(724 572)">{HEART}</g>')

def svg(vb, body, bg=None):
    x, y, w, h = vb
    r = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}">{r}{body}</svg>'

SUB = f'<text x="435" y="712" text-anchor="middle" font-family="Montserrat" font-weight="700" font-size="40" letter-spacing="26" fill="{INK}" fill-opacity=".75">PLAY GAME</text>'
out = {
    'pg-mark': (svg((90, 160, 700, 470), mark()), 1400),
    'pg-logo': (svg((90, 160, 700, 590), mark() + SUB), 1400),
    'pg-icon': (svg((40, 0, 800, 800), f'<g transform="translate(440 400) scale(.86) translate(-440 -400)">{mark()}</g>', BG), 1024),
}
for name, (body, px) in out.items():
    open(f'{name}.svg', 'w').write(body)
    subprocess.run(['rsvg-convert', '-w', str(px), f'{name}.svg', '-o', f'{name}.png'], check=True)
subprocess.run(['convert', 'pg-icon.png', '-resize', '512x512', 'pg-icon-512.png'], check=True)
