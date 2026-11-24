"""Simple, light tech background beat (original), 100 BPM, A minor: Am - F - C - G."""
import numpy as np, sys, wave

SR = 44100
BPM = 100
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 52.0
OUT = sys.argv[2] if len(sys.argv) > 2 else "music.wav"
beat = 60 / BPM
n = int(SR * DUR)
t = np.arange(n) / SR
mix = np.zeros(n)

def note(f):  # midi -> Hz
    return 440 * 2 ** ((f - 69) / 12)

def add(sig, start):
    i = int(start * SR)
    if i >= n: return
    e = min(n, i + len(sig))
    mix[i:e] += sig[: e - i]

def env(length, a=0.005, d=0.3, s=0.0, r=0.0):
    m = int(length * SR); x = np.arange(m) / SR
    y = np.minimum(1, x / max(a, 1e-4)) * (s + (1 - s) * np.exp(-x / max(d, 1e-4)))
    if r: y *= np.clip((length - x) / r, 0, 1)
    return y

def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y

chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
bass_roots = [45, 41, 36, 43]
bar = beat * 4
rng = np.random.default_rng(7)

# pad: soft detuned saw, filtered, one chord per bar (precompute 4 chord tones)
pad_cache = {}
for ci, ch in enumerate(chords):
    L = bar; m = int(L * SR); x = np.arange(m) / SR
    s = np.zeros(m)
    for p in ch:
        for det in (-0.12, 0.12):
            f = note(p + 12) * 2 ** (det / 12)
            s += 2 * ((x * f) % 1) - 1
    s = lowpass(s / 6, 1200) * env(L, a=0.4, d=10, s=1, r=0.4)
    pad_cache[ci] = s * 0.10

# pluck arpeggio
def pluck(f, L=0.35):
    m = int(L * SR); x = np.arange(m) / SR
    s = np.sin(2 * np.pi * f * x) + 0.4 * np.sin(4 * np.pi * f * x)
    return s * env(L, a=0.002, d=0.12) * 0.07

def kick():
    L = 0.4; x = np.arange(int(L * SR)) / SR
    f = 50 + 90 * np.exp(-x * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 9) * 0.55

def hat():
    L = 0.06; m = int(L * SR)
    s = rng.standard_normal(m); s = s - lowpass(s, 7000)
    return s * env(L, a=0.001, d=0.015) * 0.10

def snap():
    L = 0.18; m = int(L * SR); x = np.arange(m) / SR
    s = rng.standard_normal(m); s = lowpass(s, 4000) - lowpass(s, 900)
    return (s * 1.4 + 0.3 * np.sin(2 * np.pi * 190 * x)) * np.exp(-x * 25) * 0.22

def bassnote(f, L):
    m = int(L * SR); x = np.arange(m) / SR
    s = np.sin(2 * np.pi * f * x) + 0.25 * np.sin(4 * np.pi * f * x)
    return s * env(L, a=0.01, d=0.5, s=0.6, r=0.05) * 0.22

K, H, S = kick(), hat(), snap()
nbars = int(DUR / bar) + 1
for b in range(nbars):
    t0 = b * bar; ci = b % 4
    add(pad_cache[ci], t0)
    intro = b < 1            # first bar lighter
    for q in range(4):
        tb = t0 + q * beat
        if not intro and q in (0, 2): add(K, tb)
        if not intro and q in (1, 3): add(S, tb)
        add(bassnote(note(bass_roots[ci]), beat * 0.9), tb) if not intro else None
        for e in (0, 0.5):
            add(H * (1.0 if e else 0.6), tb + e * beat)
    arp = chords[ci] + [chords[ci][0] + 12]
    for k in range(8):
        add(pluck(note(arp[k % 4] + 12)), t0 + k * beat / 2)

# master: gentle fade in/out, normalize
fade = np.ones(n)
fi = int(1.0 * SR); fo = int(2.5 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
mix *= fade
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.8
st = np.stack([mix, mix], 1)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok", DUR)
