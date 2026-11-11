"""Warm, unhurried café bed for the Moments video: 88 BPM in F major, detuned
pads, soft felt-piano arpeggios, a sub pulse and a brushed shaker from the
cafetería on, airy whooshes and glass chimes on every scene change, one
chime per flower card, and a long ringing chord under the call to action.

Deterministic (seeded) so the track re-renders identically.
Usage: python3 -I scripts/make-music.py out.wav
Then: ffmpeg -i out.wav -af "loudnorm=I=-15:TP=-1.5:LRA=9" -c:a aac -b:a 192k assets/audio/moments-bgm.m4a
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 45.0
BPM = 88
BEAT = 60 / BPM
BAR = 4 * BEAT
PULSE = 9.5                                    # soft groove from the cafetería on
SCENES = [5.0, 9.5, 14.5, 21.5, 26.0, 36.0, 40.0]  # scene starts in index.html
CHIMES = [15.2, 17.15, 19.1, 27.2, 29.6, 32.0]  # flower cards, then web callouts
END_CHORD = 40.0
rng = np.random.default_rng(11)

n = int(SR * DUR)
L = np.zeros(n)
R = np.zeros(n)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t_(d):
    return np.arange(int(d * SR)) / SR


def add(sig, start, pan=0.0, gain=1.0):
    i0 = int(start * SR)
    if i0 >= n or i0 < 0:
        return
    i1 = min(n, i0 + len(sig))
    seg = sig[: i1 - i0] * gain
    L[i0:i1] += seg * np.sqrt(0.5 * (1 - pan))
    R[i0:i1] += seg * np.sqrt(0.5 * (1 + pan))


def onepole(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    out = np.empty_like(x)
    acc = 0.0
    B = 256
    for i0 in range(0, len(x), B):
        xb = x[i0:i0 + B]
        p = a ** np.arange(1, len(xb) + 1)
        yb = (1 - a) * p * np.cumsum(xb / p) + p * acc
        out[i0:i0 + B] = yb
        acc = yb[-1]
    return out


def tri(f, tt):
    return 2 * np.abs(2 * ((f * tt) % 1.0) - 1) - 1


# F major colour: Fmaj9 - Dm7 - Bbmaj7 - Csus4, one chord per bar (LA VITE's progression up a minor third)
PROG = [[m + 3 for m in c] for c in [[62, 66, 69, 73, 76], [59, 62, 66, 69, 73], [55, 59, 62, 66, 71], [57, 62, 64, 69, 74]]]
ROOTS = [41, 38, 34, 36]

# --- Pads
nb = int(np.ceil(DUR / BAR))
for b in range(nb):
    t0 = b * BAR
    if t0 >= END_CHORD:
        break
    d = BAR + 0.6
    tt = t_(d)
    sig = np.zeros_like(tt)
    for m in PROG[b % 4][:4]:
        for det in (-0.07, 0.07):
            sig += tri(midi_hz(m + det), tt) + 0.5 * np.sin(2 * np.pi * midi_hz(m + 12 + det) * tt)
    e = np.minimum(1, tt / 0.8) * np.minimum(1, np.maximum(0, (d - tt) / 0.6))
    add(onepole(sig * e, 1600), t0, 0.0, 0.020)

# --- Felt piano
def piano(f, d=1.6):
    tt = t_(d)
    s = sum(np.sin(2 * np.pi * f * k * tt * (1 + 0.0004 * k * k)) * np.exp(-tt * (2.2 + 1.4 * k)) / k ** 1.2 for k in range(1, 6))
    return onepole(s * np.minimum(1, tt / 0.004), 3200)


for b in range(nb):
    t0 = b * BAR
    if t0 >= END_CHORD:
        break
    ch = PROG[b % 4]
    order = [0, 2, 1, 3, 4, 3, 1, 2] if b % 2 == 0 else [0, 1, 2, 4, 3, 2, 4, 1]
    for k, idx in enumerate(order):
        vel = 0.10 if t0 < PULSE else 0.085
        add(piano(midi_hz(ch[idx] + 12)), t0 + k * BEAT / 2, -0.3 if k % 2 else 0.3, vel)

# --- Sub pulse + shaker + soft rim from the treatments on
def sub(f, d):
    tt = t_(d)
    return np.sin(2 * np.pi * f * tt) * np.minimum(1, tt / 0.01) * np.exp(-tt * 2.4)


def kick():
    tt = t_(0.4)
    f = 45 + 70 * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8)


def shaker():
    tt = t_(0.08)
    nz = rng.standard_normal(len(tt))
    return (nz - onepole(nz, 5500)) * np.exp(-tt * 55)


def rim():
    tt = t_(0.12)
    nz = rng.standard_normal(len(tt))
    return (nz - onepole(nz, 1800)) * np.exp(-tt * 40) * 0.6 + np.sin(2 * np.pi * 1700 * tt) * np.exp(-tt * 60) * 0.4


K = kick()
t = PULSE
while t < END_CHORD - 0.01:
    beat = round((t - PULSE) / BEAT)
    b = int(t // BAR)
    if beat % 4 == 0:
        add(sub(midi_hz(ROOTS[b % 4]), BAR * 0.9), t, 0, 0.30)
    if beat % 2 == 0:
        add(K, t, 0, 0.40)
    if beat % 4 == 2:
        add(rim(), t, 0.1, 0.10)
    for s in range(2):
        add(shaker(), t + s * BEAT / 2, 0.35, 0.05 if s else 0.035)
    t += BEAT

# --- Airy whooshes and glass chimes
def whoosh(d=1.1):
    tt = t_(d)
    nz = rng.standard_normal(len(tt))
    env = np.sin(np.pi * np.minimum(1, tt / d)) ** 2
    return (onepole(nz, 3000) - onepole(nz, 500)) * env


def chime(f, d=2.2):
    tt = t_(d)
    s = np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 4) + 0.2 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 8)
    return s * np.exp(-tt * 2.0) * np.minimum(1, tt / 0.002)


for s in SCENES:
    add(whoosh(), s - 0.7, -0.5, 0.16)
    add(whoosh(), s - 0.65, 0.5, 0.16)
    add(chime(midi_hz(89)), s, 0.2, 0.05)

for i, c in enumerate(CHIMES):
    add(chime(midi_hz([84, 86, 88, 89, 91, 93][i])), c, (-1) ** i * 0.4, 0.04)

# opening shimmer
add(chime(midi_hz(77), 3.5), 0.15, -0.3, 0.06)
add(chime(midi_hz(84), 3.5), 0.35, 0.3, 0.05)

# --- Final ringing chord
d = DUR - END_CHORD
tt = t_(d)
sig = np.zeros_like(tt)
for m in [41, 53, 60, 65, 69, 72, 76]:
    sig += np.sin(2 * np.pi * midi_hz(m) * tt) * np.exp(-tt * 0.55) * 0.5
    sig += tri(midi_hz(m), tt) * np.exp(-tt * 0.9) * 0.15
add(onepole(sig, 2500), END_CHORD, 0, 0.10)
for k, m in enumerate([77, 81, 84, 88, 89]):
    add(piano(midi_hz(m), 3.0), END_CHORD + 0.1 + k * 0.12, (k - 2) * 0.2, 0.09)
add(K, END_CHORD, 0, 0.45)

# --- Master
mix = np.stack([L, R], axis=1)
fade = np.ones(n)
fi = int(2.0 * SR)
fade[-fi:] = np.linspace(1, 0, fi)
fade[: int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
mix *= fade[:, None]
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix /= max(1e-9, np.abs(mix).max()) / 0.9
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", sys.argv[1], DUR, "s")
