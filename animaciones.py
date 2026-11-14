"""Animaciones de ejercicios: muñeco de palitos dibujado con QPainter.

Cada animación son 2+ poses clave (hombro, cadera, mano, pie, ...) que se interpolan.
Los codos y rodillas se calculan con cinemática inversa. Coordenadas: suelo en y=112, x hacia la derecha.
"""
import math
import time
import unicodedata

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

GROUND = 112
TORSO, THIGH, SHIN, UARM, FARM = 38, 27, 27, 21, 21


def P(sh, hip, hand, foot, hand2=None, foot2=None, ht=0):
    return dict(sh=sh, hip=hip, hand=hand, foot=foot, hand2=hand2, foot2=foot2, ht=ht)


# ek/kk: sentido del doblez de codo/rodilla (+1 = antihorario en pantalla). ek2/kk2: miembros lejanos.
ANIMS = {
    "flexion": dict(
        texto="Cuerpo recto como una tabla. Baja el pecho casi hasta el suelo con los codos pegados al cuerpo y sube extendiendo los brazos.",
        frames=[P((156, 68), (122, 85), (158, 112), (66, 112)), P((160, 98), (122, 104), (158, 112), (66, 112))],
        ek=-1, kk=1, toes=False),
    "flex_rodillas": dict(
        texto="Apoya las rodillas, mantén la línea de rodillas a cabeza recta y baja el pecho al suelo. Sube sin arquear la espalda.",
        frames=[P((150, 70), (119, 92), (152, 112), (66, 104)), P((152, 98), (118, 106), (152, 112), (66, 106))],
        ek=-1, kk=-1, toes=False),
    "flex_inclinada": dict(
        texto="Manos en un banco o mesa estables. Cuerpo recto: baja el pecho hacia el borde y empuja para subir.",
        frames=[P((130, 53), (101, 77), (158, 84), (60, 112)), P((141, 69), (108, 87), (158, 84), (60, 112))],
        ek=-1, kk=1, toes=False,
        props=[("rect", 150, 84, 50, 6), ("line", 156, 90, 156, 112), ("line", 196, 90, 196, 112)]),
    "pike": dict(
        texto="Caderas altas formando una V invertida. Dobla los codos llevando la cabeza hacia el suelo, entre las manos, y empuja hacia arriba.",
        frames=[P((141, 71), (104, 62), (150, 112), (80, 112)), P((136, 94), (104, 66), (150, 112), (80, 112))],
        ek=-1, kk=1, toes=False),
    "pino": dict(
        texto="Pino con los talones apoyados en la pared. Brazos rectos, abdomen apretado y cuerpo alineado. Respira y aguanta.",
        frames=[P((110, 72), (112, 34), (110, 112), (114, -20)), P((111, 72), (113, 34), (110, 112), (115, -20))],
        ek=-1, kk=1, toes=False, dur=1.6,
        props=[("line", 126, -30, 126, 112)]),
    "pino_flex": dict(
        texto="En pino contra la pared, baja la cabeza controlada hasta rozar el suelo y empuja hasta extender los brazos.",
        frames=[P((110, 72), (112, 34), (110, 112), (114, -20)), P((111, 96), (113, 58), (110, 112), (115, 4))],
        ek=-1, kk=1, toes=False,
        props=[("line", 126, -30, 126, 112)]),
    "fondo_banco": dict(
        texto="Manos en el borde del banco, detrás de ti. Baja la cadera flexionando los codos hacia atrás hasta unos 90° y sube estirando.",
        frames=[P((98, 46), (104, 82), (90, 86), (150, 112)), P((98, 68), (104, 104), (90, 86), (150, 112))],
        ek=-1, kk=1, toes=True,
        props=[("rect", 26, 86, 70, 6), ("line", 34, 92, 34, 112), ("line", 88, 92, 88, 112)]),
    "fondo_paralelas": dict(
        texto="Sujeto en las paralelas con los brazos rectos, hombros lejos de las orejas. Baja hasta 90° de codo y empuja para subir.",
        frames=[P((100, 14), (100, 52), (100, 56), (84, 104)), P((102, 38), (104, 76), (100, 56), (88, 128))],
        ek=-1, kk=-1, toes=True,
        props=[("line", 84, 56, 124, 56), ("line", 124, 56, 124, 112), ("line", 84, 56, 84, 112)]),
    "remo": dict(
        texto="Cuerpo recto bajo la barra. Tira del pecho hacia la barra juntando las escápulas y baja con control.",
        frames=[P((142, 98), (104, 104), (148, 56), (52, 112)), P((128, 74), (97, 98), (148, 56), (52, 112))],
        ek=1, kk=1, toes=False,
        props=[("line", 140, 56, 192, 56), ("line", 192, 56, 192, 112), ("line", 140, 56, 140, 70)]),
    "dominada": dict(
        texto="Cuelga con los brazos estirados, baja las escápulas y tira hasta pasar la barbilla por encima de la barra. Baja despacio.",
        frames=[P((100, 50), (100, 88), (100, 8), (88, 120)), P((100, 30), (102, 66), (100, 8), (88, 98))],
        ek=1, kk=-1, toes=True,
        props=[("line", 56, 8, 144, 8)]),
    "sentadilla": dict(
        texto="Pies al ancho de hombros. Lleva la cadera atrás y abajo con la espalda recta, talones en el suelo, y sube empujando el suelo.",
        frames=[P((100, 20), (100, 58), (138, 24), (100, 112)), P((108, 60), (80, 88), (146, 62), (100, 112))],
        ek=1, kk=1, toes=True),
    "salto": dict(
        texto="Baja a media sentadilla y salta explosivo estirando todo el cuerpo. Aterriza suave flexionando las rodillas.",
        frames=[P((108, 60), (80, 88), (146, 62), (100, 112)), P((100, 4), (100, 42), (104, -36), (100, 96))],
        ek=1, kk=1, toes=True, dur=0.7),
    "zancada": dict(
        texto="Da un paso largo y baja hasta que ambas rodillas formen 90°. Torso erguido; empuja con el pie delantero para volver.",
        frames=[P((100, 20), (100, 58), (112, 56), (110, 112), foot2=(90, 112)),
                P((100, 50), (100, 88), (112, 86), (136, 112), foot2=(66, 112))],
        ek=1, kk=1, kk2=1, toes=True),
    "bulgara": dict(
        texto="Pie trasero apoyado en una silla. Baja en vertical con el torso recto hasta que el muslo delantero quede paralelo al suelo.",
        frames=[P((110, 20), (108, 58), (122, 56), (112, 112), foot2=(58, 76)),
                P((108, 50), (106, 88), (122, 86), (124, 112), foot2=(58, 76))],
        ek=1, kk=1, kk2=1, toes=True,
        props=[("rect", 40, 76, 24, 5), ("line", 46, 81, 46, 112), ("line", 58, 81, 58, 112)]),
    "pistol": dict(
        texto="Sobre una pierna, con la otra estirada al frente. Baja controlado hasta abajo del todo y sube sin que el talón se levante.",
        frames=[P((100, 20), (100, 58), (140, 30), (100, 112), foot2=(152, 60)),
                P((108, 64), (80, 92), (146, 66), (100, 112), foot2=(134, 92))],
        ek=1, kk=1, kk2=1, toes=True),
    "puente": dict(
        texto="Tumbado boca arriba con rodillas dobladas. Sube la cadera apretando los glúteos hasta formar una línea hombro-rodilla; baja despacio.",
        frames=[P((50, 104), (88, 104), (92, 108), (120, 112)), P((50, 104), (80, 82), (92, 108), (120, 112))],
        ek=1, kk=1, toes=True),
    "puente1": dict(
        texto="Puente con una pierna estirada en el aire. Sube la cadera con la pierna de apoyo sin que la pelvis gire.",
        frames=[P((50, 104), (88, 104), (92, 108), (120, 112), foot2=(132, 73)),
                P((50, 104), (80, 82), (92, 108), (120, 112), foot2=(124, 51))],
        ek=1, kk=1, kk2=1, toes=True),
    "nordico": dict(
        texto="De rodillas con los pies sujetos. Cae hacia delante lo más lento posible, resistiendo con los isquios, y ayúdate con las manos para subir.",
        frames=[P((78, 36), (78, 74), (100, 50), (40, 112)), P((140, 98), (112, 104), (146, 108), (40, 112))],
        ek=1, kk=1, toes=False),
    "gemelo": dict(
        texto="De pie, sube de puntillas todo lo que puedas, pausa un segundo arriba y baja despacio.",
        frames=[P((100, 20), (100, 58), (102, 60), (100, 112)), P((100, 10), (100, 48), (102, 50), (100, 102))],
        ek=1, kk=1, toes=True),
    "plancha": dict(
        texto="Antebrazos en el suelo, codos bajo los hombros. Cuerpo recto de cabeza a talones, abdomen y glúteos apretados. Respira.",
        frames=[P((152, 91), (115, 100), (173, 112), (66, 112)), P((152, 89), (115, 98), (173, 112), (66, 112))],
        ek=1, kk=1, toes=False, dur=1.6),
    "deadbug": dict(
        texto="Boca arriba, brazos al techo y rodillas a 90°. Estira a la vez el brazo y la pierna contrarios sin despegar la lumbar del suelo.",
        frames=[P((50, 104), (88, 104), (50, 62), (115, 78), hand2=(62, 66), foot2=(115, 80)),
                P((50, 104), (88, 104), (50, 62), (115, 78), hand2=(6, 98), foot2=(138, 96))],
        ek=1, kk=1, kk2=1, toes=True),
    "rodillas_tumbado": dict(
        texto="Boca arriba, manos tras la cabeza. Lleva las rodillas al pecho elevando un poco la pelvis y vuelve sin tocar el suelo con los pies.",
        frames=[P((50, 104), (88, 104), (40, 88), (140, 100)), P((50, 104), (92, 100), (40, 88), (112, 82))],
        ek=1, kk=1, toes=True),
    "piernas_tumbado": dict(
        texto="Boca arriba con las piernas rectas. Súbelas hasta la vertical y baja despacio sin arquear la espalda baja.",
        frames=[P((50, 104), (88, 104), (90, 108), (140, 102)), P((50, 104), (88, 104), (90, 108), (88, 50))],
        ek=1, kk=1, toes=True),
    "hollow": dict(
        texto="Boca arriba, lumbar pegada al suelo. Levanta hombros y piernas formando un plátano, brazos junto a las orejas. Aguanta.",
        frames=[P((50, 92), (86, 104), (6, 86), (138, 92)), P((50, 95), (86, 104), (6, 90), (138, 95))],
        ek=1, kk=1, toes=True, dur=1.6),
    "lsit": dict(
        texto="Manos apoyadas, brazos rectos y hombros hacia abajo. Eleva las piernas estiradas en horizontal y aguanta.",
        frames=[P((96, 58), (98, 96), (100, 100), (152, 96)), P((96, 58), (98, 99), (100, 100), (152, 93))],
        ek=1, kk=1, toes=True, dur=1.6,
        props=[("line", 88, 100, 112, 100), ("line", 88, 100, 88, 112), ("line", 112, 100, 112, 112)]),
    "colgado_rodillas": dict(
        texto="Colgado de la barra, sube las rodillas hacia el pecho sin balancearte y baja con control.",
        frames=[P((100, 50), (100, 88), (100, 8), (96, 142)), P((100, 50), (96, 88), (100, 8), (118, 96))],
        ek=1, kk=1, toes=True,
        props=[("line", 56, 8, 144, 8)]),
    "colgado_piernas": dict(
        texto="Colgado de la barra, sube las piernas rectas hasta la horizontal (o hasta tocar la barra) y baja despacio.",
        frames=[P((100, 50), (100, 88), (100, 8), (96, 142)), P((100, 50), (96, 88), (100, 8), (152, 86))],
        ek=1, kk=1, toes=True,
        props=[("line", 56, 8, 144, 8)]),
    "bicicleta": dict(
        texto="Boca arriba, manos tras la cabeza. Pedalea lento llevando el codo hacia la rodilla contraria.",
        frames=[P((50, 100), (88, 104), (40, 88), (110, 84), foot2=(140, 96)),
                P((50, 100), (88, 104), (40, 88), (140, 96), foot2=(110, 84))],
        ek=1, kk=1, kk2=1, toes=True),
    "superman": dict(
        texto="Boca abajo. Levanta a la vez brazos, pecho y piernas apretando la espalda y los glúteos; aguanta un segundo.",
        frames=[P((100, 104), (62, 104), (142, 104), (8, 104)), P((100, 94), (62, 102), (142, 90), (8, 90))],
        ek=1, kk=1, toes=False),
    "jacks": dict(
        texto="Salta abriendo piernas y subiendo los brazos por encima de la cabeza; vuelve al centro. Ritmo constante.",
        frames=[P((100, 20), (100, 58), (88, 60), (92, 112), hand2=(112, 60), foot2=(108, 112)),
                P((100, 14), (100, 52), (70, -14), (74, 108), hand2=(130, -14), foot2=(126, 108))],
        ek=1, kk=1, toes=False, dur=0.5, front=True),
    "escalador": dict(
        texto="En posición de plancha alta, lleva una rodilla al pecho y cambia de pierna rápido, con la cadera baja.",
        frames=[P((156, 68), (122, 85), (158, 112), (66, 112), foot2=(138, 108)),
                P((156, 68), (122, 85), (158, 112), (138, 108), foot2=(66, 112))],
        ek=-1, kk=1, kk2=1, toes=False, dur=0.45),
    "burpee": dict(
        texto="De pie, baja con las manos al suelo, lleva los pies atrás a plancha, haz una flexión, vuelve y salta con los brazos arriba.",
        mode="loop", dur=0.55,
        frames=[P((100, 20), (100, 58), (102, 60), (100, 112)),
                P((118, 74), (88, 90), (130, 112), (100, 112)),
                P((156, 68), (122, 85), (158, 112), (66, 112)),
                P((118, 74), (88, 90), (130, 112), (100, 112)),
                P((100, 6), (100, 44), (104, -34), (100, 98))],
        ek=1, kk=1, toes=False),
    "gatovaca": dict(
        texto="A cuatro apoyos. Redondea la espalda mirando al ombligo (gato) y luego arquéala subiendo la mirada (vaca), al ritmo de la respiración.",
        frames=[P((128, 80), (92, 76), (130, 112), (56, 112), ht=50), P((128, 76), (92, 84), (130, 112), (56, 112), ht=-35)],
        ek=1, kk=1, toes=False, dur=1.4),
    "pecho": dict(
        texto="Antebrazos en el marco de la puerta, codos a 90°. Da un pequeño paso adelante notando el estiramiento del pecho. Aguanta 20-30 s.",
        frames=[P((100, 20), (100, 58), (62, -6), (92, 112), hand2=(138, -6), foot2=(108, 112)),
                P((100, 21), (100, 59), (62, -6), (92, 112), hand2=(138, -6), foot2=(108, 112))],
        ek=1, kk=1, toes=False, dur=1.8, front=True,
        props=[("line", 58, -20, 58, 112), ("line", 142, -20, 142, 112)]),
    "nino": dict(
        texto="Siéntate sobre los talones y estira los brazos al frente apoyando la frente en el suelo. Relaja hombros y espalda y respira hondo.",
        frames=[P((104, 96), (66, 98), (150, 108), (30, 110), ht=40), P((106, 94), (66, 96), (152, 108), (30, 110), ht=40)],
        ek=1, kk=1, toes=False, dur=1.8),
}

