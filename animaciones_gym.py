"""Animaciones de gimnasio (barras, mancuernas, poleas, máquinas y cardio). Se registran en ANIMS."""
from animaciones import ANIMS, P

_BANCO = [("rect", 24, 96, 110, 6), ("line", 30, 102, 30, 112), ("line", 128, 102, 128, 112)]

ANIMS.update({
    "banca": dict(
        texto="Tumbado en el banco con los pies firmes. Baja la barra al pecho con control y empuja en vertical hasta estirar los brazos.",
        frames=[P((50, 90), (88, 90), (52, 48), (122, 112)), P((50, 90), (88, 90), (54, 76), (122, 112))],
        ek=-1, kk=1, toes=True, carga="barra", props=_BANCO),
    "banca_incl": dict(
        texto="Banco inclinado a 30°. Baja las mancuernas a la parte alta del pecho y empuja hacia arriba juntándolas ligeramente.",
        frames=[P((70, 62), (96, 92), (74, 20), (130, 112)), P((70, 62), (96, 92), (80, 50), (130, 112))],
        ek=-1, kk=1, toes=True, carga="db",
        props=[("line", 56, 46, 94, 96), ("rect", 86, 96, 50, 6), ("line", 92, 102, 92, 112), ("line", 130, 102, 130, 112)]),
    "aperturas": dict(
        texto="Tumbado con las mancuernas arriba. Abre los brazos en arco, con los codos ligeramente flexionados, hasta notar el pecho estirado, y ciérralos.",
        frames=[P((50, 90), (88, 90), (54, 48), (122, 112)), P((50, 90), (88, 90), (30, 66), (122, 112))],
        ek=-1, kk=1, toes=True, carga="db", props=_BANCO),
    "pecho_maq": dict(
        texto="Sentado con la espalda en el respaldo. Empuja los agarres al frente hasta casi estirar los brazos y vuelve despacio.",
        frames=[P((70, 42), (72, 80), (92, 48), (104, 112)), P((70, 42), (72, 80), (112, 42), (104, 112))],
        ek=-1, kk=1, toes=True,
        props=[("rect", 60, 80, 40, 5), ("line", 60, 26, 62, 80), ("line", 80, 85, 80, 112)]),
    "jalon": dict(
        texto="Sentado con los muslos bajo el rodillo. Tira de la barra hacia la clavícula llevando los codos hacia abajo y atrás; sube con control.",
        frames=[P((86, 38), (92, 76), (104, -2), (120, 112)), P((86, 38), (92, 76), (106, 40), (120, 112))],
        ek=-1, kk=1, toes=True, carga="cable", ancla=(106, -46),
        props=[("rect", 76, 78, 36, 5), ("line", 100, 66, 124, 66), ("line", 94, 83, 94, 112)]),
    "remo_polea": dict(
        texto="Sentado con las piernas ligeramente flexionadas. Tira del agarre hacia el abdomen juntando las escápulas, sin balancear el torso.",
        frames=[P((84, 60), (70, 96), (126, 62), (118, 100)), P((74, 60), (70, 96), (90, 80), (118, 100))],
        ek=-1, kk=1, toes=True, carga="cable", ancla=(196, 70),
        props=[("rect", 52, 100, 44, 5), ("rect", 118, 88, 5, 24)]),
    "remo_barra": dict(
        texto="Tronco inclinado a unos 45° con la espalda neutra. Tira de la barra hacia el abdomen llevando los codos atrás y baja sin perder la postura.",
        frames=[P((110, 40), (80, 66), (114, 80), (96, 112)), P((110, 40), (80, 66), (104, 66), (96, 112))],
        ek=-1, kk=1, toes=True, carga="barra"),
    "remo_db": dict(
        texto="Una rodilla y una mano en el banco, espalda plana. Tira de la mancuerna hacia la cadera con el codo pegado y baja estirando el brazo.",
        frames=[P((118, 56), (82, 60), (112, 98), (92, 112), hand2=(136, 82), foot2=(100, 82)),
                P((118, 56), (82, 60), (104, 66), (92, 112), hand2=(136, 82), foot2=(100, 82))],
        ek=-1, kk=1, kk2=1, toes=True, carga="db1",
        props=[("rect", 92, 82, 70, 6), ("line", 98, 88, 98, 112), ("line", 156, 88, 156, 112)]),
    "peso_muerto": dict(
        texto="Barra sobre la mitad del pie, espalda neutra. Empuja el suelo con las piernas y estira la cadera hasta quedar erguido; baja la barra pegada a las piernas.",
        frames=[P((116, 56), (78, 70), (104, 96), (100, 112)), P((100, 20), (100, 58), (104, 66), (100, 112))],
        ek=-1, kk=1, toes=True, carga="barra"),
    "rdl": dict(
        texto="Piernas casi rectas, cadera atrás, espalda neutra. Baja el peso pegado a las piernas hasta notar el isquio tenso y sube empujando la cadera adelante.",
        frames=[P((114, 66), (78, 62), (118, 96), (100, 112)), P((100, 20), (100, 58), (106, 66), (100, 112))],
        ek=-1, kk=1, toes=True, carga="barra"),
    "press_hombro_db": dict(
        texto="Sentado o de pie con el abdomen apretado. Empuja las mancuernas desde los hombros hasta estirar los brazos arriba, sin arquear la lumbar.",
        frames=[P((100, 20), (100, 58), (114, 12), (100, 112)), P((100, 20), (100, 58), (102, -20), (100, 112))],
        ek=-1, kk=1, toes=True, carga="db"),
    "press_militar": dict(
        texto="De pie con glúteos y abdomen apretados. Empuja la barra desde la clavícula hasta arriba, pasando cerca de la cara, y baja con control.",
        frames=[P((100, 20), (100, 58), (114, 12), (100, 112)), P((100, 20), (100, 58), (102, -20), (100, 112))],
        ek=-1, kk=1, toes=True, carga="barra"),
    "elev_lat": dict(
        texto="De pie con una mancuerna en cada mano. Sube los brazos a los lados hasta la altura de los hombros con los codos ligeramente flexionados y baja despacio.",
        frames=[P((100, 20), (100, 58), (82, 58), (92, 112), hand2=(118, 58), foot2=(108, 112)),
                P((100, 20), (100, 58), (60, 22), (92, 112), hand2=(140, 22), foot2=(108, 112))],
        ek=1, kk=1, toes=False, carga="db", front=True),
    "curl_db": dict(
        texto="De pie con los codos pegados al cuerpo. Sube las mancuernas hacia los hombros sin balancear y baja despacio.",
        frames=[P((100, 20), (100, 58), (106, 60), (100, 112)), P((100, 20), (100, 58), (116, 26), (100, 112))],
        ek=-1, kk=1, toes=True, carga="db"),
    "curl_barra": dict(
        texto="De pie con los codos fijos junto al cuerpo. Sube la barra hasta los hombros y baja en 3 segundos.",
        frames=[P((100, 20), (100, 58), (106, 60), (100, 112)), P((100, 20), (100, 58), (116, 26), (100, 112))],
        ek=-1, kk=1, toes=True, carga="barra"),
    "triceps_polea": dict(
        texto="De pie con los codos pegados al cuerpo. Empuja el agarre hacia abajo hasta estirar los brazos y sube controlando.",
        frames=[P((102, 22), (100, 58), (122, 36), (100, 112)), P((102, 22), (100, 58), (112, 60), (100, 112))],
        ek=-1, kk=1, toes=True, carga="cable", ancla=(122, -40)),
    "triceps_cabeza": dict(
        texto="Mancuerna a dos manos sobre la cabeza con los codos hacia el techo. Baja detrás de la cabeza doblando solo los codos y estira.",
        frames=[P((100, 20), (100, 58), (102, -20), (100, 112)), P((100, 20), (100, 58), (84, 12), (100, 112))],
        ek=-1, kk=1, toes=True, carga="db1"),
    "sent_barra": dict(
        texto="Barra sobre los trapecios, pies al ancho de hombros. Baja la cadera atrás y abajo con la espalda neutra y sube empujando el suelo.",
        frames=[P((100, 20), (100, 58), (106, 24), (100, 112)), P((108, 60), (80, 88), (114, 64), (100, 112))],
        ek=1, kk=1, toes=True, carga="espalda"),
    "goblet": dict(
        texto="Mancuerna pegada al pecho. Baja entre las rodillas con la espalda recta hasta que los muslos queden paralelos y sube.",
        frames=[P((100, 20), (100, 58), (110, 34), (100, 112)), P((108, 60), (80, 88), (122, 70), (100, 112))],
        ek=-1, kk=1, toes=True, carga="db1"),
    "prensa": dict(
        texto="Espalda y cadera pegadas al respaldo. Empuja la plataforma hasta casi estirar las piernas, sin bloquear las rodillas, y vuelve controlando.",
        frames=[P((40, 64), (66, 90), (72, 80), (92, 76)), P((40, 64), (66, 90), (72, 80), (108, 56))],
        ek=1, kk=1, toes=False, carga="plat",
        props=[("line", 24, 36, 62, 86), ("rect", 56, 92, 26, 5), ("line", 80, 98, 150, 26)]),
    "ext_cuad": dict(
        texto="Sentado con la espalda en el respaldo. Estira las piernas hasta arriba, pausa un segundo apretando el cuádriceps y baja despacio.",
        frames=[P((66, 50), (80, 88), (86, 86), (104, 112)), P((66, 50), (80, 88), (86, 86), (134, 88))],
        ek=1, kk=1, toes=True,
        props=[("rect", 60, 92, 36, 5), ("line", 54, 44, 60, 92), ("line", 70, 97, 70, 112)]),
    "curl_fem": dict(
        texto="Tumbado boca abajo con el rodillo sobre los gemelos. Flexiona las rodillas llevando los talones al glúteo y baja en 3 segundos.",
        frames=[P((122, 92), (84, 92), (150, 98), (34, 92)), P((122, 92), (84, 92), (150, 98), (64, 56))],
        ek=1, kk=1, toes=False,
        props=[("rect", 30, 98, 110, 6), ("line", 40, 104, 40, 112), ("line", 128, 104, 128, 112)]),
    "hip_thrust": dict(
        texto="Espalda alta apoyada en el banco, barra sobre la cadera. Sube la cadera apretando glúteos hasta alinear rodillas, cadera y hombros; baja sin tocar el suelo.",
        frames=[P((48, 90), (90, 102), (90, 96), (124, 112)), P((48, 90), (86, 80), (88, 84), (124, 112))],
        ek=1, kk=1, toes=True, carga="cadera",
        props=[("rect", 28, 96, 40, 6), ("line", 34, 102, 34, 112), ("line", 62, 102, 62, 112)]),
    "zancada_db": dict(
        texto="Mancuernas a los lados. Da un paso largo, baja hasta 90° en ambas rodillas con el torso erguido y empuja para volver.",
        frames=[P((100, 20), (100, 58), (102, 62), (110, 112), foot2=(90, 112)),
                P((100, 50), (100, 88), (102, 92), (136, 112), foot2=(66, 112))],
        ek=-1, kk=1, kk2=1, toes=True, carga="db"),
    "crunch": dict(
        texto="Tumbado con las rodillas dobladas y las manos junto a la cabeza. Sube las costillas hacia la pelvis, sin tirar del cuello, y baja despacio.",
        frames=[P((50, 104), (88, 104), (40, 92), (120, 112)), P((62, 84), (88, 104), (54, 74), (120, 112))],
        ek=-1, kk=1, toes=True),
    "rueda": dict(
        texto="De rodillas con la rueda bajo los hombros. Rueda hacia delante estirando el cuerpo hasta donde controles la lumbar y vuelve con el abdomen.",
        frames=[P((112, 58), (84, 84), (118, 104), (56, 110)), P((146, 98), (110, 96), (170, 106), (56, 110))],
        ek=-1, kk=1, toes=False, carga="rueda"),
    "crunch_polea": dict(
        texto="De rodillas frente a la polea alta, cuerda junto a la cabeza. Redondea la espalda llevando los codos hacia las rodillas y vuelve controlando.",
        frames=[P((96, 46), (90, 84), (106, 32), (60, 110)), P((114, 72), (90, 84), (124, 80), (60, 110))],
        ek=-1, kk=1, toes=False, carga="cable", ancla=(104, -40)),
    "run": dict(
        texto="Zancada natural con el cuerpo ligeramente inclinado, apoyo en la parte media del pie y brazos a 90° al ritmo de las piernas.",
        frames=[P((108, 22), (100, 58), (122, 40), (74, 92), hand2=(80, 44), foot2=(122, 92)),
                P((108, 22), (100, 58), (80, 44), (122, 92), hand2=(122, 40), foot2=(74, 92))],
        ek=-1, kk=1, kk2=1, toes=True, dur=0.35, hold=0.0,
        props=[("rect", 24, 113, 170, 5), ("line", 176, 113, 178, 30), ("line", 152, 30, 192, 30)]),
    "walk": dict(
        texto="Camina erguido con pasos firmes y brazos relajados. Sube la inclinación de la cinta sin agarrarte a las barras.",
        frames=[P((100, 20), (100, 58), (110, 52), (88, 112), hand2=(90, 56), foot2=(112, 112)),
                P((100, 20), (100, 58), (90, 56), (112, 112), hand2=(110, 52), foot2=(88, 112))],
        ek=-1, kk=1, kk2=1, toes=True, dur=0.6, hold=0.0,
        props=[("rect", 24, 113, 170, 5), ("line", 176, 113, 178, 30), ("line", 152, 30, 192, 30)]),
    "bici": dict(
        texto="Sentado con la espalda recta y la cadera estable. Pedalea con cadencia constante, sin balancear las caderas.",
        mode="loop", dur=0.22, hold=0.0,
        frames=[P((108, 30), (76, 56), (138, 46), (110, 92), foot2=(82, 92)),
                P((108, 30), (76, 56), (138, 46), (96, 106), foot2=(96, 78)),
                P((108, 30), (76, 56), (138, 46), (82, 92), foot2=(110, 92)),
                P((108, 30), (76, 56), (138, 46), (96, 78), foot2=(96, 106))],
        ek=1, kk=1, kk2=1, toes=True,
        props=[("circ", 96, 92, 14), ("line", 66, 60, 90, 60), ("line", 76, 62, 96, 92), ("line", 96, 92, 138, 48),
               ("circ", 154, 98, 16)]),
    "eliptica": dict(
        texto="Postura erguida; empuja los pedales con todo el pie y mueve los brazos al ritmo de las piernas.",
        frames=[P((100, 20), (100, 58), (118, 46), (84, 108), hand2=(84, 50), foot2=(120, 100)),
                P((100, 20), (100, 58), (84, 50), (120, 100), hand2=(118, 46), foot2=(84, 108))],
        ek=-1, kk=1, kk2=1, toes=True, dur=0.6, hold=0.0,
        props=[("line", 124, 30, 128, 112), ("rect", 66, 112, 100, 4)]),
    "remo_erg": dict(
        texto="Empuja primero con las piernas, luego inclina el torso atrás y termina con los brazos al abdomen. Vuelve en orden inverso: brazos, torso, piernas.",
        frames=[P((120, 66), (96, 100), (156, 78), (130, 108)), P((62, 70), (78, 102), (80, 78), (130, 108))],
        ek=-1, kk=1, toes=True, carga="cable", ancla=(172, 92), dur=0.8, hold=0.1,
        props=[("line", 50, 112, 180, 112), ("circ", 176, 90, 20), ("rect", 128, 98, 5, 14)]),
    "comba": dict(
        texto="Saltos pequeños y rápidos con las rodillas ligeramente flexionadas, aterrizando de puntillas y moviendo solo las muñecas.",
        frames=[P((100, 20), (100, 58), (118, 60), (100, 112)), P((100, 12), (100, 50), (118, 54), (100, 102))],
        ek=-1, kk=1, toes=True, dur=0.3, hold=0.0),
})

