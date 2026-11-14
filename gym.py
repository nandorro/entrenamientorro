"""GymBrocoli: generador de planes de gimnasio de 12 semanas con progresión.

Inspirado en los programas habituales de las apps de entreno (Fitbod, Hevy, Jefit, StrongLifts, PPL):
  * 3 fases de 4 semanas: Adaptación (máquinas/técnica) -> Construcción (mancuernas) -> Intensificación (barra).
  * Dentro de cada fase: semana 1-3 con menos reservas (RIR) cada vez y la semana 4 de descarga.
  * Sesiones separadas por bloques: Musculación, Abdominales y Cardio (LISS o HIIT).
  * Doble progresión: cuando haces el máximo de reps en todas las series, sube el peso.
"""
from ejercicios import PATRONES

FASES = [
    ("Fase 1 · Adaptación", "Máquinas y técnica. Aprende los movimientos con cargas moderadas."),
    ("Fase 2 · Construcción", "Mancuernas y más volumen. Empieza a apretar de verdad."),
    ("Fase 3 · Intensificación", "Barra libre y cargas altas. Aquí se nota el progreso."),
]
SEMANAS = 12

# (nombre, nota, tipo)
GYM = {
    "pecho_press": [
        ("Press de pecho en máquina", "Espalda pegada al respaldo; empuja sin bloquear los codos de golpe.", "reps"),
        ("Press de banca con mancuernas", "Baja hasta 90° de codo con las escápulas juntas y los pies firmes.", "reps"),
        ("Press de banca con barra", "Agarre algo más ancho que los hombros; baja al pecho y empuja en línea. Usa soportes de seguridad.", "reps"),
    ],
    "pecho_acc": [
        ("Aperturas con mancuernas", "Codos ligeramente flexionados; abre en arco hasta notar el estiramiento del pecho.", "reps"),
        ("Press inclinado con mancuernas", "Banco a 30°; empuja sobre la parte alta del pecho.", "reps"),
    ],
    "espalda_vert": [
        ("Jalón al pecho en polea", "Tira hacia la clavícula llevando los codos abajo; sin balanceo.", "reps"),
        ("Dominadas asistidas con goma", "Usa goma o máquina de asistencia para completar todo el recorrido.", "reps"),
        ("Dominadas", "Pecho a la barra, sin balanceo. Añade lastre cuando sean fáciles.", "reps"),
    ],
    "espalda_horiz": [
        ("Remo en polea baja", "Espalda recta; junta las escápulas al tirar.", "reps"),
        ("Remo con mancuerna a una mano", "Apoyado en un banco; tira del codo hacia la cadera.", "reps"),
        ("Remo con barra", "Tronco a ~45°, espalda neutra; tira hacia el abdomen.", "reps"),
    ],
    "hombro_press": [
        ("Press de hombros con mancuernas", "Sentado con respaldo; empuja arriba sin arquear la lumbar.", "reps"),
        ("Press militar con barra", "De pie, glúteos y abdomen apretados; la barra sube pegada a la cara.", "reps"),
    ],
    "hombro_lat": [
        ("Elevaciones laterales con mancuernas", "Sube hasta la altura del hombro con el codo ligeramente flexionado; peso ligero.", "reps"),
    ],
    "biceps": [
        ("Curl de bíceps con mancuernas", "Codos pegados al cuerpo; sube sin balancear.", "reps"),
        ("Curl martillo con mancuernas", "Agarre neutro; trabaja también el antebrazo.", "reps"),
        ("Curl con barra", "Codos fijos; baja despacio en 3 segundos.", "reps"),
    ],
    "triceps": [
        ("Extensión de tríceps en polea", "Codos pegados al cuerpo; estira del todo abajo.", "reps"),
        ("Extensión de tríceps sobre la cabeza con mancuerna", "Codos apuntando al techo; baja detrás de la cabeza.", "reps"),
        ("Fondos de tríceps en banco", "Espalda pegada al banco; baja hasta 90°.", "reps"),
    ],
    "cuadriceps": [
        ("Prensa de piernas", "Pies a la anchura de los hombros; no bloquees las rodillas arriba.", "reps"),
        ("Sentadilla goblet con mancuerna", "Mancuerna pegada al pecho; baja con la espalda recta.", "reps"),
        ("Sentadilla con barra", "Barra sobre los trapecios, talones en el suelo, rodillas alineadas con los pies.", "reps"),
    ],
    "femoral": [
        ("Curl femoral tumbado en máquina", "Caderas pegadas al banco; sube y baja en 3 segundos.", "reps"),
        ("Peso muerto rumano con mancuernas", "Cadera atrás, espalda neutra; baja hasta notar el isquio tenso.", "reps"),
        ("Peso muerto rumano con barra", "Barra pegada a las piernas; empuja la cadera atrás y sube apretando glúteos.", "reps"),
    ],
    "gluteo": [
        ("Puente de glúteo", "Aprieta arriba 1 s; costillas abajo.", "reps"),
        ("Hip thrust con barra", "Espalda alta en el banco; sube la cadera hasta alinear rodilla-cadera-hombro.", "reps"),
    ],
    "unilateral": [
        ("Zancadas con mancuernas", "Torso erguido; rodilla delantera sobre el pie.", "reps"),
        ("Sentadilla búlgara", "Pie trasero en el banco; baja en vertical.", "reps"),
    ],
    "cuad_acc": [
        ("Extensión de cuádriceps en máquina", "Pausa 1 s arriba, baja controlado.", "reps"),
    ],
    "gemelos": [
        ("Elevación de talones de pie", "Rango completo con pausa de 1 s arriba.", "reps"),
    ],
    "peso_muerto": [
        ("Peso muerto con barra", "Espalda neutra, barra pegada a las piernas; empuja el suelo con los pies.", "reps"),
    ],
    # abdominales
    "abs_flex": [
        ("Crunch abdominal", "Lumbar pegada al suelo; sube las costillas hacia la pelvis, sin tirar del cuello.", "reps"),
        ("Crunch en polea alta", "De rodillas; redondea la espalda llevando los codos a las rodillas.", "reps"),
    ],
    "abs_core": [
        ("Plancha", "Pelvis neutra; no hundas la zona lumbar.", "seg"),
        ("Rueda abdominal", "Estira hasta donde controles la lumbar; vuelve con el abdomen.", "reps"),
    ],
    "abs_piernas": [
        ("Elevación de piernas tumbado", "Sin arquear la espalda baja.", "reps"),
        ("Elevación de rodillas colgado", "Sin balanceo; sube la pelvis al final.", "reps"),
    ],
    "abs_rot": [
        ("Bicicleta abdominal", "Lento y controlado; codo hacia rodilla contraria.", "reps"),
        ("Russian twist sin peso", "Pies elevados, gira el torso entero.", "reps"),
    ],
}

