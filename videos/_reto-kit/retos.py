"""Five 'follow the ball' challenges: stage, colours, anchors, script."""
import math


def ring(r, angles, cx=540, cy=1060):
    return [(round(cx + r * math.cos(math.radians(a)), 1), round(cy + r * math.sin(math.radians(a)), 1)) for a in angles]


PITCH = """
<rect class="neon" x="160" y="480" width="760" height="1160" rx="22"/>
<line class="line" x1="160" y1="1060" x2="920" y2="1060"/>
<circle class="line" cx="540" cy="1060" r="130"/><circle class="dot" cx="540" cy="1060" r="9"/>
<rect class="line" x="330" y="480" width="420" height="220"/><rect class="line" x="430" y="480" width="220" height="80"/>
<rect class="line" x="330" y="1420" width="420" height="220"/><rect class="line" x="430" y="1560" width="220" height="80"/>
<path class="line" d="M440 700 A115 115 0 0 0 640 700"/><path class="line" d="M440 1420 A115 115 0 0 1 640 1420"/>
<circle class="dot" cx="540" cy="640" r="7"/><circle class="dot" cx="540" cy="1480" r="7"/>"""

GRID = """
<rect class="neon" x="210" y="690" width="660" height="660" rx="44"/>
<line class="line" x1="430" y1="720" x2="430" y2="1320"/><line class="line" x1="650" y1="720" x2="650" y2="1320"/>
<line class="line" x1="240" y1="910" x2="840" y2="910"/><line class="line" x1="240" y1="1130" x2="840" y2="1130"/>"""

ORBITS = """
<g id="spin">
<circle class="line" cx="540" cy="1060" r="220"/><circle class="line" cx="540" cy="1060" r="360"/><circle class="line" cx="540" cy="1060" r="480" style="opacity:.6"/>
<circle class="dot" cx="760" cy="1060" r="10"/><circle class="dot" cx="285" cy="805" r="12"/><circle class="dot" cx="540" cy="1540" r="9"/>
</g>
<circle cx="540" cy="1060" r="74" style="fill:#ffcf5a;filter:drop-shadow(0 0 30px #ffb02e) drop-shadow(0 0 70px #ff8a1f)"/>"""

HEART = """
<path class="neon" d="M540 1500 C300 1340 140 1180 140 960 C140 780 270 660 410 660 C480 660 520 690 540 730 C560 690 600 660 670 660 C810 660 940 780 940 960 C940 1180 780 1340 540 1500 Z"/>
<path class="line" style="opacity:.35" d="M540 1420 C340 1290 210 1150 210 965 C210 820 315 730 420 730 C480 730 515 760 540 800 C565 760 600 730 660 730 C765 730 870 820 870 965 C870 1150 740 1290 540 1420 Z"/>"""

PHONE_ANCH = [(x, y) for y in (640, 810, 980, 1150, 1320, 1490) for x in (380, 540, 700)]
PHONE = ("""
<rect class="neon" x="250" y="470" width="580" height="1190" rx="80"/>
<rect class="dot" x="470" y="500" width="140" height="26" rx="13"/>
<rect class="dot" x="440" y="1612" width="200" height="10" rx="5" style="opacity:.7"/>"""
         + "".join(f'<rect class="soft" x="{x - 56}" y="{y - 56}" width="112" height="112" rx="28"/>' for x, y in PHONE_ANCH))