ANIMS["banca_db"] = dict(ANIMS["banca"], carga="db",
                         texto="Tumbado con una mancuerna en cada mano. Baja hasta que los codos formen 90° y empuja juntándolas arriba.")
ANIMS["curl_martillo"] = dict(ANIMS["curl_db"],
                              texto="Agarre neutro (palmas enfrentadas). Sube las mancuernas sin mover los codos y baja despacio.")

# El orden importa: las reglas más específicas primero. Textos ya sin acentos.
REGLAS_GYM = [
    ("press de banca con barra", "banca"), ("press de banca con mancuernas", "banca_db"),
    ("press de pecho en maquina", "pecho_maq"), ("press inclinado", "banca_incl"), ("aperturas", "aperturas"),
    ("jalon", "jalon"), ("remo en polea", "remo_polea"), ("remo con barra", "remo_barra"),
    ("remo con mancuerna", "remo_db"), ("remo en ergometro", "remo_erg"), ("intervalos de remo", "remo_erg"),
    ("peso muerto rumano", "rdl"), ("peso muerto", "peso_muerto"),
    ("press de hombros", "press_hombro_db"), ("press militar", "press_militar"), ("elevaciones laterales", "elev_lat"),
    ("curl martillo", "curl_martillo"), ("curl femoral", "curl_fem"), ("curl con barra", "curl_barra"),
    ("curl de biceps", "curl_db"), ("triceps en polea", "triceps_polea"), ("sobre la cabeza", "triceps_cabeza"),
    ("sentadilla con barra", "sent_barra"), ("goblet", "goblet"), ("prensa", "prensa"),
    ("extension de cuadriceps", "ext_cuad"), ("hip thrust con barra", "hip_thrust"),
    ("zancadas con mancuernas", "zancada_db"), ("crunch en polea", "crunch_polea"), ("crunch", "crunch"),
    ("rueda abdominal", "rueda"), ("caminata", "walk"), ("carrera continua", "run"), ("sprints", "run"),
    ("bicicleta estatica", "bici"), ("eliptica", "eliptica"), ("comba", "comba"),
]
