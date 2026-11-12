"""Music bed + final mix for the "2 € al día" video.

Light, upbeat explainer bed at 104 BPM (soft kick, offbeat hats, warm pad
on Am-F-C-G, plucked arpeggio), a whoosh on every scene change and a coin
"ding" when the counters land. The voice-over clips from make-voice.py are
laid on top at their timeline positions and the music ducks under them.

Deterministic (seeded) so the track re-renders identically.
Usage: python3 -I scripts/make-audio.py out.wav
Then:  ffmpeg -i out.wav -af "loudnorm=I=-14:TP=-1.5:LRA=9" -c:a aac -b:a 192k assets/audio/mix.m4a
"""
import json
import pathlib
import sys
import wave

import numpy as np

SR = 48000
DUR = 43.0
BPM = 104
BEAT = 60 / BPM
SCENES = [3.29, 8.32, 20.54, 30.62, 38.13]          # scene cuts in index.html
DINGS = [0.9, 9.9, 12.4, 15.2, 18.0, 23.7, 28.0]     # counters landing
root = pathlib.Path(__file__).resolve().parent.parent
rng = np.random.default_rng(11)

n = int(SR * DUR)
L = np.zeros(n)
R = np.zeros(n)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def add(sig, start, pan=0.0, gain=1.0, bus=None):
    i0 = int(start * SR)
    if i0 >= n:
        return
    s = sig[: n - i0] * gain
    lg, rg = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    (bus or (L, R))[0][i0:i0 + len(s)] += s * lg
    (bus or (L, R))[1][i0:i0 + len(s)] += s * rg


def env(t, a, d):
    return np.minimum(1, t / a) * np.exp(-t / d)


# --- chords: Am F C G, one bar each -----------------------------------------
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
BAR = 4 * BEAT
nbars = int(DUR / BAR) + 1
for b in range(nbars):
    ch = CH[b % 4]
    t = tt(BAR + 0.4)
    e = np.minimum(1, t / 0.25) * np.minimum(1, (BAR + 0.4 - t) / 0.4)
    for k, m in enumerate(ch):
        for det in (-0.12, 0.12):
            f = hz(m) * 2 ** (det / 12)
            s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
            add(s * e, b * BAR, pan=det * 4, gain=0.022)
    # bass
    tb = tt(BAR)
    fb = hz(ch[0] - 12)
    add(np.sin(2 * np.pi * fb * tb) * env(tb, 0.01, 0.9), b * BAR, gain=0.10)
    add(np.sin(2 * np.pi * fb * tb) * env(tb, 0.01, 0.5), b * BAR + 2 * BEAT, gain=0.07)
    # pluck arpeggio, eighth notes
    arp = ch + [ch[0] + 12, ch[1] + 12, ch[2], ch[1], ch[0] + 12]
    for k in range(8):
        tp = tt(0.5)
        f = hz(arp[k] + 12)
        s = (np.sin(2 * np.pi * f * tp) + 0.25 * np.sin(6 * np.pi * f * tp)) * env(tp, 0.003, 0.12)
        add(s, b * BAR + k * BEAT / 2, pan=0.35 if k % 2 else -0.35, gain=0.035)

# --- drums ------------------------------------------------------------------
beats = int(DUR / BEAT)
kick_t = tt(0.35)
kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kick_t / 0.04)) * kick_t) * np.exp(-kick_t / 0.12)
hat_t = tt(0.06)
for i in range(beats):
    t0 = i * BEAT
    if t0 > DUR - 1.2:
        break
    add(kick, t0, gain=0.22)
    hat = rng.standard_normal(len(hat_t)) * np.exp(-hat_t / 0.012)
    hat = np.diff(hat, prepend=0)
    add(hat, t0 + BEAT / 2, pan=0.2, gain=0.035)
    if i % 4 in (1, 3):
        st = tt(0.2)
        snr = rng.standard_normal(len(st)) * np.exp(-st / 0.05)
        add(snr, t0, gain=0.035)

# sidechain pump
pos = (np.arange(n) / SR) % BEAT
pump = 0.6 + 0.4 * np.minimum(1, pos / 0.18)
L *= pump
R *= pump

# --- whooshes and dings -------------------------------------------------------
for s0 in SCENES:
    d = 0.7
    t = tt(d)
    nz = rng.standard_normal(len(t))
    k = np.exp(-((t - 0.45) ** 2) / 0.03)
    sm = np.convolve(nz, np.ones(12) / 12, mode="same")
    add(sm * k, s0 - 0.45, pan=-0.3, gain=0.22)
    add(np.roll(sm, 37) * k, s0 - 0.45, pan=0.3, gain=0.22)
for d0 in DINGS:
    t = tt(1.0)
    s = (np.sin(2 * np.pi * 1975 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t)) * env(t, 0.002, 0.22)
    add(s, d0, gain=0.05)

# fade the music in/out
fade = np.ones(n)
fi, fo = int(0.3 * SR), int(1.5 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo)
L *= fade
R *= fade

# --- voice-over + ducking ----------------------------------------------------
timing = json.loads((root / "scripts" / "vo-timing.json").read_text())
vo = np.zeros(n)
for x in timing:
    with wave.open(str(root / "assets" / "audio" / f"vo-{x['i']:02d}.wav")) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
    a = np.interp(np.arange(0, len(a), sr / SR), np.arange(len(a)), a)
    i0 = int(x["start"] * SR)
    vo[i0:i0 + len(a)] += a[: n - i0]
lvl = np.convolve(np.abs(vo), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
duck = 1 - 0.55 * np.clip(lvl / 0.03, 0, 1)
L = L * duck + vo * 0.9
R = R * duck + vo * 0.9

peak = max(np.abs(L).max(), np.abs(R).max())
st = np.stack([L, R], 1) / peak * 0.9
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok")
