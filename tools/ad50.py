import sys, math, random, subprocess
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from style_ad import (background, brackets, word_img, blurred, chat_icon, badge, site_card, bot_icon, bot_eyes,
                      gradient, text_img, rounded, place, ease_out, ease_back, prog, clamp,
                      NAVY, DNAVY, BLUE, CYAN, PURPLE, WHITE, GRAY, AR, EN, EN_SB, W, H, FPS)

DUR = 49.5
N = int(DUR * FPS)
CX, CY = W // 2, 860
TY = 1390

# ---------- captions: (start, end, [(word, accent)]) ----------
def L(s, e, text, acc=()):
    ws = text.split()
    return (s, e, [(w, (i in acc)) for i, w in enumerate(ws)])

LINES = [
    L(1.11, 2.55, "كم زبون ضيّعت اليوم…", (1,)),
    L(2.70, 4.6, "وإنت ما تدري؟", (1, 2)),
    L(4.90, 6.3, "زبون يسأل عن السعر", (3,)),
    L(6.39, 7.95, "الساعة ثنتين بالليل…", (1,)),
    L(8.05, 9.05, "محد يرد.", (0, 1)),
    L(9.16, 9.98, "والصبح؟", ()),
    L(10.11, 12.3, "اشترى من غيرك.", (0, 2)),
    L(12.66, 13.9, "هنا يجي دور", ()),
    L(13.95, 15.85, "موظف المبيعات الذكي", (0, 1, 2)),
    L(15.95, 16.9, "يرد بثانية", (1,)),
    L(16.97, 19.7, "ماسنجر · إنستغرام · واتساب", ()),
    L(19.81, 21.0, "يجاوب على الأسئلة", (0,)),
    L(21.11, 22.25, "يعرض منتجاتك", (0,)),
    L(22.34, 23.5, "ويثبّت الطلب", (0, 1)),
    L(23.58, 25.4, "وإنت نايم", (1,)),
    L(25.84, 27.1, "وإذا ما عندك موقع؟", (3,)),
    L(27.21, 29.15, "موقع احترافي وسريع", (1, 2)),
    L(29.23, 31.9, "يخلّي الزبون يثق بيك", (3,)),
    L(32.90, 34.1, "ثلاث خطوات بس", (0, 1)),
]
WORD_T = []
for s, e, ws in LINES:
    speak_end = min(e, s + 0.75 * (e - s) + 0.3)
    total = sum(len(w) for w, _ in ws)
    acc_t = s
    out = []
    for w, a in ws:
        out.append((w, a, acc_t))
        acc_t += (speak_end - s) * len(w) / total
    WORD_T.append((s, e, out))

def captions(f, t, y=TY, size_scale=1.0):
    for s, e, ws in WORD_T:
        if t < s - 0.01 or t > e + 0.25: continue
        out = 1 - prog(t, e, 0.22)
        imgs = [word_img(w, a) for w, a, _ in ws]
        gap = -40
        total = sum(im.width for im in imgs) + gap * (len(imgs) - 1)
        sc = min(1.0, 980 / max(total, 1))
        x = W / 2 + total * sc / 2
        for (w, a, st), im in zip(ws, imgs):
            if t >= st:
                p = ease_out(prog(t, st, 0.26))
                b = int(round((1 - p) * 8))
                place(f, blurred(w, a, b), x - im.width * sc / 2, y + (1 - p) * 26, p * out, sc * (1.08 - 0.08 * p))
            x -= (im.width + gap) * sc

def overlay(f):
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); return lay, ImageDraw.Draw(lay)

