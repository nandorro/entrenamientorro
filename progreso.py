"""Datos de las gráficas de la pantalla final «Analizando tus respuestas»: proyección de peso y carga semanal."""
import math
import re

import gym
import plan as calis


def r1(x):
    return math.floor(x * 10 + 0.5) / 10


def proyeccion_peso(r: dict, ritmo=None):
    """Curva de peso prevista hacia el peso objetivo a un ritmo saludable (perder 0,5 kg/sem, ganar 0,25), máx. 52 semanas."""
    po, peso = r.get("peso_obj"), r["peso"]
    if not po or abs(po - peso) < 1:
        return None
    diff = po - peso
    if not ritmo:
        ritmo = 0.5 if diff < 0 else 0.25
    semanas = min(52, max(4, math.ceil(abs(diff) / ritmo)))
    f = min(1.0, semanas * ritmo / abs(diff))
    pts = []
    for i in range(7):
        u = i / 6
        pts.append([math.floor(semanas * u + 0.5), r1(peso + diff * f * (1 - (1 - u) ** 1.5))])
    return {"semanas": semanas, "alcanza": f >= 1.0, "inicio": peso, "meta": po, "puntos": pts}


def _series(texto: str) -> int:
    m = re.match(r"\s*(\d+)", texto)
    return int(m.group(1)) if m else 0


def carga_semanal(plan: dict):
    """Series totales por semana (musculación y abdominales) a lo largo del plan: se ve la progresión y las descargas."""
    r = plan["resumen"]
    out = []
    for sem in range(1, plan["semanas"] + 1):
        total = 0
        for s in plan["sesiones"]:
            if plan.get("tipo") == "gym":
                for b in s["bloques"]:
                    if b["tipo"] == "Cardio":
                        continue
                    for ej in b["ejercicios"]:
                        real = gym.ejercicio_en(ej, sem)
                        total += _series(gym.prescripcion_gym(r, b, ej, real, sem)[0])
            else:
                for e in s["ejercicios"]:
                    total += _series(calis.prescripcion(r, e, sem))
        out.append(total)
    return out
