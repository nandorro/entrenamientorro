/* Motor de animación de los muñecos de palitos (port de animaciones.py) sobre <canvas>. */
(function (root) {
  const D = root.DATA;
  const GROUND = 112, TORSO = 38, THIGH = 27, SHIN = 27, UARM = 21, FARM = 21;

  const lerp2 = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];

  function mezcla(f1, f2, t) {
    const out = {};
    for (const k of ["sh", "hip", "hand", "foot"]) out[k] = lerp2(f1[k], f2[k], t);
    const def = (f, k, base) => f[k] || [f[base][0] - 3, k === "hand2" ? f[base][1] - 2 : f[base][1]];
    out.hand2 = lerp2(def(f1, "hand2", "hand"), def(f2, "hand2", "hand"), t);
    out.foot2 = lerp2(def(f1, "foot2", "foot"), def(f2, "foot2", "foot"), t);
    out.ht = f1.ht + (f2.ht - f1.ht) * t;
    return out;
  }

  function ik(a, b, l1, l2, bend) {
    const dx = b[0] - a[0], dy = b[1] - a[1];
    const d = Math.max(Math.hypot(dx, dy), 1e-6);
    const dc = Math.min(d, l1 + l2 - 0.01);
    const c = Math.max(-1, Math.min(1, (l1 * l1 + dc * dc - l2 * l2) / (2 * l1 * dc)));
    const ang = Math.atan2(dy, dx) - bend * Math.acos(c);
    return [a[0] + l1 * Math.cos(ang), a[1] + l1 * Math.sin(ang)];
  }

  function normTorso(sh, hip) {
    const dx = hip[0] - sh[0], dy = hip[1] - sh[1];
    const d = Math.max(Math.hypot(dx, dy), 1e-6);
    return [sh[0] + dx / d * TORSO, sh[1] + dy / d * TORSO];
  }

  function bbox(anim) {
    const xs = [], ys = [];
    for (const f of anim.frames) {
      for (const k of ["sh", "hip", "hand", "foot", "hand2", "foot2"]) if (f[k]) { xs.push(f[k][0]); ys.push(f[k][1]); }
      xs.push(f.sh[0] - 20, f.sh[0] + 20); ys.push(f.sh[1] - 24, f.sh[1] + 24);
    }
    if (anim.ancla) { xs.push(anim.ancla[0]); ys.push(anim.ancla[1]); }
    for (const p of anim.props || []) {
      if (p[0] === "line") { xs.push(p[1], p[3]); ys.push(p[2], p[4]); }
      else if (p[0] === "circ") { xs.push(p[1] - p[3], p[1] + p[3]); ys.push(p[2] - p[3], p[2] + p[3]); }
      else { xs.push(p[1], p[1] + p[3]); ys.push(p[2], p[2] + p[4]); }
    }
    ys.push(GROUND + 2);
    return [Math.min(...xs) - 10, Math.min(...ys) - 8, Math.max(...xs) + 24, Math.max(...ys) + 6];
  }

  function poseEn(anim, t) {
    const fr = anim.frames, n = fr.length;
    const dur = anim.dur === undefined ? 1.1 : anim.dur;
    let hold = anim.hold === undefined ? 0.25 : anim.hold;
    let seq;
    if (anim.mode === "loop") {
      seq = [...Array(n).keys()].concat([0]);
      hold = 0.05;
    } else {
      seq = [...Array(n).keys()];
      for (let i = n - 2; i > 0; i--) seq.push(i);
      seq.push(0);
    }
    const seg = dur + hold, total = seg * (seq.length - 1);
    t = ((t % total) + total) % total;
    const i = Math.floor(t / seg);
    let u = t - i * seg;
    u = u < hold ? 0 : (u - hold) / dur;
    u = u * u * (3 - 2 * u);
    return mezcla(fr[seq[i]], fr[seq[i + 1]], u);
  }

  const rgba = (hex, a) => {
    const h = hex.replace("#", "");
    const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  };

  class AnimView {
    constructor(canvas) {
      this.cv = canvas;
      this.ctx = canvas.getContext("2d");
      this.anim = null;
      this.t0 = performance.now();
      this.text = "#ffffff";
      this.accent = "#ffb02e";
      this.raf = 0;
      this.loop = this.loop.bind(this);
      this.raf = requestAnimationFrame(this.loop);
    }
    destroy() { cancelAnimationFrame(this.raf); this.raf = 0; }
    setTheme(t) { this.text = t.text; this.accent = t.accent; }
    setAnim(clave) {
      this.anim = clave ? D.ANIMS[clave] : null;
      this.bb = this.anim ? bbox(this.anim) : null;
      this.t0 = performance.now();
    }
    loop() {
      if (!this.cv.isConnected) { this.raf = 0; return; }
      this.draw();
      this.raf = requestAnimationFrame(this.loop);
    }
    draw() {
      const cv = this.cv, ctx = this.ctx;
      const dpr = window.devicePixelRatio || 1;
      const w = cv.clientWidth, h = cv.clientHeight;
      if (!w || !h) return;
      if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) {
        cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "rgba(0,0,0,0.27)";
      ctx.strokeStyle = "rgba(255,255,255,0.16)";
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.roundRect(1.5, 1.5, w - 3, h - 3, 14); ctx.fill(); ctx.stroke();
      const a = this.anim;
      if (!a) {
        ctx.fillStyle = this.text; ctx.font = "14px system-ui,sans-serif"; ctx.textAlign = "center";
        ctx.fillText("Elige un ejercicio de la lista", w / 2, h / 2);
        return;
      }
      const [x0, y0, x1, y1] = this.bb;
      const s = Math.min((w - 6) / (x1 - x0), (h - 6) / (y1 - y0));
      ctx.save();
      ctx.translate(w / 2 - (x0 + x1) / 2 * s, h / 2 - (y0 + y1) / 2 * s);
      ctx.scale(s, s);
      ctx.lineCap = "round"; ctx.lineJoin = "round";
      const pose = poseEn(a, (performance.now() - this.t0) / 1000);
      const line = (p1, p2, wd, col) => {
        ctx.strokeStyle = col; ctx.lineWidth = wd;
        ctx.beginPath(); ctx.moveTo(p1[0], p1[1]); ctx.lineTo(p2[0], p2[1]); ctx.stroke();
      };
      const ac = rgba(this.accent, 0.86), gc = rgba(this.text, 0.43);
      line([x0, GROUND + 3], [x1, GROUND + 3], 3, gc);
      for (const pr of a.props || []) {
        if (pr[0] === "line") line([pr[1], pr[2]], [pr[3], pr[4]], 4, ac);
        else if (pr[0] === "circ") {
          ctx.strokeStyle = ac; ctx.lineWidth = 3;
          ctx.beginPath(); ctx.arc(pr[1], pr[2], pr[3], 0, 7); ctx.stroke();
        } else {
          ctx.fillStyle = ac; ctx.beginPath(); ctx.roundRect(pr[1], pr[2], pr[3], pr[4], 2); ctx.fill();
        }
      }
      const sh = pose.sh, hip = normTorso(sh, pose.hip);
      const ek = a.ek === undefined ? 1 : a.ek, kk = a.kk === undefined ? 1 : a.kk;
      const near = rgba(this.text, 1), far = rgba(this.text, 0.51);
      const toes = a.toes === undefined ? true : a.toes;
      const miembro = (raiz, dest, l1, l2, bend, col, pies) => {
        const j = ik(raiz, dest, l1, l2, bend);
        line(raiz, j, 7, col); line(j, dest, 7, col);
        if (pies) line(dest, [dest[0] + 11, Math.min(GROUND, dest[1] + 9)], 6, col);
      };
      miembro(hip, pose.foot2, THIGH, SHIN, a.kk2 === undefined ? kk : a.kk2, far, toes);
      miembro(sh, pose.hand2, UARM, FARM, a.ek2 === undefined ? ek : a.ek2, far, false);
      line(sh, hip, 9, near);
      miembro(hip, pose.foot, THIGH, SHIN, kk, near, toes);
      miembro(sh, pose.hand, UARM, FARM, ek, near, false);
      const d = Math.atan2(sh[1] - hip[1], sh[0] - hip[0]) + pose.ht * Math.PI / 180;
      line(sh, [sh[0] + Math.cos(d) * 7, sh[1] + Math.sin(d) * 7], 5, near);
      ctx.strokeStyle = near; ctx.lineWidth = 2; ctx.fillStyle = this.accent;
      ctx.beginPath(); ctx.arc(sh[0] + Math.cos(d) * 16, sh[1] + Math.sin(d) * 16, 9, 0, 7); ctx.fill(); ctx.stroke();
      this.carga(ctx, a, pose, sh, hip, line);
      ctx.restore();
    }
    carga(ctx, a, pose, sh, hip, line) {
      const c = a.carga;
      if (!c) return;
      const acc = this.accent;
      const disco = (pt, r) => {
        ctx.strokeStyle = acc; ctx.lineWidth = 2.5; ctx.fillStyle = "rgba(25,25,30,0.92)";
        ctx.beginPath(); ctx.arc(pt[0], pt[1], r, 0, 7); ctx.fill(); ctx.stroke();
        ctx.fillStyle = acc; ctx.beginPath(); ctx.arc(pt[0], pt[1], r * 0.28, 0, 7); ctx.fill();
      };
      const h = pose.hand, h2 = pose.hand2;
      if (c === "barra") disco(h, 12);
      else if (c === "db") { disco(h2, 6.5); disco(h, 6.5); }
      else if (c === "db1") disco(h, 8);
      else if (c === "espalda") disco([sh[0] - 7, sh[1] - 3], 12);
      else if (c === "cadera") disco(hip, 12);
      else if (c === "rueda") disco(h, 9);
      else if (c === "plat") { const f = pose.foot; line([f[0] + 8, f[1] + 14], [f[0] + 22, f[1] - 20], 6, acc); }
      else if (c === "cable") {
        line(h, a.ancla, 2, rgba(acc, 0.75));
        line([h[0] - 5, h[1]], [h[0] + 5, h[1]], 5, acc);
      }
    }
  }

  root.AnimView = AnimView;
})(window);
