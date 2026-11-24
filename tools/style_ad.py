import sys, math, subprocess
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from render import (gradient, text_img, rounded, place, ease_out, ease_back, prog, clamp,
                    NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, EN, EN_SB)

W, H, FPS = 1080, 1920, 30
DUR = 10.8
N = int(DUR * FPS)
CX, CY = W // 2, 860          # icon centre
TY = 1390                      # caption baseline centre

# ---------- word timeline (seconds from voiceover) ----------
# (word, start, accent, line)
WORDS = [
    ("زبونك", 0.05, False, 0), ("راسلك…", 0.55, False, 0),
    ("ومحد", 1.49, False, 1), ("رد؟", 1.85, True, 1),
    ("نيكسو", 2.67, True, 2), ("تسويلك", 3.15, False, 2),
    ("موقع", 3.75, True, 3), ("احترافي", 4.10, True, 3),
    ("وموظف", 4.72, True, 4), ("مبيعات", 5.20, True, 4), ("ذكي", 5.70, True, 4),
    ("يبيع", 6.15, False, 5), ("بدالك", 6.65, True, 5),
    ("أربعة", 7.55, False, 6), ("وعشرين", 7.95, False, 6), ("ساعة", 8.40, True, 6),
]
LINE_END = {0: 1.45, 1: 2.6, 2: 3.7, 3: 4.68, 4: 6.1, 5: 7.45, 6: 9.15}

# ---------- background ----------
def make_bg():
    bg = Image.new("RGBA", (W, H), NAVY + (255,))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((CX - 520, CY - 520, CX + 520, CY + 520), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(220)).point(lambda v: int(v * 0.35))
    bg.paste(Image.new("RGBA", (W, H), DNAVY + (255,)), (0, 0), glow)
    tint = Image.new("L", (W, H), 0)
    ImageDraw.Draw(tint).ellipse((CX - 380, CY - 380, CX + 380, CY + 380), fill=255)
    tint = tint.filter(ImageFilter.GaussianBlur(200)).point(lambda v: int(v * 0.10))
    bg.paste(Image.new("RGBA", (W, H), BLUE + (255,)), (0, 0), tint)
    return bg

BG = make_bg()

@lru_cache(None)
def rings():
    s = 1500
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = s // 2
    for r, a in [(330, 26), (470, 18), (640, 12)]:
        d.ellipse((c - r, c - r, c + r, c + r), outline=GRAY + (a,), width=2)
    # dashed outer ring
    r = 560
    for k in range(0, 360, 6):
        a0 = math.radians(k); a1 = math.radians(k + 3)
        d.line((c + r * math.cos(a0), c + r * math.sin(a0), c + r * math.cos(a1), c + r * math.sin(a1)), fill=GRAY + (30,), width=2)
    # tick ring
    r1, r2 = 395, 410
    for k in range(0, 360, 3):
        a = math.radians(k)
        d.line((c + r1 * math.cos(a), c + r1 * math.sin(a), c + r2 * math.cos(a), c + r2 * math.sin(a)), fill=CYAN + (22,), width=2)
    return im