RETOS = [
    dict(id="reto-futbol-vertical", title="Sigue la pelota amarilla — campo de fútbol", color="amarilla", tc="#ffd23f", oc="#f4f4f4",
         neon="#5dff9e", glow="#1fc46a", fill="rgba(30,120,70,.16)", bg=("#123f2c", "#0b1f1a"), stage=PITCH, r=34, n=5, speed=1.0, answer=2,
         anchors=[(300, 620), (540, 600), (780, 620), (300, 860), (540, 880), (780, 860), (300, 1260), (540, 1240), (780, 1260),
                  (300, 1500), (540, 1520), (780, 1500), (540, 1060)],
         init=[12, 1, 3, 8, 10],
         palette=["#3DDC97", "#4FE3FF", "#B48CFF", "#FF6FD8"],
         intro=[("¿Eres capaz de seguir", "¿Eres capaz de seguir"), ("la pelota <b class=t>amarilla</b>?", "la pelota amarilla?")],
         intro2=[("No la pierdas", "No la pierdas"), ("de vista ni un <b class=y>segundo</b>", "de vista ni un segundo.")]),
    dict(id="reto-tablero-vertical", title="Sigue la pelota azul — tablero", color="azul", tc="#3d8bff", oc="#ffd23f",
         neon="#ff5edb", glow="#c21bb0", fill="rgba(140,30,120,.16)", bg=("#3b0f40", "#1a0b24"), stage=GRID, r=40, n=4, speed=0.95, answer=4,
         anchors=[(x, y) for y in (800, 1020, 1240) for x in (320, 540, 760)],
         init=[4, 0, 2, 7],
         palette=["#3DDC97", "#FF9B25", "#FF6FD8", "#9BFF4F"],
         intro=[("¿Puedes seguir", "¿Puedes seguir"), ("la pelota <b class=t>azul</b>?", "la pelota azul?")],
         intro2=[("Fíjate bien", "Fíjate bien"), ("en <b class=y>ella</b>", "en ella.")]),
    dict(id="reto-orbitas-vertical", title="Sigue la pelota rosa — órbitas", color="rosa", tc="#ff4fc3", oc="#cfe9ff",
         neon="#8fa8ff", glow="#4b5cff", fill="none", bg=("#1c2468", "#0e1236"), stage=ORBITS, r=34, n=5, speed=0.9, answer=5, spin=True,
         anchors=ring(220, (45, 135, 225, 315)) + ring(360, (0, 90, 180, 270)) + ring(480, (30, 150, 210, 330)),
         init=[5, 0, 3, 6, 11],
         palette=["#4FE3FF", "#9BFF4F", "#FF9B25", "#B48CFF"],
         intro=[("¿Puedes seguir", "¿Puedes seguir"), ("la pelota <b class=t>rosa</b>?", "la pelota rosa?")],
         intro2=[("Ojo, que este", "Ojo, que este"), ("es más <b class=r>difícil</b>", "es más difícil.")]),
    dict(id="reto-corazon-vertical", title="Sigue la pelota verde — corazón", color="verde", tc="#3ddc6b", oc="#ffd23f",
         neon="#ff4f6d", glow="#ff1f4a", fill="rgba(150,20,50,.18)", bg=("#40101f", "#1d0b14"), stage=HEART, r=38, n=4, speed=0.95, answer=1,
         anchors=[(320, 860), (760, 860), (540, 900), (260, 1000), (820, 1000), (420, 1080), (660, 1080), (540, 1200),
                  (420, 1290), (660, 1290), (540, 1400)],
         init=[10, 0, 1, 7],
         palette=["#4FE3FF", "#B48CFF", "#FF9B25", "#E8E8FF"],
         intro=[("¿Puedes seguir", "¿Puedes seguir"), ("la pelota <b class=t>verde</b>?", "la pelota verde?")],
         intro2=[("Pon toda", "Pon toda"), ("tu <b class=y>atención</b>", "tu atención en ella.")]),
    dict(id="reto-movil-vertical", title="Sigue la pelota naranja — nivel difícil", color="naranja", tc="#ff8a1f", oc="#c9d4ff",
         neon="#4fa8ff", glow="#1f6bff", fill="rgba(20,50,120,.2)", bg=("#10285a", "#0b1430"), stage=PHONE, r=32, n=6, speed=0.8, answer=6,
         anchors=PHONE_ANCH,
         init=[7, 0, 2, 9, 15, 17],
         palette=["#4FE3FF", "#B48CFF", "#9BFF4F", "#FF6FD8"],
         intro=[("<b class=r>Nivel difícil</b>:", "Nivel difícil:"), ("¿puedes seguir", "¿puedes seguir"), ("la pelota <b class=t>naranja</b>?", "la pelota naranja?")],
         intro2=[("Hay <b class=y>6 pelotas</b>", "Hay seis pelotas."), ("No la pierdas", "No la pierdas.")]),
]
