"""PLAY GAME 告知動画をつくる。
  python3 make.py op                      → out/op.mp4（全イベント共通のオープニング）
  python3 make.py ed                      → out/ed.mp4（全イベント共通のエンディング）
  python3 make.py event events/league01.json → out/<id>_body.mp4 と out/<id>.mp4（OP＋本編＋ED）
  python3 make.py frames op 1.5 3.0       → 確認用の静止画
"""
import sys, os, json, math, random, subprocess
from PIL import Image, ImageDraw, ImageChops
from pgfx import *

OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)

# ======================= OP（約5秒） =======================
OP_DUR = 5.0
LOGO_CY = 385
def op_frame(t):
    img = background(t)
    stars(img, t, prog(t, .6, 1.2))
    cx, cy = W // 2, LOGO_CY
    # 最後に左上へ（本編の最初のフレームとつながる）
    mv = ease_io(prog(t, 3.9, 4.6))
    # リング：広がって回り、最後は速く回りながら外へ消える
    grow = prog(t, .35, 1.4); spin = 1 + 5 * ease_in(prog(t, 3.4, 4.4))
    ra = 1 - prog(t, 3.9, 4.5)
    if ra > 0:
        center_glow(img, cx, cy, 300, prog(t, .4, 1.4) * ra)
        rg = rings(t + 3 * ease_in(prog(t, 3.4, 4.4)), R=300, grow=grow * (1 + .6 * ease_in(prog(t, 3.9, 4.5))), alpha=ra, spin=spin)
        paste_center(img, rg, cx, cy)
    # ロゴ
    lay = logo_assembled(1.0, t, heart_at=1.85)
    s0 = .68; s = s0 + (CORNER_S - s0) * mv
    lx0, ly0 = cx - LOGO_W * s0 / 2, cy - LOGO_H * s0 / 2
    lx, ly = lx0 + (CORNER_XY[0] - lx0) * mv, ly0 + (CORNER_XY[1] - ly0) * mv
    img.alpha_composite(scaled(lay, s), (int(lx), int(ly)))
    # 揃った瞬間：フラッシュと衝撃波
    if 1.85 < t < 2.1: img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(150 * (1 - prog(t, 1.85, 2.1))))))
    shockwave(img, cx, cy, prog(t, 1.85, 2.7), INK); shockwave(img, cx, cy, prog(t, 1.95, 2.9), ACCENT)
    # PLAY GAME / プレイゲーム / PRESENTS
    a = prog(t, 2.2, 2.6) * (1 - prog(t, 3.7, 4.0))
    if a > 0:
        en = scaled(EN, .72); kana = scaled(KANA, .54)
        y = cy + LOGO_H * s0 / 2 + 70
        paste_center(img, with_alpha(en, a), cx, y + en.height / 2)
        paste_center(img, with_alpha(kana, a), cx, y + en.height + 12 + kana.height / 2)
        pr = pixel_text('PRESENTS', 12, 3, fill=MUTED, shadow=False)
        if t > 2.8 and int((t - 2.8) * 4) % 2 == 0 or t > 3.3:
            paste_center(img, with_alpha(pr, a), cx, y + en.height + kana.height + 56)
    marquee(img, t, prog(t, .7, 1.1)); corners(img, prog(t, .7, 1.1))
    img = finish(img, t)
    return crt_on(img, prog(t, 0, .55))

