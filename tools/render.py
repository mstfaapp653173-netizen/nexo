import math, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
DUR = 10.6
N = int(DUR * FPS)

NAVY = (5, 11, 26); DNAVY = (7, 19, 38); BLUE = (0, 102, 255); CYAN = (0, 212, 255)
PURPLE = (123, 44, 255); WHITE = (255, 255, 255); GRAY = (169, 184, 204)

import os as _os
_FD = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fonts")
AR = _os.path.join(_FD, "Cairo-ExtraBold.ttf")
AR_BLACK = _os.path.join(_FD, "Cairo-Black.ttf")
AR_REG = _os.path.join(_FD, "Cairo-SemiBold.ttf")
EN = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
EN_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def prog(t, start, dur): return clamp((t - start) / dur)

@lru_cache(None)
def font(path, size): return ImageFont.truetype(path, size)

def gradient(w, h, c1, c2, c3=None):
    import numpy as np
    x = np.linspace(0, 1, w)[None, :]; y = np.linspace(0, 1, h)[:, None]
    k = np.clip((x * w + y * h) / (w + h), 0, 1)[..., None]
    a = np.array(c1, float); b = np.array(c2, float)
    out = a + (b - a) * k
    if c3:
        c = np.array(c3, float); m = (np.clip(y, 0, 1) * 0.6)[..., None] * np.ones((1, w, 1))
        out = out * (1 - m) + c * m
    return Image.fromarray(out.astype("uint8"), "RGB")

@lru_cache(None)
def _text_img(s, path, size, color=WHITE, grad=None, rtl=True, glow=0):
    f = font(path, size)
    kw = dict(direction="rtl", language="ar") if rtl else {}
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), s, font=f, **kw)
    pad = 40 + glow * 2
    w, h = r - l + pad * 2, b - t + pad * 2
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - l, pad - t), s, font=f, fill=255, **kw)
    if grad:
        fill = gradient(w, h, *grad).convert("RGBA")
    else:
        fill = Image.new("RGBA", (w, h), color + (255,))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if glow:
        gcol = Image.new("RGBA", (w, h), CYAN + (255,))
        gm = mask.filter(ImageFilter.GaussianBlur(glow)).point(lambda v: int(v * 0.55))
        img.paste(gcol, (0, 0), gm)
    img.paste(fill, (0, 0), mask)
    return img

_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

@lru_cache(None)
def text_img(s, path, size, color=WHITE, grad=None, rtl=True, glow=0):
    # Cairo has no check mark: draw it with a fallback font at the end of the line
    if "✓" in s and path != _FALLBACK:
        main = _text_img(s.replace("✓", "").strip(), path, size, color, grad, rtl, glow)
        mark = _text_img("✓", _FALLBACK, int(size * 0.85), color, None, False, glow)
        gap = int(size * 0.25)
        w = main.width + mark.width - 80 + gap
        h = max(main.height, mark.height)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        out.alpha_composite(mark, (0, (h - mark.height) // 2))
        out.alpha_composite(main, (mark.width - 80 + gap, (h - main.height) // 2))
        return out
    return _text_img(s, path, size, color, grad, rtl, glow)

def place(frame, img, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01: return
    if abs(scale - 1) > 0.01:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BICUBIC)
    if alpha < 0.99:
        img = img.copy(); a = img.getchannel("A").point(lambda v: int(v * alpha)); img.putalpha(a)
    frame.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))

@lru_cache(None)
def rounded(w, h, r, fill, border=None, grad=None, shadow=True):
    pad = 40
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=255)
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.5))
        col = (CYAN if grad else (0, 0, 0))
        img.paste(Image.new("RGBA", img.size, col + (255,)), (0, 0), sh)
    body = gradient(*img.size, *grad).convert("RGBA") if grad else Image.new("RGBA", img.size, fill + (255,))
    img.paste(body, (0, 0), mask)
    if border:
        ImageDraw.Draw(img).rounded_rectangle((pad, pad, pad + w, pad + h), r, outline=border, width=3)
    return img

# ---------- background ----------
def make_glow(color, radius):
    s = radius * 2
    g = Image.new("L", (s, s), 0)
    ImageDraw.Draw(g).ellipse((radius * 0.6, radius * 0.6, s - radius * 0.6, s - radius * 0.6), fill=255)
    g = g.filter(ImageFilter.GaussianBlur(radius * 0.22))
    img = Image.new("RGBA", (s, s), color + (0,)); img.putalpha(g.point(lambda v: int(v * 0.42)))
    return img

GLOWS = [make_glow(BLUE, 620), make_glow(PURPLE, 520), make_glow(CYAN, 420)]
DOTS = Image.new("RGBA", (W, H + 120), (0, 0, 0, 0))
dd = ImageDraw.Draw(DOTS)
for y in range(40, H + 120, 60):
    for x in range(30, W, 60):
        dd.ellipse((x - 2, y - 2, x + 2, y + 2), fill=GRAY + (28,))

