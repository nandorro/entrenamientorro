"""Exporta los datos de Python (ejercicios, animaciones, temas, preguntas…) a docs/data.js
para que la versión web/APK use exactamente los mismos.  Ejecutar:  python export_datos.py
"""
import json
from pathlib import Path

import calistenia as app
import ejercicios as ej
import gym
import nutricion as nu
import plan
from animaciones import ANIMS, REGLAS, REGLAS_GYM

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "docs" / "data.js"


def main():
    objetivos = {k: {"reps": list(v["reps"]), "series": v["series"], "descanso": v["descanso"], "cardio": v["cardio"]}
                 for k, v in plan.OBJETIVOS.items()}
    datos = {
        "PATRONES": ej.PATRONES,
        "NIVEL_EMPUJE": {k: ej.nivel_empuje(k) for k in ("0-5", "6-15", "16-30", "31+")},
        "NIVEL_TRACCION": {k: ej.nivel_traccion(k) for k in ("0", "1-4", "5-10", "11+")},
        "OBJETIVOS": objetivos,
        "NOMBRES_DIAS": plan.NOMBRES_DIAS,
        "DISTRIBUCION": {str(k): v for k, v in plan.DISTRIBUCION.items()},
        "ESTRUCTURA_CALIS": {str(d): [[n, p] for n, p in plan._estructura(d)] for d in range(2, 7)},
        "FOTOS": {k: [f"fotos/{k}_0.jpg", f"fotos/{k}_1.jpg"] for k in ANIMS
                  if (AQUI / "docs" / "fotos" / f"{k}_0.jpg").exists() and (AQUI / "docs" / "fotos" / f"{k}_1.jpg").exists()},
        "NUTRI": {"FRECUENCIA": nu.FRECUENCIA, "AJUSTE": nu.AJUSTE, "PROTEINA_GKG": nu.PROTEINA_GKG,
                  "FACTOR_DIA": nu.FACTOR_DIA, "BASAL_SEXO": nu.BASAL_SEXO, "MINIMO_KCAL": nu.MINIMO_KCAL,
                  "COMIDAS": {str(k): v for k, v in nu.COMIDAS.items()}, "HORA_DESAYUNO": nu.HORA_DESAYUNO,
                  "MENUS": nu.MENUS, "ANTOJOS": nu.ANTOJOS, "AVISO": nu.AVISO},
        "ZONA_PATRONES": plan.ZONA_PATRONES,
        "SENTADILLAS": plan.SENTADILLAS,
        "ZONA_SLOTS": gym.ZONA_SLOTS,
        "SECCION": app.SECCION,
        "GYM": gym.GYM,
        "CARDIO_LISS": gym.CARDIO_LISS,
        "CARDIO_HIIT": gym.CARDIO_HIIT,
        "CARDIO_SUAVE_RODILLAS": sorted(gym.CARDIO_SUAVE_RODILLAS),
        "EQUIPO_EJ": gym.EQUIPO_EJ, "PERMITIDO": gym.PERMITIDO,
        "CARDIO_CASA_LISS": gym.CARDIO_CASA_LISS, "CARDIO_CASA_HIIT": gym.CARDIO_CASA_HIIT,
        "SENALES": gym.SENALES_DESCARGA, "SENALES_TEXTO": gym.SENALES_TEXTO,
        "COMPUESTOS": sorted(gym.COMPUESTOS),
        "SLOTS": gym.SLOTS,
        "NOMBRES_SLOTS": gym.NOMBRES_SLOTS,
        "FASES": gym.FASES,
        "SEMANAS_GYM": gym.SEMANAS,
        "ESTRUCTURA_GYM": {o: {str(d): [list(x) for x in gym._estructura(d, o)] for d in range(2, 7)}
                           for o in plan.OBJETIVOS},
        "REPS_GYM": gym._REPS,
        "SERIES_GYM": gym._SERIES,
        "RIR_GYM": gym._RIR,
        "ANIMS": ANIMS,
        "REGLAS": REGLAS,
        "REGLAS_GYM": REGLAS_GYM,
        "THEMES": app.THEMES,
        "PREG": app.PREG,
        "ORDEN": app.ORDEN,
        "SOLO_MODO": app.SOLO_MODO,
        "MODOS": app.MODOS,
        "PERFIL_KEYS": app.PERFIL_KEYS,
    }
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text("window.DATA = " + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";\n",
                      encoding="utf8")
    print("escrito", SALIDA, SALIDA.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
