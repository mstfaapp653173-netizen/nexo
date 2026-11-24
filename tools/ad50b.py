import sys, math, subprocess
from PIL import Image, ImageDraw
import ad50
from ad50 import *   # scenes, helpers
from style_ad import background, brackets, bot_icon

SHIFT = 1.0
HOOK_END = 5.75
DUR2 = 50.5
N2 = int(DUR2 * FPS)

HOOK_LINES = [
    L(0.05, 1.4, "هلا بيك…", (0, 1)),
    L(1.50, 2.85, "عندي سؤال صغير", (1, 2)),
    L(2.98, 4.55, "منو يرد على زبائنك", (3,)),
    L(4.63, 5.6, "من تكون نايم؟", (2,)),
]
def timed(lines):
    out = []
    for s, e, ws in lines:
        speak_end = min(e, s + 0.75 * (e - s) + 0.3)
        total = sum(len(w) for w, _ in ws); acc = s; row = []
        for w, a in ws:
            row.append((w, a, acc)); acc += (speak_end - s) * len(w) / total
        out.append((s, e, row))
    return out
HOOK_T = timed(HOOK_LINES)

def hook_captions(f, t):
    saved = ad50.WORD_T
    ad50.WORD_T = HOOK_T
    ad50.captions(f, t)
    ad50.WORD_T = saved

def happy_bot(f, t, a, sc):
    # friendly bot: smiling eyes, smile, waving hand
    place(f, bot_icon(), CX, CY, a, sc)
    lay, d = overlay(f)
    col = CYAN + (int(255 * a),)
    for sx in (-1, 1):   # happy ^ ^ eyes
        ex, ey = CX + sx * 70 * sc, CY + 40 * sc
        d.arc((ex - 32 * sc, ey - 26 * sc, ex + 32 * sc, ey + 30 * sc), 200, 340, fill=col, width=int(12 * sc))
    d.arc((CX - 48 * sc, CY + 50 * sc, CX + 48 * sc, CY + 110 * sc), 20, 160, fill=col, width=int(10 * sc))
    # waving hand
    ang = math.sin(t * 9) * 0.45
    hx0, hy0 = CX + 240 * sc, CY + 40 * sc
    hx, hy = hx0 + math.sin(ang) * 120 * sc, hy0 - math.cos(ang) * 120 * sc
    d.line((hx0, hy0, hx, hy), fill=WHITE + (int(255 * a),), width=int(26 * sc))
    d.ellipse((hx - 42 * sc, hy - 42 * sc, hx + 42 * sc, hy + 42 * sc), fill=WHITE + (int(255 * a),))
    f.alpha_composite(lay)

def sparkles(f, t, a):
    lay, d = overlay(f)
    for k in range(14):
        ph = (t * 0.35 + k * 0.071) % 1
        x = CX + math.sin(k * 2.3) * 380 + math.sin(t + k) * 20
        y = CY + 380 - ph * 760
        r = 5 + 4 * math.sin(k)
        al = int(200 * a * math.sin(ph * math.pi))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(CYAN if k % 2 else BLUE) + (al,))
    f.alpha_composite(lay)

def scene_hook_friendly(f, t):
    out = 1 - prog(t, 5.45, 0.3)
    sparkles(f, t, out)
    # bot greets (0 - 2.9)
    if t < 3.1:
        p = ease_back(prog(t, 0.0, 0.6)); o2 = 1 - prog(t, 2.8, 0.3)
        happy_bot(f, t, clamp(p * 1.4) * o2, (0.55 + 0.45 * p) * (1 + 0.03 * math.sin(t * 4)))
        # greeting bubble
        q = ease_back(prog(t, 0.15, 0.45))
        if q > 0.01:
            b = text_img("هلا بيك", AR, 54, WHITE)
            bb = rounded(b.width - 80 + 70, 104, 52, BLUE, grad=(BLUE, (0, 160, 255)), shadow=False).copy()
            bb.alpha_composite(b, ((bb.width - b.width) // 2, (bb.height - b.height) // 2))
            place(f, bb, CX - 230, CY - 330 + (1 - q) * 30, clamp(q * 1.5) * o2, 0.8 + 0.2 * q)
        # small question bubble
        q2 = ease_back(prog(t, 1.55, 0.4))
        if q2 > 0.01:
            qb = rounded(150, 150, 75, DNAVY, border=(0, 212, 255, 220), shadow=False).copy()
            qi = text_img("؟", AR, 100, CYAN)
            qb.alpha_composite(qi, ((qb.width - qi.width) // 2, (qb.height - qi.height) // 2))
            place(f, qb, CX + 250, CY - 300 + math.sin(t * 3) * 10, clamp(q2 * 1.5) * o2, 0.7 + 0.3 * q2)
    # night scene with gentle moon + stars + phone glow (2.9 - 5.75)
    if t > 2.8:
        p = ease_back(prog(t, 2.95, 0.6)); a = clamp(p * 1.4) * out
        lay, d = overlay(f)
        r = 170 * (0.7 + 0.3 * p)
        d.ellipse((CX - r, CY - 60 - r, CX + r, CY - 60 + r), fill=WHITE + (int(235 * a),))
        d.ellipse((CX - r * 0.45, CY - 60 - r * 1.25, CX + r * 1.45, CY - 60 + r * 0.6), fill=NAVY + (int(255 * a),))
        for k in range(9):
            x = CX + math.cos(k * 1.9) * 360; y = CY - 60 + math.sin(k * 2.7) * 330
            tw = 0.5 + 0.5 * math.sin(t * 4 + k)
            s = 7 + 5 * tw
            d.polygon([(x, y - s * 2), (x + s * 0.5, y - s * 0.5), (x + s * 2, y), (x + s * 0.5, y + s * 0.5), (x, y + s * 2), (x - s * 0.5, y + s * 0.5), (x - s * 2, y), (x - s * 0.5, y - s * 0.5)], fill=CYAN + (int(220 * a * tw),))
        f.alpha_composite(lay)
        # incoming message notifications softly stacking
        for i, st in enumerate([3.4, 3.9, 4.4]):
            q = ease_back(prog(t, st, 0.4))
            if q > 0.01:
                b = pill(["رسالة جديدة", "زبون يسأل…", "رسالة جديدة"][i], 40, border=(169, 184, 204, 140))
                place(f, b, CX + (i - 1) * 40, CY + 190 + i * 80, clamp(q * 1.5) * out, 0.85 + 0.15 * q)
    hook_captions(f, t)

def frame2(i):
    t = i / FPS
    f = background(t)
    if t < HOOK_END:
        scene_hook_friendly(f, t)
    else:
        to = t - SHIFT
        scene_problem(f, to); scene_bot(f, to); scene_site(f, to); scene_steps(f, to); scene_outro(f, to)
        if 4.6 < to < 12.5: captions(f, to)
    w = int(W * clamp(t / DUR2))
    if w > 0: f.alpha_composite(gradient(w, 8, BLUE, CYAN).convert("RGBA"), (0, H - 8))
    return f.convert("RGB")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for ts in sys.argv[1:]:
            frame2(int(float(ts) * FPS)).save(f"r_{ts}.png")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "19", "-pix_fmt", "yuv420p", "ad50b.mp4"], stdin=subprocess.PIPE)
    for i in range(N2):
        p.stdin.write(frame2(i).tobytes())
    p.stdin.close(); p.wait()