CARDIO_LISS = [
    ("Caminata en cinta inclinada", "Inclinación 6-10%, sin agarrarte a las barras.", "min"),
    ("Bicicleta estática", "Cadencia 70-90 rpm, resistencia moderada.", "min"),
    ("Elíptica", "Postura erguida, empuja con todo el pie.", "min"),
    ("Carrera continua en cinta", "Ritmo en el que puedas hablar.", "min"),
    ("Remo en ergómetro", "Empuja con piernas, luego espalda, luego brazos.", "min"),
]
CARDIO_HIIT = [
    ("Intervalos en bicicleta estática", "Esfuerzo fuerte (RPE 8-9) y recuperación suave.", "min"),
    ("Sprints en cinta", "Aumenta la velocidad en la fase fuerte; agárrate al botón de parada.", "min"),
    ("Intervalos de remo", "Palada potente en la fase fuerte.", "min"),
    ("Comba", "Saltos pequeños y rápidos con las muñecas.", "min"),
    ("Burpees", "Pecho al suelo y salto arriba.", "min"),
]
CARDIO_SUAVE_RODILLAS = {"Carrera continua en cinta", "Sprints en cinta", "Comba", "Burpees"}

COMPUESTOS = {"pecho_press", "espalda_vert", "espalda_horiz", "hombro_press", "cuadriceps",
              "femoral", "peso_muerto", "unilateral", "gluteo"}

