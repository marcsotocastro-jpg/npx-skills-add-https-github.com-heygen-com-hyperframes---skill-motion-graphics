"""Place the ElevenLabs voice-over on the video timeline, one block per scene, and duck the music under it.

The voice file is cut at the middle of its pauses; each block is moved so its first word lands on its scene.
Usage: python3 -I scripts/place-voice.py   (run from the project folder)
Writes assets/audio/yoco-voz.m4a (voice alone, 60 s) and assets/audio/yoco-mix.m4a (voice + ducked music).
"""
import subprocess

SRC = "assets/audio/yoco-voz-original.mp3"
BGM = "assets/audio/yoco-bgm.m4a"
DUR = 60.0
# (cut start, first word, cut end) in the source file  ->  film time of the first word
BLOCKS = [
    ((0.00, 0.00, 4.42), 0.40),    # Hola. Te presento la nueva web de YOCOMOTORS…
    ((4.42, 4.62, 11.97), 4.90),   # Nada más entrar… Directo, de un vistazo.
    ((11.97, 12.19, 16.79), 12.75),  # Tu cinco de cinco en Google…
    ((16.79, 16.99, 23.73), 17.30),  # Explica por qué elegirte…
    ((23.73, 23.94, 29.14), 24.10),  # Todos tus servicios…
    ((29.14, 29.31, 33.45), 29.40),  # Y cómo trabajáis…
    ((33.45, 33.64, 36.66), 34.00),  # Una sección para conductores de paso…
    ((36.66, 36.81, 40.22), 38.80),  # Las opiniones reales…
    ((40.22, 40.35, 43.62), 43.60),  # Dirección, horario y teléfono…
    ((43.62, 43.78, 46.20), 48.20),  # Y en el móvil, WhatsApp siempre a mano.
    ((46.20, 46.40, 51.23), 52.00),  # Tu coche en buenas manos… ¿La vemos juntos?
]

parts, labels = [], []
for i, ((a, onset, b), at) in enumerate(BLOCKS):
    delay = int(round((at - (onset - a)) * 1000))
    parts.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a - 0.04:.3f}:d=0.04,adelay={delay}|{delay}[v{i}]")
    labels.append(f"[v{i}]")
voice = ";".join(parts) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{DUR},aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=9"

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", voice + "[vo]", "-map", "[vo]", "-c:a", "aac", "-b:a", "192k", "assets/audio/yoco-voz.m4a"], check=True)
mix = (
    "[1:a]aresample=48000,asplit=2[vo][sc];"
    "[0:a]aresample=48000,volume=-6dB[m];"
    "[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=30:release=600:makeup=1[duck];"
    f"[duck][vo]amix=inputs=2:normalize=0,atrim=0:{DUR},loudnorm=I=-14:TP=-1.5:LRA=9[out]"
)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", BGM, "-i", "assets/audio/yoco-voz.m4a", "-filter_complex", mix, "-map", "[out]", "-c:a", "aac", "-b:a", "192k", "assets/audio/yoco-mix.m4a"], check=True)
print("wrote assets/audio/yoco-voz.m4a and assets/audio/yoco-mix.m4a")
