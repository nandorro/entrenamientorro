"""Descarga las fotos de ejercicios (posición inicial y final) de Free Exercise DB (licencia Unlicense: dominio público)
https://github.com/yuhonas/free-exercise-db  y las guarda en docs/fotos/<animación>_<0|1>.jpg.

Cada animación de animaciones*.py se asocia a un ejercicio de esa base. Las animaciones sin equivalente no llevan foto.
Ejecutar:  python fotos_ejercicios.py
"""
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DEST = AQUI / "docs" / "fotos"
BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main"

# animación -> id del ejercicio en Free Exercise DB
MAPA = {
    # calistenia
    "flexion": "Pushups", "flex_inclinada": "Incline_Push-Up", "pino": "Handstand_Push-Ups", "pino_flex": "Handstand_Push-Ups",
    "fondo_banco": "Bench_Dips", "fondo_paralelas": "Dips_-_Triceps_Version", "remo": "Inverted_Row", "dominada": "Pullups",
    "sentadilla": "Bodyweight_Squat", "salto": "Freehand_Jump_Squat", "zancada": "Bodyweight_Walking_Lunge",
    "bulgara": "Split_Squats", "puente": "Butt_Lift_Bridge", "puente1": "Butt_Lift_Bridge", "nordico": "Natural_Glute_Ham_Raise",
    "gemelo": "Standing_Calf_Raises", "plancha": "Plank", "deadbug": "Dead_Bug", "piernas_tumbado": "Flat_Bench_Lying_Leg_Raise",
    "colgado_rodillas": "Hanging_Leg_Raise", "colgado_piernas": "Hanging_Leg_Raise", "bicicleta": "Air_Bike",
    "superman": "Superman", "escalador": "Mountain_Climbers", "gatovaca": "Cat_Stretch", "pecho": "Dynamic_Chest_Stretch",
    "nino": "Childs_Pose",
    # gimnasio
    "banca": "Barbell_Bench_Press_-_Medium_Grip", "banca_db": "Dumbbell_Bench_Press", "banca_incl": "Incline_Dumbbell_Press",
    "aperturas": "Dumbbell_Flyes", "pecho_maq": "Machine_Bench_Press", "jalon": "Wide-Grip_Lat_Pulldown",
    "remo_polea": "Seated_Cable_Rows", "remo_barra": "Bent_Over_Barbell_Row", "remo_db": "One-Arm_Dumbbell_Row",
    "peso_muerto": "Barbell_Deadlift", "rdl": "Romanian_Deadlift", "press_hombro_db": "Dumbbell_Shoulder_Press",
    "press_militar": "Standing_Military_Press", "elev_lat": "Side_Lateral_Raise", "curl_db": "Dumbbell_Bicep_Curl",
    "curl_martillo": "Hammer_Curls", "curl_barra": "Barbell_Curl", "triceps_polea": "Triceps_Pushdown",
    "triceps_cabeza": "Standing_Dumbbell_Triceps_Extension", "sent_barra": "Barbell_Squat", "goblet": "Goblet_Squat",
    "prensa": "Leg_Press", "ext_cuad": "Leg_Extensions", "curl_fem": "Lying_Leg_Curls", "hip_thrust": "Barbell_Hip_Thrust",
    "zancada_db": "Dumbbell_Lunges", "crunch": "Crunches", "rueda": "Ab_Roller", "crunch_polea": "Cable_Crunch",
    "run": "Running_Treadmill", "walk": "Walking_Treadmill", "bici": "Bicycling_Stationary", "eliptica": "Elliptical_Trainer",
    "remo_erg": "Rowing_Stationary", "comba": "Rope_Jumping",
}


def bajar(args):
    clave, ej, n = args
    destino = DEST / f"{clave}_{n}.jpg"
    if destino.exists() and destino.stat().st_size > 1000:
        return clave, n, True
    try:
        with urllib.request.urlopen(f"{BASE}/exercises/{ej}/{n}.jpg", timeout=30) as r:
            destino.write_bytes(r.read())
        return clave, n, True
    except Exception:
        return clave, n, False


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(f"{BASE}/dist/exercises.json", timeout=60) as r:
        ids = {e["id"] for e in json.load(r)}
    faltan = {k: v for k, v in MAPA.items() if v not in ids}
    print("sin equivalente en la base:", faltan or "ninguno")
    trabajos = [(k, v, n) for k, v in MAPA.items() if v in ids for n in (0, 1)]
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(bajar, trabajos))
    ok = {}
    for k, n, bien in res:
        if bien:
            ok.setdefault(k, []).append(n)
    completas = sorted(k for k, v in ok.items() if sorted(v) == [0, 1])
    print(f"{len(completas)} animaciones con dos fotos; carpeta {DEST} ({sum(f.stat().st_size for f in DEST.glob('*.jpg')) // 1024} KB)")


if __name__ == "__main__":
    main()
