"""Base de ejercicios de calistenia organizada en cadenas de progresión.

Cada patrón tiene una lista ordenada de niveles (0 = más fácil). Cada ejercicio:
(nombre, tipo, nota)  tipo: "reps" o "seg" (isométrico)
"""

PATRONES = {
    "empuje": [
        ("Flexiones inclinadas (manos en banco/mesa)", "reps", "Cuerpo recto, codos a 45°."),
        ("Flexiones con rodillas", "reps", "Glúteos apretados, pecho al suelo."),
        ("Flexiones estándar", "reps", "Baja controlado 2 s, sube explosivo."),
        ("Flexiones diamante", "reps", "Manos juntas, foco en tríceps."),
        ("Flexiones arqueras", "reps", "Alterna el peso a cada lado."),
        ("Flexiones pseudo-planche", "reps", "Manos a la altura de la cintura, inclínate adelante."),
    ],
    "empuje_vertical": [
        ("Pike push-up con pies en suelo", "reps", "Caderas altas, cabeza entre los brazos."),
        ("Pike push-up con pies elevados", "reps", "Más carga sobre los hombros."),
        ("Pino en pared (aguante)", "seg", "Abdomen hacia la pared, cuerpo alineado."),
        ("Flexiones de pino en pared (parciales)", "reps", "Rango corto y controlado."),
        ("Flexiones de pino en pared", "reps", "Rango completo."),
    ],
    "fondos": [
        ("Fondos de tríceps en banco (rodillas flexionadas)", "reps", "Espalda pegada al banco."),
        ("Fondos de tríceps en banco (piernas rectas)", "reps", "Hombros hacia atrás."),
        ("Fondos en paralelas con apoyo de pies", "reps", "Baja hasta 90° de codo."),
        ("Fondos en paralelas", "reps", "Torso ligeramente inclinado."),
        ("Fondos en anillas / lastrados", "reps", "Control total, sin balanceo."),
    ],
    "traccion": [
        ("Remo invertido bajo mesa (rodillas flexionadas)", "reps", "Escápulas juntas arriba."),
        ("Remo invertido bajo mesa / barra baja", "reps", "Cuerpo recto como una tabla."),
        ("Dominadas negativas", "reps", "Sube con salto, baja en 4-5 s."),
        ("Dominadas", "reps", "Pecho a la barra, sin balanceo."),
        ("Dominadas agarre ancho / arquero", "reps", "Más dificultad lateral."),
        ("Dominadas explosivas", "reps", "Sube con potencia, pecho a la barra."),
    ],
    "traccion_sin_barra": [
        ("Remo con toalla en puerta (inclinado)", "reps", "Agarra la toalla en una puerta firme."),
        ("Superman con retracción escapular", "reps", "Aguanta 1 s arriba."),
        ("Remo invertido bajo mesa", "reps", "Cuida que la mesa sea estable."),
        ("Remo invertido a una mano asistido", "reps", "Segunda mano ayuda poco."),
    ],
    "piernas": [
        ("Sentadilla con peso corporal", "reps", "Talones en el suelo, rodillas alineadas."),
        ("Zancadas alternas", "reps", "Rodilla delantera sin pasar mucho la punta."),
        ("Sentadilla búlgara", "reps", "Pie trasero en silla."),
        ("Sentadilla con salto", "reps", "Aterriza suave."),
        ("Pistol squat asistida", "reps", "Agárrate a un marco o TRX."),
        ("Pistol squat", "reps", "Sentadilla a una pierna completa."),
    ],
    "gluteo_isquio": [
        ("Puente de glúteo", "reps", "Aprieta arriba 1 s."),
        ("Puente a una pierna", "reps", "Caderas niveladas."),
        ("Hip thrust a una pierna con hombros elevados", "reps", "Espalda sobre el sofá."),
        ("Curl nórdico excéntrico", "reps", "Baja lo más lento posible."),
    ],
    "gemelos": [
        ("Elevación de talones", "reps", "Pausa 1 s arriba."),
        ("Elevación de talones a una pierna", "reps", "En un escalón, rango completo."),
    ],
    "core": [
        ("Plancha", "seg", "Pelvis neutra, no hundas la zona lumbar."),
        ("Dead bug", "reps", "Lumbar pegada al suelo."),
        ("Elevación de rodillas tumbado", "reps", "Sube la pelvis al final."),
        ("Elevación de piernas tumbado", "reps", "Sin arquear la espalda."),
        ("Hollow body hold", "seg", "Forma de plátano, lumbar pegada."),
        ("L-sit en suelo / paralelas", "seg", "Piernas rectas, hombros deprimidos."),
    ],
    "core_colgado": [
        ("Elevación de rodillas colgado", "reps", "Sin balanceo."),
        ("Elevación de piernas rectas colgado", "reps", "Control en la bajada."),
        ("Toes to bar", "reps", "Punta de pies a la barra."),
    ],
    "core_rotacion": [
        ("Plancha lateral", "seg", "Cada lado."),
        ("Bicicleta abdominal", "reps", "Lento y controlado."),
        ("Russian twist sin peso", "reps", "Pies elevados."),
    ],
    "cardio": [
        ("Jumping jacks", "seg", "Ritmo constante."),
        ("Mountain climbers", "seg", "Caderas bajas."),
        ("Burpees", "reps", "Pecho al suelo y salto."),
        ("Sentadilla con salto", "seg", "Aterrizaje suave."),
    ],
    "movilidad": [
        ("Gato-vaca", "reps", "Respira con el movimiento."),
        ("Estiramiento de pectoral en marco de puerta", "seg", "20-30 s cada lado."),
        ("Postura del niño", "seg", "Relaja hombros y espalda."),
        ("Zancada baja con rotación", "reps", "Abre cadera y columna torácica."),
    ],
}

# Nivel de partida según resultados de test (0-5)
def nivel_empuje(flexiones: str) -> int:
    return {"0-5": 1, "6-15": 2, "16-30": 3, "31+": 4}[flexiones]


def nivel_traccion(dominadas: str) -> int:
    return {"0": 1, "1-4": 3, "5-10": 4, "11+": 5}[dominadas]
