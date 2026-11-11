"""Builds the "Curiosidades de la vida" vertical shorts as HyperFrames projects.

Each episode = real photos (Wikimedia Commons, see CREDITS.md in each project)
+ a Spain-Spanish voice-over (Piper, voice es_ES-sharvard-medium, speaker M)
+ a generated music bed + two-line uppercase captions (white / yellow).

Usage (from this folder):
  python3 -I build.py <photos_dir>      # photos_dir holds the downloaded originals
Then in each project: npm run check && npm run render
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEOS = os.path.dirname(HERE)
PHOTOS = sys.argv[1]
TEMPLATE_PROJECT = os.path.join(VIDEOS, "flamencos-vertical")

# shots: (photo, start, object-position, zoom "in"/"out", pan px)
# captions: one entry per voice line; "|" splits on-screen chunks, "/" splits white / yellow line.
EPISODES = [
    {
        "slug": "curiosidades-nutrias",
        "ep": "01",
        "title": "Las nutrias marinas se dan la mano para dormir",
        "vo": "nutrias",
        "shots": [
            ("o_hands.jpg", 0.0, "50% 50%", "in", 0),
            ("o_four.jpg", 4.0, "48% 50%", "out", -60),
            ("o_snooze.jpg", 7.75, "50% 45%", "in", 0),
            ("o_face.jpg", 12.1, "45% 40%", "in", 0),
            ("o_hedin.jpg", 14.7, "40% 50%", "out", 40),
            ("o_octo.jpg", 19.2, "82% 55%", "in", -40),
            ("o_raft.jpg", 22.1, "42% 50%", "in", 0),
        ],
        "captions": [
            "¿Sabías que/las nutrias marinas|se dan la mano/para dormir?",
            "Lo hacen para que/la corriente|no las separe/mientras descansan.",
            "A veces, incluso/se enrollan en algas,|como si fueran/una manta.",
            "Y hay algo todavía/más sorprendente.",
            "Bajo el brazo tienen/un bolsillo de piel|donde guardan/su piedra favorita.",
            "La usan para/romper conchas|y abrir/su comida.",
            "¿Conocías/este secreto?",
        ],
        "credits": [
            ("Sea otters holding hands.jpg", "Joe Robertson", "CC BY 2.0"),
            ("Four sea otters.JPG", "Mike Baird", "CC BY 2.0"),
            ("Snoozing otter.jpg", "Doug Knuth", "CC BY-SA 2.0"),
            ("Enhydra lutris face.jpg", "Mike Baird", "CC BY 2.0"),
            ("Sea Otter (Enhydra lutris) (25169790524).jpg", "Marshal Hedin", "CC BY-SA 2.0"),
            ("Sea otter with a dinner of octopus on its chest.jpg", "National Park Service", "Public domain"),
            ("Sea Otters (Enhydra lutris), from a raft of about 15, (8625968237).jpg", "Mike Baird", "CC BY 2.0"),
        ],
    },
    {
        "slug": "curiosidades-cuervos",
        "ep": "02",
        "title": "Los cuervos recuerdan tu cara durante años",
        "vo": "cuervos",
        "shots": [
            ("c_amer2.jpg", 0.0, "55% 45%", "in", 0),
            ("c_smile.jpg", 3.95, "70% 50%", "out", -40),
            ("c_carr.jpg", 8.8, "45% 40%", "in", 50),
            ("c_amer.jpg", 14.0, "40% 45%", "in", 0),
            ("c_murder.jpg", 16.65, "50% 35%", "out", 0),
            ("c_flock.jpg", 21.7, "50% 45%", "in", -60),
            ("c_cong.jpg", 24.05, "50% 50%", "in", -50),
        ],
        "captions": [
            "¿Sabías que/los cuervos|pueden recordar/tu cara|/durante años?",
            "En un experimento,/unos científicos|con una máscara/atraparon|a varios/cuervos.",
            "Años después,/los cuervos|seguían graznando/a cualquiera|que llevara/esa máscara.",
            "Y hay algo todavía/más sorprendente.",
            "Enseñaron a otros/cuervos a reconocerla,|incluso a los que/nunca la habían visto.",
            "Así que mejor/llévate bien con ellos.",
            "¿Conocías/este secreto?",
        ],
        "credits": [
            ("AMERICAN CROW (7143675301).jpg", "cuatrok77", "CC BY 2.0"),
            ("Smiling crow - Flickr - marneejill.jpg", "marneejill", "CC BY-SA 2.0"),
            ("Carrion crows Corvus corone, Tottenham, London, England 1.jpg", "Acabashi", "CC BY-SA 4.0"),
            ("American Crow, Crystal Springs Rhododendron Garden, 201803 DSC0100 (cropped).jpg", "CEKeech", "CC0"),
            ("A Murder of Crows Perched in a in Tree, Spies Road, Freedom Township, Michigan - panoramio.jpg", "Dwight Burdette", "CC BY 3.0"),
            ("Crows - Flickr - ms.bailey.jpg", "Mary Bailey", "CC BY 2.0"),
            ("Crows congregating.jpg", "Controller666", "CC0"),
        ],
    },
    {
        "slug": "curiosidades-abejas",
        "ep": "03",
        "title": "Las abejas bailan para decirse dónde hay comida",
        "vo": "abejas",
        "shots": [
            ("b_flight.jpg", 0.0, "50% 40%", "in", 0),
            ("b_oreg.jpg", 3.65, "40% 45%", "out", 40),
            ("b_csiro.jpg", 6.1, "50% 45%", "in", -40),
            ("b_dance.png", 8.45, "50% 50%", "in", 0),
            ("b_macro.jpg", 11.7, "55% 50%", "in", 0),
            ("b_flower.jpg", 14.25, "50% 40%", "out", 0),
            ("b_busy.jpg", 18.2, "42% 40%", "in", 0),
            ("b_pollen.jpg", 20.5, "50% 50%", "in", -40),
        ],
        "captions": [
            "¿Sabías que las abejas/bailan|para decirse/dónde hay comida?",
            "Cuando una abeja/encuentra flores,|vuelve a la colmena/y baila|dibujando/un ocho.",
            "El ángulo del baile/indica la dirección|respecto/al sol.",
            "Y hay algo todavía/más sorprendente.",
            "Cuanto más tiempo/mueve el abdomen,|más lejos/están las flores.",
            "Es como un mapa/hecho con el cuerpo.",
            "¿Conocías/este secreto?",
        ],
        "credits": [
            ("Honey bee in flight.jpg", "Plaksin Alexander", "CC BY 4.0"),
            ("Honey bee on oregano flower.jpg", "Conall", "CC BY 4.0"),
            ("CSIRO ScienceImage 6586 A frame from a beehive at a cherry farm near Young New South Wales.jpg", "Nick Pitsas, CSIRO", "CC BY 3.0"),
            ("Waggle dance photo.png", "J. Tautz and M. Kleinhenz", "CC BY 2.5"),
            ("Macro shot of a honey bee on a flower (32068102187).jpg", "Ivan Radic", "CC BY 2.0"),
            ("Honey Bee (Ápis melliféra) on a flower.jpg", "Plaksin Alexander", "CC BY 4.0"),
            ("Considering-busy-honey bee-macro - Virginia - ForestWander.jpg", "ForestWander", "CC BY-SA 3.0 US"),
            ("Bee pollen cells.jpg", "John Pons", "CC BY-SA 4.0"),
        ],
    },
]


def words(s):
    return [w for w in re.sub(r"[¿?¡!.,:;/|]", " ", s).split() if w]


def caption_chunks(vo, captions):
    """Time each on-screen chunk from the word timestamps of its voice line."""
    out = []
    lines = vo["lines"]
    for li, (line, cap) in enumerate(zip(lines, captions)):
        assert words(cap) == words(line["text"]), (cap, line["text"])
        heard = line["words"]
        parts = cap.split("|")
        n_total = len(words(line["text"]))
        exact = len(heard) == n_total
        idx = 0
        for pi, part in enumerate(parts):
            nw = len(words(part))
            if exact:
                t0 = heard[idx][0] if pi else line["start"]
            else:
                t0 = line["start"] + (line["end"] - line["start"]) * idx / n_total
            idx += nw
            out.append({"t0": round(max(0.0, t0 - 0.05), 2), "part": part, "line": li})
    # each chunk ends when the next starts, or shortly after its line ends
    for i, c in enumerate(out):
        line_end = lines[c["line"]]["end"]
        nxt = out[i + 1]["t0"] if i + 1 < len(out) else None
        if nxt is not None and out[i + 1]["line"] == c["line"]:
            c["t1"] = nxt
        else:
            c["t1"] = round(min(line_end + 0.25, nxt) if nxt is not None else line_end + 0.6, 2)
    return out


def prep_photo(src, dst):
    im = Image.open(src).convert("RGB")
    im.thumbnail((1600, 1600))
    im.save(dst, "JPEG", quality=86)


def build(ep):
    proj = os.path.join(VIDEOS, ep["slug"])
    for d in ("assets/img", "assets/audio", "assets/fonts", "assets/vendor", "scripts", "renders"):
        os.makedirs(os.path.join(proj, d), exist_ok=True)
    for f in ("CLAUDE.md", "AGENTS.md", "hyperframes.json"):
        shutil.copy(os.path.join(TEMPLATE_PROJECT, f), proj)
    shutil.copy(os.path.join(TEMPLATE_PROJECT, "assets/vendor/gsap.min.js"), os.path.join(proj, "assets/vendor"))
    for f in os.listdir(os.path.join(HERE, "fonts")):
        shutil.copy(os.path.join(HERE, "fonts", f), os.path.join(proj, "assets/fonts"))
    json.dump({"name": ep["slug"], "private": True, "type": "module", "scripts": {
        "dev": "npx --yes hyperframes@0.8.162 preview",
        "check": "npx --yes hyperframes@0.8.162 check",
        "render": "npx --yes hyperframes@0.8.162 render",
        "publish": "npx --yes hyperframes@0.8.162 publish"}}, open(os.path.join(proj, "package.json"), "w"), indent=2)
    json.dump({"id": ep["slug"], "name": ep["slug"], "createdAt": "2026-11-11T23:00:00.000Z"},
              open(os.path.join(proj, "meta.json"), "w"), indent=2)

    vo = json.load(open(os.path.join(HERE, "vo", ep["vo"] + ".json")))
    dur = round(vo["total"] + 0.4, 2)
    hit_line = next(l for l in vo["lines"] if "sorprendente" in l["text"])
    hit = hit_line["start"]

    # audio: voice + generated bed
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(HERE, "vo", ep["vo"] + ".wav"),
                    "-af", "loudnorm=I=-15:TP=-1.5:LRA=7", "-ar", "48000", "-c:a", "aac", "-b:a", "160k",
                    os.path.join(proj, "assets/audio/voz.m4a")], check=True)
    cuts = [s[1] for s in ep["shots"][1:]]
    cfg = os.path.join(proj, "scripts/music.json")
    json.dump({"duration": dur, "cuts": cuts, "hit": hit}, open(cfg, "w"))
    shutil.copy(os.path.join(HERE, "make-music.py"), os.path.join(proj, "scripts/make-music.py"))
    tmp = os.path.join(proj, "renders", "_music.wav")
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "make-music.py"), cfg, tmp], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "loudnorm=I=-29:TP=-3:LRA=9", "-ar", "48000",
                    "-c:a", "aac", "-b:a", "160k", os.path.join(proj, "assets/audio/musica.m4a")], check=True)
    os.remove(tmp)
    shutil.copy(os.path.join(HERE, "vo", ep["vo"] + ".txt"), os.path.join(proj, "scripts/narracion.txt"))

    # photos
    shots_html = []
    shots_js = []
    for i, (photo, t0, pos, zoom, pan) in enumerate(ep["shots"]):
        name = f"shot{i + 1}.jpg"
        prep_photo(os.path.join(PHOTOS, photo), os.path.join(proj, "assets/img", name))
        t1 = ep["shots"][i + 1][1] if i + 1 < len(ep["shots"]) else dur
        start = max(0.0, t0 - (0.35 if i else 0.0))
        d = round(t1 - start + (0.0 if i + 1 == len(ep["shots"]) else 0.0), 2)
        shots_html.append(
            f'      <div id="sh{i + 1}" class="clip shot" data-start="{start:.2f}" data-duration="{d:.2f}" data-track-index="1" style="z-index:{i + 1}">\n'
            f'        <img id="im{i + 1}" src="assets/img/{name}" alt="" style="object-position:{pos}" data-layout-allow-overflow />\n'
            f'      </div>')
        s0, s1 = (1.16, 1.02) if zoom == "out" else (1.02, 1.16)
        shots_js.append(f'tl.fromTo("#im{i + 1}", {{ scale: {s0}, x: {-pan / 2:.0f} }}, {{ scale: {s1}, x: {pan / 2:.0f}, duration: {d:.2f}, ease: "none" }}, {start:.2f});')
        if i:
            shots_js.append(f'tl.fromTo("#sh{i + 1}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35, ease: "power1.inOut" }}, {start:.2f});')

    # captions
    chunks = caption_chunks(vo, ep["captions"])
    cap_html = []
    cap_js = []
    for i, c in enumerate(chunks):
        white, yellow = (c["part"].split("/") + [""])[:2]
        w = f'<span class="w">{html.escape(white.strip().upper())}</span>' if white.strip() else ""
        y = f'<span class="y">{html.escape(yellow.strip().upper())}</span>' if yellow.strip() else ""
        cap_html.append(f'        <div class="cap" id="cap{i}">{w}{y}</div>')
        cap_js.append(f'tl.fromTo("#cap{i}", {{ opacity: 0, scale: 0.86, y: 18 }}, {{ opacity: 1, scale: 1, y: 0, duration: 0.18, ease: "back.out(2.2)" }}, {c["t0"]:.2f});')
        cap_js.append(f'tl.to("#cap{i}", {{ opacity: 0, duration: 0.08 }}, {max(c["t0"] + 0.25, c["t1"] - 0.08):.2f});')

    page = PAGE.format(
        title=html.escape(ep["title"]), dur=f"{dur:.2f}", vodur=f'{vo["total"]:.2f}', ep=ep["ep"],
        shots="\n".join(shots_html), caps="\n".join(cap_html),
        js="\n      ".join(shots_js + cap_js), hit=f"{hit:.2f}", hit2=f"{hit + 0.08:.2f}")
    open(os.path.join(proj, "index.html"), "w").write(page)

    cr = [f"# Créditos de las fotos — {ep['title']}", "",
          "Todas las fotos son de Wikimedia Commons (https://commons.wikimedia.org).", ""]
    for i, (f, a, lic) in enumerate(ep["credits"], 1):
        cr.append(f"- shot{i}.jpg — «{f}» — {a} — {lic}")
    cr += ["", "Voz: Piper TTS, voz es_ES-sharvard-medium (hablante M).", "Música: generada con scripts/make-music.py."]
    open(os.path.join(proj, "CREDITS.md"), "w").write("\n".join(cr) + "\n")
    print("built", ep["slug"], dur, len(chunks), "captions")


PAGE = """<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Curiosidades de la vida — {title}</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Montserrat"; font-weight: 800; src: url("assets/fonts/montserrat-latin-800-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Montserrat"; font-weight: 900; src: url("assets/fonts/montserrat-latin-900-normal.woff2") format("woff2"); }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 100vw; height: 100vh; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; font-family: "Montserrat", system-ui, sans-serif; background: #000; }}
      .clip {{ position: absolute; inset: 0; }}
      .shot {{ overflow: hidden; background: #000; }}
      .shot img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(1.08) contrast(1.06); }}
      #grade {{ z-index: 50; pointer-events: none;
        background:
          linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 16%, rgba(0,0,0,0) 58%, rgba(0,0,0,0.62) 86%, rgba(0,0,0,0.75) 100%),
          radial-gradient(ellipse 85% 70% at 50% 48%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%); }}
      #flash {{ z-index: 55; background: #fff; opacity: 0; }}
      #brand {{ position: absolute; z-index: 60; left: 0; right: 0; top: 118px; text-align: center; font: 800 30px/1 "Montserrat", sans-serif; letter-spacing: 0.12em; color: #ffd400; -webkit-text-stroke: 6px #000; paint-order: stroke fill; text-shadow: 0 2px 6px rgba(0,0,0,0.85); }}
      #brand i {{ font-style: normal; color: #fff; margin: 0 14px; }}
      #caps {{ z-index: 70; }}
      .cap {{ position: absolute; left: 60px; right: 60px; top: 1380px; text-align: center; opacity: 0; }}
      .cap span {{ display: block; white-space: nowrap; font: 900 58px/1.14 "Montserrat", sans-serif; letter-spacing: 0.01em; -webkit-text-stroke: 9px #000; paint-order: stroke fill; text-shadow: 0 6px 14px rgba(0,0,0,0.7); }}
      .cap .w {{ color: #fff; }}
      .cap .y {{ color: #ffd400; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
      <audio id="voz" data-start="0" data-duration="{vodur}" data-volume="1" src="assets/audio/voz.m4a"></audio>
      <audio id="musica" data-start="0" data-duration="{dur}" data-volume="1" data-fade-out="1.2" src="assets/audio/musica.m4a"></audio>

{shots}

      <div id="grade" class="clip" data-start="0" data-duration="{dur}" data-track-index="2"></div>
      <div id="flash" class="clip" data-start="0" data-duration="{dur}" data-track-index="3"></div>
      <div id="brand" class="clip" data-start="0" data-duration="{dur}" data-track-index="4" style="inset: auto; left: 0; right: 0; top: 118px">CURIOSIDADES DE LA VIDA<i>•</i>EP. {ep}</div>
      <div id="caps" class="clip" data-start="0" data-duration="{dur}" data-track-index="5">
{caps}
      </div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {js}
      tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: 0.55, duration: 0.08, ease: "none" }}, {hit});
      tl.to("#flash", {{ opacity: 0, duration: 0.5, ease: "power2.out" }}, {hit2});
      tl.set({{}}, {{}}, {dur});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    for ep in EPISODES:
        build(ep)
