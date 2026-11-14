"""Generador del plan de entrenamiento a partir de las respuestas del quiz."""
import math
from ejercicios import PATRONES, nivel_empuje, nivel_traccion

OBJETIVOS = {
    "musculo": {"reps": (8, 12), "series": 4, "descanso": 75, "cardio": False},
    "grasa": {"reps": (12, 18), "series": 3, "descanso": 40, "cardio": True},
    "fuerza": {"reps": (4, 8), "series": 5, "descanso": 120, "cardio": False},
    "general": {"reps": (10, 15), "series": 3, "descanso": 60, "cardio": False},
}
# Zonas que el usuario quiere priorizar -> patrones de calistenia que se colocan primero en cada sesión
ZONA_PATRONES = {
    "pecho": ["empuje", "fondos", "empuje_vertical"],
    "espalda": ["traccion", "traccion_sin_barra", "core_colgado"],
    "hombros": ["empuje_vertical"],
    "brazos": ["fondos", "traccion", "traccion_sin_barra"],
    "piernas": ["piernas", "gemelos"],
    "gluteos": ["gluteo_isquio", "piernas"],
    "abdomen": ["core", "core_colgado", "core_rotacion"],
}
SENTADILLAS = {"0-10": 0, "11-25": 1, "26-50": 2, "51+": 3}
NOMBRES_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DISTRIBUCION = {
    2: [0, 3], 3: [0, 2, 4], 4: [0, 1, 3, 4], 5: [0, 1, 2, 3, 4], 6: [0, 1, 2, 3, 4, 5],
}


def _ej(patron, nivel):
    cadena = PATRONES[patron]
    return cadena[max(0, min(nivel, len(cadena) - 1))] + (patron,)


def _estructura(dias):
    """Devuelve la lista de sesiones (nombre, patrones) según días por semana."""
    full_a = ("Cuerpo completo A", ["empuje", "traccion", "piernas", "core", "empuje_vertical", "gluteo_isquio"])
    full_b = ("Cuerpo completo B", ["piernas", "empuje_vertical", "traccion", "fondos", "core_colgado", "gemelos"])
    full_c = ("Cuerpo completo C", ["empuje", "traccion", "gluteo_isquio", "core_rotacion", "fondos", "gemelos"])
    sup = ("Tren superior", ["empuje", "traccion", "empuje_vertical", "fondos", "core"])
    inf = ("Tren inferior + core", ["piernas", "gluteo_isquio", "gemelos", "core", "core_rotacion"])
    push = ("Empuje (pecho/hombro/tríceps)", ["empuje", "empuje_vertical", "fondos", "core"])
    pull = ("Tracción (espalda/bíceps)", ["traccion", "traccion", "core_colgado", "core_rotacion"])
    legs = ("Piernas y glúteo", ["piernas", "gluteo_isquio", "gemelos", "core"])
    return {
        2: [full_a, full_b],
        3: [full_a, full_b, full_c],
        4: [sup, inf, sup, inf],
        5: [push, pull, legs, sup, inf],
        6: [push, pull, legs, push, pull, legs],
    }[dias]


