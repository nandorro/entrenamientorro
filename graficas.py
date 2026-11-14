"""Widgets de la pantalla final «Analizando tus respuestas»: anillo de progreso con pasos y gráficas (línea y barras)."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class _Base(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = QColor("#ffffff")
        self.accent = QColor("#ffb02e")
        self.accent2 = QColor("#fff0b3")

    def set_theme(self, t):
        self.text, self.accent, self.accent2 = QColor(t["text"]), QColor(t["accent"]), QColor(t["accent2"])
        self.update()

    def _marco(self, p, r):
        p.setPen(QPen(QColor(255, 255, 255, 40), 1))
        p.setBrush(QColor(0, 0, 0, 70))
        p.drawRoundedRect(r, 14, 14)


class Analisis(_Base):
    """Anillo con porcentaje y lista de pasos que se van marcando."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pct = 0.0
        self.pasos = []
        self.setMinimumHeight(300)

    def set_pasos(self, pasos):
        self.pasos, self.pct = list(pasos), 0.0
        self.update()

    def set_pct(self, v):
        self.pct = max(0.0, min(100.0, v))
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        d = min(h - 150, w * 0.5, 190)
        d = max(d, 90)
        cx, top = w / 2, 12
        r = QRectF(cx - d / 2, top, d, d)
        p.setPen(QPen(QColor(255, 255, 255, 50), 12, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(r, 0, 360 * 16)
        p.setPen(QPen(self.accent, 12, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(r, 90 * 16, int(-self.pct / 100 * 360 * 16))
        f = QFont(self.font())
        f.setPointSize(int(d / 6))
        f.setBold(True)
        p.setFont(f)
        p.setPen(self.text)
        p.drawText(r, Qt.AlignCenter, f"{int(self.pct)}%")
        f.setPointSize(11)
        f.setBold(False)
        p.setFont(f)
        n = max(1, len(self.pasos))
        y = top + d + 22
        for i, txt in enumerate(self.pasos):
            hecho = self.pct >= (i + 1) / n * 100 - 0.01
            actual = not hecho and self.pct >= i / n * 100
            p.setPen(self.accent if hecho else (self.text if actual else QColor(255, 255, 255, 110)))
            p.drawText(QRectF(cx - 190, y + i * 24, 380, 22), Qt.AlignVCenter | Qt.AlignLeft,
                       ("✓  " if hecho else ("…  " if actual else "○  ")) + txt)
        p.end()


class GraficaLinea(_Base):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.datos = None
        self.setMinimumHeight(230)

    def set_datos(self, d):
        """d = {'titulo','puntos':[[x,y]...],'unidad_x','unidad_y','nota'}"""
        self.datos = d
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        self._marco(p, r)
        d = self.datos
        if not d:
            return
        f = QFont(self.font())
        f.setBold(True)
        p.setFont(f)
        p.setPen(self.accent)
        p.drawText(QRectF(r.left() + 14, r.top() + 8, r.width() - 28, 22), Qt.AlignLeft, d["titulo"])
        f.setBold(False)
        f.setPointSize(9)
        p.setFont(f)
        p.setPen(self.accent2)
        p.drawText(QRectF(r.left() + 14, r.bottom() - 26, r.width() - 28, 20), Qt.AlignLeft, d.get("nota", ""))
        pts = d["puntos"]
        gx0, gx1 = r.left() + 56, r.right() - 28
        gy0, gy1 = r.top() + 48, r.bottom() - 52
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        ymin, ymax = min(ys), max(ys)
        pad = max(0.5, (ymax - ymin) * 0.15)
        ymin, ymax = ymin - pad, ymax + pad
        xmax = max(xs) or 1

        def X(x):
            return gx0 + (gx1 - gx0) * x / xmax

        def Y(y):
            return gy1 - (gy1 - gy0) * (y - ymin) / (ymax - ymin)

        p.setPen(QPen(QColor(255, 255, 255, 40), 1, Qt.DashLine))
        for i in range(4):
            yy = gy0 + (gy1 - gy0) * i / 3
            p.drawLine(QPointF(gx0, yy), QPointF(gx1, yy))
            val = ymax - (ymax - ymin) * i / 3
            p.setPen(self.text)
            p.drawText(QRectF(r.left() + 6, yy - 9, 46, 18), Qt.AlignRight | Qt.AlignVCenter, f"{val:.0f}")
            p.setPen(QPen(QColor(255, 255, 255, 40), 1, Qt.DashLine))
        path = QPainterPath(QPointF(X(xs[0]), Y(ys[0])))
        for x, y in pts[1:]:
            path.lineTo(QPointF(X(x), Y(y)))
        area = QPainterPath(path)
        area.lineTo(QPointF(X(xs[-1]), gy1))
        area.lineTo(QPointF(X(xs[0]), gy1))
        g = QLinearGradient(0, gy0, 0, gy1)
        c1 = QColor(self.accent)
        c1.setAlpha(110)
        c2 = QColor(self.accent)
        c2.setAlpha(0)
        g.setColorAt(0, c1)
        g.setColorAt(1, c2)
        p.setPen(Qt.NoPen)
        p.setBrush(g)
        p.drawPath(area)
        p.setPen(QPen(self.accent, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        p.setBrush(self.accent2)
        p.setPen(QPen(QColor(20, 20, 20), 2))
        for i, (x, y) in enumerate(pts):
            p.drawEllipse(QPointF(X(x), Y(y)), 5, 5)
        p.setPen(self.text)
        for idx in (0, len(pts) - 1):
            x, y = pts[idx]
            txt = f"{y:g} {d.get('unidad_y', '')}".replace(".", ",")
            cx = min(r.right() - 54, max(gx0 + 34, X(x)))
            p.drawText(QRectF(cx - 50, Y(y) - 26, 100, 18), Qt.AlignCenter, txt)
        p.drawText(QRectF(gx0 - 10, gy1 + 4, 60, 16), Qt.AlignLeft, "Hoy")
        p.drawText(QRectF(gx1 - 90, gy1 + 4, 100, 16), Qt.AlignRight, f"semana {int(xmax)}")
        p.end()


class GraficaBarras(_Base):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.datos = None
        self.setMinimumHeight(230)

    def set_datos(self, d):
        """d = {'titulo','valores':[...],'etiquetas':[...],'resaltar':[idx...],'nota'}"""
        self.datos = d
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        self._marco(p, r)
        d = self.datos
        if not d:
            return
        f = QFont(self.font())
        f.setBold(True)
        p.setFont(f)
        p.setPen(self.accent)
        p.drawText(QRectF(r.left() + 14, r.top() + 8, r.width() - 28, 22), Qt.AlignLeft, d["titulo"])
        f.setBold(False)
        f.setPointSize(9)
        p.setFont(f)
        p.setPen(self.accent2)
        p.drawText(QRectF(r.left() + 14, r.bottom() - 26, r.width() - 28, 20), Qt.AlignLeft, d.get("nota", ""))
        vals, etq = d["valores"], d["etiquetas"]
        n = len(vals)
        gx0, gx1 = r.left() + 20, r.right() - 20
        gy0, gy1 = r.top() + 56, r.bottom() - 56
        vmax = max(vals) or 1
        ancho = (gx1 - gx0) / n
        for i, v in enumerate(vals):
            h = (gy1 - gy0) * v / vmax
            x = gx0 + i * ancho + ancho * 0.18
            rect = QRectF(x, gy1 - h, ancho * 0.64, h)
            col = QColor(self.accent2 if i in d.get("resaltar", []) else self.accent)
            g = QLinearGradient(0, rect.top(), 0, rect.bottom())
            c2 = QColor(col)
            c2.setAlpha(120)
            g.setColorAt(0, col)
            g.setColorAt(1, c2)
            p.setPen(Qt.NoPen)
            p.setBrush(g)
            p.drawRoundedRect(rect, 5, 5)
            p.setPen(self.text)
            p.drawText(QRectF(x - 6, rect.top() - 18, ancho * 0.64 + 12, 16), Qt.AlignCenter, f"{v:g}")
            p.drawText(QRectF(x - 10, gy1 + 4, ancho * 0.64 + 20, 16), Qt.AlignCenter, str(etq[i]))
        p.end()
