"""PG 新ロゴのラフ案（サイバー寄り）。python3 concepts.py → concept_*.svg / *.png"""
import subprocess
BG, INK, PINK = '#0A0A0D', '#F6F6F8', '#FF3FD0'
P = 'M180 600 V200 H320 L370 250 V350 L320 400 H180'
G = 'M690 250 L640 200 H540 L490 250 V550 L540 600 H640 L690 550 V420 H590'
HEART = ''.join(f'<rect x="{x*9}" y="{y*9}" width="9" height="9"/>' for y, row in enumerate([".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]) for x, c in enumerate(row) if c == 'X')
SUB = f'<text x="400" y="712" text-anchor="middle" font-family="Montserrat" font-weight="700" font-size="34" letter-spacing="22" fill="{INK}" fill-opacity=".7">PLAY GAME</text>'

def svg(body, w=800, h=800):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="{BG}"/>{body}</svg>'

def stroke(d, col, w, extra=''):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="miter" stroke-linecap="square" {extra}/>'

# A：太い角ばった線のモノグラム＋ピンクの二重線
A = svg(stroke(P, INK, 58) + stroke(G, INK, 58)
        + stroke('M120 560 L760 300', BG, 16) + stroke('M120 584 L760 324', PINK, 6)
        + f'<g fill="{PINK}" transform="translate(700 600)">{HEART}</g>' + SUB)

# B：中が抜けた線の文字＋回路の線とノード
traces = [('M190 600 V660 H110', (110, 660)), ('M690 420 H740 V140', (740, 140)), ('M320 200 V130 H560', (560, 130))]
B = svg(''.join(stroke(d, '#55555F', 4) + f'<rect x="{x-9}" y="{y-9}" width="18" height="18" fill="{PINK}"/>' for d, (x, y) in traces)
        + stroke(P, INK, 58) + stroke(G, INK, 58) + stroke(P, BG, 34) + stroke(G, BG, 34)
        + f'<rect x="581" y="411" width="18" height="18" fill="{PINK}"/>'
        + f'<g fill="{PINK}" transform="translate(640 650) scale(.8)">{HEART}</g>' + SUB.replace('y="712"', 'y="740"'))

# C：横にずれるグリッチのブロック文字＋かっこ
letters = stroke(P, INK, 64) + stroke(G, INK, 64)
bands = [(140, 300, 0), (300, 345, 26), (345, 455, 0), (455, 490, -16), (490, 660, 0)]
defs = ''.join(f'<clipPath id="c{k}"><rect x="0" y="{a}" width="800" height="{b-a}"/></clipPath>' for k, (a, b, _) in enumerate(bands))
body = f'<defs>{defs}</defs>'
for k, (a, b, dx) in enumerate(bands):
    if dx: body += f'<g clip-path="url(#c{k})" transform="translate({dx-14} 0)" opacity=".9">{stroke(P, PINK, 64)}{stroke(G, PINK, 64)}</g>'
    body += f'<g clip-path="url(#c{k})" transform="translate({dx} 0)">{letters}</g>'
br = stroke('M130 160 H100 V640 H130', INK, 6) + stroke('M720 160 H750 V640 H720', INK, 6)
C = svg(body + br + SUB.replace('y="712"', 'y="730"'))

for name, s in [('a', A), ('b', B), ('c', C)]:
    open(f'concept_{name}.svg', 'w').write(s)
    subprocess.run(['rsvg-convert', '-w', '800', f'concept_{name}.svg', '-o', f'concept_{name}.png'], check=True)
