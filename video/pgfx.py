"""PLAY GAME 告知動画の共通パーツ（色・ドット文字・ロゴ・回るリング・背景）。"""
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = 1920, 1080, 30
BG = (11, 8, 20)
PANEL = (23, 17, 38)
LINE = (58, 45, 87)
INK = (243, 239, 255)
MUTED = (185, 173, 217)
PINK = (255, 63, 208)
CYAN = (47, 216, 255)
MINT = (79, 255, 192)
VIOLET = (122, 92, 255)
SHADOW = (162, 75, 234)
GRAD = [PINK, VIOLET, CYAN, MINT]
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets') if os.path.isdir(os.path.join(HERE, 'assets')) else os.path.join(HERE, '..', 'img')

# ---------- 数値 ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def ease(x): return 1 - (1 - x) ** 3
def ease_in(x): return x ** 3
def ease_io(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def back(x, s=1.7): x -= 1; return x * x * ((s + 1) * x + s) + 1
def rgba(c, a): return (c[0], c[1], c[2], int(255 * clamp(a)))
def mix(c1, c2, k): return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))

def with_alpha(im, a):
    if a >= 1: return im
    im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * clamp(a)))); return im

def scaled(im, s, smooth=False):
    s = max(s, .01)
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS if smooth else Image.NEAREST)

def paste_center(img, lay, cx, cy):
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

# ---------- ドット文字 ----------
MONO = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
def pfont(px): return ImageFont.truetype(MONO, px, index=5)  # Noto Sans Mono CJK JP Bold

def pixel_mask(txt, px):
    f = pfont(px)
    m = Image.new('L', (int(f.getlength(txt)) + 4, px + 8), 0)
    d = ImageDraw.Draw(m); d.fontmode = '1'; d.text((2, 1), txt, font=f, fill=255)
    return m.crop(m.getbbox()) if m.getbbox() else m

