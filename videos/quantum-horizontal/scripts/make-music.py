"""Electronic bed for the Quantum video: 120 BPM pulse, sub bass, synth arps,
a whoosh on every camera move, a riser into the finale and an impact on the outro.

Deterministic (seeded) so the track re-renders identically.
Usage: python3 -I scripts/make-music.py out.wav
Then: ffmpeg -i out.wav -af "loudnorm=I=-14:TP=-1.5:LRA=9" -c:a aac -b:a 192k assets/audio/quantum-bgm.m4a
"""
import sys
import wave

import numpy as np

SR = 48000
DUR = 58.0
BPM = 120
BEAT = 60 / BPM
DROP = 5.0       # camera dives into the world: drums start
MOVES = [4.0, 9.0, 13.0, 19.0, 25.0, 30.0, 36.0, 41.0, 46.0]  # camera transit starts (index.html)
REVEAL = 50.0    # pull back into the galaxy
OUTRO = 52.0
rng = np.random.default_rng(27)

n = int(SR * DUR)
L = np.zeros(n)
R = np.zeros(n)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0):
    i0 = int(start * SR)
    if i0 >= n:
        return
    i1 = min(n, i0 + len(sig))
    seg = sig[: i1 - i0] * gain
    L[i0:i1] += seg * np.sqrt(0.5 * (1 - pan))
    R[i0:i1] += seg * np.sqrt(0.5 * (1 + pan))


def env(length, a, r):
    e = np.ones(length)
    ai = max(1, min(int(a * SR), length))
    ri = max(1, min(int(r * SR), length))
    e[:ai] = np.linspace(0, 1, ai)
    e[length - ri:] *= np.linspace(1, 0, ri) ** 2
    return e


def lowpass(x, cutoff, block=128):
    # one-pole, cutoff may be an array (sweeps); coefficient held per block, solved in closed form
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    y = np.empty_like(x)
    acc = 0.0
    for i0 in range(0, len(x), block):
        xb = x[i0:i0 + block]
        a = np.exp(-2 * np.pi * c[i0] / SR)
        p = a ** np.arange(1, len(xb) + 1)
        yb = (1 - a) * p * np.cumsum(xb / p) + p * acc
        y[i0:i0 + block] = yb
        acc = yb[-1]
    return y


def saw(f, tt):
    ph = (f * tt) % 1.0
    return 2 * ph - 1


# A minor: Am - F - C - G, one chord per bar (2 s)
PROG = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]
BAR = 4 * BEAT

# Pads: detuned saws through a soft filter, whole film
for b in range(int(DUR / BAR) + 1):
    t0 = b * BAR
    if t0 >= OUTRO:
        break
    ch = PROG[b % 4]
    length = BAR + 0.4
    tt = np.arange(int(length * SR)) / SR
    for m in ch:
        f = midi_hz(m)
        s = sum(saw(f * 2 ** (d / 1200), tt) for d in (-9, 0, 8)) / 3
        s = lowpass(s, 900 + 500 * np.sin(np.pi * tt / length))
        add(s * env(len(tt), 0.35, 0.5), t0, pan=rng.uniform(-0.5, 0.5), gain=0.05)

# Sub bass: root on every beat after the drop, pumping (sidechain feel)
for k in range(int((OUTRO - DROP) / BEAT)):
    t0 = DROP + k * BEAT
    if REVEAL - 0.01 < t0 < OUTRO:
        continue
    ch = PROG[int(t0 / BAR) % 4]
    f = midi_hz(ch[0] - 24)
    tt = np.arange(int(BEAT * SR)) / SR
    s = np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)
    e = np.minimum(1, tt / 0.06) * np.exp(-tt * 2.5)
    add(s * e, t0, gain=0.22)

# Kick on the beat, hats on the off-beat (from the drop to the reveal)
for k in range(int((REVEAL - DROP) / BEAT)):
    t0 = DROP + k * BEAT
    tt = np.arange(int(0.35 * SR)) / SR
    f = 50 + 110 * np.exp(-tt * 30)
    kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
    add(kick, t0, gain=0.42)
    hn = rng.standard_normal(int(0.06 * SR))
    hat = np.diff(hn, prepend=0) * np.exp(-np.arange(len(hn)) / SR * 70)
    add(hat, t0 + BEAT / 2, pan=0.25, gain=0.06)
    if k % 4 == 2:  # soft clap on beat 3
        cn = rng.standard_normal(int(0.18 * SR))
        clap = lowpass(np.diff(cn, prepend=0), 3500) * np.exp(-np.arange(len(cn)) / SR * 18)
        add(clap, t0, pan=-0.15, gain=0.18)

