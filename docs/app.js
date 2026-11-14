/* Entrenamientorro: Calistenia + GymBrocoli. Interfaz web/APK (mismo comportamiento que la app de PC). */
(function () {
  "use strict";
  const D = window.DATA, L = window.LOGIC, Sync = window.DriveSync;
  const $ = (s, r) => (r || document).querySelector(s);
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const KEY = "entrenamientorro.datos";
  const view = $("#view");

  if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
      r = Math.min(r, w / 2, h / 2);
      this.moveTo(x + r, y); this.arcTo(x + w, y, x + w, y + h, r); this.arcTo(x + w, y + h, x, y + h, r);
      this.arcTo(x, y + h, x, y, r); this.arcTo(x, y, x + w, y, r); this.closePath();
    };
  }

  // ------------------------------------------------------------ estado y datos
  function cargar() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
  let datos = cargar();
  let modo = D.MODOS[datos.modo] ? datos.modo : "calistenia";
  let tkey = D.THEMES[datos.tema] ? datos.tema : "fuego";
  let paso = 0, resp = {}, preguntas = [], reutiliza = false;
  let anim = null, timerSync = 0, subiendo = false, pendiente = false;
  let plan = null, r = null, esGym = false;

  const sec = () => (datos[modo] = datos[modo] || {});

  function guardar(sincronizar) {
    datos.modificado = L.ahora();
    try { localStorage.setItem(KEY, JSON.stringify(datos)); } catch (e) { /* sin almacenamiento */ }
    if (sincronizar !== false && datos.usuario && Sync.activo) {
      clearTimeout(timerSync);
      timerSync = setTimeout(subirAhora, 1800);
    }
  }

  function setEstado(txt) {
    const u = datos.usuario;
    const quien = u ? `👤 ${esc(u.nombre)} (${u.edad})` : "";
    $("#sync").innerHTML = [quien, esc(txt || "")].filter(Boolean).join(" · ");
  }

  async function subirAhora() {
    if (!datos.usuario) return;
    if (subiendo) { pendiente = true; return; }
    subiendo = true;
    setEstado("☁️ Guardando en Drive…");
    const ok = await Sync.subir(datos.usuario.nombre, JSON.stringify(datos, null, 1));
    subiendo = false;
    setEstado(ok ? "☁️ Guardado en Drive" : "⚠️ No se pudo guardar en Drive");
    if (pendiente) { pendiente = false; subirAhora(); }
  }

  // ------------------------------------------------------------ fondo animado (degradado + partículas + guirnalda)
  const bg = $("#bg"), bctx = bg.getContext("2d");
  let parts = [], tick = 0;
  function pintarFondo() {
    const t = D.THEMES[tkey], dpr = window.devicePixelRatio || 1;
    const w = innerWidth, h = innerHeight;
    if (bg.width !== Math.round(w * dpr) || bg.height !== Math.round(h * dpr)) { bg.width = Math.round(w * dpr); bg.height = Math.round(h * dpr); }
    bctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    bctx.clearRect(0, 0, w, h);
    tick++;
    while (parts.length < 60) parts.push([Math.random() * w, -Math.random() * h, 0.6 + Math.random() * 1.6, (Math.random() - 0.5) * 0.8, 1.5 + Math.random() * 2.5, Math.random() * 6.28]);
    const rg = (hex, a) => { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; };
    for (const p of parts) {
      p[1] += p[2]; p[0] += p[3] * 0.5 + Math.sin(tick / 30 + p[5]) * 0.3;
      if (p[1] > h) { p[0] = Math.random() * w; p[1] = -Math.random() * 30; }
      if (t.particles === "sparkle") {
        const a = 0.3 + 0.6 * Math.abs(Math.sin(tick / 14 + p[5]));
        const g = bctx.createRadialGradient(p[0], p[1], 0, p[0], p[1], p[4] * 3);
        g.addColorStop(0, rg(t.pcolor, a)); g.addColorStop(1, rg(t.pcolor, 0));
        bctx.fillStyle = g; bctx.beginPath(); bctx.arc(p[0], p[1], p[4] * 3, 0, 7); bctx.fill();
      } else {
        bctx.fillStyle = rg(t.pcolor, 0.75); bctx.beginPath(); bctx.arc(p[0], p[1], p[4], 0, 7); bctx.fill();
      }
    }
    bctx.strokeStyle = "rgba(16,16,16,.8)"; bctx.lineWidth = 2; bctx.beginPath();
    for (let x = 0; x <= w + 8; x += 8) { const y = 14 + 14 * Math.sin(x / w * Math.PI * 6); x ? bctx.lineTo(x, y) : bctx.moveTo(x, y); }
    bctx.stroke();
    t.bulbs.forEach((_, i) => {});
    for (let i = 0, x = 20; x < w; x += 46, i++) {
      const y = 14 + 14 * Math.sin(x / w * Math.PI * 6) + 10 + 8, c = t.bulbs[i % t.bulbs.length];
      const on = (Math.floor(tick / 12) + i) % 3 !== 0;
      const g = bctx.createRadialGradient(x, y, 0, x, y, 22);
      g.addColorStop(0, rg(c, on ? 0.6 : 0.12)); g.addColorStop(1, rg(c, 0));
      bctx.fillStyle = g; bctx.beginPath(); bctx.arc(x, y, 22, 0, 7); bctx.fill();
      bctx.fillStyle = rg(c, on ? 1 : 0.43); bctx.beginPath(); bctx.ellipse(x, y, 6, 9, 0, 0, 7); bctx.fill();
    }
    requestAnimationFrame(pintarFondo);
  }

  // ------------------------------------------------------------ tema y cabecera
  const sel = $("#tema");
  for (const [k, t] of Object.entries(D.THEMES)) sel.add(new Option(t.label, k));
  sel.value = tkey;
  sel.onchange = () => aplicarTema(sel.value, true);

  function aplicarTema(key, guardarYa) {
    tkey = key;
    const t = D.THEMES[key], s = document.documentElement.style;
    s.setProperty("--top", t.top); s.setProperty("--bottom", t.bottom); s.setProperty("--panel", t.panel);
    s.setProperty("--text", t.text); s.setProperty("--accent", t.accent); s.setProperty("--accent2", t.accent2);
    s.setProperty("--sel", t.select_text);
    document.querySelector('meta[name="theme-color"]').content = t.top;
    parts = [];
    if (anim) anim.setTheme(t);
    datos.tema = key;
    if (guardarYa) guardar();
    titulos();
  }

  function titulos() {
    const m = D.MODOS[modo];
    $("#title").textContent = m.title;
    $("#tagline").textContent = m.tagline || D.THEMES[tkey].tagline;
    $("#modos").querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.m === modo));
  }

  const nav = $("#modos");
  for (const [k, m] of Object.entries(D.MODOS)) {
    const b = document.createElement("button");
    b.textContent = m.label; b.dataset.m = k; b.onclick = () => cambiarModo(k);
    nav.appendChild(b);
  }

  function cambiarModo(m) {
    modo = m; datos.modo = m; guardar();
    titulos(); entrarModo();
  }
  function entrarModo() {
    nav.style.display = "";
    titulos();
    if (sec().plan) mostrarPlan(); else iniciarQuiz(false);
  }

  // ------------------------------------------------------------ vincular Drive con un código (web)
  function formVincular(id) {
    return `<details class="vinc"><summary class="hint">🔗 Sincronizar con mi Drive (código de vinculación)</summary>
      <p class="hint">En la app de PC: Más → «Copiar código de vinculación». Pégalo aquí una sola vez; se guarda solo en este navegador y puedes desvincularlo cuando quieras. No lo compartas: da acceso a tu Drive.</p>
      <textarea id="${id}t" rows="3" placeholder="Pega aquí el código" style="width:100%;border-radius:10px;padding:8px;background:rgba(0,0,0,.43);color:inherit;border:1px solid var(--accent)"></textarea>
      <button class="btn" id="${id}b" style="margin-top:6px">Vincular</button><div class="hint msg" id="${id}m"></div></details>`;
  }
  function initVincular(id, tras) {
    const b = $("#" + id + "b");
    if (!b) return;
    b.onclick = () => {
      if (Sync.vincular($("#" + id + "t").value)) tras();
      else $("#" + id + "m").textContent = "⚠️ Ese código no es válido. Cópialo otra vez desde la app de PC.";
    };
  }

  // ------------------------------------------------------------ bienvenida (nombre y edad)
  function mostrarBienvenida() {
    nav.style.display = "none";
    const u = datos.usuario || {};
    const drive = Sync.activo;
    view.innerHTML = `<div class="centro stack" style="max-width:420px;margin:30px auto">
      <div class="pregunta" style="text-align:center">¡Hola! 👋</div>
      <p class="hint">Dime tu nombre y tu edad. ${drive ? "Guardaré tu perfil y tus planes en tu carpeta de Drive «entrenamientorro»." : "Guardaré tu perfil y tus planes en este dispositivo (puedes exportarlos desde «Más»)."}</p>
      <input type="text" id="nombre" placeholder="Tu nombre" maxlength="40" autocomplete="given-name" value="${esc(u.nombre || "")}">
      <input type="number" id="edad" min="14" max="90" value="${u.edad || (datos.perfil && datos.perfil.edad) || 30}" aria-label="Edad">
      <button class="btn" id="entrar">Entrar →</button>
      ${drive ? `<p class="hint">☁️ Drive vinculado${Sync.origen === "codigo" ? " en este navegador" : ""}.</p>` : formVincular("v1")}
      <div class="hint msg" id="msg"></div></div>`;
    if (!drive) initVincular("v1", () => mostrarBienvenida());
    const entrar = async () => {
      const nombre = $("#nombre").value.trim();
      if (!nombre) { $("#msg").textContent = "Escribe tu nombre para continuar."; return; }
      const edad = Math.max(14, Math.min(90, parseInt($("#edad").value, 10) || 30));
      datos.usuario = { nombre, edad };
      if (datos.perfil) datos.perfil.edad = edad;
      if (!Sync.activo) { guardar(false); setEstado(""); entrarModo(); return; }
      $("#entrar").disabled = true;
      $("#msg").textContent = "☁️ Buscando tus datos en Drive…";
      const { estado, texto } = await Sync.descargar(nombre);
      remotoRecibido(estado, texto, false);
    };
    $("#entrar").onclick = entrar;
    $("#nombre").onkeydown = (e) => { if (e.key === "Enter") entrar(); };
  }

  function remotoRecibido(estado, texto, arranque) {
    const usuario = datos.usuario;
    if (estado === "ok") {
      let remoto = null;
      try { remoto = JSON.parse(texto); } catch (e) { /* ignorar */ }
      const localVacio = !Object.keys(D.MODOS).some((m) => datos[m] && datos[m].plan);
      if (remoto && (localVacio || (remoto.modificado || "") > (datos.modificado || ""))) {
        const tema = datos.tema;
        datos = remoto; datos.usuario = usuario; if (tema) datos.tema = tema;
        modo = D.MODOS[datos.modo] ? datos.modo : "calistenia";
        guardar(false);
        setEstado("☁️ Datos cargados de Drive");
        entrarModo();
        return;
      }
      guardar(); setEstado("☁️ Drive al día");
    } else if (estado === "no_existe") {
      guardar(); setEstado("☁️ Creando tu archivo en Drive…");
    } else {
      setEstado("⚠️ Sin conexión con Drive (guardo en este dispositivo)");
    }
    if (!arranque) entrarModo();
  }

  // ------------------------------------------------------------ quiz
  function iniciarQuiz(completo) {
    const perfil = datos.perfil;
    const usa = !!(perfil && !completo);
    const cubierta = (k) => k.startsWith("info") || (k === "datos" ? ("altura" in perfil && "peso" in perfil) : k in perfil);
    const claves = D.ORDEN[modo].filter((k) => !(usa && cubierta(k)));
    preguntas = claves.map((k) => D.PREG[k]);
    reutiliza = usa;
    paso = 0; resp = {};
    mostrarPregunta();
  }

  function mostrarPregunta() {
    const p = preguntas[paso], total = preguntas.length;
    let h = `<div class="barra"><i style="width:${paso / total * 100}%"></i><span>${esc(D.SECCION[p.k] || "Quiz")} · ${paso + 1} de ${total}</span></div>`;
    if (reutiliza && paso === 0) h += `<p class="hint">✅ Ya tenemos tu perfil (objetivo, nivel y datos): solo faltan estas preguntas.</p>`;
    h += `<div class="pregunta">${esc(p.t)}</div>`;
    if (p.info) {
      h += `<p class="hint" style="font-size:16px">${esc(p.texto)}</p><button class="btn" id="sig">Continuar →</button>`;
    } else if (p.form) {
      h += `<div class="form"><label><span class="hint">Altura (cm)</span><input type="number" id="alt" min="120" max="220" value="175"></label>
        <label><span class="hint">Peso (kg)</span><input type="number" id="peso" min="35" max="200" step="0.5" value="75"></label>
        <label><span class="hint">Peso objetivo (kg)</span><input type="number" id="pobj" min="35" max="200" step="0.5" value="72"></label></div>
        <button class="btn" id="sig">${paso + 1 < total ? "Siguiente →" : "Crear mi plan 🚀"}</button>`;
    } else if (p.multi) {
      h += p.o.map(([e, v], i) => `<button class="opcion" data-i="${i}">${esc(e)}</button>`).join("") + `<button class="btn" id="sig">Continuar →</button>`;
    } else {
      h += p.o.map(([e], i) => `<button class="opcion" data-i="${i}">${esc(e)}</button>`).join("");
    }
    if (paso > 0) h += `<br><button class="atras" id="atras">← Atrás</button>`;
    view.innerHTML = h;
    if (p.info) {
      $("#sig").onclick = () => responder(null);
    } else if (p.form) {
      $("#sig").onclick = () => responder({ altura: parseInt($("#alt").value, 10) || 175, peso: parseFloat($("#peso").value) || 75, peso_obj: parseFloat($("#pobj").value) || 72 });
    } else if (p.multi) {
      view.querySelectorAll(".opcion").forEach((b) => (b.onclick = () => b.classList.toggle("on")));
      $("#sig").onclick = () => responder([...view.querySelectorAll(".opcion.on")].map((b) => p.o[+b.dataset.i][1]));
    } else {
      view.querySelectorAll(".opcion").forEach((b) => (b.onclick = () => responder(p.o[+b.dataset.i][1])));
    }
    if (paso > 0) $("#atras").onclick = () => { paso--; mostrarPregunta(); };
  }

  function responder(v) {
    if (!preguntas[paso].info) resp[preguntas[paso].k] = v;
    if (paso + 1 < preguntas.length) { paso++; mostrarPregunta(); } else iniciarCarga();
  }

  const PASOS = {
    calistenia: ["Perfil y objetivo", "Nivel de fuerza (flexiones, dominadas, sentadillas)", "Estilo de vida y descanso", "Medidas y meta de peso", "Construyendo tu plan de 4 semanas"],
    gym: ["Perfil y objetivo", "Nivel de fuerza (flexiones, dominadas, sentadillas)", "Estilo de vida y descanso", "Medidas y meta de peso", "Construyendo tu plan de 12 semanas"],
    nutricion: ["Perfil y objetivo", "Gasto de energía (metabolismo)", "Hábitos de comida y agua", "Medidas y meta de peso", "Calculando calorías, macros y menús"],
  };
  function iniciarCarga() {
    nav.style.display = "none";
    view.innerHTML = `<div class="centro"><div class="pregunta" style="text-align:center">🔎 Analizando tus respuestas…</div><canvas class="analisis" id="an"></canvas></div>`;
    let pct = 0;
    const id = setInterval(() => {
      pct += 1.2;
      if (!$("#an")) { clearInterval(id); return; }
      Graficas.anillo($("#an"), Math.min(100, pct), PASOS[modo], D.THEMES[tkey]);
      if (pct >= 100) { clearInterval(id); setTimeout(terminarCarga, 450); }
    }, 45);
  }

  function terminarCarga() {
    const rr = Object.assign({}, resp);
    Object.assign(rr, rr.datos || {}); delete rr.datos;
    const perfil = Object.assign({}, datos.perfil || {});
    for (const k of D.PERFIL_KEYS) if (k in rr) perfil[k] = rr[k];
    perfil.edad = (datos.usuario && datos.usuario.edad) || perfil.edad || 30;
    datos.perfil = perfil;
    const todo = Object.assign({}, perfil);
    for (const [k, v] of Object.entries(rr)) if (!D.PERFIL_KEYS.includes(k)) todo[k] = v;
    const p = modo === "gym" ? L.generarPlanGym(todo) : modo === "nutricion" ? L.generarPlanNutricion(todo) : L.generarPlan(todo);
    p.creado = L.hoy();
    datos[modo] = { plan: p, log: {} };
    guardar();
    mostrarResultado();
  }

  /** Pantalla final con las gráficas de progreso previsto. */
  function mostrarResultado() {
    nav.style.display = "none";
    const pl = sec().plan, rr = pl.resumen, t = D.THEMES[tkey];
    const proy = L.proyeccionPeso(rr);
    const g = [];
    if (proy) {
      const nota = (proy.alcanza ? `Meta de ${String(proy.meta).replace(".", ",")} kg hacia la semana ${proy.semanas} a un ritmo saludable. `
        : `A ritmo saludable en 52 semanas llegarías a ${String(proy.puntos[proy.puntos.length - 1][1]).replace(".", ",")} kg. `) + "Estimación orientativa.";
      g.push(["Graficas.linea", { titulo: "Tu peso previsto", puntos: proy.puntos, unidad_y: "kg", nota }]);
    }
    if (pl.tipo === "nutricion") {
      const m = pl.macros;
      g.push(["Graficas.barras", { titulo: "Reparto de tus calorías (kcal)", valores: [m.p * 4, m.c * 4, m.g * 9], etiquetas: ["Proteína", "Hidratos", "Grasa"],
        nota: `Objetivo diario: ${pl.kcal} kcal · agua ${String(pl.agua).replace(".", ",")} L` }]);
    } else {
      const v = L.cargaSemanal(pl);
      g.push(["Graficas.barras", { titulo: "Series por semana (tu progresión)", valores: v, etiquetas: v.map((_, i) => String(i + 1)),
        resaltar: v.map((_, i) => i).filter((i) => (i + 1) % 4 === 0), nota: "Las barras claras son semanas de descarga: bajas el volumen para recuperar." }]);
    }
    view.innerHTML = `<div class="pregunta" style="text-align:center">🎉 ¡Tu plan está listo!</div>` +
      g.map((_, i) => `<canvas class="graf" id="g${i}"></canvas>`).join("") + `<button class="btn" id="ver" style="width:100%">Ver mi plan →</button>`;
    g.forEach(([fn, d], i) => Graficas[fn.split(".")[1]]($("#g" + i), d, t));
    $("#ver").onclick = mostrarPlan;
  }

  // ------------------------------------------------------------ plan
  function mostrarPlan() {
    nav.style.display = "";
    plan = sec().plan; r = plan.resumen; esGym = plan.tipo === "gym";
    if (plan.tipo === "nutricion") return mostrarPlanNutri();
    const imc = r.peso / Math.pow(r.altura / 100, 2);
    const kp = [[r.dias, "días / semana"], [r.duracion + " min", "por sesión"], [plan.semanas, "semanas"], [imc.toFixed(1), "IMC"]];
    view.innerHTML = `<div class="kpis">${kp.map(([v, t]) => `<div class="kpi"><b>${v}</b><span class="hint">${t}</span></div>`).join("")}</div>
      <div class="tabs" id="tabs"><button data-t="0">📅 Semana</button><button data-t="1">🏋️ Sesiones</button><button data-t="2">✅ Progreso</button><button data-t="3">⚙️ Más</button></div>
      <div id="t0" class="caja">${htmlSemana()}</div>
      <div id="t1" hidden>${htmlSesiones()}</div>
      <div id="t2" hidden></div>
      <div id="t3" hidden></div>`;
    const tabs = $("#tabs");
    tabs.querySelectorAll("button").forEach((b) => (b.onclick = () => verTab(+b.dataset.t)));
    initSesiones(); pintarProgreso(); initMas();
    verTab(modoTab);
  }
  let modoTab = 0;
  function verTab(i) {
    modoTab = i;
    for (let k = 0; k < 4; k++) $("#t" + k).hidden = k !== i;
    $("#tabs").querySelectorAll("button").forEach((b) => b.classList.toggle("on", +b.dataset.t === i));
  }

  function htmlSemana() {
    let h = "<h3>🧬 Tu perfil</h3><ul>" + L.resumenPerfil(r).map((l) => `<li>${esc(l)}</li>`).join("") + "</ul><h3>Tu semana tipo</h3>";
    for (const dia of D.NOMBRES_DIAS) {
      const s = plan.calendario[dia];
      if (!s) h += `<p style="opacity:.6">${dia} — descanso 😴</p>`;
      else if (esGym) {
        const partes = s.bloques.map((b) => {
          const ico = { "Musculación": "💪", "Abdominales": "🧱", "Cardio": "❤️" }[b.tipo];
          return `${ico} ${b.tipo}` + (b.tipo === "Cardio" ? ` ${b.modo} ${b.minutos}'` : ` ×${b.ejercicios.length}`);
        });
        h += `<p><b>${dia}</b> — ${esc(s.nombre)}<br><i>${partes.join(" · ")}</i></p>`;
      } else h += `<p><b>${dia}</b> — ${esc(s.nombre)} <i>(${s.ejercicios.length} ejercicios)</i></p>`;
    }
    if (esGym) {
      h += "<h3>Tus 12 semanas</h3>";
      D.FASES.forEach(([n, d], i) => { h += `<p><b>${n}</b> (semanas ${i * 4 + 1}-${i * 4 + 4})<br>${d}</p>`; });
      h += `<p><i>En cada fase: semanas 1-3 cada vez más cerca del límite (menos repeticiones en reserva, RIR) y la semana 4 de descarga con la mitad de series y la misma carga (RIR 3).</i></p>
        <p><b>Doble progresión:</b> cuando hagas el máximo de repeticiones en todas las series con buena técnica, sube el peso (1-2 kg en tren superior, 2-5 kg en pierna).</p>`;
    } else {
      h += "<p><i>Semanas 1-3: sube reps o tiempo cada semana. Semana 4: descarga. Cuando llegues al tope de reps en todas las series, pasa al siguiente ejercicio de la progresión.</i></p>";
    }
    h += "<h3>🩺 ¿Cuándo descargar antes?</h3><ul>" + D.SENALES.map((x) => `<li>${esc(x)}</li>`).join("") + `</ul><p><i>${esc(D.SENALES_TEXTO)}</i></p>`;
    return h;
  }

  // ---- nutrición
  const FR = { 0: "", 0.25: "¼", 0.5: "½", 0.75: "¾" };
  function racion(x) { const e = Math.floor(x), f = Math.round((x - e) * 4) / 4; return (e ? String(e) : "") + FR[f] || "0"; }

  function mostrarPlanNutri() {
    const m = plan.macros, kc = plan.kcal;
    const kp = [[kc, "kcal / día"], [m.p + " g", "proteína"], [String(plan.agua).replace(".", ",") + " L", "agua"], [r.comidas, "comidas"]];
    const pct = (g, k) => Math.round(g * k * 100 / kc);
    let h0 = `<h3>🎯 Tu objetivo diario</h3><ul><li><b>${kc} kcal</b> al día (mantenimiento ≈ ${plan.mantenimiento} kcal)</li>
      <li>Proteína <b>${m.p} g</b> (${pct(m.p, 4)}%) · Hidratos <b>${m.c} g</b> (${pct(m.c, 4)}%) · Grasa <b>${m.g} g</b> (${pct(m.g, 9)}%)</li>
      <li>Agua: <b>${String(plan.agua).replace(".", ",")} L</b> (≈ ${Math.round(plan.agua * 4)} vasos de 250 ml)</li>`;
    if (plan.delta) h0 += `<li>${plan.delta < 0 ? "Déficit" : "Superávit"} de ${Math.abs(plan.delta)} kcal/día: ritmo previsto ≈ ${String(plan.ritmo_kg_sem).replace(".", ",")} kg/semana</li>`;
    h0 += `</ul><h3>🧠 Consejos para ti</h3><ul>${plan.consejos.map((c) => `<li>${esc(c)}</li>`).join("")}</ul><p><i>⚠️ ${esc(plan.aviso)}</i></p>`;
    let h1 = `<p><i>Raciones ajustadas a las calorías de cada comida. Tu dieta: ${esc(r.dieta)}.</i></p>`;
    for (const c of plan.comidas) {
      h1 += `<h3>🕗 ${c.hora} · ${esc(c.nombre)} — ${c.kcal} kcal</h3><ul>` +
        c.opciones.map((o) => `<li>${esc(o.nombre)} — <b>${racion(o.racion)} ración</b> (≈ ${o.kcal} kcal · P ${o.p} · H ${o.c} · G ${o.g})</li>`).join("") + "</ul>";
    }
    view.innerHTML = `<div class="kpis">${kp.map(([v, t]) => `<div class="kpi"><b>${v}</b><span class="hint">${t}</span></div>`).join("")}</div>
      <div class="tabs" id="tabs"><button data-t="0">🍽️ Plan</button><button data-t="1">📋 Menú</button><button data-t="2">💧 Hoy</button><button data-t="3">⚙️ Más</button></div>
      <div id="t0" class="caja">${h0}</div><div id="t1" class="caja" hidden>${h1}</div><div id="t2" hidden></div><div id="t3" hidden></div>`;
    $("#tabs").querySelectorAll("button").forEach((b) => (b.onclick = () => verTab(+b.dataset.t)));
    pintarHoy(); initMas();
    verTab(modoTab);
  }

  function hoyNutri() {
    const log = (sec().log = sec().log || {});
    let d = log[L.hoy()];
    if (!d || typeof d !== "object") d = log[L.hoy()] = {};
    if (d.agua === undefined) d.agua = 0;
    if (!d.comidas) d.comidas = plan.comidas.map(() => false);
    return d;
  }
  function pintarHoy() {
    const d = hoyNutri(), meta = Math.round(plan.agua * 4);
    $("#t2").innerHTML = `<div class="caja"><div class="pregunta" style="margin-top:0">💧 ${d.agua} / ${meta} vasos</div>
      <div class="barra"><i style="width:${Math.min(100, d.agua / meta * 100)}%"></i><span>${d.agua} de ${meta} vasos</span></div>
      <div class="vasos"><button class="btn" id="vm">− 1 vaso</button><button class="btn" id="vp">+ 1 vaso 💧</button></div>
      <p class="hint">Comidas de hoy</p>${plan.comidas.map((c, i) => `<label class="chk"><input type="checkbox" data-i="${i}" ${d.comidas[i] ? "checked" : ""}> ${c.hora} · ${esc(c.nombre)} (${c.kcal} kcal)</label>`).join("")}</div>`;
    $("#vm").onclick = () => { d.agua = Math.max(0, d.agua - 1); guardar(); pintarHoy(); };
    $("#vp").onclick = () => { d.agua += 1; guardar(); pintarHoy(); };
    $("#t2").querySelectorAll("input[type=checkbox]").forEach((c) => (c.onchange = () => { d.comidas[+c.dataset.i] = c.checked; guardar(); }));
  }

  // ---- sesiones
  function htmlSesiones() {
    const semanas = [];
    for (let i = 1; i <= plan.semanas; i++) semanas.push(`<option value="${i}">${esGym ? L.tituloSemana(i) : "Semana " + i + (i === 4 ? " · descarga" : "")}</option>`);
    const dias = D.NOMBRES_DIAS.filter((d) => plan.calendario[d]).map((d) => `<option>${d}</option>`);
    return `<div class="fila"><select id="selSem" style="flex:3">${semanas.join("")}</select><select id="selDia" style="flex:2">${dias.join("")}</select></div>
      <div class="ses"><ul class="lista" id="lista"></ul>
      <div class="der"><div class="vis" id="vis"><canvas class="anim" id="cv"></canvas><div class="foto" id="foto" hidden><img id="f0" alt=""><img id="f1" alt=""><small>Fotos: Free Exercise DB · dominio público</small></div></div><div class="caja" id="det"></div></div></div>`;
  }

  let entradasAct = [];
  function entradas(dia, sem) {
    const s = plan.calendario[dia], out = [["hdr", "🔥 CALENTAMIENTO · 5 min"]];
    for (const e of plan.calentamiento) out.push(["ex", "•", e, "Calentamiento", null, false]);
    if (esGym) {
      for (const b of s.bloques) {
        const ico = { "Musculación": "💪", "Abdominales": "🧱", "Cardio": "❤️" }[b.tipo];
        out.push(["hdr", b.tipo === "Cardio" ? `${ico} CARDIO · ${b.modo}` : `${ico} ${b.tipo.toUpperCase()} · ${b.titulo}`]);
        b.ejercicios.forEach((ej, i) => {
          const real = L.ejercicioEn(ej, sem);
          const [txt, desc] = L.prescripcionGym(r, b, ej, real, sem);
          out.push(["ex", b.tipo !== "Cardio" ? `${i + 1}.` : "•", real, b.tipo, txt + (desc ? ` · descanso ${desc} s` : ""), true]);
        });
      }
    } else {
      const fuerza = s.ejercicios.filter((e) => !e.patron.startsWith("core"));
      const core = s.ejercicios.filter((e) => e.patron.startsWith("core"));
      for (const [t, lista] of [["💪 MUSCULACIÓN", fuerza], ["🧱 ABDOMINALES / CORE", core]]) {
        if (!lista.length) continue;
        out.push(["hdr", t]);
        lista.forEach((e, i) => out.push(["ex", `${i + 1}.`, e, "Ejercicio", `${L.prescripcion(r, e, sem)} · descanso ${r.descanso} s`, true]));
      }
      if (s.finisher) {
        out.push(["hdr", "❤️ CARDIO · finisher (3 rondas 30 s / 15 s)"]);
        for (const e of s.finisher) out.push(["ex", "•", e, "Finisher", null, true]);
      }
    }
    out.push(["hdr", "🧊 VUELTA A LA CALMA"]);
    for (const e of plan.enfriamiento) out.push(["ex", "•", e, "Vuelta a la calma", null, false]);
    return out;
  }

  function initSesiones() {
    if (anim) anim.destroy();
    anim = new window.AnimView($("#cv"));
    anim.setTheme(D.THEMES[tkey]);
    $("#selSem").onchange = $("#selDia").onchange = pintarSesion;
    pintarSesion();
  }

  function pintarSesion() {
    const sem = +$("#selSem").value, dia = $("#selDia").value;
    entradasAct = entradas(dia, sem);
    let primero = -1;
    $("#lista").innerHTML = entradasAct.map((e, i) => {
      if (e[0] === "hdr") return `<li class="hdr">${esc(e[1])}</li>`;
      if (primero < 0 && e[5]) primero = i;
      return `<li class="ex" data-i="${i}">${e[1]} ${esc(e[2].nombre)}</li>`;
    }).join("");
    $("#lista").querySelectorAll("li.ex").forEach((li) => (li.onclick = () => elegir(+li.dataset.i)));
    if (primero < 0) primero = entradasAct.findIndex((e) => e[0] === "ex");
    elegir(primero);
  }

  // ---- temporizador de descanso y registro de series (como en Hevy)
  let timerDesc = 0;
  function pararTimer() { clearInterval(timerDesc); timerDesc = 0; }
  function pitar() {
    try { const a = new (window.AudioContext || window.webkitAudioContext)(), o = a.createOscillator(); o.connect(a.destination); o.frequency.value = 880; o.start(); setTimeout(() => { o.stop(); a.close(); }, 350); } catch (e) { /* sin audio */ }
    if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
  }
  function iniciarTimer(seg) {
    pararTimer();
    let left = seg;
    const pinta = () => { const o = $("#tleft"); if (o) o.textContent = left > 0 ? `⏳ ${Math.floor(left / 60)}:${String(left % 60).padStart(2, "0")}` : "¡Siguiente serie! 💪"; };
    pinta();
    timerDesc = setInterval(() => {
      left--;
      if (!$("#tleft")) { pararTimer(); return; }
      pinta();
      if (left <= 0) { pararTimer(); pitar(); }
    }, 1000);
  }

  function htmlRegistro(e, tipo, presc) {
    if (!["Musculación", "Abdominales", "Ejercicio"].includes(tipo) || !["reps", "seg"].includes(e.tipo)) return "";
    const m = /descanso (\d+) s/.exec(presc || ""), def = m ? +m[1] : 60;
    const segs = [...new Set([30, 45, 60, 90, 120, 150, 180, def])].sort((a, b) => a - b);
    return `<div class="caja" id="reg" style="margin-top:10px">
      <div class="fila"><select id="tsel">${segs.map((s) => `<option value="${s}" ${s === def ? "selected" : ""}>${s} s</option>`).join("")}</select>
        <button class="btn" id="tgo">⏱ Descanso</button><span class="hint" id="tleft"></span></div>
      <h4 style="margin:8px 0">📒 Registro de series</h4>
      <div class="fila"><input type="number" id="rkg" inputmode="decimal" step="0.5" min="0" placeholder="kg (0 = peso corporal)">
        <input type="number" id="rrep" inputmode="numeric" min="1" placeholder="${e.tipo === "seg" ? "segundos" : "repeticiones"}">
        <select id="rtipo">${L.TIPOS_SERIE.map(([v, t]) => `<option value="${v}">${t}</option>`).join("")}</select></div>
      <button class="btn" id="radd" style="width:100%">➕ Añadir serie</button>
      <div id="rhoy" style="margin-top:8px"></div><div id="rhist" class="hint" style="margin-top:4px"></div>
      <textarea class="nota" id="rnota" rows="2" placeholder="Notas de este ejercicio…"></textarea></div>`;
  }

  function initRegistro(e, presc) {
    if (!$("#reg")) return;
    const nombre = e.nombre;
    const hist = () => ((sec().registro = sec().registro || {})[nombre] = (sec().registro[nombre] || {}));
    let aviso = "";
    const pinta = () => {
      const h = hist(), hoy = L.hoy(), hs = h[hoy] || [], r = L.resumenRegistro(h, hoy);
      $("#rhoy").innerHTML = hs.length ? "<b>Hoy:</b> " + hs.map((s, i) => `<span class="chip">${esc(L.fmtSerie(s))} <a href="#" data-i="${i}">✕</a></span>`).join("")
        : `<span class="hint">Aún no has registrado series hoy.</span>`;
      let t = aviso ? `<b>${aviso}</b><br>` : "";
      if (r.ultimo) t += `Última vez (${r.ultimo.fecha}): ` + r.ultimo.sets.map((s) => esc(L.fmtSerie(s))).join(" · ") + "<br>";
      if (r.mejor > 0) t += `Mejor 1RM estimado: <b>${String(r.mejor).replace(".", ",")} kg</b> (${r.fecha_mejor})` + (r.pr_hoy ? " 🏆" : "");
      $("#rhist").innerHTML = t;
      $("#rhoy").querySelectorAll("a").forEach((a) => (a.onclick = (ev) => { ev.preventDefault(); h[hoy].splice(+a.dataset.i, 1); if (!h[hoy].length) delete h[hoy]; aviso = ""; guardar(); pinta(); }));
    };
    $("#tgo").onclick = () => iniciarTimer(+$("#tsel").value);
    $("#radd").onclick = () => {
      const peso = Math.max(0, parseFloat($("#rkg").value) || 0), reps = parseInt($("#rrep").value, 10);
      if (!(reps > 0)) { $("#rrep").focus(); return; }
      const serie = { peso, reps, tipo: $("#rtipo").value }, h = hist(), hoy = L.hoy();
      aviso = L.esPR(h, hoy, serie) ? "🏆 ¡Nuevo récord de 1RM estimado!" : "";
      (h[hoy] = h[hoy] || []).push(serie);
      guardar(); pinta();
      iniciarTimer(+$("#tsel").value);   // descanso automático tras cada serie
    };
    const notas = (sec().notas = sec().notas || {});
    $("#rnota").value = notas[nombre] || "";
    let t = 0;
    $("#rnota").oninput = () => { clearTimeout(t); t = setTimeout(() => { sec().notas[nombre] = $("#rnota").value; guardar(); }, 700); };
    pinta();
  }

  function elegir(i) {
    pararTimer();
    $("#lista").querySelectorAll("li.ex").forEach((li) => li.classList.toggle("on", +li.dataset.i === i));
    const [, , e, tipo, presc] = entradasAct[i];
    const clave = L.animPara(e.nombre);
    anim.setAnim(clave);
    const fotos = clave && D.FOTOS[clave];
    $("#foto").hidden = !fotos;
    $("#vis").classList.toggle("solo", !fotos);
    if (fotos) { $("#f0").src = fotos[0]; $("#f1").src = fotos[1]; }
    let h = `<h3>${esc(e.nombre)}</h3><p><i>${esc(tipo)}</i></p>`;
    if (presc) h += `<p><b>${esc(presc)}</b></p>`;
    if (clave) h += `<p><b>Cómo se hace:</b> ${esc(D.ANIMS[clave].texto)}</p>`;
    h += `<p>💡 ${esc(e.nota)}</p>`;
    $("#det").innerHTML = h + htmlRegistro(e, tipo, presc);
    initRegistro(e, presc);
  }

  // ---- progreso
  function pintarProgreso() {
    const log = (sec().log = sec().log || {});
    const hecho = !!log[L.hoy()], total = plan.semanas * r.dias;
    $("#t2").innerHTML = `<div class="stack"><button class="btn" id="hoy">${hecho ? "↩️ Quitar el entrenamiento de hoy" : "✅ Marcar entrenamiento de hoy como hecho"}</button>
      <div class="barra"><i style="width:${Math.min(100, Object.keys(log).length / total * 100)}%"></i><span>${Object.keys(log).length} de ${total} sesiones</span></div>
      <ul class="lista" style="max-height:none">${Object.keys(log).sort().reverse().map((d) => `<li>💪 ${d}</li>`).join("")}</ul></div>`;
    $("#hoy").onclick = () => { if (log[L.hoy()]) delete log[L.hoy()]; else log[L.hoy()] = true; guardar(); pintarProgreso(); };
  }

  // ---- más
  function descargar(nombre, texto, tipo) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([texto], { type: tipo }));
    a.download = nombre; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }

  function initMas() {
    $("#t3").innerHTML = `<div class="stack">
      <button class="btn" id="bMd">⬇️ Guardar plan en Markdown</button>
      <button class="btn" id="bExp">💾 Exportar mis datos (.json)</button>
      <button class="btn" id="bImp">📂 Importar mis datos (.json)</button>
      <input type="file" id="fImp" accept=".json,application/json" hidden>
      <button class="btn" id="bPar">${modo === "nutricion" ? "🔁 Rehacer solo las preguntas de nutrición" : "🔁 Cambiar solo días y tiempo (mantengo mi perfil)"}</button>
      <button class="btn" id="bTodo">🔄 Rehacer el quiz completo</button>
      <button class="btn" id="bUsu">👤 Cambiar de usuario</button>
      ${Sync.origen === "apk" ? `<p class="hint">☁️ Drive activo en esta app.</p>`
        : Sync.origen === "codigo" ? `<p class="hint">☁️ Drive vinculado en este navegador.</p><button class="btn" id="bDesv">🔌 Desvincular Drive de este navegador</button>`
        : formVincular("v2")}
      <p class="hint msg" id="msgMas"></p></div>`;
    if (Sync.origen === null) {
      initVincular("v2", () => {
        setEstado("☁️ Sincronizando…");
        Sync.descargar(datos.usuario.nombre).then((x) => remotoRecibido(x.estado, x.texto, true));
        initMas();
      });
    }
    if ($("#bDesv")) $("#bDesv").onclick = () => { Sync.desvincular(); setEstado("Drive desvinculado"); initMas(); };
    $("#bMd").onclick = () => {
      const md = [`# Plan de ${D.MODOS[modo].label} (${plan.creado})`];
      if (plan.tipo === "nutricion") {
        const m = plan.macros;
        md.push(`\n**${plan.kcal} kcal/día** · P ${m.p} g · H ${m.c} g · G ${m.g} g · agua ${plan.agua} L`);
        for (const c of plan.comidas) {
          md.push(`\n## ${c.hora} ${c.nombre} (${c.kcal} kcal)`);
          for (const o of c.opciones) md.push(`- ${o.nombre}: ${racion(o.racion)} ración (≈ ${o.kcal} kcal)`);
        }
        md.push("\n## Consejos", ...plan.consejos.map((c) => "- " + c), `\n_${plan.aviso}_`);
        return descargar(`plan_${modo}.md`, md.join("\n"), "text/markdown");
      }
      const semanas = esGym ? [...Array(plan.semanas).keys()].map((x) => x + 1) : [1];
      for (const sem of semanas) {
        md.push(`\n# ${esGym ? L.tituloSemana(sem) : "Semana 1"}`);
        for (const dia of Object.keys(plan.calendario)) {
          md.push(`\n## ${dia}`);
          for (const e of entradas(dia, sem)) {
            if (e[0] === "hdr") md.push(`\n**${e[1]}**`); else if (e[4]) md.push(`- ${e[2].nombre}: ${e[4]}`);
          }
        }
      }
      descargar(`plan_${modo}.md`, md.join("\n"), "text/markdown");
    };
    $("#bExp").onclick = () => descargar(`entrenamientorro-${datos.usuario ? L.slug(datos.usuario.nombre) : "datos"}.json`, JSON.stringify(datos, null, 1), "application/json");
    $("#bImp").onclick = () => $("#fImp").click();
    $("#fImp").onchange = async (ev) => {
      const f = ev.target.files[0];
      if (!f) return;
      try {
        const nuevo = JSON.parse(await f.text());
        if (typeof nuevo !== "object" || nuevo === null) throw new Error("formato");
        const usuario = datos.usuario, tema = datos.tema;
        datos = nuevo; datos.usuario = usuario || nuevo.usuario; datos.tema = tema || nuevo.tema;
        modo = D.MODOS[datos.modo] ? datos.modo : "calistenia";
        guardar(); entrarModo();
      } catch (e) { $("#msgMas").textContent = "⚠️ Ese archivo no es válido."; }
    };
    $("#bPar").onclick = () => rehacer(false);
    $("#bTodo").onclick = () => rehacer(true);
    $("#bUsu").onclick = () => {
      if (!confirm("¿Entrar con otro nombre? " + (Sync.activo ? "Tus datos actuales quedan guardados en Drive." : "Exporta antes tus datos si quieres conservarlos."))) return;
      clearTimeout(timerSync);
      if (Sync.activo && datos.usuario) subirAhora();
      const tema = datos.tema;
      datos = tema ? { tema } : {};
      setEstado(""); mostrarBienvenida();
    };
  }

  function rehacer(completo) {
    if (!confirm(completo ? "¿Borrar tu perfil y los planes y repetir el quiz completo?" : "¿Crear un plan nuevo cambiando solo los días y el tiempo?")) return;
    delete sec().plan;
    if (completo) delete datos.perfil;
    guardar();
    iniciarQuiz(completo);
  }

  // ------------------------------------------------------------ arranque
  aplicarTema(tkey, false);
  pintarFondo();
  if (datos.usuario) {
    setEstado("");
    entrarModo();
    if (Sync.activo) {
      setEstado("☁️ Sincronizando…");
      Sync.descargar(datos.usuario.nombre).then((x) => remotoRecibido(x.estado, x.texto, true));
    }
  } else mostrarBienvenida();

  if ("serviceWorker" in navigator && location.protocol.startsWith("http") && !window.Capacitor) {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  }
})();
