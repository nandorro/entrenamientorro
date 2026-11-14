"""
Calistenia Plan — app de escritorio (PySide6) con quiz y plan de entrenamiento.
Interfaz amable al estilo de Navidad IPTV: fondo degradado animado, guirnalda de luces,
partículas, paneles redondeados y varios temas.

Ejecutar:  iniciar.bat   (o  python calistenia.py)
"""
import json
import math
import re
import random
import sys
import threading
import traceback
from datetime import date, datetime
from pathlib import Path

from PySide6.QtCore import QObject, QPointF, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFrame, QHBoxLayout, QLineEdit,
                               QLabel, QListWidget, QListWidgetItem, QMessageBox, QProgressBar, QPushButton, QScrollArea,
                               QPlainTextEdit, QSpinBox, QStackedWidget, QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

import drive
import registro as reg
from html import escape as esc
from animaciones import ANIMS, AnimWidget, FotoWidget, anim_para
from gym import (SENALES_DESCARGA, SENALES_TEXTO, FASES, ejercicio_en, generar_plan_gym, prescripcion_gym, titulo_semana)
from graficas import Analisis, GraficaBarras, GraficaLinea
from nutricion import generar_plan_nutricion
from plan import NOMBRES_DIAS, generar_plan, prescripcion, resumen_perfil
from progreso import carga_semanal, proyeccion_peso

AQUI = Path(__file__).resolve().parent
DATA = AQUI / "datos.json"

THEMES = {
    "fuego": dict(
        label="🔥 Fuego", title="💪 Calistenia Plan 💪", tagline="Tu cuerpo es tu gimnasio. ¡Vamos a por ello!",
        top="#3a0d05", bottom="#c8431a", panel="rgba(50,10,4,165)", text="#fff1e4",
        accent="#ffb02e", accent2="#fff0b3", select_text="#3a0d05",
        bulbs=["#ffb02e", "#ff5a36", "#fff0b3"], particles="sparkle", pcolor="#ffd9a0"),
    "bosque": dict(
        label="🌲 Bosque", title="🌲 Calistenia Plan 🌲", tagline="Entrena al aire libre, aunque sea en tu salón.",
        top="#07300a", bottom="#2a8a1f", panel="rgba(2,28,4,160)", text="#eaffd0",
        accent="#b6ff3a", accent2="#e8ffb0", select_text="#06240a",
        bulbs=["#e8161b", "#b6ff3a", "#ffe14a"], particles="snow", pcolor="#d8ffd0"),
    "oceano": dict(
        label="🌊 Océano", title="🌊 Calistenia Plan 🌊", tagline="Fluye, respira y empuja.",
        top="#041c3a", bottom="#1d78b5", panel="rgba(4,24,50,160)", text="#e8f6ff",
        accent="#5fe0ff", accent2="#c2f2ff", select_text="#04223c",
        bulbs=["#5fe0ff", "#ffffff", "#8fb8ff"], particles="snow", pcolor="#d8f2ff"),
    "navidad": dict(
        label="🎅 Navidad", title="🎅 Calistenia Plan 🎅", tagline="¡Jo, jo, jo! Quema los turrones.",
        top="#7a0a0a", bottom="#d92222", panel="rgba(70,0,0,160)", text="#ffffff",
        accent="#ffd24a", accent2="#ffffff", select_text="#5a0000",
        bulbs=["#ffffff", "#ffd24a", "#38c15a"], particles="snow", pcolor="#ffffff"),
    "noche": dict(
        label="🌙 Noche", title="🌙 Calistenia Plan 🌙", tagline="Entrenamiento tranquilo bajo las estrellas.",
        top="#0b0a24", bottom="#3a2f8a", panel="rgba(12,10,44,165)", text="#f0eeff",
        accent="#ffd84a", accent2="#c9bfff", select_text="#15103a",
        bulbs=["#ffd84a", "#c9bfff", "#ff8fd0"], particles="sparkle", pcolor="#ffffff"),
}

def qcol(c, a=255):
    q = QColor(c)
    q.setAlpha(a)
    return q


def make_qss(t):
    return f"""
    QWidget {{ color:{t['text']}; font-size:14px; }}
    QLabel#title {{ color:{t['accent']}; font-family:Georgia; font-size:32px; font-weight:bold; font-style:italic; }}
    QLabel#tagline {{ color:{t['accent2']}; font-size:14px; font-style:italic; }}
    QLabel#pregunta {{ color:{t['accent']}; font-size:21px; font-weight:bold; }}
    QLabel#hint {{ color:{t['accent2']}; font-size:13px; }}
    QFrame#panel {{ background:{t['panel']}; border:2px solid {t['accent']}; border-radius:18px; }}
    QFrame#kpi {{ background:rgba(0,0,0,70); border:1px solid {t['accent2']}; border-radius:12px; }}
    QLabel#kpiv {{ color:{t['accent']}; font-size:22px; font-weight:bold; }}
    QPushButton {{ background:{t['accent']}; color:{t['select_text']}; border:none; border-radius:12px;
                  padding:8px 16px; font-weight:bold; }}
    QPushButton:hover {{ background:{t['accent2']}; }}
    QPushButton#opcion {{ background:rgba(255,255,255,28); color:{t['text']}; border:2px solid {t['accent2']};
                         padding:13px; font-size:16px; text-align:left; }}
    QPushButton#opcion:hover {{ border-color:{t['accent']}; background:rgba(255,255,255,55); }}
    QPushButton#opcion:checked {{ background:{t['accent']}; color:{t['select_text']}; border-color:{t['accent']}; }}
    QPushButton#modo {{ background:rgba(0,0,0,90); color:{t['text']}; border:2px solid {t['accent2']};
                      border-radius:14px; padding:10px; font-size:16px; }}
    QPushButton#modo:checked {{ background:{t['accent']}; color:{t['select_text']}; border-color:{t['accent']}; }}
    QPushButton#atras {{ background:transparent; color:{t['accent2']}; border:none; }}
    QComboBox, QSpinBox, QDoubleSpinBox {{ background:rgba(0,0,0,110); border:1px solid {t['accent']};
                                         border-radius:10px; padding:5px 8px; }}
    QComboBox QAbstractItemView {{ background:{t['top']}; selection-background-color:{t['accent']};
                                   selection-color:{t['select_text']}; border:1px solid {t['accent']}; }}
    QProgressBar {{ background:rgba(0,0,0,100); border:1px solid {t['accent2']}; border-radius:9px;
                   text-align:center; height:18px; }}
    QProgressBar::chunk {{ background:{t['accent']}; border-radius:8px; }}
    QTabWidget::pane {{ border:0; }}
    QTabBar::tab {{ background:rgba(0,0,0,70); color:{t['text']}; padding:9px 18px; margin-right:4px;
                   border-radius:10px; font-weight:bold; }}
    QTabBar::tab:selected {{ background:{t['accent']}; color:{t['select_text']}; }}
    QTextBrowser, QListWidget {{ background:rgba(0,0,0,80); border:1px solid {t['accent2']};
                                border-radius:12px; padding:6px; }}
    QListWidget {{ outline:0; }}
    QListWidget::item {{ padding:7px 8px; border-radius:8px; }}
    QListWidget::item:hover {{ background:rgba(255,255,255,40); }}
    QListWidget::item:selected {{ background:{t['accent']}; color:{t['select_text']}; }}
    QScrollArea {{ background:transparent; border:0; }}
    QScrollBar:vertical {{ background:transparent; width:10px; }}
    QScrollBar::handle:vertical {{ background:{t['accent2']}; border-radius:5px; min-height:24px; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height:0; }}
    """


