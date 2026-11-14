"""Build 'follow the ball' challenge videos from retos.py.

For each challenge: simulate the shuffle with a seed chosen so the target
ball moves a lot and ends on the planned number, record the voice-over
with Piper (es_ES davefx), write index.html from template.html and build
the mix with the curiosity kit's music bed. Render afterwards with
`npm run render` in each project.

Usage: python3 -I make.py /path/to/es_ES-davefx-medium.onnx [id ...]
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

KIT = pathlib.Path(__file__).resolve().parent
VIDEOS = KIT.parent
sys.path.insert(0, str(VIDEOS / "_curiosidades-kit"))
from build import music_mix  # noqa: E402
from retos import RETOS  # noqa: E402

BASE_PHASES = [(0.9, 6.4, 1.25, 0.85, 0.0), (7.9, 12.9, 0.95, 0.8, 0.15),
               (13.3, 18.3, 0.62, 0.52, 0.35), (18.7, 23.3, 0.44, 0.38, 0.55)]
COLOR_T, STOP = 7.3, 23.45
WORDS = {1: "uno", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis"}


def darker(hexc, k=0.45):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))


def simulate(cfg, seed):
    rng = random.Random(seed)
    A, n = cfg["anchors"], cfg["n"]
    pos = list(cfg["init"])
    moves, tmoves = [], 0
    f = cfg["speed"]

    def arc(a, b, sign):
        (x0, y0), (x1, y1) = A[a], A[b]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        k = sign * max(60, 0.3 * L)
        return (x0 + x1) / 2 - dy / L * k, (y0 + y1) / 2 + dx / L * k

    def mv(t, d, b, fa, ta, s):
        cx, cy = arc(fa, ta, s)
        moves.append(dict(t=round(t, 3), d=round(d, 3), b=b, x0=A[fa][0], y0=A[fa][1], cx=round(cx, 1), cy=round(cy, 1), x1=A[ta][0], y1=A[ta][1]))

    for (t0, t1, per, dur, dbl) in BASE_PHASES:
        per, dur = per * f, dur * f
        t = t0
        while t + dur <= t1 + 0.01:
            busy = set()
            for _ in range(2 if rng.random() < dbl + (0.1 if n > 4 else 0) else 1):
                free = [b for b in range(n) if b not in busy]
                if not free:
                    break
                b = 0 if (0 in free and rng.random() < 0.45) else rng.choice(free)
                rest = [o for o in free if o != b]
                if rest and rng.random() < 0.6:
                    o = rng.choice(rest)
                    s = rng.choice((-1, 1))
                    mv(t, dur, b, pos[b], pos[o], s)
                    mv(t, dur, o, pos[o], pos[b], s)
                    pos[b], pos[o] = pos[o], pos[b]
                    busy |= {b, o}
                    tmoves += int(0 in (b, o))
                else:
                    empty = [i for i in range(len(A)) if i not in pos]
                    ta = rng.choice(empty)
                    mv(t, dur, b, pos[b], ta, rng.choice((-1, 1)))
                    pos[b] = ta
                    busy.add(b)
                    tmoves += int(b == 0)
            t += per
    order = sorted(range(n), key=lambda b: (A[pos[b]][1], A[pos[b]][0]))
    number = {b: k + 1 for k, b in enumerate(order)}
    return moves, pos, number, tmoves


def build(cfg, model, base_seed):
    root = VIDEOS / cfg["id"]
    for d in ("assets/audio", "assets/fonts", "assets/vendor", "renders"):
        (root / d).mkdir(parents=True, exist_ok=True)
    for seed in range(base_seed, base_seed + 2000):
        moves, pos, number, tm = simulate(cfg, seed)
        if number[0] == cfg["answer"] and tm >= 14 and pos[0] != cfg["init"][0]:
            break
    else:
        raise SystemExit(f"no seed for {cfg['id']}")
    N, col = number[0], cfg["color"]
    lines = [
        (0.3, cfg["intro"]),
        (3.2, cfg["intro2"]),
        (6.2, [("Ahora todas", "Ahora todas"), ("cambian de <b class=g>color</b>", "cambian de color.")]),
        (12.9, [("Más <b class=o>rápido</b>...", "Más rápido.")]),
        (18.3, [("Y más rápido", "Y más rápido"), ("<b class=o>todavía</b>", "todavía.")]),
        (23.6, [("<b class=r>¡STOP!</b>", "¡Stop!"), ("¿Dónde está", "¿Dónde está"), (f"la pelota <b class=t>{col}</b>?", f"la pelota {col}?"), ("Tienes <b class=y>3 segundos</b>", "Tienes tres segundos.")]),
        (None, [(f"¡Era la <b class=g>número {N}</b>!", f"¡Era la número {WORDS[N]}!"), ("¿Acertaste?", "¿Acertaste?"), ("Dímelo en <b class=y>comentarios</b>", "Dímelo en comentarios.")]),
    ]
    timing = []
    for i, (st, chunks) in enumerate(lines):
        text = " ".join(sp for _, sp in chunks)
        wav = root / "assets" / "audio" / f"vo-{i:02d}.wav"
        subprocess.run([sys.executable, "-m", "piper", "-m", model, "--length-scale", "0.85", "-f", str(wav)],
                       input=text.encode(), check=True, capture_output=True)
        with wave.open(str(wav)) as w:
            d = w.getnframes() / w.getframerate()
        timing.append({"i": i, "start": st, "dur": round(d, 3), "text": text})
    CD = round(timing[5]["start"] + timing[5]["dur"] + 0.25, 2)
    REVEAL = round(CD + 3.0, 2)
    timing[6]["start"] = REVEAL + 0.15
    for a, b in zip(timing, timing[1:]):
        assert a["start"] + a["dur"] < b["start"], f"{cfg['id']}: voice overlap after line {a['i']}"
    END = round(timing[6]["start"] + timing[6]["dur"] + 1.2, 2)
    caps = []
    for (_, chunks), x in zip(lines, timing):
        w = [len(sp) + (5 if re.search(r"[,.:?!]$", sp) else 1) for _, sp in chunks]
        tot, acc = sum(w), 0
        for k, (html, _) in enumerate(chunks):
            t0 = x["start"] + x["dur"] * acc / tot
            acc += w[k]
            t1 = x["start"] + x["dur"] * acc / tot if k < len(chunks) - 1 else x["start"] + x["dur"] + 0.25
            caps.append([round(t0, 3), round(t1, 3), html])

    music_mix(root, timing, [COLOR_T, 13.3, 18.7, STOP], [STOP + 0.05, CD, CD + 1, CD + 2, REVEAL], END, mood=len(cfg["id"]) % 3, seed=base_seed)

    pal = cfg["palette"]
    game = dict(n=cfg["n"], r=cfg["r"], moves=moves, init=[cfg["anchors"][a] for a in cfg["init"]], number=number, red=N,
                tc=cfg["tc"], td=darker(cfg["tc"]), oc=cfg["oc"], od=darker(cfg["oc"], 0.55), fc="#7d68e8", fd="#2e2180",
                colorT=COLOR_T, stop=STOP, cd=CD, reveal=REVEAL, end=END, caps=caps, spin=bool(cfg.get("spin")), bumps=[13.3, 18.7],
                levels=[(COLOR_T + 0.4, 0.2, "#7CFF4F"), (13.3, 0.5, "#FFD23F"), (18.7, 0.8, "#FF9B25"), (21.5, 1.0, "#FF4D5E")],
                palette=[(t, c, darker(c)) for t, c in zip((COLOR_T, 13.3, 18.7, 21.0), pal)])
    label = f'SIGUE LA PELOTA <em>{col.upper()}</em>'
    html = (KIT / "template.html").read_text()
    for k, v in {"__TITLE__": cfg["title"], "__NEON__": cfg["neon"], "__GLOW__": cfg["glow"], "__FILL__": cfg["fill"],
                 "__TC__": cfg["tc"], "__BG1__": cfg["bg"][0], "__BG2__": cfg["bg"][1], "__STAGE__": cfg["stage"],
                 "__D__": str(2 * cfg["r"]), "__NF__": str(int(cfg["r"] * 1.15)), "__LABEL__": label,
                 "__GAME__": json.dumps(game), "__END__": str(END)}.items():
        html = html.replace(k, v)
    (root / "index.html").write_text(html)
    for fnt in (VIDEOS / "ahorro-vertical" / "assets" / "fonts").glob("*.woff2"):
        shutil.copy(fnt, root / "assets" / "fonts" / fnt.name)
    shutil.copy(VIDEOS / "ahorro-vertical" / "assets" / "vendor" / "gsap.min.js", root / "assets" / "vendor" / "gsap.min.js")
    for fl in ("hyperframes.json", "CLAUDE.md", "AGENTS.md"):
        shutil.copy(VIDEOS / "ahorro-vertical" / fl, root / fl)
    (root / "package.json").write_text(json.dumps({
        "name": cfg["id"], "private": True, "type": "module",
        "scripts": {k: f"npx --yes hyperframes@0.8.162 {k if k != 'dev' else 'preview'}" for k in ("dev", "check", "render", "publish")},
    }, indent=2) + "\n")
    (root / "meta.json").write_text(json.dumps({"id": cfg["id"], "name": cfg["id"], "createdAt": "2026-11-14T16:00:00.000Z"}, indent=2) + "\n")
    (root / "game.json").write_text(json.dumps(dict(seed=seed, answer=N, target_moves=tm, timing=timing), ensure_ascii=False, indent=1) + "\n")
    print(f"{cfg['id']:24s} seed={seed:4d} answer={N} target_moves={tm} moves={len(moves)} END={END}")


if __name__ == "__main__":
    model = sys.argv[1]
    want = set(sys.argv[2:])
    for k, cfg in enumerate(RETOS):
        if not want or cfg["id"] in want:
            build(cfg, model, base_seed=1 + 1000 * k)
