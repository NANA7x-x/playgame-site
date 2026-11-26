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
def body_frame(t, ev):
    img = background(t + 40)
    stars(img, t + OP_DUR, 1)
    x0 = 110
    # 左上のロゴ（OPの最後と同じ位置）
    img.alpha_composite(scaled(LOGO_FULL, CORNER_S), CORNER_XY)
    # 右側：回るリング＋チーム（またはゲーム名）
    TC = (1480, 440)
    center_glow(img, *TC, 260, prog(t, 0, .6))
    paste_center(img, rings(t + 5, R=250, grow=prog(t, .0, .9), spin=.9), *TC)
    n = ev.get('teams')
    d = ImageDraw.Draw(img)
    if n:
        R = 200
        pts = [(TC[0] + R * math.cos(math.radians(-90 + 360 / n * k)), TC[1] + R * math.sin(math.radians(-90 + 360 / n * k))) for k in range(n)]
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        m = int(len(pairs) * prog(t, 1.6, 3.0))
        for k, (i, j) in enumerate(pairs[:m]): d.line([pts[i], pts[j]], fill=rgba(GRAD[k % 4], .5), width=3)
        if m == len(pairs):
            pl = prog(t, 3.0, 3.3); r = 52 + 6 * math.sin(t * 6)
            d.ellipse([TC[0] - r, TC[1] - r, TC[0] + r, TC[1] + r], fill=rgba(BG, pl), outline=rgba(MINT, pl), width=4)
            paste_center(img, with_alpha(pixel_text(str(len(pairs)), 14, 4, fill=MINT, shadow=False), pl), TC[0], TC[1] - 8)
            paste_center(img, with_alpha(pixel_text('MATCHES', 12, 2, fill=MUTED, shadow=False), pl), TC[0], TC[1] + 26)
        for k, (x, y) in enumerate(pts):
            p = prog(t, .9 + k * .08, 1.1 + k * .08)
            if p <= 0: continue
            s = max(8, 40 * back(p)); c = GRAD[k % 4]
            d.rectangle([x - s, y - s, x + s, y + s], fill=rgba(PANEL, 1), outline=(255, 255, 255, 255), width=4)
            d.rectangle([x - s + 6, y - s + 6, x + s - 6, y + s - 6], outline=rgba(c, 1), width=3)
            if p >= 1: paste_center(img, pixel_text(f'T{k + 1}', 14, 3, fill=c, shadow=False), x, y)
    else:
        # チーム数がないイベント：ゲーム名が輪の上を回る
        games = ev.get('games') or [ev.get('game', '')]
        for k, g in enumerate(games):
            a = math.radians(t * 25 + 360 / len(games) * k); x = TC[0] + 230 * math.cos(a); y = TC[1] + 230 * .55 * math.sin(a)
            lab = pixel_text(g, 12, 3, fill=GRAD[k % 4], shadow=True)
            paste_center(img, with_alpha(lab, prog(t, .8 + k * .1, 1.2 + k * .1)), x, y)
    # タイトル
    a = prog(t, .15, .45)
    if a > 0: img.alpha_composite(with_alpha(pixel_text(ev['prefix'], 16, 4, fill=CYAN, shadow=False), a), (x0 + 6, 290))
    val = pixel_text(ev['game_title'], 16, 6, fill=INK)
    p = prog(t, .25, .7)
    if p > 0: img.alpha_composite(val.crop((0, 0, max(1, int(val.width * int(p * 8) / 8)), val.height)), (x0, 350))
    tl = pixel_text(ev['title'], 20, ev.get('title_scale', 11), grad=True, outline=True)
    p = prog(t, .6, 1.3)
    if p > 0:
        jit = 1 - prog(t, .6, 1.4); rnd = random.Random(int(t * FPS))
        if jit > 0:
            for col, dx in ((PINK, 14), (CYAN, -14)):
                gh = Image.new('RGBA', tl.size, rgba(col, 1)); gh.putalpha(ImageChops.multiply(tl.getchannel('A'), Image.new('L', tl.size, int(140 * jit))))
                img.alpha_composite(gh, (x0 + int(dx * jit) + rnd.randint(-6, 6), 470 + rnd.randint(-4, 4)))
        img.alpha_composite(tl.crop((0, 0, max(1, int(tl.width * int(p * 9) / 9)), tl.height)), (x0, 470))
    a = prog(t, 1.2, 1.6)
    if a > 0:
        for k in range(int(46 * a)): d.rectangle([x0 + 6 + k * 18, 700, x0 + 17 + k * 18, 711], fill=GRAD[(k // 3) % 4])
        img.alpha_composite(with_alpha(pixel_text(ev['sub'], 16, 3, fill=MINT, shadow=False), a), (x0 + 6, 734))
    # メッセージ窓
    p = prog(t, 3.3, 3.6)
    if p > 0:
        X0, Y0, X1, Y1 = 130, 795, 1790, 985; h = int((Y1 - Y0) * ease(p)); yc = (Y0 + Y1) // 2
        d = ImageDraw.Draw(img)
        d.rectangle([X0, yc - h // 2, X1, yc + h // 2], fill=rgba(PANEL, .96), outline=(255, 255, 255, 255), width=6)
        d.rectangle([X0 + 10, yc - h // 2 + 10, X1 - 10, yc + h // 2 - 10], outline=rgba(VIOLET, 1), width=3)
        if p >= 1:
            for k, (tag, text) in enumerate(ev['info'][:3]):
                st = 3.7 + k * .5; q = prog(t, st, st + .45)
                if q <= 0: continue
                img.alpha_composite(pixel_text('▶ ' + tag, 14, 3, fill=GRAD[(k + 2) % 4], shadow=False), (X0 + 40, Y0 + 28 + k * 50))
                s = text[:int(len(text) * q)]
                if s: img.alpha_composite(pixel_text(s, 14, 3, fill=INK, shadow=False), (X0 + 270, Y0 + 28 + k * 50))
            if t > 5.3 and int(t * 4) % 2 == 0: d.polygon([(X1 - 60, Y1 - 46), (X1 - 36, Y1 - 46), (X1 - 48, Y1 - 30)], fill=INK)
    # 締め：ENTRY OPEN など
    p = prog(t, 6.0, 6.4)
    if p > 0:
        img.alpha_composite(Image.new('RGBA', (W, H), rgba(BG, .82 * ease(p))))
        big = pixel_text(ev['cta'], 20, 12, grad=True, outline=True)
        paste_center(img, rings(t, R=420, grow=prog(t, 6.0, 6.8), alpha=.55, spin=1.4), W // 2, 380)
        q = prog(t, 6.2, 6.7); y = 300; x = (W - big.width) // 2
        rows = int(big.height * q) // 12 * 12
        if rows > 0: img.alpha_composite(big.crop((0, big.height - rows, big.width, big.height)), (x, y + big.height - rows))
        if ev.get('cta_sub'):
            a = prog(t, 6.7, 7.0); sub = pixel_text(ev['cta_sub'], 20, 3, fill=MINT)
            paste_center(img, with_alpha(sub, a), W // 2, y + big.height + 60)
        if t > 7.0 and int((t - 7.0) * 2.5) % 2 == 0:
            paste_center(img, pixel_text('▶ PRESS ENTRY', 16, 4, fill=INK), W // 2, y + big.height + 145)
        a = prog(t, 7.2, 7.6)
        if a > 0 and ev.get('how'):
            cta = pixel_text(ev['how'], 14, 3, fill=INK, shadow=False); d = ImageDraw.Draw(img)
            bx = (W - cta.width) // 2; by = 850
            d.rectangle([bx - 36, by - 22, bx + cta.width + 36, by + cta.height + 22], fill=rgba(VIOLET, a), outline=rgba((255, 255, 255), a), width=4)
            img.alpha_composite(with_alpha(cta, a), (bx, by))
    # 右上：ゲームのスコア風
    s1 = pixel_text(ev.get('stage', 'STAGE 01'), 12, 3, fill=CYAN, shadow=False)
    img.alpha_composite(with_alpha(s1, prog(t, .3, .6)), (W - 110 - s1.width, 90))
    marquee(img, t + OP_DUR, 1); corners(img, 1)
    img = finish(img, t)
    # 最後は暗くしてEDへ
    e = prog(t, body_dur(ev) - .35, body_dur(ev))
    if e > 0: img = Image.blend(img, Image.new('RGBA', (W, H), BG + (255,)), e)
    return img

def body_dur(ev): return ev.get('duration', 9.0)

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
