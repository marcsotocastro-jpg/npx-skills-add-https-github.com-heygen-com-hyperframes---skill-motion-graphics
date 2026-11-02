"""Warm, upbeat bed for the Insitu video: 120 BPM groove (kick, clap, shaker),
round bass, plucked "mandolin" chords with tremolo, whooshes on every scene change,
a riser into the call to action and a final ringing chord.

Deterministic (seeded) so the track re-renders identically.
Usage: python3 -I scripts/make-music.py out.wav
Then: ffmpeg -i out.wav -af "loudnorm=I=-14:TP=-1.5:LRA=9" -c:a aac -b:a 192k assets/audio/insitu-bgm.m4a
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 50.0
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
GROOVE = 4.0                            # drums start when the menu opens
SCENES = [4.0, 10.0, 16.0, 24.0, 32.0, 42.0]   # scene starts in index.html
POPS = [25.3, 25.6, 25.9, 26.2, 26.5, 26.8, 27.1, 27.4]  # ingredient pills
CTA = 42.0
END_CHORD = 47.0
rng = np.random.default_rng(11)

n = int(SR * DUR)
L = np.zeros(n)
R = np.zeros(n)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0):
    i0 = int(start * SR)
    if i0 >= n or i0 < 0:
        return
    i1 = min(n, i0 + len(sig))
    seg = sig[: i1 - i0] * gain
    L[i0:i1] += seg * np.sqrt(0.5 * (1 - pan))
    R[i0:i1] += seg * np.sqrt(0.5 * (1 + pan))


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def onepole_fast(x, cutoff):
    # vectorised one-pole via block recursion (fine for constant cutoff)
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


# C major, I - vi - IV - V (C, Am, F, G), one chord per bar
PROG = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
ROOTS = [36, 33, 29, 31]


def chord_at(t):
    return int(t // BAR) % 4


# --- Pad: soft detuned triangles, whole film, swells under intro and CTA
def tri(f, tt):
    return 2 * np.abs(2 * ((f * tt) % 1.0) - 1) - 1


for b in range(int(DUR / BAR)):
    t0 = b * BAR
    if t0 >= END_CHORD:
        break
    tt = t_(BAR + 0.3)
    sig = np.zeros_like(tt)
    for m in PROG[b % 4]:
        for det in (-0.08, 0.08):
            sig += tri(midi_hz(m + 12 + det), tt)
    e = np.minimum(1, tt / 0.25) * np.minimum(1, np.maximum(0, (BAR + 0.3 - tt) / 0.3))
    g = 0.022 if (t0 < GROOVE or t0 >= CTA) else 0.014
    add(onepole_fast(sig * e, 2200), t0, 0.0, g)

# --- Mandolin-style plucks: tremolo on the intro, rhythmic stabs in the groove
def pluck(f, dur=0.35, bright=1.0):
    tt = t_(dur)
    s = sum(np.sin(2 * np.pi * f * k * tt) / k ** (1.6 - 0.4 * bright) for k in range(1, 7))
    return s * np.exp(-tt * 9)


for b in range(int(DUR / BAR)):
    t0 = b * BAR
    if t0 >= END_CHORD:
        break
    notes = PROG[b % 4]
    if t0 < GROOVE:
        # tremolo strum (16ths) with a light swell
        for k in range(16):
            for j, m in enumerate(notes):
                add(pluck(midi_hz(m + 12), 0.2), t0 + k * BEAT / 4 + j * 0.012, (j - 1) * 0.4, 0.05 + 0.03 * k / 16)
    else:
        # syncopated stabs: 1, 2&, 3, 4&
        for off in (0, 1.5, 2, 3.5):
            for j, m in enumerate(notes):
                add(pluck(midi_hz(m + 12), 0.3), t0 + off * BEAT + j * 0.01, (j - 1) * 0.5, 0.055)
        # arp sparkle on the upper octave, every other bar
        if b % 2 == 1:
            for k, m in enumerate(notes + [notes[0] + 12, notes[1] + 12, notes[2], notes[1], notes[0] + 12]):
                add(pluck(midi_hz(m + 24), 0.22, 1.4), t0 + k * BEAT / 2, 0.35 if k % 2 else -0.35, 0.025)

# --- Bass: round sine + a little harmonic, root / octave bounce
for b in range(int(GROOVE / BAR), int(END_CHORD / BAR)):
    t0 = b * BAR
    r = ROOTS[b % 4]
    pattern = [(0, r, 0.9), (1.5, r + 12, 0.45), (2, r, 0.7), (3, r + 7, 0.5), (3.5, r + 12, 0.4)]
    for off, m, d in pattern:
        tt = t_(d)
        f = midi_hz(m)
        s = np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)
        s *= np.minimum(1, tt / 0.005) * np.exp(-tt * 3.0)
        add(s, t0 + off * BEAT, 0.0, 0.32)

# --- Drums
def kick():
    tt = t_(0.35)
    f = 50 + 110 * np.exp(-tt * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt * 7) + 0.3 * np.exp(-tt * 300) * rng.standard_normal(len(tt)) * 0.3


def clap():
    tt = t_(0.25)
    nz = rng.standard_normal(len(tt))
    nz = nz - onepole_fast(nz, 900)
    e = np.exp(-tt * 18)
    for d in (0.0, 0.011, 0.022):
        e = e + 0.6 * np.exp(-np.maximum(0, tt - d) * 120) * (tt >= d)
    return nz * e * 0.5


def shaker():
    tt = t_(0.07)
    nz = rng.standard_normal(len(tt))
    nz = nz - onepole_fast(nz, 5000)
    return nz * np.exp(-tt * 60)


K, C = kick(), clap()
t = GROOVE
while t < END_CHORD - 0.01:
    beat = round((t - GROOVE) / BEAT)
    in_phone = 32.0 <= t < 40.0
    if not in_phone or beat % 2 == 0:
        add(K, t, 0, 0.55)
    if beat % 4 in (1, 3):
        add(C, t, 0.05, 0.22 if not in_phone else 0.14)
    for s in range(4):
        add(shaker(), t + s * BEAT / 4 + (0.012 if s % 2 else 0), 0.3, 0.05 if s % 2 else 0.09)
    t += BEAT

# --- Whooshes into every scene
def whoosh(d=0.9):
    tt = t_(d)
    nz = rng.standard_normal(len(tt))
    env = np.sin(np.pi * np.minimum(1, tt / d)) ** 2
    lo = onepole_fast(nz, 2500)
    return (nz - onepole_fast(nz, 600)) * 0.4 * env + lo * 0.3 * env


for s in SCENES:
    add(whoosh(), s - 0.55, -0.4, 0.22)
    add(whoosh(), s - 0.5, 0.4, 0.22)

# --- Hit at the very top (pizza slam) and at the CTA
def impact():
    tt = t_(1.6)
    f = 40 + 60 * np.exp(-tt * 12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
    nz = rng.standard_normal(len(tt)) * np.exp(-tt * 9)
    return boom + 0.35 * onepole_fast(nz, 3000)


add(impact(), 0.25, 0, 0.6)
add(impact(), CTA, 0, 0.6)

# --- Riser into the CTA
rd = 3.0
tt = t_(rd)
nz = rng.standard_normal(len(tt))
f = 300 + 3000 * (tt / rd) ** 2
riser = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + (nz - onepole_fast(nz, 1500)) * 0.35
add(riser * (tt / rd) ** 2, CTA - rd, 0, 0.3)

# --- Pops for the ingredient pills
for p in POPS:
    tt = t_(0.08)
    f = 900 + 900 * np.exp(-tt * 60)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 45), p, rng.uniform(-0.5, 0.5), 0.12)

# --- Final ringing C chord
tt = t_(DUR - END_CHORD)
sig = np.zeros_like(tt)
for m in [48, 60, 64, 67, 72]:
    sig += np.sin(2 * np.pi * midi_hz(m) * tt) * np.exp(-tt * 1.1) * 0.5
    sig += tri(midi_hz(m), tt) * np.exp(-tt * 1.6) * 0.25
add(sig, END_CHORD, 0, 0.12)
add(K, END_CHORD, 0, 0.55)

# --- Master: soft clip, fade out
mix = np.stack([L, R], axis=1)
fade = np.ones(n)
fi = int(1.5 * SR)
fade[-fi:] = np.linspace(1, 0, fi)
mix *= fade[:, None]
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
mix /= max(1e-9, np.abs(mix).max()) / 0.9
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", sys.argv[1], DUR, "s")
