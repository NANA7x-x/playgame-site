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
    shockwave(img, cx, cy, prog(t, 1.85, 2.7), CYAN); shockwave(img, cx, cy, prog(t, 1.95, 2.9), PINK)
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
    shockwave(img, cx, cy, prog(t, .55, 1.3), MINT)
    # メッセージ
    a = prog(t, 1.0, 1.4)
    if a > 0:
        msg = pixel_text('SEE YOU IN PLAY GAME!', 16, 5, grad=True, outline=True)
        paste_center(img, with_alpha(msg, a), cx, 740)
    lines = [('HP', 'nana7x-x.github.io/playgame-site', CYAN), ('DISCORD', '「イベント情報」チャンネルをチェック', PINK), ('X', '@7x_x7x_x7', MINT)]
    for k, (tag, body, col) in enumerate(lines):
        q = prog(t, 1.6 + k * .25, 2.0 + k * .25)
        if q <= 0: continue
        tg = pixel_text(tag, 12, 3, fill=col, shadow=False); bd = pixel_text(body, 14, 3, fill=INK, shadow=False)
        total = 150 + bd.width; x = cx - total / 2; y = 812 + k * 50
        img.alpha_composite(with_alpha(tg, q), (int(x + 140 - tg.width), y + 4)); img.alpha_composite(with_alpha(bd, q), (int(x + 160), y))
    if t > 2.6 and int((t - 2.6) * 2.5) % 2 == 0 and t < 4.6:
        ps = pixel_text('PRESS START', 16, 4, fill=INK)
        paste_center(img, ps, cx, 655)
    marquee(img, t + 7, 1); corners(img, 1)
    img = finish(img, t)
    s = prog(t, 0, .35)
    if s < 1: img = Image.blend(Image.new('RGBA', (W, H), BG + (255,)), img, s)
    return crt_off(img, prog(t, 4.6, 5.5))

# ======================= 本編（イベントごと） =======================
# タイトル → 情報を1ページに1つずつ大きく（ページをめくるように切り替え）→ 締め。
# 色は抑えめ：タイトルと締めの文字だけPGのグラデーション、ほかは白と紫系。
SOFT = (150, 135, 215)
ACC = CYAN
T_TITLE, T_PAGE, T_FIN = 3.2, 2.8, 3.0     # タイトル・1ページ・締めの長さ
TURN = .35                                 # ページをめくる時間

def body_dur(ev): return T_TITLE + T_PAGE * len(ev['pages']) + T_FIN