# ======================= ED（約5秒） =======================
ED_DUR = 5.5
def ed_frame(t):
    img = background(t + 100)
    stars(img, t, 1, seed=9)
    cx, cy = W // 2, 350
    center_glow(img, cx, cy, 260, prog(t, 0, .8))
    paste_center(img, rings(t, R=255, grow=prog(t, 0, 1.0), spin=1.2), cx, cy)
    # ロゴがぽんっと出る
    p = prog(t, .3, .8)
    if p > 0:
        lay = scaled(LOGO_FULL, .52 * back(p))
        paste_center(img, lay, cx, cy)
    if .55 < t < .75: img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(90 * (1 - prog(t, .55, .75))))))
    shockwave(img, cx, cy, prog(t, .55, 1.3), INK)
    # メッセージ
    a = prog(t, 1.0, 1.4)
    if a > 0:
        msg = pixel_text('SEE YOU IN PLAY GAME!', 16, 5, fill=INK, shadow=False)
        paste_center(img, with_alpha(msg, a), cx, 740)
    lines = [('HP', 'nana7x-x.github.io/playgame-site', ACCENT), ('DISCORD', '「イベント情報」チャンネルをチェック', ACCENT), ('X', '@7x_x7x_x7', ACCENT)]
    for k, (tag, body, col) in enumerate(lines):
        q = prog(t, 1.6 + k * .25, 2.0 + k * .25)
        if q <= 0: continue
        tg = jp_text(tag, 34, fill=col, weight='black'); bd = jp_text(body, 38, weight='bold')
        total = 180 + bd.width; x = cx - total / 2; y = 800 + k * 58
        img.alpha_composite(with_alpha(tg, q), (int(x + 160 - tg.width), y + 3)); img.alpha_composite(with_alpha(bd, q), (int(x + 185), y))
    if t > 2.6 and int((t - 2.6) * 2.5) % 2 == 0 and t < 4.6:
        ps = pixel_text('PRESS START', 16, 4, fill=INK)
        paste_center(img, ps, cx, 655)
    marquee(img, t + 7, 1); corners(img, 1)
    img = finish(img, t)
    s = prog(t, 0, .35)
    if s < 1: img = Image.blend(Image.new('RGBA', (W, H), BG + (255,)), img, s)
    return crt_off(img, prog(t, 4.6, 5.5))

# ======================= 本編（イベントごと） =======================
# タイトル → 情報を1ページに1つずつ大きく → 締め。
# ページの切り替えは斜めの帯がサッと横切るワイプ。文字は1文字ずつ下からせり上がる。
# 右側のリング（ゲームのアイテムが回る）はずっとループで動き続ける。
SOFT = (120, 120, 132)
ACC = ACCENT
T_TITLE, T_PAGE, T_FIN = 4.2, 4.6, 4.6     # タイトル・1ページ・締めの長さ（秒）
WIPE = .8                                  # 切り替えの帯が横切る時間

def body_dur(ev): return T_TITLE + T_PAGE * len(ev['pages']) + T_FIN
def bounds(ev): return [T_TITLE + T_PAGE * k for k in range(len(ev['pages']) + 1)]

def page_index(t, ev):
    """いまのページ番号（0=タイトル, 1..n=情報, n+1=締め）と、そのページが始まってからの時間。"""
    st = 0; idx = 0
    for k, b in enumerate(bounds(ev)):
        if t >= b: idx, st = k + 1, b
    return idx, t - st

def kinetic(lay, txt, px, x, y, t, t0=0, gap=.045, weight='black', fill=INK, shadow=8):
    """1文字ずつ下からせり上がる文字。幅を返す。"""
    f = jfont(px, weight); cx = x
    base = jp_char('国', px, weight=weight, shadow=shadow).height
    for k, ch in enumerate(txt):
        w = f.getlength(ch)
        if ch != ' ':
            q = prog(t, t0 + k * gap, t0 + k * gap + .45)
            if q > 0:
                im = jp_char(ch, px, fill=fill, weight=weight, shadow=shadow)
                dy = int((1 - back(q, 1.2)) * base * .9)
                vis = im.height - max(0, dy)
                if vis > 0: lay.alpha_composite(im.crop((0, 0, im.width, vis)), (int(cx) - 4, y + max(0, dy)))
        cx += w
    return cx - x

def fit_px(txt, px, maxw, weight='black'):
    while px > 40 and jfont(px, weight).getlength(txt) > maxw: px -= 4
    return px