REGLAS = [
    ("pino en pared (aguante)", "pino"), ("flexiones de pino", "pino_flex"), ("pike", "pike"),
    ("inclinadas", "flex_inclinada"), ("flexiones con rodillas", "flex_rodillas"), ("flexiones", "flexion"),
    ("fondos de triceps en banco", "fondo_banco"), ("fondos", "fondo_paralelas"),
    ("superman", "superman"), ("remo", "remo"), ("dominadas", "dominada"),
    ("sentadilla bulgara", "bulgara"), ("sentadilla con salto", "salto"), ("pistol", "pistol"),
    ("sentadilla", "sentadilla"), ("zancada", "zancada"),
    ("una pierna", "puente1"), ("puente", "puente"), ("hip thrust", "puente"), ("nordico", "nordico"),
    ("talones", "gemelo"), ("plancha", "plancha"), ("dead bug", "deadbug"),
    ("rodillas tumbado", "rodillas_tumbado"), ("piernas tumbado", "piernas_tumbado"),
    ("hollow", "hollow"), ("l-sit", "lsit"), ("rodillas colgado", "colgado_rodillas"),
    ("colgado", "colgado_piernas"), ("toes to bar", "colgado_piernas"),
    ("bicicleta", "bicicleta"), ("russian", "bicicleta"), ("jumping", "jacks"),
    ("mountain", "escalador"), ("burpee", "burpee"), ("gato", "gatovaca"),
    ("pectoral", "pecho"), ("nino", "nino"),
]


