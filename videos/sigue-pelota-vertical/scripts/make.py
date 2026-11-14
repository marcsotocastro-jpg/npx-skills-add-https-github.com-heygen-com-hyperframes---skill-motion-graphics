"""'Sigue la pelota roja' attention challenge, 9:16.

Simulates the shuffle up front (seeded, so the red ball really travels a
trackable path), works out which number the red ball ends on, records the
voice-over with Piper (es_ES davefx), writes index.html and builds the mix
with the curiosity kit's music bed.

Usage: python3 -I scripts/make.py /path/to/es_ES-davefx-medium.onnx
"""
import json
import math
import pathlib
import random
import re
import shutil
import subprocess
import sys
import wave

ROOT = pathlib.Path(__file__).resolve().parent.parent
VIDEOS = ROOT.parent
sys.path.insert(0, str(VIDEOS / "_curiosidades-kit"))
from build import music_mix  # noqa: E402

MODEL = sys.argv[1]

# Ball anchors on the silhouette (canvas 1080x1920)
ANCH = [(540, 560), (470, 800), (610, 800), (540, 960), (316, 1040), (764, 1040),
        (486, 1260), (594, 1260), (486, 1470), (594, 1470), (382, 840), (698, 840)]
INIT = [0, 1, 5, 3]          # red, then the three others
# Phases: (start, end, period, duration, double-move chance)
PHASES = [(0.9, 6.4, 1.25, 0.85, 0.0), (7.9, 12.9, 0.95, 0.8, 0.15),
          (13.3, 18.3, 0.62, 0.52, 0.35), (18.7, 23.3, 0.44, 0.38, 0.55)]
COLOR_T = 7.3
STOP = 23.45


def simulate(seed):
    rng = random.Random(seed)
    pos = list(INIT)
    moves = []
    red_moves = 0

    def arc(a, b, sign):
        (x0, y0), (x1, y1) = ANCH[a], ANCH[b]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        k = sign * max(70, 0.32 * L)
        return mx - dy / L * k, my + dx / L * k

    for (t0, t1, per, dur, dbl) in PHASES:
        t = t0
        while t + dur <= t1 + 0.01:
            n_act = 2 if rng.random() < dbl else 1
            busy = set()
            for _ in range(n_act):
                free_balls = [b for b in range(4) if b not in busy]
                if len(free_balls) < 1:
                    break
                # make the red ball take part about half the time
                b = 0 if (0 in free_balls and rng.random() < 0.5) else rng.choice(free_balls)
                others = [o for o in free_balls if o != b]
                if others and rng.random() < 0.6:
                    o = rng.choice(others)
                    a1, a2 = pos[b], pos[o]
                    s = rng.choice((-1, 1))
                    for ball, fa, ta, sg in ((b, a1, a2, s), (o, a2, a1, s)):
                        cx, cy = arc(fa, ta, sg)
                        moves.append(dict(t=round(t, 3), d=dur, b=ball, x0=ANCH[fa][0], y0=ANCH[fa][1], cx=round(cx, 1), cy=round(cy, 1), x1=ANCH[ta][0], y1=ANCH[ta][1]))
                    pos[b], pos[o] = a2, a1
                    busy |= {b, o}
                    red_moves += int(0 in (b, o))
                else:
                    empty = [i for i in range(len(ANCH)) if i not in pos]
                    ta = rng.choice(empty)
                    fa = pos[b]
                    cx, cy = arc(fa, ta, rng.choice((-1, 1)))
                    moves.append(dict(t=round(t, 3), d=dur, b=b, x0=ANCH[fa][0], y0=ANCH[fa][1], cx=round(cx, 1), cy=round(cy, 1), x1=ANCH[ta][0], y1=ANCH[ta][1]))
                    pos[b] = ta
                    busy.add(b)
                    red_moves += int(b == 0)
            t += per
    order = sorted(range(4), key=lambda b: (ANCH[pos[b]][1], ANCH[pos[b]][0]))
    number = {b: k + 1 for k, b in enumerate(order)}
    return moves, pos, number, red_moves


# pick a seed where the red ball moves a lot and does not end as number 1
for seed in range(1, 500):
    moves, pos, number, red_moves = simulate(seed)
    if number[0] == 3 and red_moves >= 14 and pos[0] != INIT[0]:
        break
N = number[0]
NUM_WORD = {1: "uno", 2: "dos", 3: "tres", 4: "cuatro"}[N]

