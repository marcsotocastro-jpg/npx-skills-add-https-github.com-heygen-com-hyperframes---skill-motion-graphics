"""Light, curious bed for the flamingo video: 100 BPM marimba plucks over
a soft pad and a tiny shaker, a bubbly "pop" on every scene change and a
little bell on the final reveal. Mixed low so it sits under the voice.

Deterministic (seeded) so the track re-renders identically.
Usage: python3 -I scripts/make-music.py out.wav
Then: ffmpeg -i out.wav -af "loudnorm=I=-27:TP=-3:LRA=9" -c:a aac -b:a 160k assets/audio/musica.m4a
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 53.0
BPM = 100
BEAT = 60 / BPM
SCENES = [5.0, 8.6, 14.0, 21.0, 28.4, 36.0, 40.3, 47.0, 50.0]  # scene starts in index.html
BELL = 47.0
rng = np.random.default_rng(11)

n = int(SR * DUR)
L = np.zeros(n)
R = np.zeros(n)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t_(d):
    return np.arange(int(d * SR)) / SR


def add(sig, start, pan=0.0, gain=1.0):
    i0 = int(start * SR)
    if i0 >= n:
        return
    sig = sig[: n - i0] * gain
    L[i0:i0 + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    R[i0:i0 + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def marimba(m, d=0.6):
    t = t_(d)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)
    return s * np.exp(-t * 7) * np.minimum(1, t * 400)


def pad(ms, d):
    t = t_(d)
    s = np.zeros_like(t)
    for m in ms:
        for det in (-0.08, 0.08):
            s += np.sin(2 * np.pi * hz(m + det) * t)
    env = np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 0.8)
    return s * env / (2 * len(ms))


def shaker(d=0.08):
    t = t_(d)
    return rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.5


def pop(f0=500):
    t = t_(0.18)
    f = f0 + 900 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)


def bell(m):
    t = t_(2.5)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) + 0.2 * np.sin(2 * np.pi * f * 5.4 * t)
    return s * np.exp(-t * 2.2)


# I - vi - IV - V in C, two bars each chord (4 beats per bar)
CHORDS = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
PATTERN = [0, 2, 1, 2, 0, 2, 1, 2]  # chord-tone index per eighth note
BAR = 4 * BEAT
end_music = 51.5
t = 0.0
k = 0
while t < end_music:
    ch = CHORDS[(k // 2) % 4]
    add(pad([c - 12 for c in ch], BAR + 0.6), t, 0.0, 0.18)
    add(marimba(ch[0] - 24, 0.9), t, 0.0, 0.35)
    for e in range(8):
        te = t + e * BEAT / 2
        if te >= end_music:
            break
        note = ch[PATTERN[e]] + (12 if e in (3, 7) else 0)
        add(marimba(note), te, -0.3 if e % 2 else 0.3, 0.22)
        if te > 5.0:
            add(shaker(), te + BEAT / 4, 0.5, 0.05)
    t += BAR
    k += 1

for i, s in enumerate(SCENES):
    add(pop(420 + 60 * (i % 3)), s - 0.05, 0.0, 0.35)

for j, m in enumerate([72, 76, 79, 84]):
    add(bell(m), BELL + j * 0.12, -0.2 + 0.13 * j, 0.12)
add(pad([60, 64, 67, 72], 3.5), 49.5, 0.0, 0.25)

fade = np.minimum(1, (DUR - np.arange(n) / SR) / 1.5).clip(0, 1)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
st = np.stack([L, R], 1) / peak * 0.8
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