def _norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def anim_para(nombre):
    n = _norm(nombre)
    for clave, anim in REGLAS_GYM + REGLAS:
        if clave in n:
            return anim
    return None


from animaciones_gym import REGLAS_GYM  # noqa: E402  (registra las animaciones de gimnasio)


# ---------------------------------------------------------------- geometría
def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _mezcla(f1, f2, t):
    out = {}
    for k in ("sh", "hip", "hand", "foot"):
        out[k] = _lerp(f1[k], f2[k], t)
    for k, base in (("hand2", "hand"), ("foot2", "foot")):
        a = f1[k] or (f1[base][0] - 3, f1[base][1] - 2 if k == "hand2" else f1[base][1])
        b = f2[k] or (f2[base][0] - 3, f2[base][1] - 2 if k == "hand2" else f2[base][1])
        out[k] = _lerp(a, b, t)
    out["ht"] = f1["ht"] + (f2["ht"] - f1["ht"]) * t
    return out


def _ik(a, b, l1, l2, bend):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = max(math.hypot(dx, dy), 1e-6)
    dc = min(d, l1 + l2 - 0.01)
    c = max(-1, min(1, (l1 * l1 + dc * dc - l2 * l2) / (2 * l1 * dc)))
    ang = math.atan2(dy, dx) - bend * math.acos(c)
    return (a[0] + l1 * math.cos(ang), a[1] + l1 * math.sin(ang))


