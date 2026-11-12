"""Build one or all curiosity video projects from specs.py.

For each spec: Piper TTS voice-over per line, timing, index.html from
template.html + engine.js, a generated music bed with whooshes and dings,
the ducked final mix (assets/audio/mix.m4a) and the HyperFrames project
files. Rendering is done afterwards with `npm run render` in each project.

Usage: python3 -I build.py /path/to/es_ES-davefx-medium.onnx [id ...]
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys
import wave

import numpy as np

from specs import SPECS

KIT = pathlib.Path(__file__).resolve().parent
VIDEOS = KIT.parent
FONTS = VIDEOS / "ahorro-vertical" / "assets" / "fonts"
GSAP = VIDEOS / "ahorro-vertical" / "assets" / "vendor" / "gsap.min.js"
START, GAP, SPEED = 0.25, 0.22, "0.8"
SR = 48000


def norm(spec):
    lines = [[(c, c) if isinstance(c, str) else c for c in ln] for ln in spec["lines"]]
    scenes = []
    for sc in spec["scenes"]:
        sc = dict(sc)
        sc["from"] = sc.pop("from_")
        scenes.append(sc)
    return lines, scenes


def voice(lines, out, model):
    t, timing = START, []
    for i, ln in enumerate(lines):
        text = " ".join(sp for _, sp in ln)
        text = text[0].upper() + text[1:]
        wav = out / f"vo-{i:02d}.wav"
        subprocess.run([sys.executable, "-m", "piper", "-m", model, "--length-scale", SPEED, "-f", str(wav)],
                       input=text.encode(), check=True, capture_output=True)
        with wave.open(str(wav)) as w:
            d = w.getnframes() / w.getframerate()
        timing.append({"i": i, "start": round(t, 3), "dur": round(d, 3), "text": text})
        t += d + GAP
    return timing


def cap_times(lines, timing):
    capT = []
    for ln, x in zip(lines, timing):
        w = [len(sp) + (5 if re.search(r"[,.:?]$", sp) else 1) for _, sp in ln]
        tot, acc, ts = sum(w), 0, []
        for k in w:
            ts.append(x["start"] + x["dur"] * acc / tot)
            acc += k
        capT.append(ts)
    return capT


def anchors(scenes, capT):
    A = lambda a: capT[a[0]][min(a[1], len(capT[a[0]]) - 1)] + (a[2] if len(a) > 2 else 0)
    dings = []
    for sc in scenes:
        for it in sc.get("items", []):
            dings.append(A(it["at"]) + 0.05)
        for b in sc.get("bars", []):
            dings.append(A(b["at"]) + b.get("d", 1.0))
        for r in sc.get("rows", []):
            dings.append(A(r["at"]) + 0.35)
        if sc["type"] == "travel":
            dings.append(A(sc["until"]))
        if sc["type"] == "myth":
            dings.append(A(sc["yesAt"]) + 0.2)
    return sorted(dings)


# ---------------------------------------------------------------- audio --
MOODS = [  # (bpm, chords as midi triads)
    (104, [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]),   # Am F C G
    (100, [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]]),   # Dm Bb F C
    (108, [[52, 55, 59], [48, 52, 55], [55, 59, 62], [50, 54, 57]]),   # Em C G D
]


def music_mix(proj, timing, scene_starts, dings, END, mood, seed):
    rng = np.random.default_rng(seed)
    bpm, CH = MOODS[mood]
    BEAT = 60 / bpm
    BAR = 4 * BEAT
    n = int(SR * END)
    L, R = np.zeros(n), np.zeros(n)
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    tt = lambda d: np.arange(int(d * SR)) / SR
    env = lambda t, a, d: np.minimum(1, t / a) * np.exp(-t / d)

    def add(sig, start, pan=0.0, gain=1.0):
        i0 = int(start * SR)
        if i0 >= n or i0 < 0:
            return
        s = sig[: n - i0] * gain
        L[i0:i0 + len(s)] += s * np.sqrt(0.5 * (1 - pan))
        R[i0:i0 + len(s)] += s * np.sqrt(0.5 * (1 + pan))

    for b in range(int(END / BAR) + 1):
        ch = CH[b % 4]
        t = tt(BAR + 0.4)
        e = np.minimum(1, t / 0.25) * np.minimum(1, (BAR + 0.4 - t) / 0.4)
        for m in ch:
            for det in (-0.12, 0.12):
                f = hz(m) * 2 ** (det / 12)
                add((np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * e, b * BAR, pan=det * 4, gain=0.022)
        tb = tt(BAR)
        fb = hz(ch[0] - 12)
        add(np.sin(2 * np.pi * fb * tb) * env(tb, 0.01, 0.9), b * BAR, gain=0.10)
        add(np.sin(2 * np.pi * fb * tb) * env(tb, 0.01, 0.5), b * BAR + 2 * BEAT, gain=0.07)
        arp = ch + [ch[0] + 12, ch[1] + 12, ch[2], ch[1], ch[0] + 12]
        for k in range(8):
            tp = tt(0.5)
            f = hz(arp[k] + 12)
            add((np.sin(2 * np.pi * f * tp) + 0.25 * np.sin(6 * np.pi * f * tp)) * env(tp, 0.003, 0.12), b * BAR + k * BEAT / 2, pan=0.35 if k % 2 else -0.35, gain=0.035)
    kt = tt(0.35)
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt / 0.04)) * kt) * np.exp(-kt / 0.12)
    ht = tt(0.06)
    for i in range(int(END / BEAT)):
        t0 = i * BEAT
        if t0 > END - 1.2:
            break
        add(kick, t0, gain=0.22)
        add(np.diff(rng.standard_normal(len(ht)) * np.exp(-ht / 0.012), prepend=0), t0 + BEAT / 2, pan=0.2, gain=0.035)
        if i % 4 in (1, 3):
            st = tt(0.2)
            add(rng.standard_normal(len(st)) * np.exp(-st / 0.05), t0, gain=0.035)
    pos = (np.arange(n) / SR) % BEAT
    pump = 0.6 + 0.4 * np.minimum(1, pos / 0.18)
    L *= pump
    R *= pump
    for s0 in scene_starts:
        t = tt(0.7)
        k = np.exp(-((t - 0.45) ** 2) / 0.03)
        sm = np.convolve(rng.standard_normal(len(t)), np.ones(12) / 12, mode="same")
        add(sm * k, s0 - 0.45, pan=-0.3, gain=0.22)
        add(np.roll(sm, 37) * k, s0 - 0.45, pan=0.3, gain=0.22)
    for d0 in dings:
        t = tt(1.0)
        add((np.sin(2 * np.pi * 1975 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t)) * env(t, 0.002, 0.22), d0, gain=0.05)
    fade = np.ones(n)
    fi, fo = int(0.3 * SR), int(1.5 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    L *= fade
    R *= fade
    vo = np.zeros(n)
    for x in timing:
        with wave.open(str(proj / "assets" / "audio" / f"vo-{x['i']:02d}.wav")) as w:
            sr = w.getframerate()
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
        a = np.interp(np.arange(0, len(a), sr / SR), np.arange(len(a)), a)
        i0 = int(x["start"] * SR)
        vo[i0:i0 + len(a)] += a[: n - i0]
    win = int(0.25 * SR)
    lvl = np.convolve(np.abs(vo), np.ones(win) / win, mode="same")
    duck = 1 - 0.55 * np.clip(lvl / 0.03, 0, 1)
    L = L * duck + vo * 0.9
    R = R * duck + vo * 0.9
    st = np.stack([L, R], 1)
    st = st / np.abs(st).max() * 0.9
    tmp = proj / "renders" / "mix.wav"
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000",
                    "-c:a", "aac", "-b:a", "192k", str(proj / "assets" / "audio" / "mix.m4a")], check=True)
    tmp.unlink()


# ---------------------------------------------------------------- build --
def build(spec, model, seed):
    proj = VIDEOS / spec["id"]
    for d in ("assets/audio", "assets/fonts", "assets/vendor", "renders"):
        (proj / d).mkdir(parents=True, exist_ok=True)
    for f in FONTS.glob("*.woff2"):
        shutil.copy(f, proj / "assets" / "fonts" / f.name)
    shutil.copy(GSAP, proj / "assets" / "vendor" / "gsap.min.js")
    for f in ("hyperframes.json", "CLAUDE.md", "AGENTS.md"):
        shutil.copy(VIDEOS / "ahorro-vertical" / f, proj / f)
    (proj / "package.json").write_text(json.dumps({
        "name": spec["id"], "private": True, "type": "module",
        "scripts": {k: f"npx --yes hyperframes@0.8.162 {k if k != 'dev' else 'preview'}" for k in ("dev", "check", "render", "publish")},
    }, indent=2) + "\n")
    (proj / "meta.json").write_text(json.dumps({"id": spec["id"], "name": spec["id"], "createdAt": "2026-11-12T13:30:00.000Z"}, indent=2) + "\n")

    lines, scenes = norm(spec)
    timing = voice(lines, proj / "assets" / "audio", model)
    END = round(timing[-1]["start"] + timing[-1]["dur"] + 1.0, 2)
    starts = [0.0] + [timing[sc["from"]]["start"] for sc in scenes[1:]]
    scn = [[round(s, 3), round(starts[i + 1] if i + 1 < len(starts) else END, 3)] for i, s in enumerate(starts)]
    capT = cap_times(lines, timing)
    music_mix(proj, timing, starts[1:], anchors(scenes, capT), END, spec["mood"], seed)

    secs = "\n".join(
        f'      <section id="s{i}" class="clip" data-start="{a}" data-duration="{round(b - a + (0.12 if i + 1 < len(scn) else 0), 3)}" data-track-index="{1 + i % 2}"></section>'
        for i, (a, b) in enumerate(scn))
    page_spec = {"id": spec["id"], "lines": lines, "scenes": scenes}
    html = (KIT / "template.html").read_text()
    html = (html.replace("__TITLE__", spec["title"]).replace("__SECTIONS__", secs)
            .replace("__SPEC__", json.dumps(page_spec, ensure_ascii=False))
            .replace("__VO__", json.dumps([[x["start"], x["dur"]] for x in timing]))
            .replace("__SCN__", json.dumps(scn)).replace("__END__", str(END))
            .replace('<script src="assets/engine.js"></script>', "<script>\n" + (KIT / "engine.js").read_text() + "    </script>"))
    (proj / "index.html").write_text(html)
    (proj / "spec.json").write_text(json.dumps(page_spec, ensure_ascii=False, indent=1) + "\n")
    (proj / "vo-timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1) + "\n")
    print(f"{spec['id']:24s} {END:5.1f}s  {len(scenes)} scenes")


if __name__ == "__main__":
    model = sys.argv[1]
    want = set(sys.argv[2:])
    for k, spec in enumerate(SPECS):
        if not want or spec["id"] in want:
            build(spec, model, seed=100 + k)