def background(t):
    f = Image.new("RGBA", (W, H), NAVY + (255,))
    pts = [(W * 0.15 + 120 * math.sin(t * 0.6), H * 0.22 + 80 * math.cos(t * 0.5)),
           (W * 0.9 + 100 * math.cos(t * 0.45), H * 0.62 + 120 * math.sin(t * 0.4)),
           (W * 0.4 + 140 * math.sin(t * 0.35 + 1), H * 0.92 + 60 * math.cos(t * 0.7))]
    for g, (x, y) in zip(GLOWS, pts):
        f.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
    f.alpha_composite(DOTS, (0, int(-(t * 18) % 60)))
    return f

# ---------- scene pieces ----------
def bubble(s, incoming=True, size=50):
    txt = text_img(s, AR_REG if incoming else AR, size, WHITE)
    w, h = txt.width - 80 + 70, txt.height - 80 + 50
    if incoming:
        b = rounded(w, h, 38, DNAVY, border=(169, 184, 204, 90), shadow=True)
    else:
        b = rounded(w, h, 38, BLUE, grad=(BLUE, (0, 150, 255)), shadow=True)
    img = b.copy()
    img.alpha_composite(txt, ((img.width - txt.width) // 2, (img.height - txt.height) // 2))
    return img

def logo_mark(size):
    return text_img("NEXO", EN, size, grad=(BLUE, CYAN, PURPLE), rtl=False, glow=14)

CUST = ["السلام عليكم، شكد السعر؟", "متوفر هسه؟", "وين موقعكم؟", "؟؟؟"]
BOT = ["أهلاً بيك! هسه أخدمك", "السعر والتفاصيل وصلتك"]

def caption(frame, s, t, start, y, size=100, grad=None, out=None):
    p = ease_out(prog(t, start, 0.35))
    a = p
    if out is not None: a *= 1 - prog(t, out, 0.25)
    img = text_img(s, AR, size, WHITE, grad=grad, glow=10 if grad else 0)
    place(frame, img, W / 2, y + (1 - p) * 50, a)

def scene1(f, t):
    out = 1 - prog(t, 3.1, 0.25)
    if out <= 0: return
    caption(f, "زبائنك يراسلوك...", t, 0.05, 330, 104, out=3.1)
    # chat card
    card = rounded(900, 1000, 56, DNAVY, border=(0, 212, 255, 60))
    place(f, card, W / 2, 1060, out * ease_out(prog(t, 0.0, 0.3)))
    # header in card
    place(f, text_img("الرسائل", AR, 46, GRAY), W / 2 + 300, 640, out)
    # unread badge
    n = sum(1 for i in range(4) if t > 0.35 + i * 0.32)
    if n:
        badge = rounded(110, 70, 35, BLUE, shadow=False)
        num = text_img(str(n), EN, 46, WHITE, rtl=False)
        b = badge.copy(); b.alpha_composite(num, ((b.width - num.width) // 2, (b.height - num.height) // 2))
        pulse = 1 + 0.15 * (1 - prog(t, 0.35 + (n - 1) * 0.32, 0.25))
        place(f, b, W / 2 - 330, 640, out, pulse)
    for i, s in enumerate(CUST):
        st = 0.35 + i * 0.32
        p = ease_back(prog(t, st, 0.35))
        if t < st: continue
        img = bubble(s, True)
        x = 150 + img.width / 2 - 40
        place(f, img, x - (1 - p) * 120, 790 + i * 190, out * clamp(p * 1.5))
    # "no reply" moment
    if t > 1.65:
        p = ease_back(prog(t, 1.65, 0.4))
        caption(f, "وما أحد يرد؟", t, 1.65, 1690, 112, grad=(WHITE, GRAY), out=3.1)
        # dim typing dots fading = nobody
        dots = Image.new("RGBA", (200, 60), (0, 0, 0, 0)); dr = ImageDraw.Draw(dots)
        for k in range(3):
            v = int(120 + 100 * math.sin(t * 6 + k))
            dr.ellipse((20 + k * 60, 15, 50 + k * 60, 45), fill=GRAY + (max(0, v - int(160 * prog(t, 1.7, 1.0))),))
        place(f, dots, W - 230, 1530, out)

def flash(f, t, at):
    p = prog(t, at - 0.08, 0.45)
    if 0 < p < 1:
        a = math.sin(p * math.pi) * 0.55
        fl = Image.new("RGBA", (W, H), CYAN + (int(255 * a * 0.5),))
        f.alpha_composite(fl)

def scene2(f, t):
    if t < 3.25 or t > 8.05: return
    out = 1 - prog(t, 7.75, 0.25)
    p = ease_back(prog(t, 3.3, 0.45))
    title = text_img("ويا بوت NEXO", AR, 112, grad=(BLUE, CYAN), glow=12)
    place(f, title, W / 2, 330, out * clamp(p * 1.4), 0.85 + 0.15 * p)
    # chat card with bot replies
    card = rounded(900, 760, 56, DNAVY, border=(0, 212, 255, 90))
    place(f, card, W / 2, 900, out * ease_out(prog(t, 3.3, 0.3)))
    q = bubble(CUST[0], True)
    place(f, q, 150 + q.width / 2 - 40, 640, out * ease_out(prog(t, 3.4, 0.3)))
    # typing dots then replies
    if 3.7 < t < 4.3:
        dots = Image.new("RGBA", (200, 70), (0, 0, 0, 0)); dr = ImageDraw.Draw(dots)
        for k in range(3):
            v = int(150 + 105 * math.sin(t * 14 + k * 1.2))
            dr.ellipse((25 + k * 55, 18, 60 + k * 55, 53), fill=CYAN + (v,))
        place(f, dots, W - 260, 820, out)
    for i, s in enumerate(BOT):
        st = 4.3 + i * 0.55
        if t < st: continue
        pp = ease_back(prog(t, st, 0.35))
        img = bubble(s, False)
        x = W - 150 - img.width / 2 + 40
        place(f, img, x + (1 - pp) * 120, 830 + i * 200, out * clamp(pp * 1.5))
    # check mark "replied in 1s"
    if t > 4.6:
        tag = text_img("رد خلال ثانية ✓", AR_REG, 40, CYAN)
        place(f, tag, W - 330, 1180, out * ease_out(prog(t, 4.9, 0.3)))
    caption(f, "الرد صار ذكي", t, 4.5, 1420, 104, out=5.85)
    # 24/7 + platforms
    if t > 5.85:
        pp = ease_back(prog(t, 5.95, 0.45))
        big = text_img("24/7", EN, 230, grad=(BLUE, CYAN, PURPLE), rtl=False, glow=16)
        place(f, big, W / 2, 1450, out * clamp(pp * 1.4), 0.7 + 0.3 * pp)
        caption(f, "أربعة وعشرين ساعة", t, 6.05, 1640, 70, out=7.75)
        for i, name in enumerate(["Messenger", "Instagram", "WhatsApp"]):
            st = 6.35 + i * 0.18
            q = ease_back(prog(t, st, 0.35))
            txt = text_img(name, EN_SB, 40, WHITE, rtl=False)
            pill = rounded(txt.width - 80 + 60, 78, 39, DNAVY, border=(0, 212, 255, 200), shadow=False).copy()
            pill.alpha_composite(txt, ((pill.width - txt.width) // 2, (pill.height - txt.height) // 2))
            place(f, pill, W / 2 + (i - 1) * 320, 1790 + (1 - q) * 40, out * clamp(q * 1.4))

def scene3(f, t):
    if t < 7.85: return
    p = ease_back(prog(t, 7.95, 0.6))
    # ring
    ring = Image.new("RGBA", (760, 760), (0, 0, 0, 0)); rd = ImageDraw.Draw(ring)
    rp = ease_out(prog(t, 7.9, 0.8))
    rd.arc((20, 20, 740, 740), -90, -90 + 360 * rp, fill=CYAN + (200,), width=6)
    rd.arc((60, 60, 700, 700), 90, 90 + 300 * rp, fill=PURPLE + (150,), width=3)
    ring = ring.rotate(-t * 25, resample=Image.BICUBIC)
    place(f, ring, W / 2, 780, clamp(rp * 1.5))
    place(f, logo_mark(250), W / 2, 780, clamp(p * 1.4), 0.6 + 0.4 * p)
    tl = text_img("Connect to the Future.", EN_SB, 62, rtl=False, grad=(WHITE, CYAN))
    q = ease_out(prog(t, 8.95, 0.45))
    place(f, tl, W / 2, 1230 + (1 - q) * 40, q)
    # CTA
    c = ease_back(prog(t, 9.35, 0.45))
    btn = rounded(640, 130, 65, BLUE, grad=(BLUE, (0, 160, 255))).copy()
    bt = text_img("راسلنا هسه", AR, 66, WHITE)
    btn.alpha_composite(bt, ((btn.width - bt.width) // 2, (btn.height - bt.height) // 2))
    pulse = 1 + 0.03 * math.sin(t * 8) * prog(t, 9.8, 0.2)
    place(f, btn, W / 2, 1460, clamp(c * 1.4), (0.8 + 0.2 * c) * pulse)
    d = ease_out(prog(t, 9.6, 0.4))
    place(f, text_img("WhatsApp  07751027553", EN_SB, 48, WHITE, rtl=False), W / 2, 1630, d)
    place(f, text_img("nexodeveloper.net", EN_SB, 44, CYAN, rtl=False), W / 2, 1710, d)

def progress_bar(f, t):
    w = int(W * clamp(t / DUR))
    bar = gradient(max(w, 1), 8, BLUE, CYAN).convert("RGBA")
    f.alpha_composite(bar, (0, H - 8))

def frame(i):
    t = i / FPS
    f = background(t)
    scene1(f, t); scene2(f, t); scene3(f, t)
    flash(f, t, 3.3); flash(f, t, 7.95)
    progress_bar(f, t)
    return f.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]:
            frame(int(float(ts) * FPS)).save(f"preview_{ts}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "18", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