def _norm_torso(sh, hip):
    dx, dy = hip[0] - sh[0], hip[1] - sh[1]
    d = max(math.hypot(dx, dy), 1e-6)
    return (sh[0] + dx / d * TORSO, sh[1] + dy / d * TORSO)


def _bbox(anim):
    xs, ys = [], []
    for f in anim["frames"]:
        for k in ("sh", "hip", "hand", "foot", "hand2", "foot2"):
            if f[k]:
                xs.append(f[k][0]); ys.append(f[k][1])
        xs += [f["sh"][0] - 20, f["sh"][0] + 20]
        ys += [f["sh"][1] - 24, f["sh"][1] + 24]
    if anim.get("ancla"):
        xs.append(anim["ancla"][0]); ys.append(anim["ancla"][1])
    for p in anim.get("props", []):
        if p[0] == "line":
            xs += [p[1], p[3]]; ys += [p[2], p[4]]
        elif p[0] == "circ":
            xs += [p[1] - p[3], p[1] + p[3]]; ys += [p[2] - p[3], p[2] + p[3]]
        else:
            xs += [p[1], p[1] + p[3]]; ys += [p[2], p[2] + p[4]]
    ys.append(GROUND + 2)
    return min(xs) - 10, min(ys) - 8, max(xs) + 24, max(ys) + 6


