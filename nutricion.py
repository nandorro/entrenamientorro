"""Plan de nutrición: calorías, macros, agua, horarios y menús orientativos.

Inspirado en el bloque de nutrición del quiz de BetterMe (tipo de dieta, comidas al día, horarios, agua, antojos,
registro de comidas), con cálculos estándar: gasto basal de Mifflin-St Jeor + actividad, déficit/superávit moderado.
Es orientativo y NO sustituye a un médico o dietista-nutricionista.
"""
import math


def rd(x, nd=0):
    """Redondeo «medio hacia arriba» idéntico en Python y JS (round() de Python redondea al par)."""
    f = 10 ** nd
    v = math.floor(x * f + 0.5) / f
    return int(v) if nd == 0 else v


FRECUENCIA = {"nunca": 0, "1-2": 2, "3-4": 4, "5+": 5}
AJUSTE = {"grasa": -0.20, "musculo": 0.10, "fuerza": 0.05, "general": 0.0}
PROTEINA_GKG = {"grasa": 2.0, "musculo": 1.8, "fuerza": 1.8, "general": 1.4}
FACTOR_DIA = {"sedentario": 1.2, "moderado": 1.3, "activo": 1.4}
BASAL_SEXO = {"hombre": 5, "mujer": -161, "otro": -78}
MINIMO_KCAL = {"hombre": 1500, "mujer": 1200, "otro": 1350}

# (nombre, porcentaje de las kcal del día, tipo de menú, desfase en horas desde el desayuno)
COMIDAS = {
    3: [("Desayuno", 0.28, "desayuno", 0), ("Comida", 0.40, "comida", 6), ("Cena", 0.32, "cena", 12.5)],
    4: [("Desayuno", 0.25, "desayuno", 0), ("Comida", 0.35, "comida", 5.5), ("Merienda", 0.12, "snack", 9),
        ("Cena", 0.28, "cena", 12.5)],
    5: [("Desayuno", 0.22, "desayuno", 0), ("Media mañana", 0.10, "snack", 3), ("Comida", 0.33, "comida", 6),
        ("Merienda", 0.10, "snack", 9), ("Cena", 0.25, "cena", 12.5)],
}
HORA_DESAYUNO = {"<7": 6.5, "7-9": 8.0, "9-11": 10.0}

