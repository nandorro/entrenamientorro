"""Registro de series (como el de Hevy): 1RM estimado, mejor marca y récords personales.

Formato en datos.json (se sincroniza con Drive):
  datos[modo]["registro"][nombre_ejercicio][fecha] = [{"peso": kg, "reps": n, "tipo": "normal|calentamiento|descarga|fallo"}, ...]
  datos[modo]["notas"][nombre_ejercicio] = "texto"
El 1RM se estima con la fórmula de Epley: peso × (1 + reps/30). Las series de calentamiento no cuentan para récords.
"""
import math

TIPOS = [("normal", "Normal"), ("calentamiento", "Calentamiento"), ("descarga", "Descarga"), ("fallo", "Al fallo")]
ICONO = {"normal": "", "calentamiento": "🔥 ", "descarga": "📉 ", "fallo": "💥 "}


def r1(x):
    return math.floor(x * 10 + 0.5) / 10


def e1rm(peso, reps):
    """1RM estimado (Epley). Con peso 0 (peso corporal) no se calcula."""
    if peso <= 0 or reps <= 0:
        return 0.0
    return r1(peso * (1 + reps / 30)) if reps > 1 else r1(peso)


def _mejor(hist, excluir=None):
    best, fecha = 0.0, None
    for f in sorted(hist):
        if f == excluir:
            continue
        for s in hist[f]:
            if s["tipo"] != "calentamiento":
                v = e1rm(s["peso"], s["reps"])
                if v > best:
                    best, fecha = v, f
    return best, fecha


def resumen(hist: dict, hoy: str) -> dict:
    """Última sesión anterior, mejor 1RM (con y sin hoy) y si hoy hay récord."""
    anteriores = sorted(f for f in hist if f != hoy)
    ultimo = {"fecha": anteriores[-1], "sets": hist[anteriores[-1]]} if anteriores else None
    previo, f_previo = _mejor(hist, excluir=hoy)
    total, f_total = _mejor(hist)
    return {"ultimo": ultimo, "mejor": total, "fecha_mejor": f_total, "previo": previo,
            "pr_hoy": previo > 0 and total > previo and f_total == hoy}


def es_pr(hist: dict, hoy: str, serie: dict) -> bool:
    """¿Esta serie (aún no añadida) supera el mejor 1RM de sesiones anteriores?"""
    if serie["tipo"] == "calentamiento":
        return False
    previo, _ = _mejor(hist, excluir=hoy)
    return previo > 0 and e1rm(serie["peso"], serie["reps"]) > previo


def fmt_serie(s):
    peso = s["peso"]
    base = f"{peso:g} kg × {s['reps']}".replace(".", ",") if peso > 0 else f"{s['reps']} (peso corporal)"
    return ICONO.get(s["tipo"], "") + base