def pose_en(anim, t):
    """Pose interpolada en el instante t (segundos)."""
    fr = anim["frames"]
    n = len(fr)
    dur, hold = anim.get("dur", 1.1), anim.get("hold", 0.25)
    if anim.get("mode") == "loop":
        seq = list(range(n)) + [0]
        hold = 0.05
    else:
        seq = list(range(n)) + list(range(n - 2, 0, -1)) + [0]
    seg = dur + hold
    total = seg * (len(seq) - 1)
    t %= total
    i = int(t // seg)
    u = t - i * seg
    u = 0.0 if u < hold else (u - hold) / dur
    u = u * u * (3 - 2 * u)
    return _mezcla(fr[seq[i]], fr[seq[i + 1]], u)


class AnimWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(230)
        self.anim = None
        self.color = QColor("#ffffff")
        self.accent = QColor("#ffb02e")
        self.t0 = time.monotonic()
        self.timer = QTimer(self, interval=33, timeout=self.update)
        self.timer.start()

    def set_theme(self, t):
        self.color = QColor(t["text"])
        self.accent = QColor(t["accent"])
        self.update()

    def set_anim(self, clave):
        self.anim = ANIMS.get(clave)
        self.bb = _bbox(self.anim) if self.anim else None
        self.t0 = time.monotonic()
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        p.setPen(QPen(QColor(255, 255, 255, 40), 1))
        p.setBrush(QColor(0, 0, 0, 70))
        p.drawRoundedRect(r, 14, 14)
        if not self.anim:
            p.setPen(self.color)
            p.drawText(r, Qt.AlignCenter, "Elige un ejercicio de la lista")
            return
        a = self.anim
        x0, y0, x1, y1 = self.bb
        s = min(r.width() / (x1 - x0), r.height() / (y1 - y0))
        p.translate(r.center().x() - (x0 + x1) / 2 * s, r.center().y() - (y0 + y1) / 2 * s)
        p.scale(s, s)
        pose = pose_en(a, time.monotonic() - self.t0)

        def L(p1, p2, w, col):
            p.setPen(QPen(col, w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawLine(QPointF(*p1), QPointF(*p2))

        # suelo y utillaje
        ac = QColor(self.accent)
        ac.setAlpha(220)
        gc = QColor(self.color)
        gc.setAlpha(110)
        L((x0, GROUND + 3), (x1, GROUND + 3), 3, gc)
        for pr in a.get("props", []):
            if pr[0] == "line":
                L((pr[1], pr[2]), (pr[3], pr[4]), 4, ac)
            elif pr[0] == "circ":
                p.setPen(QPen(ac, 3))
                p.setBrush(Qt.NoBrush)
                p.drawEllipse(QPointF(pr[1], pr[2]), pr[3], pr[3])
            else:
                p.setPen(Qt.NoPen)
                p.setBrush(ac)
                p.drawRoundedRect(QRectF(pr[1], pr[2], pr[3], pr[4]), 2, 2)

        sh = pose["sh"]
        hip = _norm_torso(sh, pose["hip"])
        ek, kk = a.get("ek", 1), a.get("kk", 1)
        near, far = QColor(self.color), QColor(self.color)
        far.setAlpha(130)

        def miembro(raiz, destino, l1, l2, bend, col, toes=False):
            j = _ik(raiz, destino, l1, l2, bend)
            L(raiz, j, 7, col)
            L(j, destino, 7, col)
            if toes:
                L(destino, (destino[0] + 11, min(GROUND, destino[1] + 9)), 6, col)

        t = a.get("toes", True)
        miembro(hip, pose["foot2"], THIGH, SHIN, a.get("kk2", kk), far, t)
        miembro(sh, pose["hand2"], UARM, FARM, a.get("ek2", ek), far)
        L(sh, hip, 9, near)
        miembro(hip, pose["foot"], THIGH, SHIN, kk, near, t)
        miembro(sh, pose["hand"], UARM, FARM, ek, near)
        # cabeza
        d = math.atan2(sh[1] - hip[1], sh[0] - hip[0]) + math.radians(pose["ht"])
        cx, cy = sh[0] + math.cos(d) * 16, sh[1] + math.sin(d) * 16
        L(sh, (sh[0] + math.cos(d) * 7, sh[1] + math.sin(d) * 7), 5, near)
        p.setPen(QPen(near, 2))
        p.setBrush(self.accent)
        p.drawEllipse(QPointF(cx, cy), 9, 9)
        self._carga(p, a, pose, sh, hip, L)
        p.end()

    def _carga(self, p, a, pose, sh, hip, L):
        c = a.get("carga")
        if not c:
            return
        acc2 = QColor(self.accent)
        oscuro = QColor(25, 25, 30, 235)

        def disco(pt, r):
            p.setPen(QPen(acc2, 2.5))
            p.setBrush(oscuro)
            p.drawEllipse(QPointF(*pt), r, r)
            p.setPen(Qt.NoPen)
            p.setBrush(acc2)
            p.drawEllipse(QPointF(*pt), r * 0.28, r * 0.28)

        h, h2 = pose["hand"], pose["hand2"]
        if c == "barra":
            disco(h, 12)
        elif c == "db":
            disco(h2, 6.5)
            disco(h, 6.5)
        elif c == "db1":
            disco(h, 8)
        elif c == "espalda":
            disco((sh[0] - 7, sh[1] - 3), 12)
        elif c == "cadera":
            disco(hip, 12)
        elif c == "rueda":
            disco(h, 9)
        elif c == "plat":
            f = pose["foot"]
            L((f[0] + 8, f[1] + 14), (f[0] + 22, f[1] - 20), 6, acc2)
        elif c == "cable":
            col = QColor(acc2)
            col.setAlpha(190)
            L(h, a["ancla"], 2, col)
            L((h[0] - 5, h[1]), (h[0] + 5, h[1]), 5, acc2)