# Arp: 16th-note pluck pattern over the chord, from the drop
step = BEAT / 4
pat = [0, 1, 2, 1, 2, 3, 2, 1]
for k in range(int((REVEAL - DROP) / step)):
    t0 = DROP + k * step
    ch = PROG[int(t0 / BAR) % 4]
    notes = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24]
    m = notes[pat[k % len(pat)]]
    tt = np.arange(int(0.3 * SR)) / SR
    s = saw(midi_hz(m), tt) * 0.6 + np.sin(2 * np.pi * midi_hz(m) * tt)
    s = lowpass(s, 2600 * np.exp(-tt * 9) + 400)
    add(s * np.exp(-tt * 11), t0, pan=0.45 * np.sin(k * 0.7), gain=0.07)

# Intro shimmer: high bell notes while the logo lights up
for i, m in enumerate([81, 76, 84, 79, 88]):
    tt = np.arange(int(2.5 * SR)) / SR
    s = np.sin(2 * np.pi * midi_hz(m) * tt) + 0.3 * np.sin(2 * np.pi * midi_hz(m) * 2.01 * tt)
    add(s * np.exp(-tt * 1.6) * np.minimum(1, tt / 0.004), 0.25 + i * 0.42, pan=(-0.5 + 0.25 * i), gain=0.05)


def whoosh(length, peak, gain):
    nn = rng.standard_normal(int(length * SR))
    tt = np.arange(len(nn)) / SR
    cut = 300 + 5200 * np.sin(np.pi * np.clip(tt / length, 0, 1)) ** 2
    s = lowpass(nn, cut)
    e = np.where(tt < peak, (tt / peak) ** 2, np.exp(-(tt - peak) * 6))
    return s * e * gain


for t in MOVES:
    add(whoosh(1.2, 0.5, 0.5), t, pan=rng.uniform(-0.3, 0.3))
# Riser into the reveal and a bigger whoosh as the camera pulls back
tt = np.arange(int(2.0 * SR)) / SR
riser = lowpass(rng.standard_normal(len(tt)), 200 + 7000 * (tt / 2.0) ** 2) * (tt / 2.0) ** 2
add(riser, REVEAL - 2.0, gain=0.35)
add(whoosh(2.4, 0.9, 0.7), REVEAL)

# Outro: low impact + wide final chord ringing out
tt = np.arange(int(3.0 * SR)) / SR
boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-tt * 6)) / SR) * np.exp(-tt * 1.6)
add(boom, OUTRO, gain=0.5)
fin = [45, 57, 60, 64, 67, 71]  # Am9
tt = np.arange(int((DUR - OUTRO) * SR)) / SR
for m in fin:
    s = sum(saw(midi_hz(m) * 2 ** (d / 1200), tt) for d in (-7, 0, 7)) / 3
    s = lowpass(s, 1400)
    add(s * env(len(tt), 0.8, 3.0), OUTRO, pan=rng.uniform(-0.6, 0.6), gain=0.05)
for k, m in enumerate([76, 72, 69, 64]):
    t2 = np.arange(int(3.0 * SR)) / SR
    s = np.sin(2 * np.pi * midi_hz(m) * t2) * np.exp(-t2 * 1.4)
    add(s, OUTRO + 0.8 + k * 0.6, pan=-0.3 + 0.2 * k, gain=0.06)

# Reverb: decaying stereo noise impulse
ir_len = int(2.2 * SR)
it = np.arange(ir_len) / SR
irs = []
for _ in range(2):
    ir = rng.standard_normal(ir_len) * np.exp(-it * 3.0)
    irs.append(ir / np.sqrt(np.sum(ir ** 2)))


def conv(x, h):
    size = 1 << int(np.ceil(np.log2(len(x) + len(h))))
    return np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(h, size), size)[: len(x)]


oL = 0.8 * L + 0.35 * conv(L, irs[0])
oR = 0.8 * R + 0.35 * conv(R, irs[1])
fade = np.ones(n)
fi, fo = int(0.3 * SR), int(3.0 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[n - fo:] = np.linspace(1, 0, fo) ** 1.5
st = np.stack([oL * fade, oR * fade], axis=1)
st /= np.max(np.abs(st)) / 0.85
pcm = (st * 32767).astype("<i2")
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", sys.argv[1])