# --------------------------------------------------------------- voice --
LINES = [  # (start, chunks[(html, spoken)])
    (0.3, [("¿Puedes seguir", "¿Puedes seguir"), ("la pelota <b class=r>roja</b>?", "la pelota roja?")]),
    (3.2, [("Pero no le quites", "Pero no le quites"), ("el <b class=y>ojo</b>", "el ojo"), ("de encima", "de encima.")]),
    (6.2, [("Ahora todas", "Ahora todas"), ("cambian de <b class=g>color</b>", "cambian de color.")]),
    (12.9, [("Más <b class=o>rápido</b>...", "Más rápido.")]),
    (18.3, [("Y más rápido", "Y más rápido"), ("<b class=o>todavía</b>", "todavía.")]),
    (23.6, [("<b class=r>¡STOP!</b>", "¡Stop!"), ("¿Dónde está", "¿Dónde está"), ("la pelota <b class=r>roja</b>?", "la pelota roja?"), ("Tienes <b class=y>3 segundos</b>", "Tienes tres segundos.")]),
    (None, [(f"¡Era la <b class=g>número {N}</b>!", f"¡Era la número {NUM_WORD}!"), ("¿Acertaste?", "¿Acertaste?"), ("Dímelo en <b class=y>comentarios</b>", "Dímelo en comentarios.")]),
]
audio = ROOT / "assets" / "audio"
audio.mkdir(parents=True, exist_ok=True)
timing = []
for i, (st, chunks) in enumerate(LINES):
    text = " ".join(sp for _, sp in chunks)
    wav = audio / f"vo-{i:02d}.wav"
    subprocess.run([sys.executable, "-m", "piper", "-m", MODEL, "--length-scale", "0.85", "-f", str(wav)],
                   input=text.encode(), check=True, capture_output=True)
    with wave.open(str(wav)) as w:
        d = w.getnframes() / w.getframerate()
    timing.append({"i": i, "start": st, "dur": round(d, 3), "text": text})
# countdown follows line 5, reveal follows the countdown
CD = round(timing[5]["start"] + timing[5]["dur"] + 0.25, 2)
REVEAL = round(CD + 3.0, 2)
timing[6]["start"] = REVEAL + 0.15
for a, b in zip(timing, timing[1:]):
    assert a["start"] + a["dur"] < b["start"], f"voice overlap at line {a['i']}: {a['start'] + a['dur']:.2f} > {b['start']}"
END = round(timing[6]["start"] + timing[6]["dur"] + 1.2, 2)

caps = []
for (st, chunks), x in zip(LINES, timing):
    w = [len(sp) + (5 if re.search(r"[,.:?!]$", sp) else 1) for _, sp in chunks]
    tot, acc = sum(w), 0
    for k, (html, _) in enumerate(chunks):
        t0 = x["start"] + x["dur"] * acc / tot
        acc += w[k]
        t1 = x["start"] + x["dur"] * acc / tot if k < len(chunks) - 1 else x["start"] + x["dur"] + 0.25
        caps.append([round(t0, 3), round(t1, 3), html])

# --------------------------------------------------------------- audio --
(ROOT / "renders").mkdir(exist_ok=True)
dings = [CD, CD + 1, CD + 2, REVEAL, STOP + 0.05]
music_mix(ROOT, timing, [COLOR_T, 13.3, 18.7, STOP], dings, END, mood=1, seed=77)

# ---------------------------------------------------------------- html --
game = dict(moves=moves, init=[ANCH[a] for a in INIT], final=[ANCH[a] for a in pos], number=number, red=N,
            colorT=COLOR_T, stop=STOP, cd=CD, reveal=REVEAL, end=END, caps=caps,
            levels=[(COLOR_T + 0.4, 0.2, "#7CFF4F"), (13.3, 0.5, "#FFD23F"), (18.7, 0.8, "#FF9B25"), (21.5, 1.0, "#FF4D5E")],
            palette=[(COLOR_T, "#3DDC97", "#0f7a4d"), (13.3, "#4FE3FF", "#1176a3"), (18.7, "#B48CFF", "#5b2fc2"), (21.0, "#9BFF4F", "#3f8f12")])
tpl = (ROOT / "scripts" / "template.html").read_text()
html = tpl.replace("__GAME__", json.dumps(game)).replace("__END__", str(END))
(ROOT / "index.html").write_text(html)
for d in ("assets/fonts", "assets/vendor"):
    (ROOT / d).mkdir(parents=True, exist_ok=True)
for f in (VIDEOS / "ahorro-vertical" / "assets" / "fonts").glob("*.woff2"):
    shutil.copy(f, ROOT / "assets" / "fonts" / f.name)
shutil.copy(VIDEOS / "ahorro-vertical" / "assets" / "vendor" / "gsap.min.js", ROOT / "assets" / "vendor" / "gsap.min.js")
for f in ("hyperframes.json", "CLAUDE.md", "AGENTS.md"):
    shutil.copy(VIDEOS / "ahorro-vertical" / f, ROOT / f)
(ROOT / "package.json").write_text(json.dumps({
    "name": "sigue-pelota-vertical", "private": True, "type": "module",
    "scripts": {k: f"npx --yes hyperframes@0.8.162 {k if k != 'dev' else 'preview'}" for k in ("dev", "check", "render", "publish")},
}, indent=2) + "\n")
(ROOT / "meta.json").write_text(json.dumps({"id": "sigue-pelota-vertical", "name": "sigue-pelota-vertical", "createdAt": "2026-11-14T15:30:00.000Z"}, indent=2) + "\n")
print(f"seed={seed} red ends as number {N} ({red_moves} red moves, {len(moves)} moves)  CD={CD} REVEAL={REVEAL} END={END}")
for x in timing:
    print(f'{x["start"]:6.2f} {x["dur"]:5.2f}  {x["text"]}')