# opción: (nombre, kcal, proteína g, hidratos g, grasa g) para una ración estándar
MENUS = {
    "omnivora": {
        "desayuno": [
            ("Tortilla de 2 huevos con tostada integral y fruta", 420, 24, 40, 17),
            ("Yogur griego con avena, nueces y plátano", 410, 24, 48, 13),
            ("Tostada de aguacate y huevo con una naranja", 450, 18, 42, 23)],
        "snack": [
            ("Fruta y un puñado de almendras (20 g)", 210, 5, 28, 9),
            ("Yogur proteico con frutos rojos", 160, 18, 16, 2),
            ("Tostada integral con pavo y tomate", 190, 14, 24, 4)],
        "comida": [
            ("Pollo a la plancha con arroz integral y ensalada", 620, 45, 65, 18),
            ("Lentejas estofadas con verduras y huevo duro", 580, 34, 70, 16),
            ("Salmón al horno con patata y brócoli", 640, 40, 48, 30)],
        "cena": [
            ("Merluza con verduras salteadas y pan integral", 430, 36, 34, 14),
            ("Crema de calabacín y tortilla francesa de 2 huevos", 400, 22, 26, 22),
            ("Ensalada completa de atún, garbanzos y huevo", 450, 36, 36, 18)],
    },
    "vegetariana": {
        "desayuno": [
            ("Yogur con granola y fruta", 400, 18, 58, 10),
            ("Tostada integral con queso fresco y tomate, y fruta", 380, 20, 48, 11),
            ("Porridge de avena con leche, canela y manzana", 390, 16, 58, 10)],
        "snack": [
            ("Fruta y un puñado de nueces", 200, 4, 26, 10),
            ("Queso fresco batido con fresas", 150, 14, 14, 3),
            ("Hummus con zanahoria y pan integral", 210, 8, 28, 8)],
        "comida": [
            ("Pasta integral con tomate, verduras y queso", 600, 26, 88, 16),
            ("Tortilla de patata ligera con ensalada", 560, 22, 50, 28),
            ("Curry de garbanzos con arroz basmati", 620, 24, 92, 16)],
        "cena": [
            ("Revuelto de huevos con champiñones y espinacas", 380, 24, 10, 26),
            ("Crema de verduras y queso fresco con nueces", 360, 20, 26, 20),
            ("Hamburguesa vegetal con ensalada y boniato", 480, 24, 56, 18)],
    },
    "vegana": {
        "desayuno": [
            ("Porridge de avena con bebida de soja, plátano y semillas", 420, 16, 64, 11),
            ("Tostada con hummus, tomate y semillas, y fruta", 400, 14, 58, 13),
            ("Batido de soja, plátano y crema de cacahuete", 430, 22, 46, 18)],
        "snack": [
            ("Fruta y un puñado de almendras", 210, 5, 28, 9),
            ("Yogur de soja con frutos rojos", 130, 7, 16, 4),
            ("Edamame (100 g) con sal", 120, 11, 9, 5)],
        "comida": [
            ("Tofu salteado con arroz integral y verduras", 600, 30, 74, 20),
            ("Lentejas con arroz y ensalada", 590, 28, 96, 9),
            ("Bol de quinoa, garbanzos, aguacate y verduras", 640, 24, 80, 26)],
        "cena": [
            ("Crema de calabaza con tempeh a la plancha", 430, 28, 34, 19),
            ("Salteado de verduras con seitán", 420, 34, 30, 16),
            ("Ensalada de legumbres con aceitunas y pan integral", 450, 20, 58, 16)],
    },
}

ANTOJOS = {
    "dulces": "Dulces: prueba fruta con una onza de chocolate negro (≥70%) o yogur con canela; guarda el dulce de verdad para un momento elegido, no para picar.",
    "salado": "Salado: palomitas caseras, frutos secos sin sal (un puñado) o edamame en lugar de patatas fritas y snacks.",
    "frituras": "Frituras: pasa a horno o airfryer con poco aceite; el sabor crujiente se mantiene con mucha menos grasa.",
    "refrescos": "Refrescos: agua con gas y limón o infusión fría; si cuesta, ve bajando el azúcar poco a poco.",
    "alcohol": "Alcohol: aporta calorías vacías y frena la recuperación; reserva para ocasiones y alterna con agua.",
}

AVISO = ("Plan orientativo basado en fórmulas estándar. No sustituye a un médico ni a un dietista-nutricionista. "
         "Consulta antes de cambiar tu alimentación si estás embarazada, tienes una enfermedad, tomas medicación "
         "o has tenido un trastorno de la conducta alimentaria.")


def _hora(h):
    m = rd((h - math.floor(h)) * 60)
    hh = math.floor(h)
    if m == 60:
        hh, m = hh + 1, 0
    return f"{hh:02d}:{m:02d}"


