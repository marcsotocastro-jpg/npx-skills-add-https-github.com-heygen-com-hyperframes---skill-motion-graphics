"""Soft ambient bed for the HONA video: warm pad + gentle piano arpeggio + reverb.

Deterministic (seeded) so the track re-renders identically.
Usage: python3 -I scripts/make-music.py out.wav
Then: ffmpeg -i out.wav -af "lowpass=f=7000,equalizer=f=1200:t=q:w=1:g=3,loudnorm=I=-14:TP=-1.5:LRA=7" -c:a aac -b:a 192k assets/audio/hona-bgm.m4a
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 36.0
CHORD_LEN = 4.5  # 8 chords x 4.5 s = 36 s
rng = np.random.default_rng(7)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# F major, calm progression; the last chord (Fmaj9) lands under the outro
CHORDS = [
    [53, 57, 60, 64],  # Fmaj7
    [45, 57, 60, 64],  # Am7 / A bass
    [50, 57, 60, 65],  # Dm7
    [46, 57, 62, 65],  # Bbmaj7
    [53, 57, 60, 64],  # Fmaj7
    [45, 55, 60, 64],  # Am7
    [46, 58, 62, 65],  # Bb
    [48, 55, 60, 65],  # Csus4
]
FINAL = [41, 53, 57, 60, 64, 67]  # Fmaj9, rings out

n = int(SR * DUR)
t = np.arange(n) / SR
left = np.zeros(n)
right = np.zeros(n)


def env_adsr(length, a, r):
    e = np.ones(length)
    ai = min(int(a * SR), length)
    ri = min(int(r * SR), length)
    e[:ai] = np.linspace(0, 1, ai) ** 2
    e[length - ri:] *= np.linspace(1, 0, ri) ** 2
    return e


def add(sig, start, pan=0.0):
    i0 = int(start * SR)
    i1 = min(n, i0 + len(sig))
    seg = sig[: i1 - i0]
    left[i0:i1] += seg * np.sqrt(0.5 * (1 - pan))
    right[i0:i1] += seg * np.sqrt(0.5 * (1 + pan))


def pad_note(m, length, amp):
    tt = np.arange(int(length * SR)) / SR
    f = midi_hz(m)
    s = np.zeros_like(tt)
    for det in (-0.12, 0.0, 0.11):
        ff = f * 2 ** (det / 12)
        s += np.sin(2 * np.pi * ff * tt) + 0.25 * np.sin(2 * np.pi * 2 * ff * tt) + 0.08 * np.sin(2 * np.pi * 3 * ff * tt)
    s *= 1 + 0.08 * np.sin(2 * np.pi * 0.23 * tt)  # slow breathing
    return amp * s / 3 * env_adsr(len(tt), 1.6, 1.8)


def piano_note(m, amp, length=3.2):
    tt = np.arange(int(length * SR)) / SR
    f = midi_hz(m)
    s = np.zeros_like(tt)
    for k, (h, d) in enumerate([(1, 1.0), (2, 0.42), (3, 0.18), (4, 0.08), (5, 0.04)]):
        s += d * np.sin(2 * np.pi * f * h * tt + k) * np.exp(-tt * (1.1 + 0.9 * k))
    attack = np.minimum(1, tt / 0.006)
    return amp * s * attack


# Pads, overlapping a little between chords
for i, ch in enumerate(CHORDS[:-1] + [CHORDS[-1]]):
    start = i * CHORD_LEN
    if i == 7:
        # Csus4 resolves into the final Fmaj9 at 31.5 s
        for m in ch:
            add(pad_note(m, CHORD_LEN + 0.6, 0.05), start - 0.3, pan=rng.uniform(-0.4, 0.4))
        continue
    for m in ch:
        add(pad_note(m, CHORD_LEN + 1.2, 0.05), max(0, start - 0.3), pan=rng.uniform(-0.4, 0.4))

# Final chord rings under the outro
for m in FINAL:
    add(pad_note(m, DUR - 31.5, 0.045), 31.5, pan=rng.uniform(-0.4, 0.4))

# Piano: sparse arpeggio, enters after the logo intro
step = CHORD_LEN / 6
pattern = [0, 2, 3, 1, 3, 2]
for i, ch in enumerate(CHORDS[:7]):
    upper = [m + 12 for m in ch[1:]] + [ch[1] + 24]
    for j, p in enumerate(pattern):
        when = i * CHORD_LEN + j * step
        if when < 3.0:
            continue
        vel = 0.06 + 0.02 * (j == 0) + rng.uniform(-0.008, 0.008)
        add(piano_note(upper[p], vel), when + rng.uniform(-0.01, 0.01), pan=rng.uniform(-0.5, 0.5))
# A few last notes over the outro
for k, m in enumerate([77, 72, 69, 65]):
    add(piano_note(m, 0.06, 4.5), 31.5 + k * 0.75, pan=(-0.3 + 0.2 * k))

# Low root bloom at the start of each chord
for i, ch in enumerate(CHORDS + [FINAL]):
    start = i * CHORD_LEN if i < 8 else 31.5
    if start == 0:
        continue
    add(piano_note(ch[0] - 12 if ch[0] > 45 else ch[0], 0.05, 4.0), start)

# Reverb: decaying stereo noise impulse
ir_len = int(3.2 * SR)
it = np.arange(ir_len) / SR
ir_l = rng.standard_normal(ir_len) * np.exp(-it * 2.2)
ir_r = rng.standard_normal(ir_len) * np.exp(-it * 2.2)
for ir in (ir_l, ir_r):
    ir /= np.sqrt(np.sum(ir ** 2))


def conv(x, h):
    size = 1 << int(np.ceil(np.log2(len(x) + len(h))))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(h, size), size)
    return y[: len(x)]


wet_l = conv(left, ir_l)
wet_r = conv(right, ir_r)
out_l = 0.7 * left + 0.55 * wet_l
out_r = 0.7 * right + 0.55 * wet_r

# Master fades
fade = np.ones(n)
fi, fo = int(1.5 * SR), int(3.0 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[n - fo:] = np.linspace(1, 0, fo) ** 1.5
stereo = np.stack([out_l * fade, out_r * fade], axis=1)
stereo /= np.max(np.abs(stereo)) / 0.8

pcm = (stereo * 32767).astype("<i2")
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", sys.argv[1])