_cache = {}
def pixel_text(txt, px, scale, fill=INK, grad=False, outline=False, shadow=True):
    """ドット文字。grad=True でPGロゴと同じ段々グラデーション＋白フチ。"""
    key = (txt, px, scale, fill, grad, outline, shadow)
    if key in _cache: return _cache[key]
    m = pixel_mask(txt, px); pad = 3
    big = Image.new('L', (m.width + pad * 2, m.height + pad * 2), 0); big.paste(m, (pad, pad)); m = big
    out = Image.new('RGBA', m.size, (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', m.size, rgba(SHADOW, 1)); sh.putalpha(ImageChops.offset(m, 1, 1)); out.alpha_composite(sh)
    if outline:
        ol = Image.new('RGBA', m.size, (255, 255, 255, 255)); ol.putalpha(m.filter(ImageFilter.MaxFilter(3))); out.alpha_composite(ol)
    if grad:
        g = Image.new('RGBA', m.size); gd = ImageDraw.Draw(g)
        for y in range(m.height):
            for x in range(0, m.width, 2):
                gd.rectangle([x, y, x + 1, y], fill=GRAD[int(((x * .35 + y) / (m.height * .9)) % 4)])
        g.putalpha(m); out.alpha_composite(g)
    else:
        f = Image.new('RGBA', m.size, rgba(fill, 1)); f.putalpha(m); out.alpha_composite(f)
    out = out.resize((out.width * scale, out.height * scale), Image.NEAREST)
    _cache[key] = out
    return out

# ---------- ロゴ ----------
def load(name, s=1.0):
    im = Image.open(os.path.join(ASSETS, name + '.png')).convert('RGBA')
    return scaled(im, s) if s != 1 else im
LOGO_PARTS = {n: load(n) for n in ['p', 'gtop', 'gbot', 'heart']}
LOGO_FULL = load('mark2')
EN = load('en'); KANA = load('kana')
LOGO_W, LOGO_H = LOGO_FULL.size  # 760 x 583
# 本編で左上に置くときの大きさ・位置（OPの最後とつなげる）
CORNER_S = .34
CORNER_XY = (110, 84)

def logo_assembled(t0, t, fly=((-900, 0), (0, -700), (0, 700)), heart_at=None):
    """t0 から組み上がるロゴ（原寸レイヤー）。"""
    lay = Image.new('RGBA', (LOGO_W, LOGO_H), (0, 0, 0, 0))
    for (name, (dx, dy)), k in zip(zip(['p', 'gtop', 'gbot'], fly), range(3)):
        p = prog(t, t0 + k * .16, t0 + .7 + k * .16)
        if p <= 0: continue
        e = back(p) if p < 1 else 1
        lay.alpha_composite(LOGO_PARTS[name], (int(dx * (1 - e)), int(dy * (1 - e))))
    hp = prog(t, heart_at, heart_at + .3) if heart_at is not None else 1
    if hp > 0:
        hb = LOGO_PARTS['heart'].getbbox(); heart = LOGO_PARTS['heart'].crop(hb)
        hs = back(hp, 3); hh = scaled(heart, hs)
        lay.alpha_composite(hh, (int((hb[0] + hb[2]) / 2 - hh.width / 2), int((hb[1] + hb[3]) / 2 - hh.height / 2)))
    return lay

# ---------- 背景 ----------
def _dot_grid():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in range(0, W, 24):
        for y in range(0, H, 24): d.rectangle([x, y, x + 1, y + 1], fill=rgba(LINE, .9))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([W * .45, -300, W * 1.2, H * .9], fill=rgba(VIOLET, .22)); gd.ellipse([-300, H * .45, W * .5, H + 300], fill=rgba(PINK, .12))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    return im
GRID = _dot_grid()
def _scan():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y in range(0, H, 4): d.line([(0, y), (W, y)], fill=(0, 0, 0, 46))
    # 画面のふちを少し暗く
    v = Image.new('L', (W, H), 0); vd = ImageDraw.Draw(v); vd.ellipse([-W * .15, -H * .2, W * 1.15, H * 1.2], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160)); dark = Image.new('RGBA', (W, H), (0, 0, 0, 150)); dark.putalpha(ImageChops.invert(v).point(lambda x: int(x * .55)))
    im.alpha_composite(dark)
    return im
SCAN = _scan()
MQ = pixel_text('PLAY GAME + プレイゲーム + ', 14, 2, fill=(165, 150, 255), shadow=False)

def background(t):
    img = Image.new('RGBA', (W, H), BG + (255,)); img.alpha_composite(GRID); return img

def marquee(img, t, a):
    if a <= 0: return
    band = 48; d = ImageDraw.Draw(img)
    for y in (0, H - band):
        d.rectangle([0, y, W, y + band], fill=rgba(PANEL, a))
        yy = y + band - 1 if y == 0 else y
        d.line([(0, yy), (W, yy)], fill=rgba(VIOLET, a), width=2)
    off = int(t * 120) % MQ.width
    for y, sgn in ((0, 1), (H - band, -1)):
        x = -off if sgn > 0 else off - MQ.width
        while x < W:
            img.alpha_composite(with_alpha(MQ, a), (x, y + (band - MQ.height) // 2)); x += MQ.width

def corners(img, a):
    if a <= 0: return
    d = ImageDraw.Draw(img); m, L, w = 72, 50, 6
    for x, y, sx, sy in [(m, m + 20, 1, 1), (W - m, m + 20, -1, 1), (m, H - m - 20, 1, -1), (W - m, H - m - 20, -1, -1)]:
        xs = sorted([x, x + sx * L]); ys = sorted([y, y + sy * w]); d.rectangle([xs[0], ys[0], xs[1], ys[1]], fill=rgba(MUTED, a))
        xs = sorted([x, x + sx * w]); ys = sorted([y, y + sy * L]); d.rectangle([xs[0], ys[0], xs[1], ys[1]], fill=rgba(MUTED, a))

def finish(img, t):
    img.alpha_composite(SCAN)
    return img

def crt_on(img, p):
    """ブラウン管が点く（p:0→1）。"""
    if p >= 1: return img
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    if p < .45:
        w = int(W * ease(p / .45)); d = ImageDraw.Draw(out)
        d.rectangle([(W - w) // 2, H // 2 - 2, (W + w) // 2, H // 2 + 2], fill=(255, 255, 255, 255))
        return out
    h = max(4, int(H * ease((p - .45) / .55)))
    out.alpha_composite(img.crop((0, (H - h) // 2, W, (H + h) // 2)), (0, (H - h) // 2))
    return out

def crt_off(img, p):
    """ブラウン管が消える（p:0→1）。"""
    if p <= 0: return img
    out = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(out)
    if p < .5:
        h = max(4, int(H * (1 - ease_in(p / .5))))
        band = img.crop((0, (H - h) // 2, W, (H + h) // 2))
        if p > .35: band = Image.blend(band, Image.new('RGBA', band.size, (255, 255, 255, 255)), (p - .35) / .15)
        out.alpha_composite(band, (0, (H - h) // 2)); return out
    if p < .8:
        w = max(6, int(W * (1 - ease_in((p - .5) / .3))))
        d.rectangle([(W - w) // 2, H // 2 - 2, (W + w) // 2, H // 2 + 2], fill=(255, 255, 255, 255)); return out
    r = int(10 * (1 - (p - .8) / .2))
    if r > 0: d.ellipse([W // 2 - r, H // 2 - r, W // 2 + r, H // 2 + r], fill=(255, 255, 255, 255))
    return out

# ---------- くるくる回るリング ----------
SS = 2  # なめらかに描くための拡大率

def _sparkle(d, x, y, r, col, a):
    """ドットの十字きらきら。"""
    c = rgba(col, a); s = max(2, int(r))
    d.rectangle([x - s * 3, y - s // 2, x + s * 3, y + s // 2], fill=c)
    d.rectangle([x - s // 2, y - s * 3, x + s // 2, y + s * 3], fill=c)
    d.rectangle([x - s, y - s, x + s, y + s], fill=rgba((255, 255, 255), a))

SPRITES = [
    ('heart', [".XX.XX.", "XoXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]),
    ('star', ["...X...", "...X...", "XXXXXXX", ".XXXXX.", "..XXX..", ".XX.XX.", "X.....X"]),
    ('pad', [".XXXXXXXX.", "XX.XXXXoXX", "X...XXoXoX", "XX.XXXXoXX", "XXXX..XXXX", ".XX....XX."]),
    ('coin', ["..XXX..", ".XoXXX.", "XoXXXXX", "XoXXXXX", "XXXXXXX", ".XXXXX.", "..XXX.."]),
    ('play', ["X.....", "XXX...", "XXXXX.", "XXXXXX", "XXXXX.", "XXX...", "X....."]),
    ('heart2', [".XX.XX.", "XoXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]),
    ('bolt', ["...XXX", "..XXX.", ".XXXX.", "XXXXXX", "..XXX.", ".XXX..", ".XX...", "XX...."]),
    ('coin2', ["..XXX..", ".XoXXX.", "XoXXXXX", "XoXXXXX", "XXXXXXX", ".XXXXX.", "..XXX.."]),
]

def rings(t, R=360, grow=1.0, alpha=1.0, spin=1.0, heart=True, mono=False, items=True):
    """中心に置く回るリング一式（RGBA, 正方形）。spin で回転の速さ、grow で大きさ（0→1）。mono=True で色を抑えた紫だけの版。"""
    if mono: PINK_, VIOLET_, CYAN_, MINT_ = (150, 120, 255), (98, 78, 190), (120, 110, 210), (140, 125, 230)
    else: PINK_, VIOLET_, CYAN_, MINT_ = PINK, VIOLET, CYAN, MINT
    GRAD_ = [PINK_, VIOLET_, CYAN_, MINT_]
    size = int(R * 2.6); S = size * SS
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    c = S / 2
    g = ease(clamp(grow))
    if g <= 0 or alpha <= 0: return Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rot = t * 40 * spin
    def circ(r, col, a, w=1):
        rr = r * g * SS; d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=rgba(col, a * alpha), width=w * SS)
    def arc(r, a0, a1, col, a, w):
        rr = r * g * SS; d.arc([c - rr, c - rr, c + rr, c + rr], a0, a1, fill=rgba(col, a * alpha), width=w * SS)
    # いちばん外：細い円＋目盛り（ゆっくり）
    circ(R * 1.18, LINE, 1, 2)
    for k in range(96):
        ang = math.radians(rot * .25 + k * 3.75); r1 = R * 1.18 * g * SS; r2 = r1 - (16 if k % 8 == 0 else 7) * SS
        d.line([(c + r1 * math.cos(ang), c + r1 * math.sin(ang)), (c + r2 * math.cos(ang), c + r2 * math.sin(ang))],
               fill=rgba(VIOLET_ if k % 8 else PINK_, (.9 if k % 8 == 0 else .5) * alpha), width=2 * SS if k % 8 == 0 else SS)
    # 点線の円（逆回り）
    for k in range(48):
        a0 = -rot * .6 + k * 7.5
        arc(R * 1.04, a0, a0 + 3.2, CYAN_, .8, 3)
    # 太い弧（速い）
    for s0, ln, col, w in [(0, 80, PINK_, 10), (120, 35, MINT_, 10), (200, 95, VIOLET_, 6), (318, 22, CYAN_, 10)]:
        arc(R * .9, rot * 1.6 + s0, rot * 1.6 + s0 + ln, col, .95, w)
    # 細い弧（逆回り）
    for s0, ln, col in [(30, 140, CYAN_), (210, 60, PINK_)]:
        arc(R * .78, -rot * 1.1 + s0, -rot * 1.1 + s0 + ln, col, .7, 2)
    circ(R * .66, VIOLET_, .45, 1)
    # ドットの円（ピクセルの四角が並んで回る）
    for k in range(36):
        ang = math.radians(rot * .8 + k * 10); rr = R * .72 * g * SS
        x, y = c + rr * math.cos(ang), c + rr * math.sin(ang); s = 5 * SS
        d.rectangle([x - s, y - s, x + s, y + s], fill=rgba(GRAD_[k % 4], .85 * alpha))
    # ゲームのアイテム（ハート・星・コイン・コントローラー・▶）がリングの上をぐるぐる回る
    if items:
        n = len(SPRITES)
        for k, (name, grid) in enumerate(SPRITES):
            ang = math.radians(rot * .45 + k * 360 / n)
            rr = R * 1.02 * g * SS
            bob = math.sin(t * 3 + k) * 6 * SS
            x, y = c + rr * math.cos(ang), c + rr * math.sin(ang) + bob
            ps = 7 * SS; hh, ww = len(grid), len(grid[0])
            x0, y0 = x - ww * ps / 2, y - hh * ps / 2
            col = (GRAD_[k % 4])
            for gy, row in enumerate(grid):
                for gx, ch in enumerate(row):
                    if ch == '.': continue
                    cc = INK if ch == 'o' else col
                    d.rectangle([x0 + gx * ps, y0 + gy * ps, x0 + (gx + 1) * ps - 1, y0 + (gy + 1) * ps - 1], fill=rgba(cc, .95 * alpha))
    out = lay.resize((size, size), Image.LANCZOS)
    # 光のにじみ
    glow = out.filter(ImageFilter.GaussianBlur(10))
    res = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    res.alpha_composite(glow); res.alpha_composite(glow); res.alpha_composite(out)
    return res

def center_glow(img, cx, cy, r, a, col=VIOLET):
    if a <= 0: return
    g = Image.new('RGBA', (int(r * 4), int(r * 4)), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse([r, r, r * 3, r * 3], fill=rgba(col, .55 * a))
    paste_center(img, g.filter(ImageFilter.GaussianBlur(r * .5)), cx, cy)

def shockwave(img, cx, cy, p, col=(255, 255, 255)):
    if p <= 0 or p >= 1: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = 80 + 900 * ease(p)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgba(col, (1 - p) * .9), width=int(14 * (1 - p)) + 2)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))

def stars(img, t, a, seed=3, n=40):
    """背景で瞬くドットの星。"""
    if a <= 0: return
    rnd = random.Random(seed); d = ImageDraw.Draw(img)
    for k in range(n):
        x, y = rnd.randrange(80, W - 80), rnd.randrange(80, H - 80); ph = rnd.random() * 6.28; sp = 1.5 + rnd.random() * 2
        b = (math.sin(t * sp + ph) + 1) / 2
        if b < .4: continue
        col = GRAD[k % 4]; s = 3 if b < .8 else 4
        d.rectangle([x - s, y - 1, x + s, y + 1], fill=rgba(col, a * b)); d.rectangle([x - 1, y - s, x + 1, y + s], fill=rgba(col, a * b))


# ---------- 読みやすい文字（なめらかな太ゴシック） ----------
BLACK = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
_ff = {}
def jfont(px, weight='black'):
    k = (px, weight)
    if k not in _ff: _ff[k] = ImageFont.truetype(BLACK if weight == 'black' else BOLD, px, index=0)
    return _ff[k]

_jc = {}
def jp_text(txt, px, fill=INK, weight='black', shadow=0, shadow_col=SHADOW, stroke=0):
    """なめらかな文字。shadow でずらした影（PGっぽい段差）、stroke で暗いフチ。"""
    key = (txt, px, fill, weight, shadow, shadow_col, stroke)
    if key in _jc: return _jc[key]
    f = jfont(px, weight)
    l, tp, r, b = f.getbbox(txt, stroke_width=stroke)
    pad = stroke + 4
    im = Image.new('RGBA', (r - l + pad * 2 + shadow, b - tp + pad * 2 + shadow), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = (pad - l, pad - tp)
    if shadow: d.text((o[0] + shadow, o[1] + shadow), txt, font=f, fill=rgba(shadow_col, 1), stroke_width=stroke, stroke_fill=rgba(shadow_col, 1))
    d.text(o, txt, font=f, fill=rgba(fill, 1), stroke_width=stroke, stroke_fill=rgba(BG, 1))
    _jc[key] = im
    return im

_cc = {}
def jp_char(ch, px, fill=INK, weight='black', shadow=0, shadow_col=SHADOW):
    """1文字を同じ高さの箱に描く（ー・、などの位置がずれない）。"""
    key = (ch, px, fill, weight, shadow, shadow_col)
    if key in _cc: return _cc[key]
    f = jfont(px, weight); asc, desc = f.getmetrics(); pad = 4
    im = Image.new('RGBA', (int(f.getlength(ch)) + pad * 2 + shadow, asc + desc + pad * 2 + shadow), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if shadow: d.text((pad + shadow, pad + shadow), ch, font=f, fill=rgba(shadow_col, 1))
    d.text((pad, pad), ch, font=f, fill=rgba(fill, 1))
    _cc[key] = im
    return im