SLOTS = {
    "FULL_A": ["cuadriceps", "pecho_press", "espalda_horiz", "hombro_lat", "biceps", "triceps", "gemelos"],
    "FULL_B": ["femoral", "espalda_vert", "hombro_press", "unilateral", "triceps", "biceps", "cuad_acc"],
    "FULL_C": ["cuadriceps", "pecho_acc", "espalda_horiz_b", "gluteo", "hombro_lat", "biceps_b", "gemelos"],
    "UPPER": ["pecho_press", "espalda_horiz", "hombro_press", "espalda_vert", "pecho_acc", "biceps", "triceps", "hombro_lat"],
    "LOWER": ["cuadriceps", "femoral", "unilateral", "gluteo", "cuad_acc", "gemelos"],
    "PUSH": ["pecho_press", "hombro_press", "pecho_acc", "hombro_lat", "triceps", "triceps_b"],
    "PULL": ["espalda_vert", "espalda_horiz", "peso_muerto", "espalda_horiz_b", "biceps", "biceps_b"],
}
NOMBRES_SLOTS = {
    "FULL_A": "Cuerpo completo A", "FULL_B": "Cuerpo completo B", "FULL_C": "Cuerpo completo C",
    "UPPER": "Torso", "LOWER": "Pierna y glúteo", "PUSH": "Empuje (pecho, hombro, tríceps)",
    "PULL": "Tracción (espalda y bíceps)",
}

# Zonas que el usuario quiere priorizar -> slots que se colocan primero en cada sesión
ZONA_SLOTS = {
    "pecho": ["pecho_press", "pecho_acc"],
    "espalda": ["espalda_vert", "espalda_horiz", "espalda_horiz_b", "peso_muerto"],
    "hombros": ["hombro_press", "hombro_lat"],
    "brazos": ["biceps", "biceps_b", "triceps", "triceps_b"],
    "piernas": ["cuadriceps", "femoral", "unilateral", "cuad_acc", "gemelos"],
    "gluteos": ["gluteo", "femoral", "unilateral"],
    "abdomen": [],
}
NOMBRES_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DISTRIBUCION = {2: [0, 3], 3: [0, 2, 4], 4: [0, 1, 3, 4], 5: [0, 1, 2, 3, 4], 6: [0, 1, 2, 3, 4, 5]}


def _estructura(dias, objetivo):
    """Lista de sesiones: (clave_slots|None, abs, cardio) donde cardio = None o 'LISS'/'HIIT'."""
    grasa = objetivo == "grasa"
    general = objetivo == "general"
    if dias == 2:
        return [("FULL_A", True, "HIIT" if grasa else None), ("FULL_B", True, "LISS")]
    if dias == 3:
        c = ["LISS" if grasa or general else None, "HIIT" if grasa else None, "LISS"]
        return [("FULL_A", True, c[0]), ("FULL_B", True, c[1]), ("FULL_C", False, c[2])]
    if dias == 4:
        return [("UPPER", False, None), ("LOWER", True, "LISS" if grasa else None),
                ("UPPER", False, "HIIT" if grasa else None), ("LOWER", True, "LISS")]
    if dias == 5:
        return [("PUSH", False, None), ("PULL", False, None), ("LOWER", False, "LISS" if grasa else None),
                ("UPPER", False, "HIIT" if grasa else None), (None, True, "HIIT" if grasa or general else "LISS")]
    return [("PUSH", False, None), ("PULL", False, None), ("LOWER", False, "LISS" if grasa else None),
            ("UPPER", False, None), ("LOWER", False, "HIIT" if grasa else None),
            (None, True, "HIIT" if grasa else "LISS")]


def _nivel(patron, fase, exp_off, lim):
    """Elige el ejercicio del patrón para una fase. Devuelve (nombre, nota, tipo) o None si no procede."""
    base = patron[:-2] if patron.endswith("_b") else patron
    delta = -1 if patron.endswith("_b") else 0
    cadena = GYM[base]
    lvl = fase + exp_off + delta
    if base == "peso_muerto" and fase + exp_off < 1:
        return None
    if "hombros" in lim and base in ("hombro_press",):
        return None
    if "hombros" in lim and base in ("pecho_press", "espalda_vert"):
        lvl = min(lvl, 0 if base == "espalda_vert" else 1)
    if "muñecas" in lim and base in ("pecho_press", "hombro_press"):
        lvl = 0 if base == "pecho_press" else lvl
    if "muñecas" in lim and base in ("biceps",):
        lvl = min(lvl, 1)
    if "muñecas" in lim and base in ("abs_core",):
        lvl = 0
    if "rodillas" in lim and base in ("unilateral", "cuad_acc"):
        return None
    if "rodillas" in lim and base == "cuadriceps":
        lvl = 0
    return cadena[max(0, min(len(cadena) - 1, lvl))]


