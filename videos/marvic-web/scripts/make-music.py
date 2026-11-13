#!/usr/bin/env python3
"""Original background track for the Marvic Digital videos, synthesised from scratch.

Usage: python3 make-music.py <config.json> <out.wav>

config: {"duration": 34, "bpm": 120, "seed": 1,
         "whoosh": [4, 6.5, ...],   # scene cuts (seconds): a filtered-noise sweep that lands on the cut
         "impact": [0, 4.5, ...],   # hits: low boom + bright transient
         "break": [[4, 6.5]],       # sections with no drums (tension), music drops back in after
         "outro": 31}               # from here the drums stop and the pad rings out
"""
import json, sys
import numpy as np

SR = 44100
cfg = json.load(open(sys.argv[1]))
DUR = float(cfg["duration"]); BPM = float(cfg.get("bpm", 120)); BEAT = 60.0 / BPM
N = int(DUR * SR); t_all = np.arange(N) / SR
rng = np.random.default_rng(cfg.get("seed", 1))
mix = np.zeros((N, 2))

def lowpass(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / cutoff) ** 4), len(x))

def highpass(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * (1 - 1 / np.sqrt(1 + (f / cutoff) ** 4)), len(x))

def place(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    sig = sig[: N - i]
    l = gain * np.cos((pan + 1) * np.pi / 4); r = gain * np.sin((pan + 1) * np.pi / 4)
    mix[i:i + len(sig), 0] += sig * l * np.sqrt(2)
    mix[i:i + len(sig), 1] += sig * r * np.sqrt(2)

def in_break(x):
    return any(a <= x < b for a, b in cfg.get("break", [])) or x >= cfg.get("outro", DUR)

def note(m):
    return 440.0 * 2 ** ((m - 69) / 12)

# ---- drum voices
def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) + 0.25 * np.exp(-t * 300) * rng.standard_normal(n) * 0.3

def clap():
    n = int(0.3 * SR); t = np.arange(n) / SR
    noise = highpass(rng.standard_normal(n), 900)
    env = np.exp(-t * 22) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 40) * (t > 0.012)
    return noise * env * 0.5

def hat(open_=False):
    n = int((0.22 if open_ else 0.06) * SR); t = np.arange(n) / SR
    return highpass(rng.standard_normal(n), 7000) * np.exp(-t * (14 if open_ else 70)) * 0.35

K, C, H, HO = kick(), clap(), hat(), hat(True)

