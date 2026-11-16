"""Mix the voiceover lines over the background music with clear, fixed levels.

Usage: python3 mix.py <voiceover.json> <video-id> <voice-dir> <music.m4a> <out.m4a>

Each voice line is loudness-normalised to the same level, the music sits at a
background level between lines and dips a further 14 dB under the voice (with
short ramps), then the whole mix is raised to about -14 LUFS for social media.
"""
import json, subprocess, sys, tempfile, os
import numpy as np

SR = 44100
spec, vid, vdir, music, out = sys.argv[1:6]
d = json.load(open(spec))[vid]
N = int(d["dur"] * SR)

def decode(path, extra_af=None):
    af = ["-af", extra_af] if extra_af else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path] + af + ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()

def db(x):
    return 10 ** (x / 20)

mus = decode(music)[:N]
if len(mus) < N:
    mus = np.vstack([mus, np.zeros((N - len(mus), 2), np.float32)])

voice = np.zeros((N, 2), np.float32)
duck = np.zeros(N, np.float32)          # 1 where the voice speaks (with ramps)
ramp = int(0.18 * SR)
for i, (start, _end, _t) in enumerate(d["lines"]):
    seg = decode(f"{vdir}/{vid}-{i}.wav", "loudnorm=I=-16:TP=-2:LRA=7")
    a = int(start * SR); b = min(N, a + len(seg))
    voice[a:b] += seg[: b - a]
    lo = max(0, a - ramp); hi = min(N, b + ramp)
    duck[a:b] = 1
    duck[lo:a] = np.maximum(duck[lo:a], np.linspace(0, 1, a - lo))
    duck[b:hi] = np.maximum(duck[b:hi], np.linspace(1, 0, hi - b))

music_gain = db(-6) * (1 - duck * (1 - db(-14)))   # -20 LUFS between lines, ~-34 under the voice
mix = mus * music_gain[:, None] + voice

with tempfile.TemporaryDirectory() as tmp:
    wav = os.path.join(tmp, "mix.f32")
    mix.astype(np.float32).tofile(wav)
    # measure, then apply one linear gain so the voice/music balance is kept
    m = subprocess.run(["ffmpeg", "-v", "info", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", wav, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    I = float([l for l in m.splitlines() if " I:" in l][-1].split("I:")[1].split()[0])
    peak = float([l for l in m.splitlines() if "Peak:" in l][-1].split("Peak:")[1].split()[0])
    gain = min(-14 - I, -1.0 - peak)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", wav,
                    "-af", f"volume={gain:.2f}dB", "-c:a", "aac", "-b:a", "192k", out], check=True)
print(f"wrote {out} (gain {gain:+.1f} dB)")