def wipe(img, p):
    """斜めの帯が左から右へ横切る（p:0→1、0.5で画面がいちばん隠れる）。"""
    if p <= 0 or p >= 1: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); sk = 360
    for k, (col, dl) in enumerate([(ACC, 0), (INK, .05), (PANEL, .12)]):
        pp = clamp((p - dl) / (1 - .12))
        lead = -sk + (W + sk * 2) * ease_io(clamp(pp * 2))
        trail = -sk + (W + sk * 2) * ease_io(clamp(pp * 2 - 1))
        if lead <= trail: continue
        d.polygon([(trail, 0), (lead, 0), (lead - sk, H), (trail - sk, H)], fill=rgba(col, 1))
    img.alpha_composite(lay)

def roundrobin(lay, n, cx, cy, R, p, lt):
    d = ImageDraw.Draw(lay)
    pts = [(cx + R * math.cos(math.radians(-90 + 360 / n * k)), cy + R * math.sin(math.radians(-90 + 360 / n * k))) for k in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    m = int(len(pairs) * lt)
    for i, j in pairs[:m]: d.line([pts[i], pts[j]], fill=rgba(SOFT, .6), width=2)
    if 0 < m < len(pairs):
        i, j = pairs[m - 1]; d.line([pts[i], pts[j]], fill=rgba(ACC, 1), width=5)
    for k, (x, y) in enumerate(pts):
        q = clamp(p * 3 - k * .2)
        if q <= 0: continue
        s = max(8, 40 * back(q))
        d.rectangle([x - s, y - s, x + s, y + s], fill=rgba(PANEL, 1), outline=rgba(SOFT, 1), width=3)
        if q >= 1: paste_center(lay, jp_text(f'T{k + 1}', 34, weight='black'), x, y)
    if m:
        done = m == len(pairs); r = 90
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(BG, .95), outline=rgba(ACC if done else SOFT, 1), width=4)
        paste_center(lay, jp_text(f'{m}', 84, fill=ACC if done else INK), cx, cy - 14)
        paste_center(lay, jp_text('全試合' if done else '試合', 30, fill=MUTED, weight='bold'), cx, cy + 50)

def side_shade(img, a):
    """文字が読みやすいように左側を暗く。"""
    if a <= 0: return
    if not hasattr(side_shade, 'm'):
        m = Image.new('L', (W, 1)); 
        for x in range(W): m.putpixel((x, 0), int(205 * clamp(1 - (x - 900) / 700)))
        side_shade.m = m.resize((W, H))
    sh = Image.new('RGBA', (W, H), BG + (255,)); sh.putalpha(side_shade.m.point(lambda v: int(v * a)))
    img.alpha_composite(sh)

def title_page(lay, t, ev):
    x0 = 150
    a = prog(t, .2, .5)
    if a > 0: lay.alpha_composite(with_alpha(pixel_text(ev['prefix'], 16, 5, fill=MUTED, shadow=False), a), (x0 + 6, 290 - int(20 * (1 - ease(a)))))
    val = pixel_text(ev['game_title'], 16, 8, fill=INK, shadow=False)
    p = prog(t, .35, .8)
    if p > 0: lay.alpha_composite(val.crop((0, 0, max(1, int(val.width * int(p * 8) / 8)), val.height)), (x0, 350))
    tl = pixel_text(ev['title'], 20, ev.get('title_scale', 13), fill=INK, shadow=False)
    p = prog(t, .7, 1.4)
    if p > 0:
        jit = 1 - prog(t, .7, 1.3); rnd = random.Random(int(t * FPS))
        if jit > 0:
            for col, dx in ((ACC, 14), (MUTED, -14)):
                gh = Image.new('RGBA', tl.size, rgba(col, 1)); gh.putalpha(ImageChops.multiply(tl.getchannel('A'), Image.new('L', tl.size, int(110 * jit))))
                lay.alpha_composite(gh, (x0 + int(dx * jit) + rnd.randint(-4, 4), 500 + rnd.randint(-3, 3)))
        lay.alpha_composite(tl.crop((0, 0, max(1, int(tl.width * int(p * 9) / 9)), tl.height)), (x0, 500))
    a = prog(t, 1.4, 1.9)
    if a > 0:
        d = ImageDraw.Draw(lay); d.rectangle([x0 + 6, 790, x0 + 6 + 900 * ease(a), 796], fill=rgba(ACC, 1))
        sub = jp_text(ev.get('sub_jp', ev['sub']), 54, weight='bold', shadow=4)
        lay.alpha_composite(with_alpha(sub, a), (x0 + 4 + int(40 * (1 - ease(a))), 822))

