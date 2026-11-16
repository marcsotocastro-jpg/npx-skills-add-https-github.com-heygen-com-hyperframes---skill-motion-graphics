import json, subprocess, os, sys
S = os.path.dirname(os.path.abspath(__file__))
voice, speed = sys.argv[1], sys.argv[2]
spec = json.load(open(f"{S}/script.json"))
env = dict(os.environ, HYPERFRAMES_PYTHON=f"{S}/../ttsvenv/bin/python")
for vid, d in spec.items():
    for i, (a, b, text) in enumerate(d["lines"]):
        out = f"{S}/{vid}-{i}.wav"
        subprocess.run(["npx", "--yes", "hyperframes@0.8.162", "tts", text, "-v", voice, "-l", "es", "-s", speed, "-o", out],
                       env=env, capture_output=True, check=True)
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
        flag = "OK " if a + dur <= b else "LONG"
        print(f"{flag} {vid}[{i}] {dur:.2f}s slot {b-a:.2f}s  {text}")