def generar_plan(resp: dict, semanas: int = 4) -> dict:
    obj = OBJETIVOS[resp["objetivo"]]
    dias = resp["dias"]
    minutos = resp["duracion"]
    barra = resp["equipo"] != "nada"
    paralelas = resp["equipo"] == "completo"

    # Nivel base
    exp = {"nunca": 0, "poco": 0, "medio": 1, "avanzado": 2}[resp["experiencia"]]
    n_emp = nivel_empuje(resp["flexiones"])
    n_tra = nivel_traccion(resp["dominadas"]) if barra else min(2, exp + (resp["dominadas"] != "0"))
    n_pier = {"nunca": 0, "poco": 1, "medio": 2, "avanzado": 3}[resp["experiencia"]]
    if resp.get("sentadillas"):
        n_pier = SENTADILLAS[resp["sentadillas"]]
    prio = {pt for z in resp.get("zonas", []) for pt in ZONA_PATRONES.get(z, [])}
    n_core = {"nunca": 0, "poco": 0, "medio": 2, "avanzado": 4}[resp["experiencia"]]
    niveles = {
        "empuje": n_emp, "empuje_vertical": max(0, n_emp - 2), "fondos": max(0, n_emp - 1),
        "traccion": n_tra, "traccion_sin_barra": n_tra, "piernas": n_pier, "gluteo_isquio": max(0, n_pier - 1),
        "gemelos": min(1, n_pier // 2), "core": n_core, "core_colgado": max(0, n_core - 2),
        "core_rotacion": max(0, n_core // 2),
    }

    # Número de ejercicios principales según duración
    n_ej = {20: 3, 30: 4, 45: 5, 60: 6}[minutos]
    lesion = resp.get("limitaciones", [])

    sesiones = []
    for i, (nombre, patrones) in enumerate(_estructura(dias)):
        patrones = sorted(patrones, key=lambda x: 0 if x in prio else 1)   # estable: primero las zonas elegidas
        ejercicios = []
        usados = set()
        for p in patrones:
            if len(ejercicios) >= n_ej:
                break
            nivel = niveles[p if p != "traccion" or barra else "traccion_sin_barra"]
            patron = p
            if p == "traccion" and not barra:
                patron = "traccion_sin_barra"
            if p == "fondos" and not paralelas:
                nivel = min(nivel, 1)  # banco/silla
            if "muñecas" in lesion and p in ("empuje", "empuje_vertical"):
                nivel = min(nivel, 0)  # inclinadas / pike suave
            if "rodillas" in lesion and p == "piernas":
                nivel = min(nivel, 0)
            if "hombros" in lesion and p == "empuje_vertical":
                continue
            # segunda tracción en día de espalda: variante distinta (un nivel menos)
            if patron in usados:
                nivel = max(0, nivel - 1)
            ej = _ej(patron, nivel)
            if ej[0] in {e["nombre"] for e in ejercicios}:
                continue
            usados.add(patron)
            ejercicios.append({"nombre": ej[0], "tipo": ej[1], "nota": ej[2], "patron": patron})
        sesiones.append({"nombre": nombre, "ejercicios": ejercicios})

    if obj["cardio"]:
        for s in sesiones:
            s["finisher"] = [
                {"nombre": e[0], "tipo": e[1], "nota": e[2]}
                for e in (PATRONES["cardio"][1], PATRONES["cardio"][2], PATRONES["cardio"][0])
            ]

    calendario = {NOMBRES_DIAS[d]: sesiones[k] for k, d in enumerate(DISTRIBUCION[dias])}

    return {
        "resumen": {**resp, "series": obj["series"], "descanso": obj["descanso"]},
        "semanas": semanas,
        "sesiones": sesiones,
        "calendario": calendario,
        "calentamiento": [
            {"nombre": e[0], "tipo": e[1], "nota": e[2]}
            for e in (PATRONES["movilidad"][0], PATRONES["movilidad"][3], PATRONES["cardio"][0])
        ],
        "enfriamiento": [
            {"nombre": e[0], "tipo": e[1], "nota": e[2]}
            for e in (PATRONES["movilidad"][1], PATRONES["movilidad"][2])
        ],
    }


def prescripcion(resp: dict, ej: dict, semana: int) -> str:
    """Series x repeticiones/segundos para una semana dada (progresión ondulante, S4 = descarga)."""
    obj = OBJETIVOS[resp["objetivo"]]
    lo, hi = obj["reps"]
    series = obj["series"]
    if resp["duracion"] <= 20:
        series = max(2, series - 1)
    if semana == 4:  # descarga: ~la mitad de series con la misma carga
        series = max(2, math.ceil(series / 2))
        extra = 0
    else:
        extra = (semana - 1) * (2 if hi >= 10 else 1)
    if ej["tipo"] == "seg":
        base = {"fuerza": 20, "musculo": 25, "grasa": 30, "general": 25}[resp["objetivo"]]
        return f"{series} × {base + (semana - 1) * 5 if semana < 4 else base} s"
    return f"{series} × {lo + extra}-{hi + extra} reps" + (" (RIR 3: misma carga, mitad de series)" if semana == 4 else "")


def resumen_perfil(r: dict) -> list:
    """Líneas del «Tu perfil» (IMC, meta de peso, nivel, zonas y hábitos), como la pantalla final de los quizzes de apps."""
    out = []
    imc = r["peso"] / (r["altura"] / 100) ** 2
    cat = "bajo peso" if imc < 18.5 else "peso normal" if imc < 25 else "sobrepeso" if imc < 30 else "obesidad"
    out.append(f"IMC {math.floor(imc * 10 + 0.5) / 10:.1f} ({cat})")  # redondeo idéntico al de la versión JS
    po = r.get("peso_obj")
    if po and abs(po - r["peso"]) >= 1:
        diff = po - r["peso"]
        lo, hi = round(abs(diff) / 0.5), round(abs(diff) / 0.25)
        verbo = "perder" if diff < 0 else "ganar"
        g = lambda x: f"{round(x, 2):g}".replace(".", ",")
        out.append(f"Meta: {g(po)} kg ({'+' if diff > 0 else '−'}{g(abs(diff))} kg). A un ritmo saludable de 0,25-0,5 kg/semana "
                   f"({verbo}) son unas {lo}-{hi} semanas.")
    nivel = {"nunca": "principiante", "poco": "principiante", "medio": "intermedio", "avanzado": "avanzado"}[r["experiencia"]]
    out.append(f"Nivel de partida: {nivel}")
    if r.get("zonas"):
        out.append("Zonas prioritarias: " + ", ".join(r["zonas"]))
    if r.get("sueno") == "<6":
        out.append("Duermes poco (<6 h): es cuando más se recupera el músculo; intenta llegar a 7-8 h.")
    if r.get("dia") == "sedentario":
        out.append("Tu día es sedentario: suma 8.000-10.000 pasos diarios además de entrenar.")
    if r.get("objetivo") == "grasa" and r.get("dias", r.get("gym_dias", 0)) >= 5:
        out.append("Para perder grasa suelen bastar 3-4 días con buena intensidad: más días no siempre aceleran el resultado. "
                   "Si te cuesta recuperar, quita un día.")
    if r.get("actual") == "nunca" and r.get("dias", r.get("gym_dias", 0)) >= 5:
        out.append("Empiezas desde cero con muchos días: si te cuesta, empieza con 3 y sube poco a poco.")
    return out
