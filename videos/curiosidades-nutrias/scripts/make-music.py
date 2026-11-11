"""Mysterious documentary bed for the "Curiosidades de la vida" shorts:
a slow A-minor pad, soft felt-piano notes, a low heartbeat-like pulse,
a whoosh on every cut, a riser into the "algo todavía más sorprendente"
line and a deep hit when it lands. Mixed low so it sits under the voice.

Deterministic (seeded). Usage:
  python3 -I make-music.py config.json out.wav
config.json: {"duration": 24.6, "cuts": [4.0, 7.7, ...], "hit": 12.1}
"""
import json
import sys
import wave

import numpy as np

cfg = json.load(open(sys.argv[1]))
SR = 48000
DUR = cfg["duration"]
CUTS = cfg["cuts"]
HIT = cfg["hit"]
rng = np.random.default_rng(5)
n = int(SR * DUR)
L = np.zeros(n)
R = np.zeros(n)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t_(d):
    return np.arange(int(d * SR)) / SR


def add(sig, start, pan=0.0, gain=1.0):
    i0 = int(max(0, start) * SR)
    if i0 >= n:
        return
    sig = sig[: n - i0] * gain
    L[i0:i0 + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i0:i0 + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def pad(ms, d):
    t = t_(d)
    s = np.zeros_like(t)
    for m in ms:
        for det in (-0.07, 0.0, 0.07):
            s += np.sin(2 * np.pi * hz(m + det) * t + det * 9)
    env = np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.5)
    return s * env / (3 * len(ms))


def piano(m, d=2.5):
    t = t_(d)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4)
    return s * np.exp(-t * 1.6) * np.minimum(1, t * 300)


def thump(d=0.5):
    t = t_(d)
    f = 50 + 40 * np.exp(-t * 20)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def whoosh(d=0.7):
    t = t_(d)
    noise = rng.standard_normal(len(t))
    # simple one-pole low-pass sweep
    out = np.zeros_like(noise)
    a = np.linspace(0.02, 0.25, len(t))
    acc = 0.0
    for i in range(len(t)):
        acc += a[i] * (noise[i] - acc)
        out[i] = acc
    env = np.sin(np.pi * t / d) ** 2
    return out * env


def riser(d=2.0):
    t = t_(d)
    f = 200 * (1 + 3 * (t / d) ** 2)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * 0.5


def boom(d=3.0):
    t = t_(d)
    f = 45 + 30 * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.4)


CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
MEL = [76, 72, 69, 71, 72, 67, 69, 64]
BAR = 3.2
t = 0.0
k = 0
while t < DUR:
    ch = CHORDS[k % 4]
    add(pad([c - 12 for c in ch], BAR + 1.6), t - 0.4, 0.0, 0.5)
    add(piano(MEL[(2 * k) % 8] - 12), t + 0.1, -0.3, 0.16)
    add(piano(MEL[(2 * k + 1) % 8] - 12), t + 1.7, 0.3, 0.12)
    t += BAR
    k += 1

beat = 0.8
p = 0.4
while p < DUR - 1.5:
    if not (HIT - 2.2 < p < HIT + 0.2):
        add(thump(), p, 0.0, 0.32)
        add(thump(), p + 0.22, 0.0, 0.18)
    p += beat * 2

for c in CUTS:
    add(whoosh(), c - 0.35, 0.0, 0.10)
add(riser(), HIT - 2.0, 0.0, 0.35)
add(boom(), HIT, 0.0, 0.9)

fade = np.minimum(1, (DUR - np.arange(n) / SR) / 1.8).clip(0, 1) * np.minimum(1, np.arange(n) / SR / 0.3)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
st = np.stack([L, R], 1) / peak * 0.8
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