def pill(txt, size=44, border=(0, 212, 255, 220), fill=DNAVY, font=AR, rtl=True, col=WHITE):
    tx = text_img(txt, font, size, col, rtl=rtl)
    p = rounded(tx.width - 80 + 70, size + 50, (size + 50) // 2, fill, border=border, shadow=False).copy()
    p.alpha_composite(tx, ((p.width - tx.width) // 2, (p.height - tx.height) // 2))
    return p

# ---------- A. HOOK 0 - 4.6 ----------
random.seed(3)
def _pos(i):
    zone = i % 4
    if zone == 0: return random.uniform(140, 940), random.uniform(250, 520)
    if zone == 1: return random.uniform(140, 940), random.uniform(1560, 1780)
    if zone == 2: return random.uniform(110, 230), random.uniform(560, 1220)
    return random.uniform(850, 970), random.uniform(560, 1220)
POPS = [(*_pos(i), random.uniform(0.28, 0.45), 1.0 + i * 0.1) for i in range(14)]

def scene_hook(f, t):
    if t > 4.75: return
    out = 1 - prog(t, 4.45, 0.3)
    # "وگف!" slam
    if t < 1.2:
        p = ease_out(prog(t, 0.0, 0.18))
        sc = 2.4 - 1.4 * p
        a = clamp(p * 2) * (1 - prog(t, 0.95, 0.25))
        shake = (1 - prog(t, 0.05, 0.5)) * 22
        dx = math.sin(t * 90) * shake; dy = math.cos(t * 77) * shake
        img = text_img("وگف!", AR, 260, WHITE, glow=18)
        place(f, img, CX + dx, CY + 40 + dy, a, sc)
        # stop sign frame
        brackets(f, CX + dx, CY + 40 + dy, 720, 0.05, t, out=1 - prog(t, 0.95, 0.25))
        if t < 0.12:
            lay, d = overlay(f); d.rectangle((0, 0, W, H), fill=CYAN + (int(140 * (1 - t / 0.12)),)); f.alpha_composite(lay)
        # glitch bars
        if 0.05 < t < 0.4:
            lay, d = overlay(f)
            for k in range(6):
                y = random.Random(int(t * 60) + k).randint(300, 1500)
                d.rectangle((0, y, W, y + random.Random(k).randint(4, 14)), fill=CYAN + (90,))
            f.alpha_composite(lay)
    # bubbles popping everywhere + counter
    if t > 0.95:
        for x, y, sc, st in POPS:
            q = ease_back(prog(t, st, 0.25))
            if q <= 0.01: continue
            place(f, chat_icon(), x, y, clamp(q * 1.5) * out * 0.9, sc * q)
        cnt = int(clamp((t - 1.0) / 2.2) * 27)
        p = ease_back(prog(t, 1.0, 0.35))
        num = text_img(str(cnt), EN, 260, CYAN, rtl=False, glow=14)
        place(f, num, CX, CY - 20, clamp(p * 1.5) * out, 0.7 + 0.3 * p)
        lab = text_img("رسالة بدون رد", AR, 56, WHITE)
        place(f, lab, CX, CY + 150, ease_out(prog(t, 1.2, 0.3)) * out)
        captions(f, t)

# ---------- B. PROBLEM 4.9 - 12.3 ----------
def phone(w=600, h=900):
    return rounded(w, h, 70, DNAVY, border=(0, 212, 255, 110))

def scene_problem(f, t):
    if t < 4.6 or t > 12.5: return
    pin = ease_out(prog(t, 4.7, 0.4)); out = 1 - prog(t, 12.1, 0.3)
    a = pin * out
    ph = phone()
    place(f, ph, CX, CY + (1 - pin) * 200, a)
    top = CY - 450 + 40 + (1 - pin) * 200
    # clock in phone header
    night = t < 9.3
    clock = "2:00 AM" if night else "9:00 AM"
    if 9.1 < t < 9.5:  # fast-forward roll
        hh = 2 + int((t - 9.1) / 0.4 * 7); clock = f"{hh}:00 AM"
    place(f, text_img(clock, EN_SB, 46, GRAY, rtl=False), CX + 180, top + 30, a)
    # moon / sun
    lay, d = overlay(f)
    ix, iy = CX - 200, top + 30
    if night:
        d.ellipse((ix - 26, iy - 26, ix + 26, iy + 26), fill=WHITE + (int(230 * a),))
        d.ellipse((ix - 12, iy - 34, ix + 36, iy + 14), fill=DNAVY + (int(255 * a),))
    else:
        d.ellipse((ix - 22, iy - 22, ix + 22, iy + 22), fill=CYAN + (int(255 * a),))
        for k in range(8):
            ang = k * math.pi / 4
            d.line((ix + 32 * math.cos(ang), iy + 32 * math.sin(ang), ix + 44 * math.cos(ang), iy + 44 * math.sin(ang)), fill=CYAN + (int(255 * a),), width=5)
    f.alpha_composite(lay)
    # customer bubble
    q = ease_back(prog(t, 5.2, 0.35))
    if q > 0.01:
        b = pill("السلام عليكم، شكد السعر؟", 42, border=(169, 184, 204, 120))
        place(f, b, CX - 270 + b.width / 2, top + 170, clamp(q * 1.5) * a, 0.8 + 0.2 * q)
        place(f, text_img("✓✓ شوهدت", AR, 32, GRAY), CX - 270 + 100, top + 250, ease_out(prog(t, 7.9, 0.3)) * a)
    # nobody replies: empty dots that die
    if 6.5 < t < 9.2:
        lay, d = overlay(f)
        for k in range(3):
            v = (0.5 + 0.5 * math.sin(t * 7 + k)) * (1 - prog(t, 8.0, 0.8))
            x = CX + 150 + k * 50
            d.ellipse((x - 14, top + 380 - 14, x + 14, top + 380 + 14), fill=GRAY + (int(200 * v * a),))
        f.alpha_composite(lay)
    # morning: customer leaves
    if t > 10.0:
        q2 = ease_back(prog(t, 10.1, 0.35))
        b2 = pill("خلاص… اشتريت من محل ثاني", 42, border=(169, 184, 204, 120))
        place(f, b2, CX - 270 + b2.width / 2, top + 330, clamp(q2 * 1.5) * a, 0.8 + 0.2 * q2)
    brackets(f, CX, CY, 720, 8.05, t, out=out * (1 - prog(t, 9.1, 0.2)))

# ---------- C. BOT 12.6 - 25.5 ----------
def platform_icon(kind, s=170):
    im = Image.new("RGBA", (s + 40, s + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im); o = 20
    g = gradient(s, s, *{"m": (BLUE, PURPLE), "i": (PURPLE, CYAN), "w": (BLUE, CYAN)}[kind]).convert("RGBA")
    m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, s, s), 44, fill=255)
    im.paste(g, (o, o), m)
    c = o + s / 2
    if kind == "m":   # bubble with zigzag
        d.ellipse((c - 52, c - 48, c + 52, c + 44), fill=WHITE + (255,))
        d.polygon([(c - 30, c + 30), (c - 40, c + 62), (c - 5, c + 38)], fill=WHITE + (255,))
        d.line([(c - 32, c + 8), (c - 10, c - 14), (c + 8, c + 4), (c + 32, c - 18)], fill=BLUE + (255,), width=9)
    elif kind == "i":  # camera
        d.rounded_rectangle((c - 50, c - 50, c + 50, c + 50), 28, outline=WHITE + (255,), width=10)
        d.ellipse((c - 24, c - 24, c + 24, c + 24), outline=WHITE + (255,), width=10)
        d.ellipse((c + 26, c - 38, c + 38, c - 26), fill=WHITE + (255,))
    else:              # phone in bubble
        d.ellipse((c - 52, c - 52, c + 52, c + 52), outline=WHITE + (255,), width=10)
        d.polygon([(c - 44, c + 30), (c - 56, c + 58), (c - 24, c + 46)], fill=WHITE + (255,))
        d.rounded_rectangle((c - 20, c - 26, c + 20, c + 26), 10, fill=WHITE + (255,))
    return im

PLAT = {k: platform_icon(k) for k in "miw"}

def scene_bot(f, t):
    if t < 12.4 or t > 25.7: return
    out = 1 - prog(t, 25.3, 0.3)
    # 12.66-15.9: bot hero
    if t < 16.1:
        p = ease_back(prog(t, 12.7, 0.5)); o2 = 1 - prog(t, 15.8, 0.25)
        sc = 0.55 + 0.45 * p; a = clamp(p * 1.5) * o2
        place(f, bot_icon(), CX, CY, a, sc * 1.1)
        bot_eyes(f, CX, CY, sc * 1.1, t, a)
        brackets(f, CX, CY, 680, 13.95, t, out=o2)
        # sparkle ring
        lay, d = overlay(f)
        for k in range(12):
            ang = k * math.pi / 6 + t * 1.2
            r = 400 * p
            x, y = CX + r * math.cos(ang), CY + r * math.sin(ang)
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=CYAN + (int(200 * a),))
        f.alpha_composite(lay)
    # 15.95-19.7: timer 00:01 + platforms
    if 15.8 < t < 19.9:
        p = ease_back(prog(t, 15.95, 0.4)); o2 = 1 - prog(t, 19.6, 0.25)
        a = clamp(p * 1.5) * o2
        secs = "00:01"
        place(f, text_img(secs, EN, 230, CYAN, rtl=False, glow=12), CX, CY - 160, a, 0.7 + 0.3 * p)
        x0, x1, y = 170, 910, CY + 30
        lay, d = overlay(f)
        for k in range(0, 49):
            x = x0 + (x1 - x0) * k / 48; hgt = 34 if k % 6 == 0 else 16
            d.line((x, y - hgt, x, y), fill=GRAY + (int(130 * a),), width=3)
        fill = ease_out(prog(t, 16.0, 0.7)); xe = x1 - (x1 - x0) * fill
        d.line((xe, y + 14, x1, y + 14), fill=CYAN + (int(255 * a),), width=8)
        d.ellipse((xe - 14, y, xe + 14, y + 28), fill=CYAN + (int(255 * a),))
        f.alpha_composite(lay)
        for i, (k, st) in enumerate([("m", 17.0), ("i", 17.75), ("w", 18.6)]):
            q = ease_back(prog(t, st, 0.35))
            if q > 0.01:
                place(f, PLAT[k], CX + (1 - i) * 260, CY + 290 + (1 - q) * 60, clamp(q * 1.5) * o2, 0.7 + 0.3 * q)
    # 19.81-23.5: live chat demo
    if 19.6 < t < 23.7:
        pin = ease_out(prog(t, 19.7, 0.35)); o2 = 1 - prog(t, 23.45, 0.25); a = pin * o2
        place(f, phone(640, 860), CX, CY + (1 - pin) * 150, a)
        top = CY - 430 + 60
        msgs = [
            (19.85, False, "عندكم توصيل؟"),
            (20.25, True, "إي نعم، نوصل لكل المحافظات"),
            (21.15, True, "هذني أكثر المنتجات طلباً:"),
            (22.4, True, "تم تثبيت طلبك ✓"),
        ]
        yy = top + 60
        for st, bot, txt in msgs:
            q = ease_back(prog(t, st, 0.3))
            if q > 0.01:
                if bot:
                    b = text_img(txt, AR, 38, WHITE)
                    bb = rounded(b.width - 80 + 60, 88, 44, BLUE, grad=(BLUE, (0, 150, 255)), shadow=False).copy()
                    bb.alpha_composite(b, ((bb.width - b.width) // 2, (bb.height - b.height) // 2))
                    place(f, bb, CX + 280 - bb.width / 2 + 20, yy + 40, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
                else:
                    bb = pill(txt, 38, border=(169, 184, 204, 120))
                    place(f, bb, CX - 280 + bb.width / 2 - 20, yy + 40, clamp(q * 1.5) * a, 0.85 + 0.15 * q)
            yy += 120
            if txt.startswith("هذني") and t > 21.4:
                # mini product cards
                for k in range(3):
                    qq = ease_back(prog(t, 21.45 + k * 0.15, 0.3))
                    cx = CX + 200 - k * 190; cy = yy + 70
                    card = rounded(160, 150, 26, DNAVY, border=(0, 212, 255, 160), shadow=False).copy()
                    g = gradient(130, 80, *[(BLUE, CYAN), (BLUE, PURPLE), (CYAN, PURPLE)][k]).convert("RGBA")
                    mm = Image.new("L", g.size, 0); ImageDraw.Draw(mm).rounded_rectangle((0, 0, 130, 80), 16, fill=255)
                    card.paste(g, (55, 55), mm)
                    ImageDraw.Draw(card).rounded_rectangle((60, 148, 150, 162), 7, fill=(169, 184, 204, 120))
                    place(f, card, cx, cy, clamp(qq * 1.5) * a, 0.8 + 0.2 * qq)
                yy += 170
    # 23.58-25.5: while you sleep
    if t > 23.4:
        p = ease_back(prog(t, 23.55, 0.45)); a = clamp(p * 1.5) * out
        lay, d = overlay(f)
        r = 150 * (0.7 + 0.3 * p)
        d.ellipse((CX - r, CY - r, CX + r, CY + r), fill=WHITE + (int(240 * a),))
        d.ellipse((CX - r * 0.45, CY - r * 1.25, CX + r * 1.45, CY + r * 0.6), fill=NAVY + (int(255 * a),))
        f.alpha_composite(lay)
        for k in range(3):
            z = (t - 23.7 - k * 0.3) % 1.5
            if t > 23.7 + k * 0.3:
                place(f, text_img("z", EN, 70 + k * 20, CYAN, rtl=False), CX + 150 + k * 60 + z * 30, CY - 130 - k * 70 - z * 60, a * (1 - z / 1.5))
        # orders ticking up while asleep
        n = int(clamp((t - 23.8) / 1.4) * 12)
        place(f, pill(f"طلبات جديدة: {n}", 46), CX, CY + 290, ease_out(prog(t, 23.9, 0.3)) * out)
    captions(f, t)

# ---------- D. WEBSITE 25.84 - 32 ----------
def scene_site(f, t):
    if t < 25.6 or t > 32.2: return
    out = 1 - prog(t, 31.85, 0.3)
    # question: empty browser with "?"
    if t < 27.3:
        p = ease_back(prog(t, 25.85, 0.4)); o2 = 1 - prog(t, 27.15, 0.2)
        frame_ = rounded(560, 420, 40, DNAVY, border=(169, 184, 204, 140)).copy()
        dd = ImageDraw.Draw(frame_)
        dd.rounded_rectangle((64, 64, 536, 110), 23, fill=(14, 32, 62, 255))
        q = text_img("؟", AR, 200, GRAY)
        frame_.alpha_composite(q, ((frame_.width - q.width) // 2, 140))
        place(f, frame_, CX, CY, clamp(p * 1.5) * o2, 0.7 + 0.3 * p)
    # build: cards slide up + loading bar fast
    if 27.1 < t < 29.4:
        starts = [27.2, 27.9, 28.55]
        for i, st in enumerate(starts):
            p = ease_out(prog(t, st, 0.4)); nx = starts[i + 1] if i < 2 else 99
            q = ease_out(prog(t, nx, 0.4))
            if p > 0.01:
                place(f, site_card(i), CX, CY + (1 - p) * 900 - q * 900, clamp(p * 2) * (1 - q) * (1 - prog(t, 29.2, 0.2)), 0.82)
        # speed bar "سريع"
        lay, d = overlay(f)
        pr = ease_out(prog(t, 28.2, 0.5)); a = ease_out(prog(t, 28.1, 0.2)) * (1 - prog(t, 29.2, 0.2))
        d.rounded_rectangle((240, CY + 400, 840, CY + 424), 12, fill=(169, 184, 204, int(60 * a)))
        d.rounded_rectangle((840 - 600 * pr, CY + 400, 840, CY + 424), 12, fill=CYAN + (int(255 * a),))
        f.alpha_composite(lay)
        place(f, text_img("0.8s", EN_SB, 44, CYAN, rtl=False), 180, CY + 412, a)
    # trust: card + shield check
    if t > 29.2:
        p = ease_back(prog(t, 29.25, 0.45)); a = clamp(p * 1.5) * out
        place(f, site_card(1), CX - 60, CY, a, 0.78)
        lay, d = overlay(f)
        sx, sy, s = CX + 230, CY + 230, 120 * (0.6 + 0.4 * p)
        pts = [(sx, sy - s), (sx + s * 0.85, sy - s * 0.6), (sx + s * 0.7, sy + s * 0.5), (sx, sy + s), (sx - s * 0.7, sy + s * 0.5), (sx - s * 0.85, sy - s * 0.6)]
        d.polygon(pts, fill=BLUE + (int(255 * a),), outline=CYAN + (int(255 * a),))
        d.line([(sx - s * 0.35, sy), (sx - s * 0.05, sy + s * 0.3), (sx + s * 0.4, sy - s * 0.3)], fill=WHITE + (int(255 * a),), width=16)
        f.alpha_composite(lay)
        # stars of trust (decorative, no numbers)
        for k in range(5):
            q = ease_back(prog(t, 29.9 + k * 0.1, 0.3))
            if q > 0.01:
                place(f, text_img("★", AR_STAR, 70, CYAN, rtl=False), CX - 240 + k * 90, CY - 420, clamp(q * 1.5) * out, q)
    captions(f, t)

AR_STAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ---------- E. STEPS 32.9 - 38.9 ----------
def step_card(n, title, icon):
    c = rounded(860, 210, 40, DNAVY, border=(0, 212, 255, 150)).copy()
    d = ImageDraw.Draw(c)
    g = gradient(130, 130, BLUE, CYAN).convert("RGBA")
    m = Image.new("L", (130, 130), 0); ImageDraw.Draw(m).ellipse((0, 0, 130, 130), fill=255)
    c.paste(g, (c.width - 40 - 40 - 130, 80 - 40 + 40 + 0), m)
    num = text_img(str(n), EN, 76, WHITE, rtl=False)
    c.alpha_composite(num, (c.width - 80 - 65 - num.width // 2, 145 - num.height // 2))
    size = 56
    tt = text_img(title, AR, size, WHITE)
    while tt.width - 80 > 470 and size > 36:
        size -= 2; tt = text_img(title, AR, size, WHITE)
    c.alpha_composite(tt, (c.width - 80 - 130 - 30 - tt.width + 40, 145 - tt.height // 2))
    ic = icon.resize((110, 110), Image.LANCZOS)
    c.alpha_composite(ic, (90, 145 - 55))
    return c

def gear_icon():
    s = 200; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s / 2
    for k in range(8):
        ang = k * math.pi / 4
        d.line((c + 50 * math.cos(ang), c + 50 * math.sin(ang), c + 85 * math.cos(ang), c + 85 * math.sin(ang)), fill=CYAN + (255,), width=30)
    d.ellipse((c - 62, c - 62, c + 62, c + 62), fill=CYAN + (255,)); d.ellipse((c - 26, c - 26, c + 26, c + 26), fill=DNAVY + (255,))
    return im

def cart_icon():
    s = 200; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(20, 40), (55, 40), (80, 140), (165, 140), (180, 70), (65, 70)], fill=CYAN + (255,), width=16, joint="curve")
    d.ellipse((75, 152, 105, 182), fill=CYAN + (255,)); d.ellipse((140, 152, 170, 182), fill=CYAN + (255,))
    return im

STEPS = None
def scene_steps(f, t):
    global STEPS
    if t < 32.6 or t > 39.3: return
    if STEPS is None:
        ci = chat_icon().resize((200, 200), Image.LANCZOS)
        STEPS = [step_card(1, "تراسلنا", ci), step_card(2, "نجهّز موقعك والبوت", gear_icon()), step_card(3, "تستلم طلبات", cart_icon())]
    out = 1 - prog(t, 38.95, 0.3)
    title = text_img("ثلاث خطوات بس", AR, 96, CYAN, glow=10)
    tp = ease_back(prog(t, 32.9, 0.4))
    place(f, title, CX, 420, clamp(tp * 1.5) * out, 0.8 + 0.2 * tp)
    for i, st in enumerate([34.15, 35.1, 36.9]):
        q = ease_back(prog(t, st, 0.4))
        if q > 0.01:
            place(f, STEPS[i], CX + (1 - q) * 500, 720 + i * 270, clamp(q * 1.5) * out)
    # progress connector
    lay, d = overlay(f)
    pr = ease_out(prog(t, 34.2, 3.2)); a = int(200 * out)
    d.line((W - 175, 720, W - 175, 720 + 540 * pr), fill=CYAN + (a,), width=6)
    f.alpha_composite(lay)

# ---------- F. OUTRO 39.7 - 49.5 ----------
def scene_outro(f, t):
    if t < 39.6: return
    p = ease_out(prog(t, 39.85, 0.55))
    logo = text_img("NEXO", EN, 260, WHITE, rtl=False)
    if p < 1:
        logo = logo.copy(); m = Image.new("L", logo.size, 0)
        ImageDraw.Draw(m).rectangle((int(logo.width * (1 - p)), 0, logo.width, logo.height), fill=255)
        logo.putalpha(Image.composite(logo.getchannel("A"), Image.new("L", logo.size, 0), m))
    place(f, logo, CX, 640, clamp(p * 2))
    place(f, text_img("نيكسو", AR, 56, WHITE), CX + 260, 780, ease_out(prog(t, 40.1, 0.35)))
    q = ease_out(prog(t, 40.3, 0.4))
    if q > 0.01:
        lay, d = overlay(f); half = 160 * q
        d.line((CX - half, 870, CX + half, 870), fill=CYAN + (int(255 * q),), width=5); f.alpha_composite(lay)
    # slogan word by word
    words = [("خلّي", False, 40.7), ("شغلك", True, 41.0), ("يشتغل", False, 41.4), ("حتى", False, 41.85), ("وإنت", False, 42.1), ("نايم", True, 42.4)]
    line1, line2 = words[:3], words[3:]
    for row, ws in enumerate([line1, line2]):
        imgs = [word_img(w, a) for w, a, _ in ws]
        gap = -40; total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
        x = W / 2 + total / 2
        for (w, a, st), im in zip(ws, imgs):
            r = ease_out(prog(t, st, 0.26))
            if r > 0.01:
                place(f, blurred(w, a, int(round((1 - r) * 8))), x - im.width / 2, 1010 + row * 130 + (1 - r) * 24, r)
            x -= im.width + gap
    # CTA
    c = ease_back(prog(t, 43.15, 0.45))
    if c > 0.01:
        btn = rounded(640, 140, 70, BLUE, grad=(BLUE, (0, 160, 255))).copy()
        bt = text_img("راسلنا هسه", AR, 70, WHITE)
        btn.alpha_composite(bt, ((btn.width - bt.width) // 2, (btn.height - bt.height) // 2))
        pulse = 1 + 0.035 * math.sin(t * 6) * prog(t, 43.7, 0.3)
        place(f, btn, CX, 1380, clamp(c * 1.4), (0.8 + 0.2 * c) * pulse)
        # tap hint ring
        if t > 44.0:
            z = ((t - 44.0) % 1.4) / 1.4
            lay, d = overlay(f); r = 80 + 120 * z
            d.ellipse((CX + 200 - r, 1380 - r, CX + 200 + r, 1380 + r), outline=CYAN + (int(200 * (1 - z)),), width=5); f.alpha_composite(lay)
    dd = ease_out(prog(t, 43.7, 0.4))
    place(f, text_img("WhatsApp  07751027553", EN_SB, 50, WHITE, rtl=False), CX, 1570, dd)
    place(f, text_img("nexodeveloper.net", EN_SB, 46, CYAN, rtl=False), CX, 1650, dd)
    place(f, text_img("Connect to the Future.", EN_SB, 40, GRAY, rtl=False), CX, 1760, ease_out(prog(t, 44.3, 0.5)))

def progress(f, t):
    w = int(W * clamp(t / DUR))
    if w > 0: f.alpha_composite(gradient(w, 8, BLUE, CYAN).convert("RGBA"), (0, H - 8))

def frame(i):
    t = i / FPS
    f = background(t)
    scene_hook(f, t); scene_problem(f, t); scene_bot(f, t); scene_site(f, t); scene_steps(f, t); scene_outro(f, t)
    if 4.6 < t < 12.5: captions(f, t)
    progress(f, t)
    return f.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]:
            frame(int(float(ts) * FPS)).save(f"q_{ts}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "19", "-pix_fmt", "yuv420p", "ad50.mp4"], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
