"""Genera los iconos de la web/APK (docs/icon-*.png e icon.svg) con una mancuerna sobre degradado."""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QPen

AQUI = Path(__file__).resolve().parent
DOCS = AQUI / "docs"


def dibujar(n: int, redondeado: bool = True) -> QImage:
    img = QImage(n, n, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    g = QLinearGradient(0, 0, 0, n)
    g.setColorAt(0, QColor("#3a0d05"))
    g.setColorAt(1, QColor("#e0541f"))
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, n, n), n * (0.22 if redondeado else 0), n * (0.22 if redondeado else 0))
    p.fillPath(path, QBrush(g))
    s = n / 512
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#ffb02e"))
    # barra
    p.drawRoundedRect(QRectF(120 * s, 238 * s, 272 * s, 36 * s), 12 * s, 12 * s)
    # discos
    for x, w, h in ((84, 40, 190), (126, 34, 140), (352, 34, 140), (388, 40, 190)):
        p.setBrush(QColor("#fff0b3") if w == 34 else QColor("#ffb02e"))
        p.drawRoundedRect(QRectF(x * s, (256 - h / 2) * s, w * s, h * s), 12 * s, 12 * s)
    # brillo
    p.setPen(QPen(QColor(255, 255, 255, 70), 6 * s))
    p.drawLine(QPointF(150 * s, 246 * s), QPointF(360 * s, 246 * s))
    p.end()
    return img


def main():
    QGuiApplication(sys.argv)
    DOCS.mkdir(exist_ok=True)
    for n in (180, 192, 512):
        dibujar(n).save(str(DOCS / f"icon-{n}.png"))
    (DOCS / "icon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#3a0d05"/><stop offset="1" stop-color="#e0541f"/></linearGradient></defs>'
        '<rect width="512" height="512" rx="112" fill="url(#g)"/><g fill="#ffb02e">'
        '<rect x="120" y="238" width="272" height="36" rx="12"/><rect x="84" y="161" width="40" height="190" rx="12"/>'
        '<rect x="388" y="161" width="40" height="190" rx="12"/></g><g fill="#fff0b3">'
        '<rect x="126" y="186" width="34" height="140" rx="12"/><rect x="352" y="186" width="34" height="140" rx="12"/></g></svg>',
        encoding="utf8")
    print("iconos listos en", DOCS)


if __name__ == "__main__":
    main()
