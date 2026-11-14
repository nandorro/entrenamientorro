/* Gráficas de la pantalla final «Analizando tus respuestas»: anillo con pasos, línea (peso previsto) y barras. */
(function (root) {
  const rgba = (hex, a) => {
    const n = parseInt(hex.replace("#", ""), 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  };

  function preparar(cv) {
    const dpr = window.devicePixelRatio || 1;
    const w = cv.clientWidth, h = cv.clientHeight;
    if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
    const ctx = cv.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    return { ctx, w, h };
  }

  function marco(ctx, w, h) {
    ctx.fillStyle = "rgba(0,0,0,0.27)"; ctx.strokeStyle = "rgba(255,255,255,0.16)"; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.roundRect(1.5, 1.5, w - 3, h - 3, 14); ctx.fill(); ctx.stroke();
  }

  const G = {};

  /** Anillo de porcentaje y lista de pasos que se van marcando. */
  G.anillo = function (cv, pct, pasos, t) {
    const { ctx, w, h } = preparar(cv);
    const d = Math.max(90, Math.min(h - 150, w * 0.5, 190)), cx = w / 2, cy = 12 + d / 2;
    ctx.lineCap = "round"; ctx.lineWidth = 12;
    ctx.strokeStyle = "rgba(255,255,255,0.2)";
    ctx.beginPath(); ctx.arc(cx, cy, d / 2, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = t.accent;
    ctx.beginPath(); ctx.arc(cx, cy, d / 2, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * pct / 100); ctx.stroke();
    ctx.fillStyle = t.text; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.font = `bold ${Math.round(d / 4)}px system-ui,sans-serif`;
    ctx.fillText(Math.floor(pct) + "%", cx, cy);
    ctx.font = "14px system-ui,sans-serif"; ctx.textAlign = "left";
    const n = pasos.length, y0 = 12 + d + 28;
    const x0 = Math.max(10, cx - 190);
    pasos.forEach((txt, i) => {
      const hecho = pct >= (i + 1) / n * 100 - 0.01, actual = !hecho && pct >= i / n * 100;
      ctx.fillStyle = hecho ? t.accent : actual ? t.text : "rgba(255,255,255,0.45)";
      ctx.fillText((hecho ? "✓  " : actual ? "…  " : "○  ") + txt, x0, y0 + i * 24);
    });
  };

  /** Línea con área: {titulo, puntos:[[x,y]..], unidad_y, nota} */
  G.linea = function (cv, d, t) {
    const { ctx, w, h } = preparar(cv);
    marco(ctx, w, h);
    ctx.textBaseline = "alphabetic"; ctx.textAlign = "left";
    ctx.font = "bold 14px system-ui,sans-serif"; ctx.fillStyle = t.accent; ctx.fillText(d.titulo, 14, 24);
    ctx.font = "12px system-ui,sans-serif"; ctx.fillStyle = t.accent2; ctx.fillText(d.nota || "", 14, h - 12);
    const pts = d.puntos, gx0 = 52, gx1 = w - 26, gy0 = 48, gy1 = h - 50;
    const ys = pts.map((p) => p[1]);
    let ymin = Math.min(...ys), ymax = Math.max(...ys);
    const pad = Math.max(0.5, (ymax - ymin) * 0.15); ymin -= pad; ymax += pad;
    const xmax = Math.max(...pts.map((p) => p[0])) || 1;
    const X = (x) => gx0 + (gx1 - gx0) * x / xmax, Y = (y) => gy1 - (gy1 - gy0) * (y - ymin) / (ymax - ymin);
    ctx.strokeStyle = "rgba(255,255,255,0.16)"; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
    ctx.fillStyle = t.text; ctx.textAlign = "right";
    for (let i = 0; i < 4; i++) {
      const yy = gy0 + (gy1 - gy0) * i / 3;
      ctx.beginPath(); ctx.moveTo(gx0, yy); ctx.lineTo(gx1, yy); ctx.stroke();
      ctx.fillText(Math.round(ymax - (ymax - ymin) * i / 3), gx0 - 8, yy + 4);
    }
    ctx.setLineDash([]);
    const g = ctx.createLinearGradient(0, gy0, 0, gy1);
    g.addColorStop(0, rgba(t.accent, 0.45)); g.addColorStop(1, rgba(t.accent, 0));
    ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y))));
    ctx.lineTo(X(pts[pts.length - 1][0]), gy1); ctx.lineTo(X(pts[0][0]), gy1); ctx.closePath();
    ctx.fillStyle = g; ctx.fill();
    ctx.strokeStyle = t.accent; ctx.lineWidth = 4; ctx.lineJoin = "round";
    ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y)))); ctx.stroke();
    ctx.fillStyle = t.accent2; ctx.strokeStyle = "rgba(20,20,20,1)"; ctx.lineWidth = 2;
    pts.forEach(([x, y]) => { ctx.beginPath(); ctx.arc(X(x), Y(y), 5, 0, 7); ctx.fill(); ctx.stroke(); });
    ctx.fillStyle = t.text; ctx.textAlign = "center"; ctx.font = "bold 12px system-ui,sans-serif";
    for (const i of [0, pts.length - 1]) {
      const [x, y] = pts[i];
      ctx.fillText(String(y).replace(".", ",") + " " + (d.unidad_y || ""), Math.min(w - 40, Math.max(gx0 + 34, X(x))), Y(y) - 12);
    }
    ctx.font = "12px system-ui,sans-serif"; ctx.textAlign = "left"; ctx.fillText("Hoy", gx0 - 6, gy1 + 18);
    ctx.textAlign = "right"; ctx.fillText("semana " + xmax, gx1 + 8, gy1 + 18);
  };

  /** Barras: {titulo, valores, etiquetas, resaltar:[i], nota} */
  G.barras = function (cv, d, t) {
    const { ctx, w, h } = preparar(cv);
    marco(ctx, w, h);
    ctx.textBaseline = "alphabetic"; ctx.textAlign = "left";
    ctx.font = "bold 14px system-ui,sans-serif"; ctx.fillStyle = t.accent; ctx.fillText(d.titulo, 14, 24);
    ctx.font = "12px system-ui,sans-serif"; ctx.fillStyle = t.accent2; ctx.fillText(d.nota || "", 14, h - 12);
    const vals = d.valores, n = vals.length, gx0 = 20, gx1 = w - 20, gy0 = 54, gy1 = h - 50;
    const vmax = Math.max(...vals) || 1, ancho = (gx1 - gx0) / n;
    vals.forEach((v, i) => {
      const alto = (gy1 - gy0) * v / vmax, x = gx0 + i * ancho + ancho * 0.18, bw = ancho * 0.64;
      const col = (d.resaltar || []).includes(i) ? t.accent2 : t.accent;
      const g = ctx.createLinearGradient(0, gy1 - alto, 0, gy1);
      g.addColorStop(0, col); g.addColorStop(1, rgba(col, 0.45));
      ctx.fillStyle = g; ctx.beginPath(); ctx.roundRect(x, gy1 - alto, bw, alto, 5); ctx.fill();
      ctx.fillStyle = t.text; ctx.textAlign = "center"; ctx.font = "12px system-ui,sans-serif";
      ctx.fillText(String(v), x + bw / 2, gy1 - alto - 6);
      ctx.fillText(d.etiquetas[i], x + bw / 2, gy1 + 16);
    });
  };

  root.Graficas = G;
})(window);
