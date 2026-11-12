"""Voice-over for the "2 € al día" video, one Piper TTS clip per line.

Writes assets/audio/vo-XX.wav and scripts/vo-timing.json (start/duration of
every line on the final timeline). Numbers are spelled out so Piper reads
them naturally; the on-screen captions live in index.html.

Usage (voice from huggingface.co/rhasspy/piper-voices, es_ES davefx medium):
  python3 -I scripts/make-voice.py /path/to/es_ES-davefx-medium.onnx
"""
import json
import pathlib
import subprocess
import sys
import wave

LINES = [
    "¿Qué pasa si ahorras dos euros al día durante diez años?",
    "Pues lo primero que pasa es que no notas nada.",
    "Dos euros es, más o menos, lo que cuesta un café.",
    "Pero al final del primer año, ya tienes setecientos treinta euros.",
    "Mes uno: unos sesenta euros. Año cinco: tres mil seiscientos cincuenta.",
    "Y en el año diez: siete mil trescientos euros. Solo de tu bolsillo.",
    "Si lo metes en una cuenta al tres por ciento anual, tendrías unos ocho mil quinientos.",
    "Con un fondo indexado al siete por ciento de media, unos diez mil quinientos. Pero ojo: eso no está garantizado.",
    "Error típico: pensar que en casa está más seguro.",
    "Con una inflación del dos por ciento, esos siete mil trescientos euros comprarán lo que hoy unos seis mil.",
    "¿Y tú, en qué gastas tus dos euros al día? Te leo en comentarios.",
]
START = 0.25   # first line starts here
GAP = 0.22     # silence between lines

root = pathlib.Path(__file__).resolve().parent.parent
out = root / "assets" / "audio"
model = sys.argv[1]
t = START
timing = []
for i, line in enumerate(LINES):
    wav = out / f"vo-{i:02d}.wav"
    subprocess.run(
        [sys.executable, "-m", "piper", "-m", model, "--length-scale", "0.8", "-f", str(wav)],
        input=line.encode(), check=True, capture_output=True,
    )
    with wave.open(str(wav)) as w:
        d = w.getnframes() / w.getframerate()
    timing.append({"i": i, "start": round(t, 3), "dur": round(d, 3), "text": line})
    t += d + GAP
(root / "scripts" / "vo-timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1))
for x in timing:
    print(f'{x["i"]:2d} {x["start"]:6.2f} {x["dur"]:5.2f}  {x["text"]}')
print("end", round(t, 2))