def info_page(lay, t, pg, k, n):
    X = 150; d = ImageDraw.Draw(lay)
    graphic = pg.get('graphic') == 'roundrobin'
    maxw = 980 if graphic else 1620
    # 見出し（色の帯がのびて文字が出る）
    tag = jp_text(pg['tag'], 40, fill=BG, weight='black')
    q = ease(prog(t, .05, .4)); tw = tag.width + 40
    if q > 0:
        d.rectangle([X, 350, X + tw * q, 350 + tag.height + 16], fill=rgba(ACC, 1))
        if q > .7: lay.alpha_composite(with_alpha(tag, prog(t, .3, .45)), (X + 20, 358))
        no = jp_text(f'{k:02d} / {n:02d}', 34, fill=MUTED, weight='bold')
        lay.alpha_composite(with_alpha(no, prog(t, .35, .6)), (X + tw + 28, 350 + (tag.height + 16 - no.height) // 2))
    # 本文（1文字ずつ）
    px = fit_px(pg['big'], 170 if not graphic else 130, maxw)
    kinetic(lay, pg['big'], px, X - 6, 450, t, t0=.35)
    bh = jp_char('国', px, shadow=8).height
    # 補足
    if pg.get('small'):
        a = prog(t, 1.0, 1.4)
        if a > 0:
            spx = fit_px(pg['small'], 58, maxw, 'bold')
            sm = jp_text(pg['small'], spx, weight='bold', shadow=4)
            yy = 450 + bh + 20
            d.rectangle([X, yy - 6, X + 8, yy + sm.height - 4], fill=rgba(ACC, a))
            lay.alpha_composite(with_alpha(sm, a), (X + 34 + int(50 * (1 - ease(a))), yy - 8))
    if graphic:
        roundrobin(lay, pg.get('teams', 8), 1460, 560, 270, prog(t, .3, 1.0), prog(t, 1.0, 3.4))

def body_frame(t, ev):
    img = background(t + 40)
    stars(img, t + OP_DUR, .45)
    pages = ev['pages']; n = len(pages)
    idx, lt = page_index(t, ev)
    graphic = 0 < idx <= n and pages[idx - 1].get('graphic')
    # ずっとループで回っているリング（右側）
    ra = .55 if idx == 0 else (.12 if graphic else .4)
    if idx <= n: paste_center(img, rings(t + 5, R=300, grow=prog(t, 0, .9), alpha=ra, spin=.5, mono=True), 1470, 540)
    # 背景の大きな番号（ゆっくり流れる）
    if 0 < idx <= n:
        num = jp_text(f'{idx:02d}', 520, fill=PANEL, weight='black')
        img.alpha_composite(with_alpha(num, .9), (W - num.width + 40 - int(lt * 18), 360))
    if 0 < idx <= n: side_shade(img, 1)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if idx == 0: title_page(lay, lt, ev)
    elif idx <= n: info_page(lay, lt, pages[idx - 1], idx, n)
    img.alpha_composite(lay)
    # ページの点
    if 0 < idx <= n:
        d = ImageDraw.Draw(img); cx = W // 2 - (n * 44) // 2
        for k in range(n):
            c = ACC if k == idx - 1 else LINE; w = 30 if k == idx - 1 else 16
            d.rectangle([cx + k * 44, 990, cx + k * 44 + w, 1000], fill=rgba(c, 1))
    # 締め
    if idx == n + 1:
        F = lt
        paste_center(img, rings(t, R=430, grow=prog(F, 0, .9), alpha=.45, spin=.8, mono=True), W // 2, 420)
        img.alpha_composite(Image.new('RGBA', (W, H), rgba(BG, .35)))
        big = pixel_text(ev['cta'], 20, 12, fill=INK, shadow=False)
        q = prog(F, .4, .9); y = 290; x = (W - big.width) // 2
        rows = int(big.height * q) // 12 * 12
        if rows > 0: img.alpha_composite(big.crop((0, big.height - rows, big.width, big.height)), (x, y + big.height - rows))
        if ev.get('cta_sub'):
            sub = jp_text(ev['cta_sub'], 76, shadow=6)
            kinetic(img, ev['cta_sub'], 76, (W - sub.width) // 2, y + big.height + 50, F, t0=1.0)
        a = prog(F, 1.7, 2.1)
        if a > 0 and ev.get('how'):
            cta = jp_text(ev['how'], 44, weight='bold'); d = ImageDraw.Draw(img)
            bx = (W - cta.width) // 2; by = 830
            d.rectangle([bx - 40, by - 22, bx + cta.width + 40, by + cta.height + 18], fill=rgba(PANEL, a), outline=rgba(SOFT, a), width=3)
            img.alpha_composite(with_alpha(cta, a), (bx, by - 4))
    img.alpha_composite(scaled(LOGO_FULL, CORNER_S), CORNER_XY)
    s1 = pixel_text(ev.get('stage', 'STAGE 01'), 12, 3, fill=MUTED, shadow=False)
    img.alpha_composite(s1, (W - 110 - s1.width, 90))
    # 切り替え：境目の前後 WIPE/2 秒で帯が横切る（真ん中でページが入れ替わる）
    for b in bounds(ev):
        if abs(t - b) < WIPE / 2: wipe(img, (t - b) / WIPE + .5)
    marquee(img, t + OP_DUR, 1); corners(img, 1)
    img = finish(img, t)
    e = prog(t, body_dur(ev) - .4, body_dur(ev))
    if e > 0: img = Image.blend(img, Image.new('RGBA', (W, H), BG + (255,)), e)
    return img

# ======================= 書き出し =======================
def render(fn, dur, out):
    tmp = out[:-4] + '.part.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)): p.stdin.write(fn(i / FPS).convert('RGB').tobytes())
    p.stdin.close()
    if p.wait() != 0: raise SystemExit('ffmpeg failed')
    os.replace(tmp, out)

def concat(parts, out):
    lst = out + '.txt'
    with open(lst, 'w') as f: f.writelines(f"file '{os.path.abspath(x)}'\n" for x in parts)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out], check=True)
    os.remove(lst)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'op': render(op_frame, OP_DUR, os.path.join(OUT, 'op.mp4'))
    elif cmd == 'ed': render(ed_frame, ED_DUR, os.path.join(OUT, 'ed.mp4'))
    elif cmd == 'event':
        ev = json.load(open(sys.argv[2], encoding='utf-8'))
        body = os.path.join(OUT, ev['id'] + '_body.mp4')
        render(lambda t: body_frame(t, ev), body_dur(ev), body)
        for part, fn, dur in (('op', op_frame, OP_DUR), ('ed', ed_frame, ED_DUR)):
            if not os.path.exists(os.path.join(OUT, part + '.mp4')): render(fn, dur, os.path.join(OUT, part + '.mp4'))
        concat([os.path.join(OUT, 'op.mp4'), body, os.path.join(OUT, 'ed.mp4')], os.path.join(OUT, ev['id'] + '.mp4'))
    elif cmd == 'frames':
        part = sys.argv[2]; ev = json.load(open(sys.argv[3], encoding='utf-8')) if part == 'body' else None
        ts = sys.argv[4:] if part == 'body' else sys.argv[3:]
        fn = {'op': op_frame, 'ed': ed_frame, 'body': lambda t: body_frame(t, ev)}[part]
        for s in ts: fn(float(s)).convert('RGB').save(os.path.join(OUT, f'{part}_{s}.png'))