# ---- harmony: Am - F - C - G (one chord per bar), bright and positive
prog = [(57, [57, 60, 64, 69]), (53, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (55, [55, 59, 62, 67])]
BAR = 4 * BEAT
nbars = int(np.ceil(DUR / BAR))

def saw(freq, n, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in (-detune, 0, detune):
        ph = (t * freq * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / 3

pad = np.zeros(N); bass = np.zeros(N); arp = np.zeros(N)
for b in range(nbars):
    root, chord = prog[b % 4]
    s = int(b * BAR * SR); n = min(int(BAR * SR), N - s)
    if n <= 0: break
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.35) * np.minimum(1, (BAR - t) / 0.2)
    p = sum(saw(note(m), n, 0.004) for m in chord) / len(chord)
    pad[s:s + n] += p * env
    # bass: root on every 8th, side-chain feel from the gate shape
    for k in range(8):
        bs = int((b * BAR + k * BEAT / 2) * SR)
        if bs >= N: break
        bn = min(int(BEAT / 2 * SR), N - bs); tb = np.arange(bn) / SR
        f = note(root - 12) * (2 if k % 4 == 3 else 1)
        bass[bs:bs + bn] += (np.sin(2 * np.pi * f * tb) + 0.3 * np.sin(4 * np.pi * f * tb)) * np.exp(-tb * 5) * np.minimum(1, tb / 0.004)
    # arp: 16ths across the chord, one octave up
    seq = [0, 1, 2, 3, 2, 1, 3, 2]
    for k in range(16):
        a_t = b * BAR + k * BEAT / 4
        as_ = int(a_t * SR)
        if as_ >= N: break
        an = min(int(0.18 * SR), N - as_); ta = np.arange(an) / SR
        f = note(chord[seq[k % 8]] + 12)
        tone = (np.sin(2 * np.pi * f * ta) + 0.35 * np.sin(2 * np.pi * 2 * f * ta)) * np.exp(-ta * 18)
        arp[as_:as_ + an] += tone * (0.0 if in_break(a_t) else 1.0)

pad = lowpass(pad, 1800)
# side-chain pump on pad + bass from the kick grid
pump = np.ones(N)
for k in range(int(DUR / BEAT) + 1):
    x = k * BEAT
    if in_break(x): continue
    i = int(x * SR); n = min(int(BEAT * SR), N - i)
    if n <= 0: break
    tt = np.arange(n) / SR
    pump[i:i + n] = 1 - 0.55 * np.exp(-tt * 9)
bass_gate = np.array([0.0 if in_break(x) else 1.0 for x in t_all[::441]])
bass_gate = np.repeat(bass_gate, 441)[:N]
bass_gate = lowpass(bass_gate, 30)

place(pad * pump * 0.30, 0, 1, -0.0)
place(lowpass(bass, 400) * pump * bass_gate * 0.55, 0)
place(lowpass(arp, 5000) * 0.13, 0, 1, 0.35)

# drums
for k in range(int(DUR / BEAT) + 1):
    x = k * BEAT
    if in_break(x): continue
    place(K, x, 0.95)
    if k % 2 == 1: place(C, x, 0.55, -0.1)
    place(H, x + BEAT / 2, 0.5, 0.25)
    if k % 4 == 3: place(HO, x + BEAT / 2, 0.35, 0.25)
    place(H, x + BEAT / 4, 0.18, 0.3); place(H, x + 3 * BEAT / 4, 0.18, 0.3)

# ---- sfx
def whoosh(length=0.7):
    n = int(length * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    # sweep a band upward by blending progressively brighter filtered copies
    for j, c in enumerate([500, 1200, 2800, 6000]):
        w = np.clip(t / length * 4 - j, 0, 1) * np.clip(j + 2 - t / length * 4, 0, 1)
        out += highpass(lowpass(noise, c * 1.8), c * 0.5) * w
    env = (t / length) ** 2.2 * np.exp(-np.maximum(t - length * 0.92, 0) * 60)
    return out * env * 0.55

def impact():
    n = int(1.6 * SR); t = np.arange(n) / SR
    f = 38 + 70 * np.exp(-t * 12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6)
    crack = highpass(rng.standard_normal(n), 2500) * np.exp(-t * 28) * 0.4
    tail = lowpass(rng.standard_normal(n), 1500) * np.exp(-t * 3) * 0.12
    return boom + crack + tail

def riser(length):
    n = int(length * SR); t = np.arange(n) / SR
    f = 200 * (8 ** (t / length))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    noise = highpass(rng.standard_normal(n), 3000) * 0.35
    return (tone + noise) * (t / length) ** 3

W, I = whoosh(), impact()
for x in cfg.get("whoosh", []):
    place(W, max(0, x - 0.65), 0.8, 0.0)
for x in cfg.get("impact", []):
    place(I, x, 0.75)
for a, b in cfg.get("break", []):
    place(riser(b - a), a, 0.55)

# outro: let the pad ring and fade
o = cfg.get("outro", DUR)
fade = np.ones(N); fi = int(min(o + 1.0, DUR - 1.2) * SR)
fade[fi:] = np.linspace(1, 0, N - fi) ** 1.5
mix *= fade[:, None]
mix[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))[:, None]

mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
pcm = (mix * 0.89 * 32767).astype(np.int16)

import wave
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote", sys.argv[2], DUR, "s")