def _ej(patron, fase_items):
    return {"patron": patron, "niveles": [dict(nombre=n, nota=nt, tipo=t) for n, nt, t in fase_items]}


def _bloque_fuerza(slots, n, exp_off, lim):
    ejercicios, vistos = [], set()
    for patron in slots:
        if len(ejercicios) >= n:
            break
        porfase = [_nivel(patron, f, exp_off, lim) for f in range(3)]
        if porfase[0] is None and porfase[1] is None and porfase[2] is None:
            continue
        porfase = [p or next(x for x in porfase if x) for p in porfase]
        if porfase[0][0] in vistos:
            continue
        vistos.add(porfase[0][0])
        ejercicios.append(_ej(patron, porfase))
    return ejercicios


def _bloque_abs(n, exp_off, lim):
    pats = ["abs_flex", "abs_core", "abs_piernas", "abs_rot"]
    ej = []
    for patron in pats[:n]:
        porfase = [_nivel(patron, f, exp_off, lim) for f in range(3)]
        ej.append(_ej(patron, porfase))
    return ej


def _bloque_cardio(modo, lim, k):
    lista = CARDIO_LISS if modo == "LISS" else CARDIO_HIIT
    if "rodillas" in lim:
        lista = [e for e in lista if e[0] not in CARDIO_SUAVE_RODILLAS]
    rot = lista[k % len(lista):] + lista[:k % len(lista)]
    return [{"patron": "cardio", "modo": modo,
             "opciones": [dict(nombre=n, nota=nt, tipo=t) for n, nt, t in rot[:4]]}]


