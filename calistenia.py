"""
Calistenia Plan — app de escritorio (PySide6) con quiz y plan de entrenamiento.
Interfaz amable al estilo de Navidad IPTV: fondo degradado animado, guirnalda de luces,
partículas, paneles redondeados y varios temas.

Ejecutar:  iniciar.bat   (o  python calistenia.py)
"""
import json
import math
import random
import sys
import threading
import traceback
from datetime import date, datetime
from pathlib import Path

from PySide6.QtCore import QObject, QPointF, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPen, QRadialGradient
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFileDialog, QFrame, QHBoxLayout, QLineEdit,
                               QLabel, QListWidget, QListWidgetItem, QMessageBox, QProgressBar, QPushButton, QScrollArea,
                               QSpinBox, QStackedWidget, QTabWidget, QTextBrowser, QVBoxLayout, QWidget)

import drive
from animaciones import ANIMS, AnimWidget, anim_para
from gym import (FASES, ejercicio_en, generar_plan_gym, prescripcion_gym, titulo_semana)
from plan import NOMBRES_DIAS, generar_plan, prescripcion

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
    {"k": "flexiones", "t": "¿Cuántas flexiones seguidas puedes hacer?", "o": [
        ("0 – 5", "0-5"), ("6 – 15", "6-15"), ("16 – 30", "16-30"), ("Más de 30", "31+")]},
    {"k": "dominadas", "t": "¿Y cuántas dominadas?\n(si no puedes o no tienes barra, elige 0)", "o": [
        ("0", "0"), ("1 – 4", "1-4"), ("5 – 10", "5-10"), ("Más de 10", "11+")]},
    {"k": "equipo", "t": "¿Con qué material cuentas para calistenia?", "o": [
        ("🏠 Nada, solo mi cuerpo", "nada"), ("🪝 Barra de dominadas", "barra"),
        ("🤸 Barra + paralelas o anillas", "completo")]},
    {"k": "dias", "t": "¿Cuántos días por semana quieres entrenar calistenia?", "o": [
        (f"{n} días", n) for n in (2, 3, 4, 5, 6)]},
    {"k": "duracion", "t": "¿Cuánto tiempo tienes por sesión de calistenia?", "o": [
        (f"⏱ {n} min", n) for n in (20, 30, 45, 60)]},
    {"k": "limitaciones", "t": "¿Tienes alguna molestia o limitación?\n(puedes elegir varias o ninguna)",
     "multi": True, "o": [("Muñecas", "muñecas"), ("Hombros", "hombros"), ("Rodillas", "rodillas")]},
    {"k": "datos", "t": "Tu altura y tu peso", "form": True},
    {"k": "gym_dias", "t": "¿Cuántos días por semana irás al gimnasio?", "o": [
        (f"{n} días", n) for n in (2, 3, 4, 5, 6)]},
    {"k": "gym_duracion", "t": "¿Cuánto tiempo tienes en el gimnasio por sesión?", "o": [
        (f"⏱ {n} min", n) for n in (30, 45, 60, 75, 90)]},
]}
ORDEN = {
    "calistenia": ["objetivo", "experiencia", "flexiones", "dominadas", "equipo", "dias", "duracion",
                   "limitaciones", "datos"],
    "gym": ["objetivo", "experiencia", "flexiones", "dominadas", "limitaciones", "datos", "gym_dias", "gym_duracion"],
}
SOLO_MODO = {"calistenia": ["equipo", "dias", "duracion"], "gym": ["gym_dias", "gym_duracion"]}
MODOS = {
    "calistenia": dict(label="💪 Calistenia", title="💪 Calistenia Plan 💪", tagline=None),
    "gym": dict(label="🥦 GymBrocoli", title="🥦 GymBrocoli 🥦",
                tagline="Hierro, brócoli y progresión semana a semana."),
}
PERFIL_KEYS = ["objetivo", "experiencia", "flexiones", "dominadas", "limitaciones", "edad", "altura", "peso"]


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

        self.p_quiz, self.p_load, self.p_plan, self.p_hola = QWidget(), QWidget(), QWidget(), QWidget()
        for w in (self.p_quiz, self.p_load, self.p_plan, self.p_hola):
            self.stack.addWidget(w)
        self.quiz_l = QVBoxLayout(self.p_quiz)
        self._init_load()
        self._init_hola()

        self.aplicar_tema(self.tkey)
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

    def _guardar(self, sincronizar=True):
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

    def aplicar_tema(self, key):
        self.tkey = key
        t = THEMES[key]
        self.setStyleSheet(make_qss(t))
        self.scene.set_theme(t)
        try:
            if self.anim is not None:
                self.anim.set_theme(t)
        except RuntimeError:
            self.anim = None
        self.datos["tema"] = key
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
        if perfil and not completo:
            claves = SOLO_MODO[self.modo]
        else:
            claves = ORDEN[self.modo]
        self.preguntas = [PREG[k] for k in claves]
        self.reutiliza = bool(perfil and not completo)
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
        barra.setFormat(f"Pregunta {self.paso + 1} de {total}")
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

        if p.get("form"):
            fila = QHBoxLayout()
            self.sp_alt = QSpinBox(); self.sp_alt.setRange(120, 220); self.sp_alt.setValue(175); self.sp_alt.setSuffix(" cm")
            self.sp_peso = QDoubleSpinBox(); self.sp_peso.setRange(35, 200); self.sp_peso.setValue(75); self.sp_peso.setSuffix(" kg")
            for etq, w in (("Altura", self.sp_alt), ("Peso", self.sp_peso)):
                c = QVBoxLayout(); c.addWidget(QLabel(etq, objectName="hint")); c.addWidget(w); fila.addLayout(c)
            self.quiz_l.addLayout(fila)
            self.quiz_l.addStretch()
            b = QPushButton("Siguiente →" if self.paso + 1 < total else "Crear mi plan 🚀")
            b.clicked.connect(lambda: self.responder({"altura": self.sp_alt.value(), "peso": self.sp_peso.value()}))
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
        self.resp[self.preguntas[self.paso]["k"]] = valor
        if self.paso + 1 < len(self.preguntas):
            self.paso += 1
            self.mostrar_pregunta()
        else:
            self.iniciar_carga()

    def atras(self):
        self.paso -= 1
        self.mostrar_pregunta()

    # ----------------------------------------------------------- CARGA
    def _init_load(self):
        l = QVBoxLayout(self.p_load)
        l.addStretch()
        self.load_lbl = QLabel("", objectName="pregunta")
        self.load_lbl.setAlignment(Qt.AlignCenter)
        self.load_bar = QProgressBar()
        l.addWidget(self.load_lbl)
        l.addSpacing(10)
        l.addWidget(self.load_bar)
        l.addStretch()

    def iniciar_carga(self):
        self.stack.setCurrentWidget(self.p_load)
        self.load_bar.setValue(0)
        self.fases = [(25, "🧮 Calculando tu nivel…"), (55, "🔗 Eligiendo ejercicios…"),
                      (85, "📅 Organizando tus semanas…"), (100, "🎉 ¡Plan listo!")]
        self.load_lbl.setText("🔎 Analizando tus respuestas…")
        self.cargando = QTimer(self, interval=650)
        self.cargando.timeout.connect(self._carga_paso)
        self.cargando.start()

    def _carga_paso(self):
        pct, txt = self.fases.pop(0)
        self.load_bar.setValue(pct)
        self.load_lbl.setText(txt)
        if not self.fases:
            self.cargando.stop()
            QTimer.singleShot(500, self._terminar_carga)

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
        else:
            plan = generar_plan(r)
        plan["creado"] = date.today().isoformat()
        self.datos[self.modo] = {"plan": plan, "log": {}}
        self._guardar()
        self.mostrar_plan()

    # ----------------------------------------------------------- PLAN
    def mostrar_plan(self):
        if self.p_plan.layout():
            self._vaciar(self.p_plan.layout())
            QWidget().setLayout(self.p_plan.layout())
        plan = self.sec["plan"]
        r = plan["resumen"]
        self.plan, self.r = plan, r
        self.es_gym = plan.get("tipo") == "gym"
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
        der.addWidget(self.anim, 3)
        der.addWidget(self.tb_ses, 2)
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
        for b in (b1, b2, b3, b4):
            ml.addWidget(b)
        ml.addStretch()
        tabs.addTab(w, "⚙️ Más")

        self.stack.setCurrentWidget(self.p_plan)

    # ---- resumen semanal
    def _html_semana(self):
        plan = self.plan
        h = ["<h3>Tu semana tipo</h3>"]
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
                     "y la semana 4 de descarga con menos series y un 10% menos de peso.</i></p>"
                     "<p><b>Doble progresión:</b> cuando hagas el máximo de repeticiones en todas las series con buena técnica, "
                     "sube el peso (1-2 kg en tren superior, 2-5 kg en pierna).</p>")
        else:
            h.append("<p><i>Semanas 1-3: sube reps o tiempo cada semana. Semana 4: descarga. Cuando llegues al "
                     "tope de reps en todas las series, pasa al siguiente ejercicio de la progresión.</i></p>")
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

    def elegir_ejercicio(self, item, _=None):
        if item is None or not item.data(Qt.UserRole):
            return
        e, tipo, presc = item.data(Qt.UserRole)
        clave = anim_para(e["nombre"])
        self.anim.set_anim(clave)
        h = [f"<h3>{e['nombre']}</h3>", f"<p><i>{tipo}</i></p>"]
        if presc:
            h.append(f"<p><b>{presc}</b></p>")
        if clave:
            h.append(f"<p><b>Cómo se hace:</b> {ANIMS[clave]['texto']}</p>")
        h.append(f"<p>💡 {e['nota']}</p>")
        self.tb_ses.setHtml("".join(h))

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
                self._guardar(sincronizar=False)
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