def generar_plan_nutricion(r: dict) -> dict:
    sexo = r.get("sexo", "otro")
    peso, altura, edad = r["peso"], r["altura"], r["edad"]
    obj = r["objetivo"]
    dieta = r.get("dieta", "omnivora")
    n = int(r.get("comidas", 4))
    dias_ent = max(FRECUENCIA.get(r.get("actual", "3-4"), 3), r.get("dias", 0), r.get("gym_dias", 0))

    basal = 10 * peso + 6.25 * altura - 5 * edad + BASAL_SEXO[sexo]
    mant = basal * FACTOR_DIA[r.get("dia", "moderado")] + dias_ent * 250 / 7
    ajuste = 0.0 if edad < 18 else AJUSTE[obj]
    kcal = mant * (1 + ajuste)
    limitado = False
    if ajuste < 0:
        suelo = max(mant * 0.75, MINIMO_KCAL[sexo])
        if kcal < suelo:
            kcal, limitado = suelo, True
    kcal = rd(kcal / 10) * 10
    mant = rd(mant / 10) * 10

    prot = rd(peso * PROTEINA_GKG[obj])
    prot = min(prot, rd(kcal * 0.35 / 4))
    grasa = rd(max(peso * 0.6, kcal * 0.25 / 9))
    hidr = max(0, rd((kcal - prot * 4 - grasa * 9) / 4))
    agua = min(4.0, max(1.5, rd((peso * 35 + (500 if dias_ent > 0 else 0)) / 100) / 10))

    inicio = HORA_DESAYUNO[r.get("desayuno", "7-9")]
    comidas = []
    for nombre, pct, tipo, desfase in COMIDAS[n]:
        k = rd(kcal * pct)
        ops = []
        for on, ok, op, oc, og in MENUS[dieta][tipo]:
            racion = min(2.0, max(0.5, rd(k / ok * 4) / 4))
            ops.append({"nombre": on, "racion": racion, "kcal": rd(ok * racion), "p": rd(op * racion),
                        "c": rd(oc * racion), "g": rd(og * racion)})
        comidas.append({"nombre": nombre, "hora": _hora(inicio + desfase), "kcal": k, "opciones": ops})

    consejos = [
        "Pon una fuente de proteína en cada comida (huevo, legumbres, pescado, lácteos, tofu…): sacia y protege el músculo.",
        "La mitad del plato, verduras; un cuarto proteína y un cuarto hidratos integrales.",
    ]
    if r.get("agua") in ("<3", "3-5"):
        agua_txt = f"{agua:g}".replace(".", ",")
        consejos.append(f"Hoy bebes poco: sube hasta {agua_txt} L al día (vasos de 250 ml). Un vaso al levantarte y otro antes de cada comida.")
    for a in r.get("antojos", []):
        if a in ANTOJOS:
            consejos.append(ANTOJOS[a])
    if r.get("registro") == "no":
        consejos.append("Apunta lo que comes durante 7 días (cuaderno o app): ver los datos suele corregir más que cualquier regla.")
    if r.get("sueno") == "<6":
        consejos.append("Dormir menos de 6 h aumenta el hambre y los antojos; mejorar el sueño ayuda tanto como la dieta.")
    if dieta == "vegana":
        consejos.append("Dieta vegana: la vitamina B12 hay que suplementarla (consúltalo con tu médico) y combina legumbres con cereales.")
    elif dieta == "vegetariana":
        consejos.append("Dieta vegetariana: cuida hierro y B12; toma las legumbres con algo de vitamina C (cítricos, pimiento).")
    if limitado:
        consejos.append("Hemos limitado el déficit para que no baje de un mínimo saludable; es mejor perder grasa despacio y mantener el músculo.")
    if edad < 18:
        consejos.append("Eres menor de 18: no recomendamos déficit calórico; este plan es de mantenimiento. Consulta con tu pediatra o médico.")

    delta = kcal - mant
    ritmo = rd(abs(delta) * 7 / 7700, 2)
    return {
        "tipo": "nutricion",
        "resumen": {**r, "dias": dias_ent, "duracion": 0, "comidas": n, "dieta": dieta},
        "kcal": kcal, "mantenimiento": mant, "basal": rd(basal),
        "macros": {"p": prot, "c": hidr, "g": grasa},
        "agua": agua, "ritmo_kg_sem": ritmo, "delta": delta,
        "comidas": comidas, "consejos": consejos, "aviso": AVISO, "semanas": 1,
        "calendario": {}, "sesiones": [], "calentamiento": [], "enfriamiento": [],
    }
