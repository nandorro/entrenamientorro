"""Generador del plan de entrenamiento a partir de las respuestas del quiz."""
from ejercicios import PATRONES, nivel_empuje, nivel_traccion

OBJETIVOS = {
    "musculo": {"reps": (8, 12), "series": 4, "descanso": 75, "cardio": False},
    "grasa": {"reps": (12, 18), "series": 3, "descanso": 40, "cardio": True},
    "fuerza": {"reps": (4, 8), "series": 5, "descanso": 120, "cardio": False},
    "general": {"reps": (10, 15), "series": 3, "descanso": 60, "cardio": False},
}
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
    if semana == 4:  # descarga
        series = max(2, series - 1)
        extra = 0
    else:
        extra = (semana - 1) * (2 if hi >= 10 else 1)
    if ej["tipo"] == "seg":
        base = {"fuerza": 20, "musculo": 25, "grasa": 30, "general": 25}[resp["objetivo"]]
        return f"{series} × {base + (semana - 1) * 5 if semana < 4 else base} s"
    return f"{series} × {lo + extra}-{hi + extra} reps" + (" (RIR 2: deja 2 en reserva)" if semana == 4 else "")
