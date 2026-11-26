"""ピンク↔ラベンダーで色が流れるロゴGIF。python3 anim.py → pg-logo-anim.gif / pg-icon-anim.gif"""
import colorsys, math, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
src = Image.open(os.path.join(HERE, '..', 'img', 'mark2.png')).convert('RGBA')
STOPS = [(255, 63, 208), (224, 74, 232), (176, 108, 242), (169, 140, 240), (201, 166, 255), (176, 108, 242), (255, 63, 208)]
def grad(u):
    u = (u % 1) * (len(STOPS) - 1); i = int(u); f = u - i
    a, b = STOPS[i], STOPS[min(i + 1, len(STOPS) - 1)]
    return tuple(a[k] + (b[k] - a[k]) * f for k in range(3))
N = 30
def frame(k, size):
    im = src.resize(size, Image.NEAREST); px = im.load(); w, h = im.size
    off = k / N
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a: continue
            hh, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s < .15: continue
            gr, gg, gb = grad(x / w * .5 + y / h * .15 - off)
            gh, gs, _ = colorsys.rgb_to_hsv(gr / 255, gg / 255, gb / 255)
            nr, ng, nb = colorsys.hsv_to_rgb(gh, gs * min(1, s / .7), v)
            # 光が斜めに走る
            sh = max(0, 1 - abs((x / w - y / h * .4) - (2.2 * (k / N) - .6)) / .06)
            px[x, y] = tuple(int(255 * min(1, c + sh * .5)) for c in (nr, ng, nb)) + (a,)
    return im
def save(name, size, canvas=None, bg=None):
    frames = []
    for k in range(N):
        f = frame(k, size)
        if canvas:
            c = Image.new('RGBA', canvas, bg); c.alpha_composite(f, ((canvas[0] - size[0]) // 2, (canvas[1] - size[1]) // 2)); f = c
        frames.append(f)
    if bg:
        frames = [f.convert('RGB').quantize(128, method=Image.MEDIANCUT) for f in frames]
        frames[0].save(name, save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
    else:
        q = []
        for f in frames:
            a = f.getchannel('A'); p = f.convert('RGB').quantize(255, method=Image.MEDIANCUT)
            p.paste(255, mask=Image.eval(a, lambda v: 255 if v < 128 else 0)); q.append(p)
        q[0].save(name, save_all=True, append_images=q[1:], duration=70, loop=0, transparency=255, disposal=2, optimize=False)
os.chdir(HERE)
save('pg-logo-anim.gif', (380, 292))
save('pg-icon-anim.gif', (400, 307), canvas=(512, 512), bg=(10, 10, 13, 255))
print(os.path.getsize('pg-logo-anim.gif'), os.path.getsize('pg-icon-anim.gif'))
