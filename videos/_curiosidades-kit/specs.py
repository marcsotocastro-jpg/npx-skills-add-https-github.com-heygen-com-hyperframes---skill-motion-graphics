"""Scripts and scene lists for the ten curiosity videos.

Each line is a list of caption chunks: (shown_html, spoken_text) or a plain
string when both are the same. The voice-over says the spoken parts joined;
captions show one chunk at a time. Anchors are [line, chunk(, offset s)].

Sources for the numbers are listed in SOURCES.md next to this file.
"""

SPECS = [
# 1 ------------------------------------------------------------------------
dict(id="pasos-vertical", title="10.000 pasos al día", mood=0, lines=[
  ["¿Qué pasa si", ("caminas <b>10.000</b>", "caminas diez mil"), ("pasos al <b>DÍA</b>?", "pasos al día?")],
  ["Pues lo primero:", ("recorres entre", "recorres entre"), ("<b>7 y 8 km</b>", "siete y ocho kilómetros.")],
  ["Y quemas", ("entre <b>300 y 500</b>", "entre trescientas y quinientas"), "calorías,", ("según tu <b>PESO</b>", "según tu peso.")],
  ["En una semana:", ("<b>70.000</b> pasos", "setenta mil pasos."), "En un año:", ("más de <b>3,5 millones</b>", "más de tres millones y medio.")],
  [("Unos <b>2.600 km</b>", "unos dos mil seiscientos kilómetros."), "Más que de Madrid", ("a <b>BERLÍN</b>", "a Berlín"), "en línea recta."],
  ["Error típico:", ("creer que 10.000", "creer que diez mil"), ("es una cifra <b>CIENTÍFICA</b>", "es una cifra científica.")],
  ["Salió de un podómetro", ("<b>JAPONÉS</b> de 1965", "japonés de mil novecientos sesenta y cinco."), ("Y en mayores de 60,", "y en mayores de sesenta,"), "el beneficio se estabiliza", ("entre <b>6.000 y 8.000</b>", "entre seis mil y ocho mil pasos.")],
  ["¿Cuántos pasos", ("das tú al <b>DÍA</b>?", "das tú al día?"), ("Te leo en <b>COMENTARIOS</b>", "te leo en comentarios.")],
], scenes=[
  dict(type="hook", from_=0, icon="shoe", chip="10.000 pasos", cal=["DÍA", "1"]),
  dict(type="duo", from_=1, items=[dict(icon="foot", label="7–8 km", at=[1, 2]), dict(icon="flame", label="300–500 kcal", at=[2, 1])], sym="+"),
  dict(type="bars", from_=3, note="Escala comprimida para que se vean todas las barras.", bars=[
    dict(label="DÍA", h=0.06, val="10.000", at=[3, 0], cv=10000, unit="pasos"),
    dict(label="SEMANA", h=0.16, val="70.000", at=[3, 1], cv=70000, unit="pasos"),
    dict(label="AÑO", h=1, val="3.650.000", at=[3, 3], cfrom=70000, cv=3650000, unit="pasos", d=1.3)]),
  dict(type="travel", from_=4, a=dict(icon="pin", label="MADRID"), b=dict(icon="pin", label="BERLÍN"), mover="dot", at=[4, 0], until=[4, 2],
       counter=dict(**{"from": 0, "to": 2600, "unit": "km", "final": "≈ 2.600"}), chips=[dict(text="1.870 km EN LÍNEA RECTA", at=[4, 3], cls="or")]),
  dict(type="myth", from_=5, no="10.000 es una cifra <b>CIENTÍFICA</b>", yes="Viene de un podómetro <b>JAPONÉS</b> de 1965", yesAt=[6, 0], illus="shoe",
       cmp=dict(at=[6, 2], sym="·", items=[dict(v="8–10 mil", label="MENORES DE 60"), dict(v="6–8 mil", label="MAYORES DE 60")]),
       note="Paluch et al., The Lancet Public Health (2022): 15 estudios, 47.471 adultos."),
  dict(type="close", from_=7, icon="shoe"),
]),
# 2 ------------------------------------------------------------------------
dict(id="luz-sol-vertical", title="La luz del Sol", mood=1, lines=[
  ["¿Cuánto tarda", ("la luz del <b>SOL</b>", "la luz del Sol"), ("en llegar a la <b>TIERRA</b>?", "en llegar a la Tierra?")],
  ["Pues unos", ("<b>8 minutos</b>", "ocho minutos"), ("y <b>20 segundos</b>", "y veinte segundos.")],
  ["La luz viaja a casi", ("<b>300.000 km</b>", "trescientos mil kilómetros"), ("por <b>SEGUNDO</b>", "por segundo.")],
  ["Y el Sol está", ("a unos <b>150 millones</b>", "a unos ciento cincuenta millones"), "de kilómetros."],
  [("Desde la <b>LUNA</b>,", "desde la Luna,"), "la luz tarda", ("poco más de <b>1 segundo</b>", "poco más de un segundo."), ("Desde <b>MARTE</b>,", "desde Marte,"), ("entre <b>3 y 22 minutos</b>", "entre tres y veintidós minutos,"), "según dónde esté."],
  ["Error típico:", "creer que ves el Sol", ("como está <b>AHORA</b>", "como está ahora.")],
  ["Lo ves como era", ("hace <b>8 minutos</b>", "hace ocho minutos."), "Si se apagara,", ("tardarías eso", "tardarías ese tiempo"), ("en <b>ENTERARTE</b>", "en enterarte.")],
  ["¿Lo sabías?", ("<b>GUÁRDALO</b> y compártelo", "guárdalo y compártelo"), "con quien no se lo crea."],
], scenes=[
  dict(type="hook", from_=0, icon="sun", chip="LUZ SOLAR", cal=["MIN", "?"]),
  dict(type="travel", from_=1, a=dict(icon="sun", label="SOL"), b=dict(icon="earth", label="TIERRA"), mover="beam", at=[1, 0], until=[1, 2, 0.8],
       counter=dict(**{"from": 0, "to": 500, "mode": "mmss", "unit": "min"}),
       chips=[dict(text="≈ 300.000 km/s", at=[2, 1], cls="cy"), dict(text="150 MILLONES DE KM", at=[3, 1], cls="or")]),
  dict(type="bars", from_=4, note="Escala comprimida. Marte: según su posición respecto a la Tierra.", bars=[
    dict(label="LUNA", h=0.03, val="1,3 s", at=[4, 2]),
    dict(label="SOL", h=0.6, val="8 min 20 s", at=[4, 0]),
    dict(label="MARTE", h=1, val="3–22 min", at=[4, 4], color="orange")]),
  dict(type="myth", from_=5, no="Ves el Sol como está <b>AHORA</b>", yes="Lo ves como era hace <b>8 MIN</b>", yesAt=[6, 0], illus="sun",
       cmp=dict(at=[6, 2], sym="→", items=[dict(v="☀ se apaga", label="EN EL SOL"), dict(v="+8:20", label="LO NOTARÍAS AQUÍ")])),
  dict(type="close", from_=7, icon="earth"),
]),
# 3 ------------------------------------------------------------------------
dict(id="corazon-vertical", title="Los latidos del corazón", mood=2, lines=[
  ["¿Cuántas veces", ("late tu <b>CORAZÓN</b>", "late tu corazón"), ("en un <b>DÍA</b>?", "en un día?")],
  ["Pues unas", ("<b>100.000</b> veces", "cien mil veces.")],
  ["En reposo, un adulto", ("late entre <b>60 y 100</b>", "late entre sesenta y cien"), "veces por minuto."],
  ["En un año:", ("unos <b>36 millones</b>", "unos treinta y seis millones de latidos."), ("En 80 años de vida:", "en ochenta años de vida:"), ("cerca de <b>3.000 millones</b>", "cerca de tres mil millones.")],
  ["Y cada minuto", ("bombea unos <b>5 litros</b>", "bombea unos cinco litros de sangre."), "Al día, más de", ("<b>7.000 litros</b>", "siete mil litros.")],
  ["Error típico:", "creer que el corazón", ("está a la <b>IZQUIERDA</b>", "está a la izquierda.")],
  [("Está casi en el <b>CENTRO</b>", "está casi en el centro del pecho,"), "entre los pulmones,", "solo un poco", ("inclinado a la izquierda", "inclinado hacia la izquierda.")],
  ["¿Cuántas pulsaciones", ("tienes <b>TÚ</b> en reposo?", "tienes tú en reposo?"), ("Te leo en <b>COMENTARIOS</b>", "te leo en comentarios.")],
], scenes=[
  dict(type="hook", from_=0, icon="heart", chip="LATIDOS", cal=["DÍA", "1"]),
  dict(type="duo", from_=1, items=[dict(icon="heart", label="≈ 100.000 / día", at=[1, 1]), dict(icon="clock", label="60–100 / min", at=[2, 1])], sym="·"),
  dict(type="bars", from_=3, note="Escala comprimida. Cálculo con unas 70 pulsaciones por minuto.", bars=[
    dict(label="DÍA", h=0.12, val="100.000", at=[3, 0], cv=100000, unit="latidos"),
    dict(label="AÑO", h=0.45, val="36 mill.", at=[3, 1], cv=36, unit="millones"),
    dict(label="80 AÑOS", h=1, val="2.900 mill.", at=[3, 3], cv=2900, unit="millones", final="≈ 3.000", color="red", d=1.3)]),
  dict(type="steps", from_=4, rows=[
    dict(badge="1 MIN", icon="drop", text="sangre bombeada en reposo", val="≈ 5 L", at=[4, 1]),
    dict(badge="1 DÍA", icon="heart", text="sangre bombeada en un día", val="+7.000 L", at=[4, 3])]),
  dict(type="myth", from_=5, no="El corazón está a la <b>IZQUIERDA</b>", yes="Está casi en el <b>CENTRO</b> del pecho", yesAt=[6, 0], illus="torso"),
  dict(type="close", from_=7, icon="heart"),
]),
# 4 ------------------------------------------------------------------------
dict(id="papel-42-vertical", title="Doblar un papel 42 veces", mood=0, lines=[
  ["¿Qué pasa si", ("doblas un <b>PAPEL</b>", "doblas un papel"), ("<b>42 veces</b>?", "cuarenta y dos veces?")],
  [("Pues que, en teoría,", "pues que, en teoría,"), ("llegarías a la <b>LUNA</b>", "llegarías a la Luna.")],
  ["Un folio mide", ("unos <b>0,1 mm</b>", "una décima de milímetro."), "Y cada doblez", ("<b>DUPLICA</b> el grosor", "duplica el grosor.")],
  [("<b>7</b> dobleces:", "siete dobleces:"), ("más de <b>1 cm</b>", "algo más de un centímetro.")],
  [("<b>23</b> dobleces:", "veintitrés dobleces:"), ("unos <b>840 metros</b>", "unos ochocientos cuarenta metros."), "más que el edificio", ("más <b>ALTO</b> del mundo", "más alto del mundo.")],
  [("<b>42</b> dobleces:", "cuarenta y dos dobleces:"), ("unos <b>440.000 km</b>", "unos cuatrocientos cuarenta mil kilómetros."), "La Luna está a", ("<b>384.000</b>", "trescientos ochenta y cuatro mil.")],
  ["Error típico:", "dicen que no se puede", ("doblar más de <b>7 VECES</b>", "doblar más de siete veces.")],
  [("En 2002, Britney Gallivan", "en dos mil dos, Britney Gallivan"), ("lo dobló <b>12 VECES</b>", "lo dobló doce veces,"), "con un papel de", ("más de <b>1 km</b>", "más de un kilómetro de largo.")],
  ["¿Cuántas veces", "has llegado tú?", ("<b>PRUÉBALO</b> y comenta", "pruébalo y comenta.")],
], scenes=[
  dict(type="hook", from_=0, icon="paper", chip="0,1 mm", cal=["VECES", "42"]),
  dict(type="duo", from_=1, items=[dict(icon="paper", label="0,1 mm", at=[1, 0]), dict(icon="moon", label="LA LUNA", at=[1, 1])], sym="→",
       chips=[dict(text="×2 EN CADA DOBLEZ", at=[2, 3], cls="or", y=960)]),
  dict(type="steps", from_=3, rows=[
    dict(badge="×7", icon="paper", text="algo más de un centímetro", val="1,28 cm", at=[3, 0]),
    dict(badge="×23", icon="tower", text="más que el Burj Khalifa (828 m)", val="≈ 840 m", at=[4, 0]),
    dict(badge="×42", icon="moon", text="la Luna está a 384.400 km", val="≈ 440.000 km", at=[5, 0])]),
  dict(type="myth", from_=6, no="No se puede doblar más de <b>7 VECES</b>", yes="Britney Gallivan: <b>12 VECES</b> (2002)", yesAt=[7, 0], illus="paper",
       cmp=dict(at=[7, 2], sym="·", items=[dict(v="12", label="DOBLECES"), dict(v="≈ 1,2 km", label="DE PAPEL")]),
       note="Los 42 dobleces son solo un cálculo: en la práctica es imposible."),
  dict(type="close", from_=8, icon="moon"),
]),
# 5 ------------------------------------------------------------------------
dict(id="agua-cuerpo-vertical", title="El agua de tu cuerpo", mood=1, lines=[
  ["¿Cuánta", ("<b>AGUA</b> hay", "agua hay"), ("en tu <b>CUERPO</b>?", "en tu cuerpo?")],
  ["Pues más de", ("la <b>MITAD</b>", "la mitad"), "de lo que pesas."],
  ["En un adulto,", ("alrededor del <b>60 %</b>", "alrededor del sesenta por ciento."), "En un recién nacido,", ("cerca del <b>75 %</b>", "cerca del setenta y cinco.")],
  [("Si pesas <b>70 kilos</b>,", "si pesas setenta kilos,"), "llevas unos", ("<b>42 litros</b> de agua", "cuarenta y dos litros de agua.")],
  ["Y cada día pierdes", ("unos <b>2,5 litros</b>", "unos dos litros y medio:"), "sudor, orina", ("y <b>RESPIRACIÓN</b>", "y respiración.")],
  ["Error típico:", "hay que beber", ("<b>2 litros</b> sí o sí", "dos litros sí o sí.")],
  ["La EFSA recomienda", ("unos <b>2 litros</b> en mujeres", "unos dos litros al día en mujeres"), ("y <b>2,5</b> en hombres,", "y dos y medio en hombres,"), ("pero contando la <b>COMIDA</b>", "pero contando el agua de la comida,"), ("que aporta un <b>20 %</b>", "que aporta alrededor de un veinte por ciento.")],
  ["¿Cuánta agua", ("bebes tú al <b>DÍA</b>?", "bebes tú al día?"), ("Te leo en <b>COMENTARIOS</b>", "te leo en comentarios.")],
], scenes=[
  dict(type="hook", from_=0, icon="drop", chip="CUERPO HUMANO", cal=["AGUA", "%"]),
  dict(type="pct", from_=1, rows=[
    dict(label="ADULTO", pct=60, val="≈ 60 %", at=[2, 1]),
    dict(label="RECIÉN NACIDO", pct=75, val="≈ 75 %", at=[2, 3])],
    chips=[dict(text="MÁS DE LA MITAD", at=[1, 1], cls="or", x=380, y=1180)]),
  dict(type="duo", from_=3, items=[dict(icon="scale", label="70 kg", at=[3, 0]), dict(icon="drop", label="≈ 42 L", at=[3, 2])], sym="→",
       chips=[dict(text="−2,5 L CADA DÍA", at=[4, 1], cls="or", y=960)]),
  dict(type="myth", from_=5, no="Hay que beber <b>2 LITROS</b> sí o sí", yes="Depende, y la <b>COMIDA</b> también cuenta", yesAt=[6, 0], illus="glass",
       cmp=dict(at=[6, 1], sym="·", items=[dict(v="2 L", label="MUJERES"), dict(v="2,5 L", label="HOMBRES")]),
       note="EFSA (2010): agua total al día, incluida la de los alimentos."),
  dict(type="close", from_=7, icon="drop"),
]),
# 6 ------------------------------------------------------------------------
dict(id="marte-vertical", title="Viaje a Marte", mood=2, lines=[
  ["¿Cuánto se tarda", ("en llegar a <b>MARTE</b>?", "en llegar a Marte?")],
  ["Pues unos", ("<b>7 meses</b>", "siete meses.")],
  [("El rover <b>PERSEVERANCE</b>", "el rover Perseverance"), ("tardó <b>203 días</b>", "tardó doscientos tres días.")],
  ["Y no va en", ("línea <b>RECTA</b>:", "línea recta:"), "da media vuelta", ("alrededor del <b>SOL</b>", "alrededor del Sol.")],
  ["La distancia cambia", ("entre <b>55 y 400</b>", "entre cincuenta y cinco y cuatrocientos"), "millones de km.", "Por eso se lanza", ("cada <b>26 meses</b>", "cada veintiséis meses.")],
  ["Error típico:", "creer que Marte es rojo", ("porque está <b>CALIENTE</b>", "porque está caliente.")],
  ["Es rojo por el", ("<b>ÓXIDO DE HIERRO</b>", "óxido de hierro de su suelo."), ("Y su media ronda", "y su temperatura media ronda"), ("los <b>−60 °C</b>", "los sesenta grados bajo cero.")],
  ["¿Irías tú", ("a <b>MARTE</b>?", "a Marte?"), ("Te leo en <b>COMENTARIOS</b>", "te leo en comentarios.")],
], scenes=[
  dict(type="hook", from_=0, icon="mars", chip="PLANETA ROJO", cal=["DÍAS", "?"]),
  dict(type="travel", from_=1, a=dict(icon="earth", label="TIERRA"), b=dict(icon="mars", label="MARTE"), mover="rocket", at=[1, 0], until=[2, 1, 0.8], arc=430,
       counter=dict(**{"from": 0, "to": 203, "unit": "días"}),
       chips=[dict(text="PERSEVERANCE · 2020-2021", at=[2, 0], cls="cy"), dict(text="RUTA CURVA ALREDEDOR DEL SOL", at=[3, 1], cls="or")]),
  dict(type="bars", from_=4, bars=[
    dict(label="MÁS CERCA", h=0.14, val="55 M km", at=[4, 1]),
    dict(label="MÁS LEJOS", h=1, val="400 M km", at=[4, 1, 0.6], color="orange")],
    chips=[dict(text="🚀 CADA 26 MESES", at=[4, 4], cls="or", y=1600, x=310)]),
  dict(type="myth", from_=5, no="Es rojo porque está <b>CALIENTE</b>", yes="Es rojo por el <b>ÓXIDO DE HIERRO</b>", yesAt=[6, 0], illus="mars",
       cmp=dict(at=[6, 2], items=[dict(v="≈ −60 °C", label="TEMPERATURA MEDIA")])),
  dict(type="close", from_=7, icon="rocket"),
]),
# 7 ------------------------------------------------------------------------
dict(id="cerebro-vertical", title="Las neuronas del cerebro", mood=0, lines=[
  ["¿Cuántas", ("<b>NEURONAS</b> tienes", "neuronas tienes"), ("en el <b>CEREBRO</b>?", "en el cerebro?")],
  ["Pues unas", ("<b>86.000 millones</b>", "ochenta y seis mil millones.")],
  ["Y cada una", "puede conectarse", ("con <b>MILES</b> de otras", "con miles de otras.")],
  ["Tu cerebro pesa", ("unos <b>1,3 kilos</b>:", "alrededor de un kilo y trescientos gramos:"), ("solo un <b>2 %</b>", "solo un dos por ciento"), "de tu cuerpo."],
  ["Pero gasta", ("cerca del <b>20 %</b>", "cerca del veinte por ciento"), ("de tu <b>ENERGÍA</b>", "de tu energía en reposo.")],
  ["Error típico:", "creer que solo usamos", ("el <b>10 %</b> del cerebro", "el diez por ciento del cerebro.")],
  ["Las resonancias muestran", ("actividad en <b>TODAS</b>", "actividad en todas"), "sus zonas", ("a lo largo del <b>DÍA</b>", "a lo largo del día.")],
  ["¿Qué otro mito", "te sabes?", ("Te leo en <b>COMENTARIOS</b>", "te leo en comentarios.")],
], scenes=[
  dict(type="hook", from_=0, icon="brain", chip="NEURONAS"),
  dict(type="duo", from_=1, items=[dict(icon="neuron", label="86.000 MILLONES", at=[1, 1]), dict(icon="neuron", label="MILES DE CONEXIONES", at=[2, 2])], sym="↔"),
  dict(type="pct", from_=3, rows=[
    dict(label="PESO DEL CUERPO", pct=2, val="2 %", at=[3, 2]),
    dict(label="ENERGÍA EN REPOSO", pct=20, val="20 %", at=[4, 1])],
    chips=[dict(text="≈ 1,3 kg", at=[3, 1], cls="cy", x=380, y=1180)]),
  dict(type="myth", from_=5, no="Solo usamos el <b>10 %</b> del cerebro", yes="Lo usamos <b>TODO</b>, por zonas y momentos", yesAt=[6, 0], illus="brain"),
  dict(type="close", from_=7, icon="brain"),
]),
# 8 ------------------------------------------------------------------------
dict(id="cielo-azul-vertical", title="Por qué el cielo es azul", mood=1, lines=[
  ["¿Por qué el cielo", ("es <b>AZUL</b>,", "es azul,"), "si la luz del Sol", ("es <b>BLANCA</b>?", "es blanca?")],
  ["Pues porque", ("el aire <b>DISPERSA</b>", "el aire dispersa"), ("más la luz <b>AZUL</b>", "más la luz azul.")],
  ["La luz blanca lleva", ("<b>TODOS</b> los colores", "todos los colores"), "mezclados."],
  [("Al chocar con el aire,", "al chocar con las moléculas del aire,"), "el azul se dispersa", ("unas <b>5 o 6 veces</b> más", "unas cinco o seis veces más"), ("que el <b>ROJO</b>", "que el rojo.")],
  ["Y nos llega", ("desde <b>TODO</b> el cielo", "desde todas partes del cielo.")],
  ["Al atardecer,", "la luz cruza", ("mucho más <b>AIRE</b>", "mucho más aire."), "El azul se pierde", ("y vemos <b>NARANJAS</b>", "y vemos naranjas y rojos.")],
  ["Error típico:", "creer que el cielo", ("<b>REFLEJA</b> el mar", "refleja el mar.")],
  ["Es la dispersión", ("de <b>RAYLEIGH</b>", "de Rayleigh."), "Por eso es azul", ("también en el <b>DESIERTO</b>", "también en pleno desierto.")],
  ["¿Sabías por qué", ("es <b>AZUL</b>?", "es azul?"), ("<b>GUÁRDALO</b> para luego", "guárdalo para luego.")],
], scenes=[
  dict(type="hook", from_=0, icon="sun", chip="LUZ BLANCA"),
  dict(type="duo", from_=1, items=[dict(icon="rainbow", label="TODOS LOS COLORES", at=[2, 0]), dict(icon="sky", label="AZUL DISPERSO", at=[1, 1])], sym="→"),
  dict(type="bars", from_=3, note="Dispersión de Rayleigh: azul (≈450 nm) frente a rojo (≈700 nm).", bars=[
    dict(label="AZUL", h=1, val="×5,9", at=[3, 2]),
    dict(label="ROJO", h=0.17, val="×1", at=[3, 3], color="red")],
    chips=[dict(text="DESDE TODO EL CIELO", at=[4, 1], cls="cy", x=380, y=1600)]),
  dict(type="duo", from_=5, items=[dict(icon="sun", label="MEDIODÍA", at=[5, 0]), dict(icon="sunset", label="ATARDECER", at=[5, 2])], sym="→"),
  dict(type="myth", from_=6, no="El cielo <b>REFLEJA</b> el mar", yes="Es la dispersión de <b>RAYLEIGH</b>", yesAt=[7, 0], illus="sky"),
  dict(type="close", from_=8, icon="sun"),
]),
# 9 ------------------------------------------------------------------------
dict(id="peso-nube-vertical", title="Cuánto pesa una nube", mood=2, lines=[
  ["¿Cuánto", ("<b>PESA</b> una nube?", "pesa una nube?")],
  ["Pues una nube normal", "puede pesar unas", ("<b>500 toneladas</b>", "quinientas toneladas.")],
  ["Un cúmulo típico", "ocupa más o menos", ("<b>1 km³</b>", "un kilómetro cúbico.")],
  ["Cada metro cúbico", "tiene unos", ("<b>0,5 gramos</b> de agua", "cero coma cinco gramos de agua.")],
  ["Multiplica", ("por <b>1.000 millones</b>", "por mil millones de metros cúbicos"), "y te sale:", ("<b>500.000 kilos</b>", "quinientos mil kilos.")],
  [("Como <b>100 elefantes</b>", "como cien elefantes"), "flotando sobre", ("tu <b>CABEZA</b>", "tu cabeza.")],
  ["Error típico:", "creer que flotan", ("porque <b>NO PESAN</b>", "porque no pesan.")],
  ["Sus gotitas son", ("<b>DIMINUTAS</b>", "diminutas"), "y caen muy despacio,", "y el aire caliente", ("las mantiene <b>ARRIBA</b>", "que sube las mantiene arriba.")],
  ["¿Lo sabías?", ("<b>COMPÁRTELO</b>", "compártelo"), "con alguien curioso."],
], scenes=[
  dict(type="hook", from_=0, icon="cloud", chip="¿KILOS?"),
  dict(type="duo", from_=1, items=[dict(icon="cloud", label="≈ 500 TONELADAS", at=[1, 2])]),
  dict(type="steps", from_=2, rows=[
    dict(badge="1 km³", icon="cloud", text="volumen de un cúmulo", val="1.000 M m³", at=[2, 2]),
    dict(badge="×", icon="drop", text="agua en cada m³", val="0,5 g", at=[3, 2]),
    dict(badge="=", icon="scale", text="peso del agua de la nube", val="500.000 kg", at=[4, 3])]),
  dict(type="duo", from_=5, items=[dict(icon="cloud", label="500 t", at=[5, 0]), dict(icon="elephant", label="× 100", at=[5, 0, 0.5])], sym="="),
  dict(type="myth", from_=6, no="Flotan porque <b>NO PESAN</b>", yes="Gotas <b>DIMINUTAS</b> y aire que sube", yesAt=[7, 0], illus="cloud",
       note="Estimación del USGS para un cúmulo de 1 km³ con 0,5 g de agua por m³."),
  dict(type="close", from_=8, icon="cloud"),
]),
# 10 -----------------------------------------------------------------------
dict(id="bacterias-vertical", title="Las bacterias de tu cuerpo", mood=0, lines=[
  ["¿Cuántas", ("<b>BACTERIAS</b> viven", "bacterias viven"), ("en tu <b>CUERPO</b>?", "en tu cuerpo?")],
  ["Pues unos", ("<b>38 billones</b>", "treinta y ocho billones.")],
  ["Y tus propias células", ("son unos <b>30 billones</b>", "son unos treinta billones.")],
  ["Casi todas viven", ("en tu <b>INTESTINO</b>,", "en tu intestino,"), "sobre todo", ("en el <b>COLON</b>", "en el colon.")],
  ["Y todas juntas", "pesan unos", ("<b>200 gramos</b>", "doscientos gramos.")],
  ["Error típico:", "creer que hay", ("<b>10 bacterias</b>", "diez bacterias"), "por cada célula."],
  ["La proporción real", ("es casi <b>1 a 1</b>", "es casi de una a una."), "Lo dice un estudio", ("de <b>2016</b>", "de dos mil dieciséis.")],
  ["¿Lo sabías?", ("<b>GUÁRDALO</b> y compártelo", "guárdalo y compártelo.")],
], scenes=[
  dict(type="hook", from_=0, icon="bacteria", chip="MICROBIOTA"),
  dict(type="bars", from_=1, bars=[
    dict(label="BACTERIAS", h=1, val="38 billones", at=[1, 1], cv=38, unit="billones", color="green"),
    dict(label="TUS CÉLULAS", h=0.79, val="30 billones", at=[2, 1], cv=30, cfrom=38, unit="billones")]),
  dict(type="duo", from_=3, items=[dict(icon="gut", label="COLON", at=[3, 1]), dict(icon="scale", label="≈ 200 g", at=[4, 2])], sym="·"),
  dict(type="myth", from_=5, no="Hay <b>10 bacterias</b> por cada célula", yes="La proporción es casi <b>1 a 1</b>", yesAt=[6, 0], illus="bacteria",
       cmp=dict(at=[6, 2], sym="→", items=[dict(v="10 : 1", label="MITO (AÑOS 70)"), dict(v="≈ 1 : 1", label="SENDER ET AL., 2016")])),
  dict(type="close", from_=7, icon="bacteria"),
]),
]
