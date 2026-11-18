"""Background bed for the YOCOMOTORS video: pad + piano arpeggio + soft pulse, kept low under a voice-over.

Deterministic (seeded) so the track re-renders identically.
Usage: python3 -I scripts/make-music.py out.wav
Then: ffmpeg -i out.wav -af "lowpass=f=7000,equalizer=f=1200:t=q:w=1:g=3,loudnorm=I=-20:TP=-1.5:LRA=7" -c:a aac -b:a 192k assets/audio/yoco-bgm.m4a
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 60.0
FINAL_T = 51.4  # outro starts here; the final chord lands on it
rng = np.random.default_rng(11)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# A minor, confident progression (Am F C G); the last chord (A5 add9) lands under the outro
BASE = [
    [45, 57, 60, 64],  # Am
    [41, 57, 60, 65],  # F
    [48, 55, 60, 64],  # C
    [43, 55, 59, 62],  # G
]
CHORDS = BASE * 4
CHORD_LEN = FINAL_T / len(CHORDS)
FINAL = [45, 57, 64, 69, 71, 76]  # A5 add9, rings out

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
    if i == len(CHORDS) - 1:
        # Csus4 resolves into the final Fmaj9
        for m in ch:
            add(pad_note(m, CHORD_LEN + 0.6, 0.05), start - 0.3, pan=rng.uniform(-0.4, 0.4))
        continue
    for m in ch:
        add(pad_note(m, CHORD_LEN + 1.2, 0.05), max(0, start - 0.3), pan=rng.uniform(-0.4, 0.4))

# Final chord rings under the outro
for m in FINAL:
    add(pad_note(m, DUR - FINAL_T, 0.045), FINAL_T, pan=rng.uniform(-0.4, 0.4))

# Piano: sparse arpeggio, enters after the logo intro
step = CHORD_LEN / 6
pattern = [0, 2, 3, 1, 3, 2]
for i, ch in enumerate(CHORDS[:-1]):
    upper = [m + 12 for m in ch[1:]] + [ch[1] + 24]
    for j, p in enumerate(pattern):
        when = i * CHORD_LEN + j * step
        if when < 3.0:
            continue
        vel = 0.06 + 0.02 * (j == 0) + rng.uniform(-0.008, 0.008)
        add(piano_note(upper[p], vel), when + rng.uniform(-0.01, 0.01), pan=rng.uniform(-0.5, 0.5))
# A few last notes over the outro
for k, m in enumerate([76, 72, 69, 64]):
    add(piano_note(m, 0.06, 4.5), FINAL_T + k * 0.75, pan=(-0.3 + 0.2 * k))

# Soft pulse: muted kick on each beat and a light shaker on the off-beats, after the intro
BEAT = CHORD_LEN / 4
kt = np.arange(int(0.35 * SR)) / SR
kick = np.sin(2 * np.pi * (52 + 70 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9)
st = np.arange(int(0.08 * SR)) / SR
b = 0
while b * BEAT < FINAL_T - 0.1:
    when = b * BEAT
    if when >= 4.4:
        add(kick * 0.16, when)
        add(rng.standard_normal(len(st)) * np.exp(-st * 60) * 0.018, when + BEAT / 2, pan=0.3)
    b += 1

# Low root bloom at the start of each chord
for i, ch in enumerate(CHORDS + [FINAL]):
    start = i * CHORD_LEN if i < len(CHORDS) else FINAL_T
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