def background(t):
    f = BG.copy()
    r = rings().rotate(t * 6, resample=Image.BICUBIC)
    f.alpha_composite(r, (CX - r.width // 2, CY - r.height // 2))
    return f

# ---------- word-by-word caption ----------
@lru_cache(None)
def word_img(w, accent, size=104):
    return text_img(w, AR, size, CYAN if accent else WHITE)

@lru_cache(None)
def blurred(w, accent, b):
    im = word_img(w, accent)
    return im.filter(ImageFilter.GaussianBlur(b)) if b else im

def captions(f, t):
    lines = {}
    for w, st, acc, ln in WORDS:
        lines.setdefault(ln, []).append((w, st, acc))
    for ln, ws in lines.items():
        start = ws[0][1]; end = LINE_END[ln]
        if t < start - 0.01 or t > end + 0.25: continue
        out = 1 - prog(t, end, 0.22)
        imgs = [word_img(w, a) for w, _, a in ws]
        gap = -40
        total = sum(im.width for im in imgs) + gap * (len(imgs) - 1)
        x = W / 2 + total / 2   # RTL: start from the right
        for (w, st, a), im in zip(ws, imgs):
            if t >= st:
                p = ease_out(prog(t, st, 0.28))
                b = int(round((1 - p) * 8))
                src = blurred(w, a, b)
                cx = x - im.width / 2
                place(f, src, cx, TY + (1 - p) * 26, p * out, 1.08 - 0.08 * p)
            x -= im.width + gap

# ---------- viewfinder brackets ----------
def brackets(f, cx, cy, size, t0, t, color=CYAN, out=1.0):
    p = ease_back(prog(t, t0, 0.35))
    if p <= 0.01 or out <= 0.01: return
    s = size * (1.35 - 0.35 * p)
    L = s * 0.22; th = 7
    a = int(255 * clamp(p) * out)
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, y0 = cx + sx * s / 2, cy + sy * s / 2
            d.line((x0, y0, x0 - sx * L, y0), fill=color + (a,), width=th)
            d.line((x0, y0, x0, y0 - sy * L), fill=color + (a,), width=th)
    f.alpha_composite(lay)

# ---------- icons ----------
@lru_cache(None)
def chat_icon():
    s = 420; im = Image.new("RGBA", (s + 80, s + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = 40
    d.rounded_rectangle((o, o, o + s, o + s * 0.78), 90, fill=WHITE + (255,))
    d.polygon([(o + 90, o + s * 0.74), (o + 70, o + s * 0.98), (o + 190, o + s * 0.74)], fill=WHITE + (255,))
    for k in range(3):
        x = o + s / 2 + (k - 1) * 95
        d.ellipse((x - 26, o + s * 0.39 - 26, x + 26, o + s * 0.39 + 26), fill=NAVY + (255,))
    return im

@lru_cache(None)
def badge(n):
    b = Image.new("RGBA", (130, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
    d.ellipse((5, 5, 125, 125), fill=BLUE + (255,), outline=NAVY + (255,), width=8)
    num = text_img(str(n), EN, 64, WHITE, rtl=False)
    b.alpha_composite(num, ((130 - num.width) // 2, (130 - num.height) // 2 - 2))
    return b

@lru_cache(None)
def site_card(variant):
    w, h = 560, 760
    card = rounded(w, h, 44, DNAVY, border=(0, 212, 255, 140))
    c = card.copy(); d = ImageDraw.Draw(c); o = 40
    # browser bar
    d.rounded_rectangle((o + 24, o + 24, o + w - 24, o + 74), 25, fill=(14, 32, 62, 255))
    for k, col in enumerate([CYAN, BLUE, PURPLE]):
        d.ellipse((o + 44 + k * 34, o + 40, o + 62 + k * 34, o + 58), fill=col + (255,))
    # hero block
    hero = gradient(w - 48, 300, *( [(BLUE, CYAN), (BLUE, PURPLE), (CYAN, PURPLE)][variant] )).convert("RGBA")
    m = Image.new("L", hero.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, hero.width, hero.height), 28, fill=255)
    c.paste(hero, (o + 24, o + 96), m)
    title = ["مطعمك أونلاين", "متجرك الإلكتروني", "شركتك بموقع"][variant]
    tt = text_img(title, AR, 50, WHITE)
    c.alpha_composite(tt, (o + w // 2 - tt.width // 2, o + 96 + 150 - tt.height // 2))
    # content lines
    for k in range(3):
        y = o + 430 + k * 52
        d.rounded_rectangle((o + 60 + k * 40, y, o + w - 60, y + 22), 11, fill=(169, 184, 204, 70))
    # button
    d.rounded_rectangle((o + 120, o + 620, o + w - 120, o + 700), 40, fill=BLUE + (255,))
    bt = text_img("اطلب هسه", AR, 40, WHITE)
    c.alpha_composite(bt, (o + w // 2 - bt.width // 2, o + 660 - bt.height // 2))
    return c

@lru_cache(None)
def bot_icon():
    s = 440; im = Image.new("RGBA", (s + 80, s + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = 40; c = o + s / 2
    d.line((c, o + 30, c, o + 95), fill=WHITE + (255,), width=16)
    d.ellipse((c - 30, o, c + 30, o + 60), fill=CYAN + (255,))
    d.rounded_rectangle((o + 30, o + 95, o + s - 30, o + s - 20), 110, fill=WHITE + (255,))
    d.rounded_rectangle((o + 80, o + 175, o + s - 80, o + 330), 70, fill=NAVY + (255,))
    d.rounded_rectangle((o, o + 210, o + 40, o + 300), 18, fill=WHITE + (255,))
    d.rounded_rectangle((o + s - 40, o + 210, o + s, o + 300), 18, fill=WHITE + (255,))
    return im

def bot_eyes(f, cx, cy, sc, t, alpha):
    if alpha <= 0.01: return
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    blink = 1.0 if (t % 1.6) > 0.12 else 0.15
    for sx in (-1, 1):
        ex = cx + sx * 70 * sc; ey = cy + 33 * sc
        rx, ry = 30 * sc, 30 * sc * blink
        d.ellipse((ex - rx, ey - ry, ex + rx, ey + ry), fill=CYAN + (int(255 * alpha),))
    f.alpha_composite(lay)

# ---------- scenes ----------
def scene_chat(f, t):
    if t > 2.85: return
    p = ease_back(prog(t, 0.0, 0.45)); out = 1 - prog(t, 2.55, 0.3)
    sc = (0.6 + 0.4 * p) * (1 - 0.3 * (1 - out))
    place(f, chat_icon(), CX, CY, clamp(p * 1.5) * out, sc)
    n = 1 + min(3, int(max(0, t - 0.3) / 0.28))
    pop = 1 + 0.25 * (1 - prog(t, 0.3 + (n - 1) * 0.28, 0.2))
    place(f, badge(n), CX + 190 * sc, CY - 175 * sc, clamp(p * 1.5) * out, pop * sc)
    brackets(f, CX, CY - 20, 560, 1.85, t, out=out)

def scene_sites(f, t):
    if t < 2.5 or t > 4.95: return
    out = 1 - prog(t, 4.6, 0.3)
    # three cards slide up in sequence, like a feed
    starts = [2.62, 3.3, 3.95]
    for i, st in enumerate(starts):
        if t < st - 0.02: continue
        p = ease_out(prog(t, st, 0.4))
        nxt = starts[i + 1] if i + 1 < len(starts) else 99
        q = ease_out(prog(t, nxt, 0.4))
        y = CY + (1 - p) * 900 - q * 900
        place(f, site_card(i), CX, y, clamp(p * 2) * out * (1 - q), 0.82)
    brackets(f, CX, CY, 640, 3.75, t, out=out)

def scene_bot(f, t):
    if t < 4.6 or t > 7.7: return
    p = ease_back(prog(t, 4.68, 0.45)); out = 1 - prog(t, 7.3, 0.3)
    sc = 0.6 + 0.4 * p
    a = clamp(p * 1.5) * out
    place(f, bot_icon(), CX, CY, a, sc)
    bot_eyes(f, CX, CY, sc, t, a)
    brackets(f, CX, CY, 620, 4.72, t, out=out)
    # sales chips at "يبيع بدالك"
    chips = [("تم الطلب ✓", 6.2, -1), ("زبون جديد", 6.6, 1)]
    for txt, st, side in chips:
        q = ease_back(prog(t, st, 0.35))
        if q <= 0: continue
        tx = text_img(txt, AR, 44, WHITE)
        pill = rounded(tx.width - 80 + 70, 92, 46, DNAVY, border=(0, 212, 255, 220), shadow=False).copy()
        pill.alpha_composite(tx, ((pill.width - tx.width) // 2, (pill.height - tx.height) // 2))
        place(f, pill, CX + side * 300, CY + side * 260 - (1 - q) * 30 * side, clamp(q * 1.5) * out, 0.8 + 0.2 * q)

def scene_timer(f, t):
    if t < 7.35 or t > 9.4: return
    p = ease_back(prog(t, 7.45, 0.45)); out = 1 - prog(t, 9.1, 0.25)
    big = text_img("24/7", EN, 300, CYAN, rtl=False, glow=12)
    place(f, big, CX, CY - 40, clamp(p * 1.5) * out, 0.7 + 0.3 * p)
    # ruler with progress line (like the reference timer)
    x0, x1, y = 170, 910, CY + 230
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * out * clamp(p * 1.5))
    for k in range(0, 49):
        x = x0 + (x1 - x0) * k / 48
        hgt = 34 if k % 6 == 0 else 16
        d.line((x, y - hgt, x, y), fill=GRAY + (int(a * 0.5),), width=3)
    fill = ease_out(prog(t, 7.55, 1.3))
    xe = x1 - (x1 - x0) * fill                  # fills right-to-left
    d.line((xe, y + 14, x1, y + 14), fill=CYAN + (a,), width=8)
    d.ellipse((xe - 14, y, xe + 14, y + 28), fill=CYAN + (a,))
    f.alpha_composite(lay)

def scene_outro(f, t):
    if t < 9.1: return
    p = ease_out(prog(t, 9.2, 0.5))
    logo = text_img("NEXO", EN, 250, WHITE, rtl=False)
    # wipe reveal from right like the reference wordmark
    if p < 1:
        logo = logo.copy(); m = Image.new("L", logo.size, 0)
        ImageDraw.Draw(m).rectangle((int(logo.width * (1 - p)), 0, logo.width, logo.height), fill=255)
        a = Image.composite(logo.getchannel("A"), Image.new("L", logo.size, 0), m); logo.putalpha(a)
    place(f, logo, CX, CY - 40, clamp(p * 2))
    sub = text_img("نيكسو", AR, 54, WHITE)
    place(f, sub, CX + 250, CY + 95, ease_out(prog(t, 9.45, 0.35)))
    q = ease_out(prog(t, 9.6, 0.45))
    if q > 0.01:
        lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); half = 150 * q
        d.line((CX - half, CY + 190, CX + half, CY + 190), fill=CYAN + (int(255 * q),), width=5)
        f.alpha_composite(lay)
    words = [("Connect", False), ("to", False), ("the", False), ("Future.", True)]
    imgs = [text_img(w, EN_SB, 62, CYAN if acc else WHITE, rtl=False) for w, acc in words]
    gap = -62; total = sum(i.width for i in imgs) + gap * 3; x = CX - total / 2
    for k, ((w, acc), im) in enumerate(zip(words, imgs)):
        s = 9.75 + k * 0.12
        r = ease_out(prog(t, s, 0.3))
        place(f, im, x + im.width / 2, TY - 20 + (1 - r) * 20, r)
        x += im.width + gap
    place(f, text_img("nexodeveloper.net", EN_SB, 44, GRAY, rtl=False), CX, TY + 110, ease_out(prog(t, 10.1, 0.35)))

def frame(i):
    t = i / FPS
    f = background(t)
    scene_chat(f, t); scene_sites(f, t); scene_bot(f, t); scene_timer(f, t); scene_outro(f, t)
    if t < 9.15: captions(f, t)
    return f.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]:
            frame(int(float(ts) * FPS)).save(f"p_{ts}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "18", "-pix_fmt", "yuv420p", "style.mp4"], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