def generar_plan_gym(resp: dict) -> dict:
    dias, minutos = resp["gym_dias"], resp["gym_duracion"]
    obj = resp["objetivo"]
    lim = resp.get("limitaciones", [])
    exp_off = {"nunca": 0, "poco": 0, "medio": 1, "avanzado": 2}[resp["experiencia"]]
    zonas = resp.get("zonas", [])
    prio = {sl for z in zonas for sl in ZONA_SLOTS.get(z, [])}
    sesiones = []
    for i, (clave, con_abs, cardio) in enumerate(_estructura(dias, obj)):
        t_abs = 10 if con_abs else 0
        if clave is None:  # día dedicado a cardio + abdominales
            t_cardio = max(20, min(45, minutos - 5 - 12))
            t_abs = 12
        else:
            t_cardio = 12 if cardio else 0
        t_fuerza = minutos - 5 - t_abs - t_cardio
        bloques = []
        if clave:
            n = max(3 if not (t_abs or t_cardio) else 2, min(8, t_fuerza // 9))
            bloques.append({"tipo": "Musculación", "titulo": NOMBRES_SLOTS[clave],
                            "ejercicios": _bloque_fuerza(sorted(SLOTS[clave], key=lambda x: 0 if x in prio else 1), n, exp_off, lim)})
        if con_abs:
            bloques.append({"tipo": "Abdominales", "titulo": "Abdominales y core",
                            "ejercicios": _bloque_abs(4 if (t_abs >= 12 or "abdomen" in zonas) else 3, exp_off, lim)})
        if cardio:
            bloques.append({"tipo": "Cardio", "titulo": f"Cardio {cardio}", "modo": cardio, "minutos": t_cardio,
                            "ejercicios": _bloque_cardio(cardio, lim, i)})
        nombre = NOMBRES_SLOTS[clave] if clave else "Cardio y abdominales"
        sesiones.append({"nombre": nombre, "bloques": bloques})
    calendario = {NOMBRES_DIAS[d]: sesiones[k] for k, d in enumerate(DISTRIBUCION[dias])}
    return {
        "tipo": "gym",
        "resumen": {**resp, "dias": dias, "duracion": minutos},
        "semanas": SEMANAS,
        "sesiones": sesiones,
        "calendario": calendario,
        "calentamiento": [
            dict(nombre="Caminata en cinta inclinada (5 min suaves)", nota="Sube el pulso y calienta articulaciones.", tipo="min"),
            dict(nombre=PATRONES["movilidad"][0][0], nota=PATRONES["movilidad"][0][2], tipo="reps"),
            dict(nombre=PATRONES["movilidad"][3][0], nota=PATRONES["movilidad"][3][2], tipo="reps"),
        ],
        "enfriamiento": [
            dict(nombre=PATRONES["movilidad"][1][0], nota=PATRONES["movilidad"][1][2], tipo="seg"),
            dict(nombre=PATRONES["movilidad"][2][0], nota=PATRONES["movilidad"][2][2], tipo="seg"),
        ],
    }


# ---------------------------------------------------------------- semana -> ejercicio y prescripción
def fase_de(semana):
    return (semana - 1) // 4


def es_descarga(semana):
    return semana % 4 == 0


def ejercicio_en(ej, semana):
    if "niveles" in ej:
        return ej["niveles"][fase_de(semana)]
    return ej["opciones"][(semana - 1) % len(ej["opciones"])]


def titulo_semana(semana):
    f = fase_de(semana)
    return f"Semana {semana} · {FASES[f][0]}" + (" · descarga" if es_descarga(semana) else "")


_REPS = {  # (compuesto), (accesorio) por fase
    "musculo": [((12, 15), (12, 15)), ((8, 12), (10, 15)), ((6, 10), (8, 12))],
    "fuerza": [((8, 12), (10, 15)), ((5, 8), (8, 12)), ((3, 6), (6, 10))],
    "grasa": [((12, 15), (15, 20)), ((10, 15), (12, 18)), ((10, 15), (12, 20))],
    "general": [((10, 15), (12, 15)), ((8, 12), (10, 15)), ((8, 12), (10, 15))],
}
_SERIES = {"musculo": [3, 4, 4], "fuerza": [3, 4, 5], "grasa": [3, 3, 4], "general": [3, 3, 4]}
_RIR = [[3, 2, 1], [2, 1, 1], [2, 1, 0]]  # por fase, semanas 1-3


def prescripcion_gym(resp, bloque, ej, ej_real, semana):
    """Devuelve (texto, descanso en segundos)."""
    f, desc = fase_de(semana), es_descarga(semana)
    w = (semana - 1) % 4
    tipo = bloque["tipo"]
    if tipo == "Cardio":
        k = semana
        if bloque["modo"] == "LISS":
            m = min(bloque.get("minutos", 30), 12 + 2 * k)
            if desc:
                m = int(m * 0.8)
            return f"{m} min a ritmo suave (podrías hablar; 60-70% de tu FC máxima)", 0
        rondas = min(12, 5 + k // 2 + (0 if not desc else -2))
        return f"{rondas} rondas de 30 s fuerte (RPE 8-9) / 60 s suave + 3 min de vuelta a la calma", 0
    if tipo == "Abdominales":
        series = 3 if not desc else 2
        if ej_real["tipo"] == "seg":
            return f"{series} × {30 + 10 * f + (5 * min(w, 2) if not desc else 0)} s", 45
        lo, hi = (12, 15) if f == 0 else (15, 20)
        return f"{series} × {lo}-{hi} reps" + (" · añade lastre/lentitud cuando sobren" if f == 2 else ""), 45
    compuesto = ej["patron"] in COMPUESTOS
    lo, hi = _REPS[resp["objetivo"]][f][0 if compuesto else 1]
    series = _SERIES[resp["objetivo"]][f] if compuesto else max(2, _SERIES[resp["objetivo"]][f] - 1)
    if desc:
        series = max(2, series - 1)
        rir = "RIR 4 · baja el peso un 10%"
    else:
        rir = f"RIR {_RIR[f][w]}" if _RIR[f][w] else "al fallo técnico (última serie)"
    descanso = {"musculo": 90, "fuerza": 150, "grasa": 60, "general": 90}[resp["objetivo"]] if compuesto else 60
    return f"{series} × {lo}-{hi} reps · {rir}", descanso