class Scene(QWidget):
    """Fondo: degradado + partículas + guirnalda de luces parpadeantes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.t = THEMES["fuego"]
        self.tick = 0
        self.parts = []
        self.timer = QTimer(self, timeout=self._step, interval=40)
        self.timer.start()

    def set_theme(self, t):
        self.t = t
        self.parts = []
        self.update()

    def _step(self):
        self.tick += 1
        w, h = max(self.width(), 1), max(self.height(), 1)
        while len(self.parts) < 70:
            self.parts.append([random.uniform(0, w), random.uniform(-h, 0), random.uniform(0.6, 2.2),
                               random.uniform(-0.4, 0.4), random.uniform(1.5, 4.0), random.uniform(0, 6.28)])
        for p in self.parts:
            p[1] += p[2]
            p[0] += p[3] + math.sin(self.tick / 30 + p[5]) * 0.3
            if p[1] > h:
                p[0], p[1] = random.uniform(0, w), random.uniform(-30, 0)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, qcol(self.t["top"]))
        g.setColorAt(1, qcol(self.t["bottom"]))
        p.fillRect(self.rect(), g)
        # partículas
        p.setPen(Qt.NoPen)
        for x, y, _, _, r, ph in self.parts:
            if self.t["particles"] == "sparkle":
                a = int(80 + 150 * abs(math.sin(self.tick / 14 + ph)))
                rg = QRadialGradient(x, y, r * 3)
                rg.setColorAt(0, qcol(self.t["pcolor"], a))
                rg.setColorAt(1, qcol(self.t["pcolor"], 0))
                p.setBrush(QBrush(rg))
                p.drawEllipse(QPointF(x, y), r * 3, r * 3)
            else:
                p.setBrush(qcol(self.t["pcolor"], 190))
                p.drawEllipse(QPointF(x, y), r, r)
        # guirnalda
        pen = QPen(qcol("#101010", 200), 2)
        p.setPen(pen)
        pts = [(x, 14 + 14 * math.sin(x / w * math.pi * 6)) for x in range(0, w + 8, 8)]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            p.drawLine(int(x1), int(y1), int(x2), int(y2))
        p.setPen(Qt.NoPen)
        bulbs = self.t["bulbs"]
        for i, x in enumerate(range(20, w, 46)):
            y = 14 + 14 * math.sin(x / w * math.pi * 6) + 10
            c = bulbs[i % len(bulbs)]
            on = (self.tick // 12 + i) % 3 != 0
            rg = QRadialGradient(x, y + 8, 22)
            rg.setColorAt(0, qcol(c, 150 if on else 30))
            rg.setColorAt(1, qcol(c, 0))
            p.setBrush(QBrush(rg))
            p.drawEllipse(QPointF(x, y + 8), 22, 22)
            p.setBrush(qcol(c, 255 if on else 110))
            p.drawEllipse(QPointF(x, y + 8), 6, 9)
        p.end()


PREG = {p["k"]: p for p in [
    {"k": "objetivo", "t": "¿Cuál es tu objetivo principal?", "o": [
        ("💪 Ganar músculo", "musculo"), ("🔥 Perder grasa", "grasa"),
        ("🏋️ Ganar fuerza", "fuerza"), ("🧘 Estar en forma en general", "general")]},
    {"k": "experiencia", "t": "¿Qué experiencia tienes entrenando?", "o": [
        ("🌱 Nunca he entrenado", "nunca"), ("🚶 Algo (menos de 6 meses)", "poco"),
        ("🏃 Entre 6 meses y 2 años", "medio"), ("🦾 Más de 2 años", "avanzado")]},
    {"k": "info_meta", "info": True, "t": "¡Vamos a hacerlo posible!",
     "texto": "Con un plan a tu medida, ajustado a tu nivel y a tu tiempo, avanzarás de forma constante sin pasarte horas entrenando."},
    {"k": "actual", "t": "¿Con qué frecuencia entrenas ahora?", "o": [
        ("😴 Nada", "nunca"), ("🚶 1-2 veces por semana", "1-2"), ("🏃 3-4 veces por semana", "3-4"),
        ("🔥 5 o más veces", "5+")]},
    {"k": "flexiones", "t": "¿Cuántas flexiones seguidas puedes hacer?", "o": [
        ("0 – 5", "0-5"), ("6 – 15", "6-15"), ("16 – 30", "16-30"), ("Más de 30", "31+")]},
    {"k": "dominadas", "t": "¿Y cuántas dominadas?\n(si no puedes o no tienes barra, elige 0)", "o": [
        ("0", "0"), ("1 – 4", "1-4"), ("5 – 10", "5-10"), ("Más de 10", "11+")]},
    {"k": "sentadillas", "t": "¿Cuántas sentadillas seguidas puedes hacer?", "o": [
        ("0 – 10", "0-10"), ("11 – 25", "11-25"), ("26 – 50", "26-50"), ("Más de 50", "51+")]},
    {"k": "info_nivel", "info": True, "t": "Así conocemos tu nivel real",
     "texto": "Estas pruebas nos ayudan a empezar con los ejercicios correctos: ni tan fáciles que no avances, ni tan duros que te lesiones."},
    {"k": "zonas", "t": "¿Qué zonas quieres priorizar?\n(puedes elegir varias o ninguna)", "multi": True, "o": [
        ("Pecho", "pecho"), ("Espalda", "espalda"), ("Hombros", "hombros"), ("Brazos", "brazos"),
        ("Abdomen", "abdomen"), ("Piernas", "piernas"), ("Glúteos", "gluteos")]},
    {"k": "equipo", "t": "¿Con qué material cuentas para calistenia?", "o": [
        ("🏠 Nada, solo mi cuerpo", "nada"), ("🪝 Barra de dominadas", "barra"),
        ("🤸 Barra + paralelas o anillas", "completo")]},
    {"k": "dias", "t": "¿Cuántos días por semana quieres entrenar calistenia?", "o": [
        (f"{n} días", n) for n in (2, 3, 4, 5, 6)]},
    {"k": "duracion", "t": "¿Cuánto tiempo tienes por sesión de calistenia?", "o": [
        (f"⏱ {n} min", n) for n in (20, 30, 45, 60)]},
    {"k": "info_estilo", "info": True, "t": "Tu día a día también cuenta",
     "texto": "El sueño, el movimiento diario y las molestias influyen en cómo te recuperas. Lo tenemos en cuenta."},
    {"k": "limitaciones", "t": "¿Tienes alguna molestia o limitación?\n(puedes elegir varias o ninguna)",
     "multi": True, "o": [("Muñecas", "muñecas"), ("Hombros", "hombros"), ("Rodillas", "rodillas")]},
    {"k": "dia", "t": "¿Cómo es tu día típico?", "o": [
        ("🪑 Sedentario (sentado casi todo el día)", "sedentario"), ("🚶 Moderado (de pie y andando a ratos)", "moderado"),
        ("🏗️ Activo (físico o en movimiento)", "activo")]},
    {"k": "sueno", "t": "¿Cuántas horas duermes normalmente?", "o": [
        ("Menos de 6 h", "<6"), ("6 – 7 h", "6-7"), ("7 – 8 h", "7-8"), ("Más de 8 h", "8+")]},
    {"k": "datos", "t": "Tus medidas", "form": True},
    {"k": "sexo", "t": "Para calcular tu gasto de energía, ¿cuál es tu sexo?", "o": [
        ("👨 Hombre", "hombre"), ("👩 Mujer", "mujer"), ("Prefiero no decirlo", "otro")]},
    {"k": "info_nutri", "info": True, "t": "Comer bien es la mitad del resultado",
     "texto": "Calculamos tus calorías, proteínas y agua según tu cuerpo y tu objetivo, y te proponemos menús sencillos. Sin dietas extremas."},
    {"k": "dieta", "t": "¿Qué tipo de dieta prefieres?", "o": [
        ("🍗 De todo (omnívora)", "omnivora"), ("🥚 Vegetariana", "vegetariana"), ("🌱 Vegana", "vegana")]},
    {"k": "comidas", "t": "¿Cuántas comidas al día prefieres?", "o": [("3 comidas", 3), ("4 comidas", 4), ("5 comidas", 5)]},
    {"k": "desayuno", "t": "¿A qué hora sueles desayunar?", "o": [
        ("Antes de las 7", "<7"), ("Entre las 7 y las 9", "7-9"), ("Entre las 9 y las 11", "9-11")]},
    {"k": "agua", "t": "¿Cuánta agua bebes al día?\n(1 vaso = 250 ml)", "o": [
        ("Menos de 3 vasos", "<3"), ("3 – 5 vasos", "3-5"), ("6 – 8 vasos", "6-8"), ("Más de 8 vasos", "8+")]},
    {"k": "antojos", "t": "¿Qué sueles antojarte?\n(puedes elegir varias o ninguna)", "multi": True, "o": [
        ("🍫 Dulces", "dulces"), ("🥨 Salado", "salado"), ("🍟 Frituras", "frituras"), ("🥤 Refrescos", "refrescos"),
        ("🍷 Alcohol", "alcohol")]},
    {"k": "registro", "t": "¿Sueles apuntar lo que comes?", "o": [("Sí, casi siempre", "si"), ("No", "no")]},
    {"k": "gym_equipo", "t": "¿Con qué material vas a entrenar?", "o": [
        ("🏋️ Gimnasio completo (máquinas, poleas y barras)", "completo"),
        ("🏠 Mancuernas, banco y barra de dominadas", "casa_barra"), ("🏠 Mancuernas y banco", "casa")]},
    {"k": "gym_cardio", "t": "¿Qué cardio prefieres?", "o": [
        ("🚶 Suave y constante (caminar, bici…)", "LISS"), ("⚡ Intervalos intensos", "HIIT"), ("🤷 Un poco de cada", "mixto")]},
    {"k": "gym_dias", "t": "¿Cuántos días por semana irás al gimnasio?", "o": [
        (f"{n} días", n) for n in (2, 3, 4, 5, 6)]},
    {"k": "gym_duracion", "t": "¿Cuánto tiempo tienes en el gimnasio por sesión?", "o": [
        (f"⏱ {n} min", n) for n in (30, 45, 60, 75, 90)]},
]}
ORDEN = {
    "calistenia": ["objetivo", "info_meta", "experiencia", "actual", "flexiones", "dominadas", "sentadillas", "info_nivel",
                   "zonas", "equipo", "dias", "duracion", "info_estilo", "limitaciones", "dia", "sueno", "datos"],
    "gym": ["objetivo", "info_meta", "experiencia", "actual", "flexiones", "dominadas", "sentadillas", "info_nivel",
            "zonas", "info_estilo", "limitaciones", "dia", "sueno", "datos", "gym_equipo", "gym_cardio", "gym_dias",
            "gym_duracion"],
}
ORDEN["nutricion"] = ["objetivo", "sexo", "dia", "sueno", "datos", "info_nutri", "dieta", "comidas", "desayuno", "agua",
                      "antojos", "registro"]
SOLO_MODO = {"calistenia": ["equipo", "dias", "duracion"], "gym": ["gym_dias", "gym_duracion"],
             "nutricion": ["dieta", "comidas", "desayuno", "agua", "antojos", "registro"]}
MODOS = {
    "calistenia": dict(label="💪 Calistenia", title="💪 Calistenia Plan 💪", tagline=None),
    "gym": dict(label="🥦 GymBrocoli", title="🥦 GymBrocoli 🥦",
                tagline="Hierro, brócoli y progresión semana a semana."),
    "nutricion": dict(label="🥗 Nutrición", title="🥗 Nutrición 🥗",
                      tagline="Calorías, proteína y agua a tu medida, sin dietas extremas."),
}
PERFIL_KEYS = ["objetivo", "experiencia", "actual", "flexiones", "dominadas", "sentadillas", "zonas", "limitaciones",
               "dia", "sueno", "sexo", "edad", "altura", "peso", "peso_obj"]
# Bloques del quiz (como el «My Profile» de las apps de entrenamiento): se muestran en la barra de progreso
SECCION = {"objetivo": "Perfil", "info_meta": "Perfil", "experiencia": "Perfil", "actual": "Perfil",
           "flexiones": "Entrenamiento", "dominadas": "Entrenamiento", "sentadillas": "Entrenamiento",
           "info_nivel": "Entrenamiento", "zonas": "Entrenamiento", "equipo": "Entrenamiento", "dias": "Entrenamiento",
           "duracion": "Entrenamiento", "gym_dias": "Entrenamiento", "gym_duracion": "Entrenamiento",
           "gym_equipo": "Entrenamiento", "gym_cardio": "Entrenamiento",
           "info_estilo": "Estilo de vida", "limitaciones": "Estilo de vida", "dia": "Estilo de vida",
           "sueno": "Estilo de vida", "datos": "Medidas", "sexo": "Perfil", "info_nutri": "Nutrición", "dieta": "Nutrición",
           "comidas": "Nutrición", "desayuno": "Nutrición", "agua": "Nutrición", "antojos": "Nutrición", "registro": "Nutrición"}


class Bus(QObject):
    estado = Signal(str)          # texto para la etiqueta de sincronización
    remoto = Signal(str, object)  # (estado, texto) al bajar los datos de Drive


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.bus = Bus()
        self.bus.estado.connect(self._estado)
        self.bus.remoto.connect(self._remoto_recibido)
        self.timer_sync = QTimer(self, singleShot=True, interval=1800)
        self.timer_sync.timeout.connect(self._subir_ahora)
        self._subiendo = False
        self._pendiente = False
        self.setWindowTitle("Calistenia Plan · GymBrocoli")
        self.resize(960, 840)
        self.datos = self._cargar()
        self._migrar()
        self.tkey = self.datos.get("tema") if self.datos.get("tema") in THEMES else "fuego"
        self.modo = self.datos.get("modo") if self.datos.get("modo") in MODOS else "calistenia"
        self.paso = 0
        self.resp = {}
        self.preguntas = []
        self.cargando = None
        self.anim = None

        self.scene = Scene(self)
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 52, 26, 18)

        cab = QHBoxLayout()
        col = QVBoxLayout()
        self.lbl_title = QLabel(objectName="title")
        self.lbl_tag = QLabel(objectName="tagline")
        col.addWidget(self.lbl_title)
        col.addWidget(self.lbl_tag)
        cab.addLayout(col, 1)
        self.lbl_sync = QLabel("", objectName="hint")
        self.lbl_sync.setAlignment(Qt.AlignRight | Qt.AlignTop)
        cab.addWidget(self.lbl_sync, 0, Qt.AlignTop)
        self.cmb = QComboBox()
        for k, t in THEMES.items():
            self.cmb.addItem(t["label"], k)
        self.cmb.setCurrentIndex(list(THEMES).index(self.tkey))
        self.cmb.currentIndexChanged.connect(lambda _: self.aplicar_tema(self.cmb.currentData()))
        cab.addWidget(self.cmb, 0, Qt.AlignTop)
        root.addLayout(cab)

        barra = QHBoxLayout()
        self.btn_modo = {}
        for k, m in MODOS.items():
            b = QPushButton(m["label"], objectName="modo")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, kk=k: self.cambiar_modo(kk))
            self.btn_modo[k] = b
            barra.addWidget(b)
        root.addLayout(barra)

        self.panel = QFrame(objectName="panel")
        pl = QVBoxLayout(self.panel)
        pl.setContentsMargins(24, 20, 24, 20)
        self.stack = QStackedWidget()
        pl.addWidget(self.stack)
        root.addWidget(self.panel, 1)

        self.p_quiz, self.p_load, self.p_plan, self.p_hola, self.p_res = (QWidget(), QWidget(), QWidget(), QWidget(),
                                                                          QWidget())
        for w in (self.p_quiz, self.p_load, self.p_plan, self.p_hola, self.p_res):
            self.stack.addWidget(w)
        self.quiz_l = QVBoxLayout(self.p_quiz)
        self._init_load()
        self._init_hola()

        self.aplicar_tema(self.tkey, False)
        if self.datos.get("usuario"):
            self._estado("")
            self.entrar_modo()
            self._sincronizar_inicio()
        else:
            self.mostrar_bienvenida()

    def resizeEvent(self, e):
        self.scene.setGeometry(0, 0, self.width(), self.height())
        self.scene.lower()

    # ----------------------------------------------------------- datos
    def _cargar(self):
        try:
            return json.loads(DATA.read_text(encoding="utf8"))
        except Exception:
            return {}

    def _guardar(self, sincronizar=True, tocar=True):
        if tocar:  # «modificado» solo cambia con cambios reales (decide qué copia manda al sincronizar)
            self.datos["modificado"] = datetime.now().isoformat(timespec="seconds")
        DATA.write_text(json.dumps(self.datos, ensure_ascii=False, indent=1), encoding="utf8")
        if sincronizar and self.datos.get("usuario"):
            self.timer_sync.start()

    def _migrar(self):
        """Versión anterior: el plan de calistenia estaba en la raíz de datos.json."""
        d = self.datos
        if "plan" in d and "calistenia" not in d:
            d["calistenia"] = {"plan": d.pop("plan"), "log": d.pop("log", {})}
            r = d["calistenia"]["plan"]["resumen"]
            d["perfil"] = {k: r[k] for k in PERFIL_KEYS if k in r}

    @property
    def sec(self):
        return self.datos.setdefault(self.modo, {})

    def aplicar_tema(self, key, guardar=True):
        self.tkey = key
        t = THEMES[key]
        self.setStyleSheet(make_qss(t))
        self.scene.set_theme(t)
        for w in getattr(self, "charts", []):
            try:
                w.set_theme(t)
            except RuntimeError:
                pass
        try:
            if self.anim is not None:
                self.anim.set_theme(t)
        except RuntimeError:
            self.anim = None
        self.datos["tema"] = key
        if guardar:
            self._guardar()
        self._titulos()

    def _titulos(self):
        m = MODOS[self.modo]
        self.lbl_title.setText(m["title"])
        self.lbl_tag.setText(m["tagline"] or THEMES[self.tkey]["tagline"])
        for k, b in self.btn_modo.items():
            b.setChecked(k == self.modo)

    @staticmethod
    def _vaciar(layout):
        while layout.count():
            it = layout.takeAt(0)
            if it.widget():
                w = it.widget()
                w.hide()
                w.setParent(None)
                w.deleteLater()
            elif it.layout():
                Main._vaciar(it.layout())

    # ----------------------------------------------------------- modos
    def cambiar_modo(self, modo):
        if self.cargando and self.cargando.isActive():
            self.cargando.stop()
        self.modo = modo
        self.datos["modo"] = modo
        self._guardar()
        self._titulos()
        self.entrar_modo()

    def entrar_modo(self):
        for b in self.btn_modo.values():
            b.setVisible(True)
        self._titulos()
        if "plan" in self.sec:
            self.mostrar_plan()
        else:
            self.iniciar_quiz()

    # ----------------------------------------------------------- QUIZ
    def iniciar_quiz(self, completo=False):
        perfil = self.datos.get("perfil")
        usa = bool(perfil and not completo)

        def cubierta(k):  # ya respondida en otra modalidad (o pantalla informativa que no hace falta repetir)
            if k.startswith("info"):
                return True
            return ("altura" in perfil and "peso" in perfil) if k == "datos" else k in perfil
        claves = [k for k in ORDEN[self.modo] if not (usa and cubierta(k))]
        self.preguntas = [PREG[k] for k in claves]
        self.reutiliza = usa
        self.paso, self.resp = 0, {}
        self.mostrar_pregunta()

    def mostrar_pregunta(self):
        self.stack.setCurrentWidget(self.p_quiz)
        self._vaciar(self.quiz_l)
        p = self.preguntas[self.paso]
        total = len(self.preguntas)
        barra = QProgressBar()
        barra.setRange(0, total)
        barra.setValue(self.paso)
        barra.setFormat(f"{SECCION.get(p['k'], 'Quiz')} · {self.paso + 1} de {total}")
        self.quiz_l.addWidget(barra)
        if self.reutiliza and self.paso == 0:
            h = QLabel("✅ Ya tenemos tu perfil (objetivo, nivel y datos): solo faltan estas preguntas.",
                       objectName="hint")
            h.setWordWrap(True)
            self.quiz_l.addWidget(h)
        self.quiz_l.addSpacing(10)
        q = QLabel(p["t"], objectName="pregunta")
        q.setWordWrap(True)
        self.quiz_l.addWidget(q)
        self.quiz_l.addSpacing(8)

        if p.get("info"):
            t = QLabel(p["texto"], objectName="hint")
            t.setWordWrap(True)
            t.setStyleSheet("font-size:16px;")
            self.quiz_l.addWidget(t)
            self.quiz_l.addStretch()
            b = QPushButton("Continuar →")
            b.clicked.connect(lambda: self.responder(None))
            self.quiz_l.addWidget(b)
        elif p.get("form"):
            fila = QHBoxLayout()
            self.sp_alt = QSpinBox(); self.sp_alt.setRange(120, 220); self.sp_alt.setValue(175); self.sp_alt.setSuffix(" cm")
            self.sp_peso = QDoubleSpinBox(); self.sp_peso.setRange(35, 200); self.sp_peso.setValue(75); self.sp_peso.setSuffix(" kg")
            self.sp_obj = QDoubleSpinBox(); self.sp_obj.setRange(35, 200); self.sp_obj.setValue(72); self.sp_obj.setSuffix(" kg")
            for etq, w in (("Altura", self.sp_alt), ("Peso", self.sp_peso), ("Peso objetivo", self.sp_obj)):
                c = QVBoxLayout(); c.addWidget(QLabel(etq, objectName="hint")); c.addWidget(w); fila.addLayout(c)
            self.quiz_l.addLayout(fila)
            self.quiz_l.addStretch()
            b = QPushButton("Siguiente →" if self.paso + 1 < total else "Crear mi plan 🚀")
            b.clicked.connect(lambda: self.responder({"altura": self.sp_alt.value(), "peso": self.sp_peso.value(),
                                                       "peso_obj": self.sp_obj.value()}))
            self.quiz_l.addWidget(b)
        elif p.get("multi"):
            self._multi = []
            for etq, val in p["o"]:
                b = QPushButton(etq, objectName="opcion")
                b.setCheckable(True)
                b.setCursor(Qt.PointingHandCursor)
                self._multi.append((b, val))
                self.quiz_l.addWidget(b)
            self.quiz_l.addStretch()
            c = QPushButton("Continuar →")
            c.clicked.connect(lambda: self.responder([v for b, v in self._multi if b.isChecked()]))
            self.quiz_l.addWidget(c)
        else:
            for etq, val in p["o"]:
                b = QPushButton(etq, objectName="opcion")
                b.setCursor(Qt.PointingHandCursor)
                b.clicked.connect(lambda _=False, v=val: self.responder(v))
                self.quiz_l.addWidget(b)
            self.quiz_l.addStretch()
        if self.paso > 0:
            a = QPushButton("← Atrás", objectName="atras")
            a.setCursor(Qt.PointingHandCursor)
            a.clicked.connect(self.atras)
            self.quiz_l.addWidget(a, 0, Qt.AlignLeft)

    def responder(self, valor):
        if not self.preguntas[self.paso].get("info"):
            self.resp[self.preguntas[self.paso]["k"]] = valor
        if self.paso + 1 < len(self.preguntas):
            self.paso += 1
            self.mostrar_pregunta()
        else:
            self.iniciar_carga()

    def atras(self):
        self.paso -= 1
        self.mostrar_pregunta()

    # ----------------------------------------------------------- ANÁLISIS Y RESULTADO
    def _init_load(self):
        l = QVBoxLayout(self.p_load)
        self.load_lbl = QLabel("🔎 Analizando tus respuestas…", objectName="pregunta")
        self.load_lbl.setAlignment(Qt.AlignCenter)
        self.analisis = Analisis()
        self.charts = [self.analisis]
        l.addWidget(self.load_lbl)
        l.addWidget(self.analisis, 1)

    def iniciar_carga(self):
        self.stack.setCurrentWidget(self.p_load)
        pasos = {
            "calistenia": ["Perfil y objetivo", "Nivel de fuerza (flexiones, dominadas, sentadillas)",
                           "Estilo de vida y descanso", "Medidas y meta de peso", "Construyendo tu plan de 4 semanas"],
            "gym": ["Perfil y objetivo", "Nivel de fuerza (flexiones, dominadas, sentadillas)",
                    "Estilo de vida y descanso", "Medidas y meta de peso", "Construyendo tu plan de 12 semanas"],
            "nutricion": ["Perfil y objetivo", "Gasto de energía (metabolismo)", "Hábitos de comida y agua",
                          "Medidas y meta de peso", "Calculando calorías, macros y menús"],
        }[self.modo]
        self.analisis.set_theme(THEMES[self.tkey])
        self.analisis.set_pasos(pasos)
        self.cargando = QTimer(self, interval=45)
        self.cargando.timeout.connect(self._carga_paso)
        self.cargando.start()

    def _carga_paso(self):
        self.analisis.set_pct(self.analisis.pct + 1.2)
        if self.analisis.pct >= 100:
            self.cargando.stop()
            QTimer.singleShot(450, self._terminar_carga)

    def _terminar_carga(self):
        resp = dict(self.resp)
        resp.update(resp.pop("datos", {}))
        perfil = dict(self.datos.get("perfil", {}))
        perfil.update({k: resp[k] for k in PERFIL_KEYS if k in resp})
        perfil["edad"] = self.datos.get("usuario", {}).get("edad", perfil.get("edad", 30))
        self.datos["perfil"] = perfil
        r = {**perfil, **{k: v for k, v in resp.items() if k not in PERFIL_KEYS}}
        if self.modo == "gym":
            plan = generar_plan_gym(r)
        elif self.modo == "nutricion":
            plan = generar_plan_nutricion(r)
        else:
            plan = generar_plan(r)
        plan["creado"] = date.today().isoformat()
        self.datos[self.modo] = {"plan": plan, "log": {}}
        self._guardar()
        self.mostrar_resultado()

    def mostrar_resultado(self):
        """Pantalla final: gráficas de progreso previsto (como el «tu plan» de las apps de entrenamiento)."""
        if self.p_res.layout():
            self._vaciar(self.p_res.layout())
            QWidget().setLayout(self.p_res.layout())
        plan = self.sec["plan"]
        r = plan["resumen"]
        t = THEMES[self.tkey]
        l = QVBoxLayout(self.p_res)
        tit = QLabel("🎉 ¡Tu plan está listo!", objectName="pregunta")
        tit.setAlignment(Qt.AlignCenter)
        l.addWidget(tit)
        self.charts = []
        proy = proyeccion_peso(r)
        if proy:
            g = GraficaLinea()
            g.set_theme(t)
            nota = (f"Meta de {proy['meta']:g} kg hacia la semana {proy['semanas']} a un ritmo saludable. "
                    if proy["alcanza"] else f"A ritmo saludable en 52 semanas llegarías a {proy['puntos'][-1][1]:g} kg. ")
            g.set_datos({"titulo": "Tu peso previsto", "puntos": proy["puntos"], "unidad_y": "kg",
                         "nota": nota.replace(".", ",", 0) + "Estimación orientativa."})
            l.addWidget(g)
            self.charts.append(g)
        if plan.get("tipo") == "nutricion":
            m = plan["macros"]
            g = GraficaBarras()
            g.set_theme(t)
            g.set_datos({"titulo": "Reparto de tus calorías (kcal)", "valores": [m["p"] * 4, m["c"] * 4, m["g"] * 9],
                         "etiquetas": ["Proteína", "Hidratos", "Grasa"],
                         "nota": f"Objetivo diario: {plan['kcal']} kcal · agua {plan['agua']:g} L".replace(".", ",", 0)})
            l.addWidget(g)
            self.charts.append(g)
        else:
            vals = carga_semanal(plan)
            g = GraficaBarras()
            g.set_theme(t)
            g.set_datos({"titulo": "Series por semana (tu progresión)", "valores": vals,
                         "etiquetas": [str(i + 1) for i in range(len(vals))],
                         "resaltar": [i for i in range(len(vals)) if (i + 1) % 4 == 0],
                         "nota": "Las barras claras son semanas de descarga: bajas el volumen para recuperar."})
            l.addWidget(g)
            self.charts.append(g)
        b = QPushButton("Ver mi plan →")
        b.clicked.connect(self.mostrar_plan)
        l.addWidget(b)
        self.stack.setCurrentWidget(self.p_res)

    # ----------------------------------------------------------- PLAN
    def mostrar_plan(self):
        if self.p_plan.layout():
            self._vaciar(self.p_plan.layout())
            QWidget().setLayout(self.p_plan.layout())
        plan = self.sec["plan"]
        r = plan["resumen"]
        self.plan, self.r = plan, r
        self.es_gym = plan.get("tipo") == "gym"
        self.es_nutri = plan.get("tipo") == "nutricion"
        if self.es_nutri:
            return self.mostrar_plan_nutri()
        l = QVBoxLayout(self.p_plan)

        kpis = QHBoxLayout()
        imc = r["peso"] / (r["altura"] / 100) ** 2
        for v, txt in ((r["dias"], "días / semana"), (f"{r['duracion']} min", "por sesión"),
                       (plan["semanas"], "semanas"), (f"{imc:.1f}", "IMC")):
            f = QFrame(objectName="kpi")
            fl = QVBoxLayout(f)
            a = QLabel(str(v), objectName="kpiv"); a.setAlignment(Qt.AlignCenter)
            b = QLabel(txt, objectName="hint"); b.setAlignment(Qt.AlignCenter)
            fl.addWidget(a); fl.addWidget(b)
            kpis.addWidget(f)
        l.addLayout(kpis)

        tabs = QTabWidget()
        l.addWidget(tabs, 1)

        # Semana
        self.tb_semana = QTextBrowser()
        tabs.addTab(self.tb_semana, "📅 Semana")
        self.tb_semana.setHtml(self._html_semana())

        # Sesiones
        w = QWidget(); sl = QVBoxLayout(w)
        fila = QHBoxLayout()
        self.cmb_sem = QComboBox()
        for i in range(1, plan["semanas"] + 1):
            self.cmb_sem.addItem(titulo_semana(i) if self.es_gym else f"Semana {i}" + (" · descarga" if i == 4 else ""))
        self.cmb_dia = QComboBox(); self.cmb_dia.addItems([d for d in NOMBRES_DIAS if d in plan["calendario"]])
        fila.addWidget(self.cmb_sem, 3); fila.addWidget(self.cmb_dia, 2)
        sl.addLayout(fila)
        cuerpo = QHBoxLayout()
        self.lst_ej = QListWidget()
        self.lst_ej.setFixedWidth(260)
        self.lst_ej.setWordWrap(True)
        self.lst_ej.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lst_ej.currentItemChanged.connect(self.elegir_ejercicio)
        cuerpo.addWidget(self.lst_ej)
        der = QVBoxLayout()
        self.anim = AnimWidget()
        self.anim.set_theme(THEMES[self.tkey])
        self.tb_ses = QTextBrowser()
        vis = QHBoxLayout()
        self.foto = FotoWidget()
        vis.addWidget(self.anim, 1)
        vis.addWidget(self.foto, 1)
        der.addLayout(vis, 3)
        der.addWidget(self.tb_ses, 2)
        der.addWidget(self._crear_panel_reg())
        cuerpo.addLayout(der, 1)
        sl.addLayout(cuerpo, 1)
        self.cmb_sem.currentIndexChanged.connect(self.pintar_sesion)
        self.cmb_dia.currentIndexChanged.connect(self.pintar_sesion)
        tabs.addTab(w, "🏋️ Sesiones")
        self.pintar_sesion()

        # Progreso
        w = QWidget(); gl = QVBoxLayout(w)
        self.btn_hoy = QPushButton()
        self.btn_hoy.clicked.connect(self.toggle_hoy)
        self.pb = QProgressBar()
        self.lst = QListWidget()
        gl.addWidget(self.btn_hoy); gl.addWidget(self.pb); gl.addWidget(self.lst)
        tabs.addTab(w, "✅ Progreso")
        self.pintar_progreso()

        # Más
        w = QWidget(); ml = QVBoxLayout(w)
        b1 = QPushButton("⬇️ Guardar plan en Markdown"); b1.clicked.connect(self.exportar)
        b2 = QPushButton("🔁 Cambiar solo días y tiempo (mantengo mi perfil)"); b2.clicked.connect(lambda: self.rehacer(False))
        b3 = QPushButton("🔄 Rehacer el quiz completo"); b3.clicked.connect(lambda: self.rehacer(True))
        b4 = QPushButton("👤 Cambiar de usuario"); b4.clicked.connect(self.cambiar_usuario)
        b5 = QPushButton("🔗 Copiar código para vincular la web con mi Drive"); b5.clicked.connect(self.copiar_codigo)
        for b in (b1, b2, b3, b4, b5):
            ml.addWidget(b)
        ml.addStretch()
        tabs.addTab(w, "⚙️ Más")

        self.stack.setCurrentWidget(self.p_plan)

    # ---- resumen semanal
    def _html_semana(self):
        plan = self.plan
        h = ["<h3>🧬 Tu perfil</h3><ul>" + "".join(f"<li>{l}</li>" for l in resumen_perfil(self.r)) + "</ul>",
             "<h3>Tu semana tipo</h3>"]
        for dia in NOMBRES_DIAS:
            s = plan["calendario"].get(dia)
            if not s:
                h.append(f"<p style='color:#aaa'>{dia} — descanso 😴</p>")
            elif self.es_gym:
                partes = []
                for b in s["bloques"]:
                    ico = {"Musculación": "💪", "Abdominales": "🧱", "Cardio": "❤️"}[b["tipo"]]
                    extra = f" {b['modo']} {b['minutos']}'" if b["tipo"] == "Cardio" else f" ×{len(b['ejercicios'])}"
                    partes.append(f"{ico} {b['tipo']}{extra}")
                h.append(f"<p><b>{dia}</b> — {s['nombre']}<br><i>{' · '.join(partes)}</i></p>")
            else:
                h.append(f"<p><b>{dia}</b> — {s['nombre']} <i>({len(s['ejercicios'])} ejercicios)</i></p>")
        if self.es_gym:
            h.append("<h3>Tus 12 semanas</h3>")
            for i, (n, d) in enumerate(FASES):
                h.append(f"<p><b>{n}</b> (semanas {i * 4 + 1}-{i * 4 + 4})<br>{d}</p>")
            h.append("<p><i>En cada fase: semanas 1-3 cada vez más cerca del límite (menos repeticiones en reserva, RIR) "
                     "y la semana 4 de descarga con la mitad de series y la misma carga (RIR 3).</i></p>"
                     "<p><b>Doble progresión:</b> cuando hagas el máximo de repeticiones en todas las series con buena técnica, "
                     "sube el peso (1-2 kg en tren superior, 2-5 kg en pierna).</p>")
        else:
            h.append("<p><i>Semanas 1-3: sube reps o tiempo cada semana. Semana 4: descarga. Cuando llegues al "
                     "tope de reps en todas las series, pasa al siguiente ejercicio de la progresión.</i></p>")
        h.append("<h3>🩺 ¿Cuándo descargar antes?</h3><ul>" + "".join(f"<li>{x}</li>" for x in SENALES_DESCARGA) + "</ul>"
                 f"<p><i>{SENALES_TEXTO}</i></p>")
        return "".join(h)

    # ---- sesiones
    def _entradas(self, dia, sem):
        s = self.plan["calendario"][dia]
        r = self.r
        out = [("hdr", "🔥 CALENTAMIENTO · 5 min")]
        for e in self.plan["calentamiento"]:
            out.append(("ex", "•", e, "Calentamiento", None, False))
        if self.es_gym:
            for b in s["bloques"]:
                ico = {"Musculación": "💪", "Abdominales": "🧱", "Cardio": "❤️"}[b["tipo"]]
                tit = f"{ico} {b['tipo'].upper()} · {b['titulo']}"
                if b["tipo"] == "Cardio":
                    tit = f"{ico} CARDIO · {b['modo']}"
                out.append(("hdr", tit))
                for i, ej in enumerate(b["ejercicios"], 1):
                    real = ejercicio_en(ej, sem)
                    txt, desc = prescripcion_gym(r, b, ej, real, sem)
                    presc = txt + (f" · descanso {desc} s" if desc else "")
                    out.append(("ex", f"{i}." if b["tipo"] != "Cardio" else "•", real, b["tipo"], presc, True))
        else:
            fuerza = [e for e in s["ejercicios"] if not e["patron"].startswith("core")]
            core = [e for e in s["ejercicios"] if e["patron"].startswith("core")]
            for titulo, lista in (("💪 MUSCULACIÓN", fuerza), ("🧱 ABDOMINALES / CORE", core)):
                if lista:
                    out.append(("hdr", titulo))
                    for i, e in enumerate(lista, 1):
                        out.append(("ex", f"{i}.", e, "Ejercicio",
                                    f"{prescripcion(r, e, sem)} · descanso {r['descanso']} s", True))
            if s.get("finisher"):
                out.append(("hdr", "❤️ CARDIO · finisher (3 rondas 30 s / 15 s)"))
                for e in s["finisher"]:
                    out.append(("ex", "•", e, "Finisher", None, True))
        out.append(("hdr", "🧊 VUELTA A LA CALMA"))
        for e in self.plan["enfriamiento"]:
            out.append(("ex", "•", e, "Vuelta a la calma", None, False))
        return out

    def pintar_sesion(self):
        sem = self.cmb_sem.currentIndex() + 1
        self.lst_ej.blockSignals(True)
        self.lst_ej.clear()
        primero = None
        t = THEMES[self.tkey]
        for ent in self._entradas(self.cmb_dia.currentText(), sem):
            if ent[0] == "hdr":
                it = QListWidgetItem(ent[1])
                it.setFlags(Qt.NoItemFlags)
                f = it.font(); f.setBold(True); f.setPointSize(f.pointSize() - 1)
                it.setFont(f)
                it.setForeground(QColor(t["accent"]))
            else:
                _, ico, e, tipo, presc, principal = ent
                it = QListWidgetItem(f"{ico} {e['nombre']}")
                it.setData(Qt.UserRole, (e, tipo, presc))
                if principal and primero is None:
                    primero = it
            self.lst_ej.addItem(it)
        self.lst_ej.blockSignals(False)
        if primero is None:
            for i in range(self.lst_ej.count()):
                if self.lst_ej.item(i).data(Qt.UserRole):
                    primero = self.lst_ej.item(i)
                    break
        self.lst_ej.setCurrentItem(primero)
        self.elegir_ejercicio(primero)

    # ---- temporizador de descanso y registro de series (como en Hevy)
    def _crear_panel_reg(self):
        self.panel_reg = QFrame(objectName="kpi")
        self._ej_reg = None
        self._desc_left = 0
        pr = QVBoxLayout(self.panel_reg)
        f1 = QHBoxLayout()
        self.cmb_desc = QComboBox()
        for sg in (30, 45, 60, 90, 120, 150, 180):
            self.cmb_desc.addItem(f"{sg} s", sg)
        self.btn_desc = QPushButton("⏱ Descanso")
        self.btn_desc.clicked.connect(lambda: self._iniciar_timer(self.cmb_desc.currentData()))
        self.lbl_desc = QLabel("", objectName="hint")
        for w in (self.cmb_desc, self.btn_desc, self.lbl_desc):
            f1.addWidget(w)
        pr.addLayout(f1)
        pr.addWidget(QLabel("📒 Registro de series", objectName="hint"))
        f2 = QHBoxLayout()
        self.sp_kg = QDoubleSpinBox(); self.sp_kg.setRange(0, 500); self.sp_kg.setSingleStep(0.5); self.sp_kg.setSuffix(" kg")
        self.sp_rep = QSpinBox(); self.sp_rep.setRange(1, 300); self.sp_rep.setValue(10); self.sp_rep.setSuffix(" reps")
        self.cmb_tipo = QComboBox()
        for v, t in reg.TIPOS:
            self.cmb_tipo.addItem(t, v)
        self.btn_serie = QPushButton("➕ Serie")
        self.btn_serie.clicked.connect(self._add_serie)
        for w in (self.sp_kg, self.sp_rep, self.cmb_tipo, self.btn_serie):
            f2.addWidget(w)
        pr.addLayout(f2)
        self.lbl_hoy = QLabel("")
        self.lbl_hoy.setWordWrap(True)
        self.lbl_hist = QLabel("", objectName="hint")
        self.lbl_hist.setWordWrap(True)
        self.btn_quitar = QPushButton("↩ Quitar última serie")
        self.btn_quitar.clicked.connect(self._quitar_serie)
        self.ed_nota = QPlainTextEdit()
        self.ed_nota.setPlaceholderText("Notas de este ejercicio…")
        self.ed_nota.setMaximumHeight(58)
        self.timer_nota = QTimer(self, singleShot=True, interval=700)
        self.timer_nota.timeout.connect(self._guardar_nota)
        self.ed_nota.textChanged.connect(self.timer_nota.start)
        self.timer_desc = QTimer(self, interval=1000)
        self.timer_desc.timeout.connect(self._tick_desc)
        for w in (self.lbl_hoy, self.lbl_hist, self.btn_quitar, self.ed_nota):
            pr.addWidget(w)
        self.panel_reg.setVisible(False)
        return self.panel_reg

    def _hist_reg(self):
        return self.sec.setdefault("registro", {}).setdefault(self._ej_reg, {})

    def _pintar_reg(self, aviso=""):
        if not self._ej_reg:
            return
        h, hoy = self._hist_reg(), date.today().isoformat()
        hs, r = h.get(hoy, []), reg.resumen(self._hist_reg(), hoy)
        self.lbl_hoy.setText(("<b>Hoy:</b> " + " · ".join(esc(reg.fmt_serie(x)) for x in hs)) if hs
                             else "Aún no has registrado series hoy.")
        t = f"<b>{aviso}</b><br>" if aviso else ""
        if r["ultimo"]:
            t += f"Última vez ({r['ultimo']['fecha']}): " + " · ".join(esc(reg.fmt_serie(x)) for x in r["ultimo"]["sets"]) + "<br>"
        if r["mejor"] > 0:
            t += f"Mejor 1RM estimado: <b>{str(r['mejor']).replace('.', ',')} kg</b> ({r['fecha_mejor']})" + (" 🏆" if r["pr_hoy"] else "")
        self.lbl_hist.setText(t)
        self.btn_quitar.setEnabled(bool(hs))

    def _add_serie(self):
        if not self._ej_reg:
            return
        serie = {"peso": self.sp_kg.value(), "reps": self.sp_rep.value(), "tipo": self.cmb_tipo.currentData()}
        h, hoy = self._hist_reg(), date.today().isoformat()
        aviso = "🏆 ¡Nuevo récord de 1RM estimado!" if reg.es_pr(h, hoy, serie) else ""
        h.setdefault(hoy, []).append(serie)
        self._guardar()
        self._pintar_reg(aviso)
        self._iniciar_timer(self.cmb_desc.currentData())   # descanso automático tras cada serie

    def _quitar_serie(self):
        h, hoy = self._hist_reg(), date.today().isoformat()
        if h.get(hoy):
            h[hoy].pop()
            if not h[hoy]:
                del h[hoy]
            self._guardar()
            self._pintar_reg()

    def _guardar_nota(self):
        if self._ej_reg:
            self.sec.setdefault("notas", {})[self._ej_reg] = self.ed_nota.toPlainText()
            self._guardar()

    def _iniciar_timer(self, seg):
        self._desc_left = int(seg)
        self._pintar_desc()
        self.timer_desc.start()

    def _tick_desc(self):
        self._desc_left -= 1
        self._pintar_desc()
        if self._desc_left <= 0:
            self.timer_desc.stop()
            QApplication.beep()

    def _pintar_desc(self):
        try:
            n = self._desc_left
            self.lbl_desc.setText(f"⏳ {n // 60}:{n % 60:02d}" if n > 0 else "¡Siguiente serie! 💪")
        except RuntimeError:
            self.timer_desc.stop()

    def elegir_ejercicio(self, item, _=None):
        if item is None or not item.data(Qt.UserRole):
            return
        e, tipo, presc = item.data(Qt.UserRole)
        clave = anim_para(e["nombre"])
        self.anim.set_anim(clave)
        self.foto.set_foto(clave)
        h = [f"<h3>{e['nombre']}</h3>", f"<p><i>{tipo}</i></p>"]
        if presc:
            h.append(f"<p><b>{presc}</b></p>")
        if clave:
            h.append(f"<p><b>Cómo se hace:</b> {ANIMS[clave]['texto']}</p>")
        h.append(f"<p>💡 {e['nota']}</p>")
        self.tb_ses.setHtml("".join(h))
        self.timer_desc.stop()
        self.lbl_desc.setText("")
        mostrar = tipo in ("Musculación", "Abdominales", "Ejercicio") and e["tipo"] in ("reps", "seg")
        self.panel_reg.setVisible(mostrar)
        self._ej_reg = e["nombre"] if mostrar else None
        if mostrar:
            m = re.search(r"descanso (\d+) s", presc or "")
            seg = int(m.group(1)) if m else 60
            if self.cmb_desc.findData(seg) < 0:
                self.cmb_desc.addItem(f"{seg} s", seg)
            self.cmb_desc.setCurrentIndex(self.cmb_desc.findData(seg))
            self.sp_rep.setSuffix(" s" if e["tipo"] == "seg" else " reps")
            self.ed_nota.blockSignals(True)
            self.ed_nota.setPlainText(self.sec.get("notas", {}).get(e["nombre"], ""))
            self.ed_nota.blockSignals(False)
            self._pintar_reg()

    # ----------------------------------------------------------- usuario y Drive
    def _init_hola(self):
        l = QVBoxLayout(self.p_hola)
        l.addStretch()
        t = QLabel("¡Hola! 👋", objectName="pregunta")
        t.setAlignment(Qt.AlignCenter)
        l.addWidget(t)
        h = QLabel("Dime tu nombre y tu edad. Guardaré tu perfil y tus planes en tu carpeta de Drive «entrenamientorro».",
                   objectName="hint")
        h.setWordWrap(True)
        h.setAlignment(Qt.AlignCenter)
        l.addWidget(h)
        l.addSpacing(12)
        self.ed_nombre = QLineEdit()
        self.ed_nombre.setPlaceholderText("Tu nombre")
        self.ed_nombre.setMaxLength(40)
        self.ed_nombre.returnPressed.connect(self.entrar_usuario)
        self.sp_edad_u = QSpinBox()
        self.sp_edad_u.setRange(14, 90)
        self.sp_edad_u.setValue(30)
        self.sp_edad_u.setSuffix(" años")
        l.addWidget(self.ed_nombre)
        l.addWidget(self.sp_edad_u)
        l.addSpacing(8)
        self.btn_entrar = QPushButton("Entrar →")
        self.btn_entrar.clicked.connect(self.entrar_usuario)
        l.addWidget(self.btn_entrar)
        self.lbl_hola = QLabel("", objectName="hint")
        self.lbl_hola.setAlignment(Qt.AlignCenter)
        l.addWidget(self.lbl_hola)
        l.addStretch()

    def mostrar_bienvenida(self):
        for b in self.btn_modo.values():
            b.setVisible(False)
        u = self.datos.get("usuario", {})
        self.ed_nombre.setText(u.get("nombre", ""))
        self.sp_edad_u.setValue(int(u.get("edad", self.datos.get("perfil", {}).get("edad", 30))))
        self.lbl_hola.setText("")
        self.btn_entrar.setEnabled(True)
        self.stack.setCurrentWidget(self.p_hola)
        self.ed_nombre.setFocus()

    def entrar_usuario(self):
        nombre = self.ed_nombre.text().strip()
        if not nombre:
            self.lbl_hola.setText("Escribe tu nombre para continuar.")
            return
        self.datos["usuario"] = {"nombre": nombre, "edad": self.sp_edad_u.value()}
        if self.datos.get("perfil"):
            self.datos["perfil"]["edad"] = self.sp_edad_u.value()
        self.btn_entrar.setEnabled(False)
        self.lbl_hola.setText("☁️ Buscando tus datos en Drive…")
        threading.Thread(target=self._bajar, args=(nombre,), daemon=True).start()

    def _bajar(self, nombre):
        estado, texto = drive.descargar(nombre)
        self.bus.remoto.emit(estado, texto)

    @staticmethod
    def _fecha(d):
        return (d or {}).get("modificado", "")

    def _remoto_recibido(self, estado, texto):
        """Respuesta de Drive al entrar (o al arrancar): decide qué datos mandan."""
        arranque = self.stack.currentWidget() is not self.p_hola
        usuario = self.datos.get("usuario")
        if estado == "ok":
            try:
                remoto = json.loads(texto)
            except Exception:
                remoto = None
            local_vacio = not any("plan" in self.datos.get(m, {}) for m in MODOS)
            if remoto and (local_vacio or self._fecha(remoto) > self._fecha(self.datos)):
                tema = self.datos.get("tema")
                self.datos = remoto
                self.datos["usuario"] = usuario
                if tema:
                    self.datos["tema"] = tema
                self.modo = self.datos.get("modo") if self.datos.get("modo") in MODOS else "calistenia"
                self._guardar(sincronizar=False, tocar=False)
                self._estado("☁️ Datos cargados de Drive")
                self.entrar_modo()
                return
            self._guardar()
            self._estado("☁️ Drive al día")
        elif estado == "no_existe":
            self._guardar()
            self._estado("☁️ Creando tu archivo en Drive…")
        else:
            self._estado("⚠️ Sin conexión con Drive (guardo en este equipo)")
        if not arranque:
            self.entrar_modo()

    def _sincronizar_inicio(self):
        nombre = self.datos["usuario"]["nombre"]
        self._estado("☁️ Sincronizando…")
        threading.Thread(target=self._bajar, args=(nombre,), daemon=True).start()

    def _subir_ahora(self):
        if not self.datos.get("usuario"):
            return
        if self._subiendo:
            self._pendiente = True
            return
        self._subiendo = True
        nombre = self.datos["usuario"]["nombre"]
        texto = json.dumps(self.datos, ensure_ascii=False, indent=1)
        self._estado("☁️ Guardando en Drive…")

        def run():
            ok = drive.subir(nombre, texto)
            self.bus.estado.emit("☁️ Guardado en Drive" if ok else "⚠️ No se pudo guardar en Drive")
            self._subiendo = False
            if self._pendiente:
                self._pendiente = False
                QTimer.singleShot(0, self._subir_ahora)

        threading.Thread(target=run, daemon=True).start()

    def _estado(self, txt):
        u = self.datos.get("usuario")
        quien = f"👤 {u['nombre']} ({u['edad']})" if u else ""
        self.lbl_sync.setText(" · ".join(x for x in (quien, txt) if x))

    def copiar_codigo(self):
        try:
            codigo = drive.codigo_vinculacion()
        except Exception as e:
            QMessageBox.warning(self, "Código de vinculación", f"No se pudo crear el código:\n{e}")
            return
        QApplication.clipboard().setText(codigo)
        QMessageBox.information(
            self, "Código copiado",
            "Código copiado al portapapeles.\n\nAbre la web (https://nandorro.github.io/entrenamientorro/), "
            "pulsa «Sincronizar con mi Drive» (o Más → Vincular) y pégalo.\n\n"
            "⚠️ Da acceso a todo tu Drive: no lo compartas ni lo publiques. Se guarda solo en ese navegador.")

    def cambiar_usuario(self):
        if QMessageBox.question(self, "Cambiar de usuario",
                                "¿Entrar con otro nombre? Tus datos actuales quedan guardados en Drive.") != QMessageBox.Yes:
            return
        if self.timer_sync.isActive():
            self.timer_sync.stop()
            self._subir_ahora()
        tema = self.datos.get("tema")
        self.datos = {"tema": tema} if tema else {}
        self._estado("")
        self.mostrar_bienvenida()

    # ----------------------------------------------------------- NUTRICIÓN
    @staticmethod
    def _racion(x):
        ent, fr = int(x), round((x - int(x)) * 4) / 4
        return (str(ent) if ent else "") + {0: "", 0.25: "¼", 0.5: "½", 0.75: "¾"}[fr] or "0"

    def mostrar_plan_nutri(self):
        plan, r = self.plan, self.r
        l = QVBoxLayout(self.p_plan)
        m = plan["macros"]
        kpis = QHBoxLayout()
        for v, txt in ((f"{plan['kcal']}", "kcal / día"), (f"{m['p']} g", "proteína"), (f"{plan['agua']:g} L".replace(".", ","), "agua"),
                       (r["comidas"], "comidas")):
            f = QFrame(objectName="kpi")
            fl = QVBoxLayout(f)
            a = QLabel(str(v), objectName="kpiv"); a.setAlignment(Qt.AlignCenter)
            b = QLabel(txt, objectName="hint"); b.setAlignment(Qt.AlignCenter)
            fl.addWidget(a); fl.addWidget(b)
            kpis.addWidget(f)
        l.addLayout(kpis)
        tabs = QTabWidget()
        l.addWidget(tabs, 1)

        # Plan
        kc = plan["kcal"]
        pct = lambda g, k: round(g * k * 100 / kc)
        h = ["<h3>🎯 Tu objetivo diario</h3><ul>",
             f"<li><b>{kc} kcal</b> al día (mantenimiento ≈ {plan['mantenimiento']} kcal)</li>",
             f"<li>Proteína <b>{m['p']} g</b> ({pct(m['p'], 4)}%) · Hidratos <b>{m['c']} g</b> ({pct(m['c'], 4)}%) · "
             f"Grasa <b>{m['g']} g</b> ({pct(m['g'], 9)}%)</li>",
             f"<li>Agua: <b>{plan['agua']:g} L</b> (≈ {round(plan['agua'] * 4)} vasos de 250 ml)</li>".replace(".", ",", 0),
             ]
        if plan["delta"]:
            h.append(f"<li>{'Déficit' if plan['delta'] < 0 else 'Superávit'} de {abs(plan['delta'])} kcal/día: "
                     f"ritmo previsto ≈ {str(plan['ritmo_kg_sem']).replace('.', ',')} kg/semana</li>")
        h.append("</ul><h3>🧠 Consejos para ti</h3><ul>" + "".join(f"<li>{c}</li>" for c in plan["consejos"]) + "</ul>")
        h.append(f"<p><i>⚠️ {plan['aviso']}</i></p>")
        tb = QTextBrowser()
        tb.setHtml("".join(h))
        tabs.addTab(tb, "🍽️ Plan")

        # Menú
        h = [f"<p><i>Raciones ajustadas a las calorías de cada comida. Tu dieta: {r['dieta']}.</i></p>"]
        for c in plan["comidas"]:
            h.append(f"<h3>🕗 {c['hora']} · {c['nombre']} — {c['kcal']} kcal</h3><ul>")
            for o in c["opciones"]:
                h.append(f"<li>{o['nombre']} — <b>{self._racion(o['racion'])} ración</b> "
                         f"(≈ {o['kcal']} kcal · P {o['p']} · H {o['c']} · G {o['g']})</li>")
            h.append("</ul>")
        tb2 = QTextBrowser()
        tb2.setHtml("".join(h))
        tabs.addTab(tb2, "📋 Menú")

        # Hoy
        w = QWidget(); gl = QVBoxLayout(w)
        self.lbl_agua = QLabel("", objectName="pregunta")
        fila = QHBoxLayout()
        bm = QPushButton("− 1 vaso"); bm.clicked.connect(lambda: self._agua(-1))
        bp = QPushButton("+ 1 vaso 💧"); bp.clicked.connect(lambda: self._agua(1))
        fila.addWidget(bm); fila.addWidget(bp)
        self.pb_agua = QProgressBar()
        gl.addWidget(self.lbl_agua); gl.addLayout(fila); gl.addWidget(self.pb_agua)
        gl.addWidget(QLabel("Comidas de hoy", objectName="hint"))
        self.chk = []
        for i, c in enumerate(plan["comidas"]):
            cb = QCheckBox(f"{c['hora']} · {c['nombre']} ({c['kcal']} kcal)")
            cb.toggled.connect(lambda v, k=i: self._comida(k, v))
            gl.addWidget(cb)
            self.chk.append(cb)
        gl.addStretch()
        tabs.addTab(w, "💧 Hoy")
        self._pintar_hoy()

        # Más
        w = QWidget(); ml = QVBoxLayout(w)
        b1 = QPushButton("⬇️ Guardar plan en Markdown"); b1.clicked.connect(self.exportar)
        b2 = QPushButton("🔁 Rehacer solo las preguntas de nutrición"); b2.clicked.connect(lambda: self.rehacer(False))
        b3 = QPushButton("🔄 Rehacer el quiz completo"); b3.clicked.connect(lambda: self.rehacer(True))
        b4 = QPushButton("👤 Cambiar de usuario"); b4.clicked.connect(self.cambiar_usuario)
        b5 = QPushButton("🔗 Copiar código para vincular la web con mi Drive"); b5.clicked.connect(self.copiar_codigo)
        for b in (b1, b2, b3, b4, b5):
            ml.addWidget(b)
        ml.addStretch()
        tabs.addTab(w, "⚙️ Más")
        self.stack.setCurrentWidget(self.p_plan)

    def _hoy(self):
        log = self.sec.setdefault("log", {})
        d = log.setdefault(date.today().isoformat(), {})
        if not isinstance(d, dict):
            d = log[date.today().isoformat()] = {}
        d.setdefault("agua", 0)
        d.setdefault("comidas", [False] * len(self.plan["comidas"]))
        return d

    def _pintar_hoy(self):
        d = self._hoy()
        meta = round(self.plan["agua"] * 4)
        self.lbl_agua.setText(f"💧 {d['agua']} / {meta} vasos")
        self.pb_agua.setRange(0, meta)
        self.pb_agua.setValue(min(meta, d["agua"]))
        for cb, v in zip(self.chk, d["comidas"]):
            cb.blockSignals(True)
            cb.setChecked(bool(v))
            cb.blockSignals(False)

    def _agua(self, delta):
        d = self._hoy()
        d["agua"] = max(0, d["agua"] + delta)
        self._guardar()
        self._pintar_hoy()

    def _comida(self, i, v):
        self._hoy()["comidas"][i] = bool(v)
        self._guardar()

    # ---- progreso
    def pintar_progreso(self):
        log = self.sec.setdefault("log", {})
        hecho = date.today().isoformat() in log
        self.btn_hoy.setText("↩️ Quitar el entrenamiento de hoy" if hecho else "✅ Marcar entrenamiento de hoy como hecho")
        total = self.plan["semanas"] * self.r["dias"]
        self.pb.setRange(0, total)
        self.pb.setValue(min(len(log), total))
        self.pb.setFormat(f"{len(log)} de {total} sesiones")
        self.lst.clear()
        self.lst.addItems([f"💪 {d}" for d in sorted(log, reverse=True)])

    def toggle_hoy(self):
        log = self.sec.setdefault("log", {})
        hoy = date.today().isoformat()
        if hoy in log:
            log.pop(hoy)
        else:
            log[hoy] = True
        self._guardar()
        self.pintar_progreso()

    def exportar(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar plan", str(Path.home() / f"plan_{self.modo}.md"), "Markdown (*.md)")
        if not ruta:
            return
        md = [f"# Plan de {MODOS[self.modo]['label']} ({self.plan['creado']})"]
        if self.es_nutri:
            pl, m = self.plan, self.plan["macros"]
            md += [f"\n**{pl['kcal']} kcal/día** · P {m['p']} g · H {m['c']} g · G {m['g']} g · agua {pl['agua']} L"]
            for c in pl["comidas"]:
                md.append(f"\n## {c['hora']} {c['nombre']} ({c['kcal']} kcal)")
                md += [f"- {o['nombre']}: {self._racion(o['racion'])} ración (≈ {o['kcal']} kcal)" for o in c["opciones"]]
            md += ["\n## Consejos"] + [f"- {c}" for c in pl["consejos"]] + [f"\n_{pl['aviso']}_"]
            Path(ruta).write_text("\n".join(md), encoding="utf8")
            return
        semanas = range(1, self.plan["semanas"] + 1) if self.es_gym else [1]
        for sem in semanas:
            md.append(f"\n# {titulo_semana(sem) if self.es_gym else 'Semana 1'}")
            for dia in self.plan["calendario"]:
                md.append(f"\n## {dia}")
                for ent in self._entradas(dia, sem):
                    if ent[0] == "hdr":
                        md.append(f"\n**{ent[1]}**")
                    elif ent[4]:
                        md.append(f"- {ent[2]['nombre']}: {ent[4]}")
        Path(ruta).write_text("\n".join(md), encoding="utf8")

    def rehacer(self, completo):
        txt = "¿Borrar tu perfil y los planes y repetir el quiz completo?" if completo else \
              "¿Crear un plan nuevo cambiando solo los días y el tiempo?"
        if QMessageBox.question(self, "Rehacer", txt) != QMessageBox.Yes:
            return
        self.sec.pop("plan", None)
        if completo:
            self.datos.pop("perfil", None)
        self._guardar()
        self.iniciar_quiz(completo)
        if not completo and not self.datos.get("perfil"):
            self.iniciar_quiz(True)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    w = Main()
    w.show()
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        (AQUI / "error.log").write_text(traceback.format_exc(), encoding="utf8")
        raise