def page_index(t, ev):
    """いまのページ番号（0=タイトル, 1..n=情報, n+1=締め）と、そのページの中の時間。"""
    if t < T_TITLE: return 0, t
    k = int((t - T_TITLE) // T_PAGE)
    if k < len(ev['pages']): return k + 1, t - T_TITLE - k * T_PAGE
    return len(ev['pages']) + 1, t - T_TITLE - len(ev['pages']) * T_PAGE

def fit_text(txt, px, max_w, max_scale, **kw):
    m = pixel_mask(txt, px)
    return pixel_text(txt, px, max(2, min(max_scale, max_w // max(1, m.width))), **kw)

def roundrobin(lay, n, cx, cy, R, p, lt):
    """n チームの総当たり図。p:出てくる度合い、lt:線を引く度合い。"""
    d = ImageDraw.Draw(lay)
    pts = [(cx + R * math.cos(math.radians(-90 + 360 / n * k)), cy + R * math.sin(math.radians(-90 + 360 / n * k))) for k in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    m = int(len(pairs) * lt)
    for i, j in pairs[:m]: d.line([pts[i], pts[j]], fill=rgba(SOFT, .65), width=2)
    if m: # いま引いている線を明るく
        i, j = pairs[m - 1]; d.line([pts[i], pts[j]], fill=rgba(ACC, 1), width=4)
    for k, (x, y) in enumerate(pts):
        q = clamp(p * 3 - k * .2)
        if q <= 0: continue
        s = max(8, 36 * back(q))
        d.rectangle([x - s, y - s, x + s, y + s], fill=rgba(PANEL, 1), outline=rgba(SOFT, 1), width=3)
        if q >= 1: paste_center(lay, pixel_text(f'T{k + 1}', 14, 3, fill=INK, shadow=False), x, y)
    if m:
        done = m == len(pairs)
        r = 74; d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(BG, .95), outline=rgba(ACC if done else SOFT, 1), width=3)
        paste_center(lay, pixel_text(f'{m}', 14, 5 if done else 4, fill=ACC if done else INK, shadow=False), cx, cy - 12)
        paste_center(lay, pixel_text('試合' if not done else '全試合', 12, 2, fill=MUTED, shadow=False), cx, cy + 36)

def title_page(lay, t, ev):
    x0 = 110
    a = prog(t, .15, .45)
    if a > 0: lay.alpha_composite(with_alpha(pixel_text(ev['prefix'], 16, 4, fill=MUTED, shadow=False), a), (x0 + 6, 300))
    val = pixel_text(ev['game_title'], 16, 7, fill=INK, shadow=False)
    p = prog(t, .25, .7)
    if p > 0: lay.alpha_composite(val.crop((0, 0, max(1, int(val.width * int(p * 8) / 8)), val.height)), (x0, 365))
    tl = pixel_text(ev['title'], 20, ev.get('title_scale', 12), grad=True, outline=True)
    p = prog(t, .6, 1.3)
    if p > 0:
        jit = 1 - prog(t, .6, 1.2); rnd = random.Random(int(t * FPS))
        if jit > 0:
            for col, dx in ((PINK, 12), (CYAN, -12)):
                gh = Image.new('RGBA', tl.size, rgba(col, 1)); gh.putalpha(ImageChops.multiply(tl.getchannel('A'), Image.new('L', tl.size, int(110 * jit))))
                lay.alpha_composite(gh, (x0 + int(dx * jit) + rnd.randint(-4, 4), 500 + rnd.randint(-3, 3)))
        lay.alpha_composite(tl.crop((0, 0, max(1, int(tl.width * int(p * 9) / 9)), tl.height)), (x0, 500))
    a = prog(t, 1.2, 1.6)
    if a > 0:
        d = ImageDraw.Draw(lay); d.rectangle([x0 + 6, 770, x0 + 6 + 900 * ease(a), 775], fill=rgba(SOFT, 1))
        lay.alpha_composite(with_alpha(pixel_text(ev['sub'], 16, 4, fill=MUTED, shadow=False), a), (x0 + 6, 800))

def info_page(lay, t, pg, k, n):
    """情報の1ページ：小さい見出し → 大きい本文 → 補足。"""
    X = 160
    d = ImageDraw.Draw(lay)
    tag = pixel_text(pg['tag'], 14, 4, fill=ACC, shadow=False)
    no = pixel_text(f'{k:02d}/{n:02d}', 12, 3, fill=MUTED, shadow=False)
    lay.alpha_composite(with_alpha(tag, prog(t, .1, .3)), (X, 340))
    lay.alpha_composite(with_alpha(no, prog(t, .1, .3)), (X + tag.width + 30, 340 + tag.height - no.height))
    d.rectangle([X, 340 + tag.height + 18, X + 140 * ease(prog(t, .15, .5)), 340 + tag.height + 24], fill=rgba(ACC, 1))
    graphic = pg.get('graphic') == 'roundrobin'
    maxw = 1000 if graphic else 1600
    big = fit_text(pg['big'], 20, maxw, 8, fill=INK, shadow=True)
    q = prog(t, .25, .65)
    if q > 0:
        rows = max(0, int(big.height * q) // 8 * 8)
        if rows: lay.alpha_composite(big.crop((0, big.height - rows, big.width, big.height)), (X, 480 + big.height - rows))
    if pg.get('small'):
        sm = fit_text(pg['small'], 14, maxw, 4, fill=MUTED, shadow=False)
        lay.alpha_composite(with_alpha(sm, prog(t, .7, 1.0)), (X + 4, 500 + big.height + 40))
    if graphic:
        roundrobin(lay, pg.get('teams', 8), 1470, 560, 250, prog(t, .2, .8), prog(t, .6, 2.0))

def body_frame(t, ev):
    img = background(t + 40)
    stars(img, t + OP_DUR, .45)
    img.alpha_composite(scaled(LOGO_FULL, CORNER_S), CORNER_XY)
    pages = ev['pages']; n = len(pages)
    idx, lt = page_index(t, ev)
    # ずっと右側でゆっくり回っているリング（情報のページではうすく）
    ra = .5 if idx == 0 else .22
    paste_center(img, rings(t + 5, R=300, grow=prog(t, 0, .9), alpha=ra, spin=.5, mono=True), 1480, 470)

    def draw(i, tt):
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        if i == 0: title_page(lay, tt, ev)
        elif i <= n: info_page(lay, tt, pages[i - 1], i, n)
        return lay
    if idx <= n:
        lay = draw(idx, lt)
        # ページをめくる：次のページへ切り替わる直前に左へ流して消える
        dur = T_TITLE if idx == 0 else T_PAGE
        out = prog(lt, dur - TURN, dur)
        if out > 0: lay = with_alpha(lay, 1 - out); off = -int(220 * ease_in(out))
        else: off = 0
        inn = prog(lt, 0, TURN) if idx > 0 else 1
        if inn < 1: off = int(220 * (1 - ease(inn))); lay = with_alpha(lay, inn)
        img.alpha_composite(lay, (off, 0))
        # めくる瞬間の縦の光
        if 0 < out < 1:
            d = ImageDraw.Draw(img); x = int(W * (1 - ease(out)))
            for k in range(6): d.rectangle([x + k * 14, 60, x + k * 14 + 6, H - 60], fill=rgba(SOFT, .25 * (1 - k / 6)))
    # ページの点（いまどこを見ているか）
    if 0 < idx <= n:
        d = ImageDraw.Draw(img); cx = W // 2 - (n * 34) // 2
        for k in range(n):
            c = ACC if k == idx - 1 else LINE
            d.rectangle([cx + k * 34, 990, cx + k * 34 + 18, 1002], fill=rgba(c, 1))
    # 締め
    if idx == n + 1:
        F = lt
        img.alpha_composite(Image.new('RGBA', (W, H), rgba(BG, .6 * ease(prog(F, 0, .3)))))
        paste_center(img, rings(t, R=430, grow=prog(F, 0, .8), alpha=.4, spin=.8, mono=True), W // 2, 400)
        big = pixel_text(ev['cta'], 20, 12, grad=True, outline=True)
        q = prog(F, .15, .65); y = 290; x = (W - big.width) // 2
        rows = int(big.height * q) // 12 * 12
        if rows > 0: img.alpha_composite(big.crop((0, big.height - rows, big.width, big.height)), (x, y + big.height - rows))
        if ev.get('cta_sub'):
            paste_center(img, with_alpha(pixel_text(ev['cta_sub'], 20, 4, fill=INK, shadow=False), prog(F, .7, 1.0)), W // 2, y + big.height + 70)
        a = prog(F, 1.1, 1.5)
        if a > 0 and ev.get('how'):
            cta = pixel_text(ev['how'], 14, 3, fill=INK, shadow=False); d = ImageDraw.Draw(img)
            bx = (W - cta.width) // 2; by = 830
            d.rectangle([bx - 36, by - 22, bx + cta.width + 36, by + cta.height + 22], fill=rgba(PANEL, a), outline=rgba(SOFT, a), width=3)
            img.alpha_composite(with_alpha(cta, a), (bx, by))
    s1 = pixel_text(ev.get('stage', 'STAGE 01'), 12, 3, fill=MUTED, shadow=False)
    img.alpha_composite(with_alpha(s1, prog(t, .3, .6)), (W - 110 - s1.width, 90))
    marquee(img, t + OP_DUR, 1); corners(img, 1)
    img = finish(img, t)
    e = prog(t, body_dur(ev) - .35, body_dur(ev))
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
