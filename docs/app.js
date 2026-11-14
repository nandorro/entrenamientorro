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
      <div class="hint msg" id="msg"></div></div>`;
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
    const claves = perfil && !completo ? D.SOLO_MODO[modo] : D.ORDEN[modo];
    preguntas = claves.map((k) => D.PREG[k]);
    reutiliza = !!(perfil && !completo);
    paso = 0; resp = {};
    mostrarPregunta();
  }

  function mostrarPregunta() {
    const p = preguntas[paso], total = preguntas.length;
    let h = `<div class="barra"><i style="width:${paso / total * 100}%"></i><span>Pregunta ${paso + 1} de ${total}</span></div>`;
    if (reutiliza && paso === 0) h += `<p class="hint">✅ Ya tenemos tu perfil (objetivo, nivel y datos): solo faltan estas preguntas.</p>`;
    h += `<div class="pregunta">${esc(p.t)}</div>`;
    if (p.form) {
      h += `<div class="form"><label><span class="hint">Altura (cm)</span><input type="number" id="alt" min="120" max="220" value="175"></label>
        <label><span class="hint">Peso (kg)</span><input type="number" id="peso" min="35" max="200" step="0.5" value="75"></label></div>
        <button class="btn" id="sig">${paso + 1 < total ? "Siguiente →" : "Crear mi plan 🚀"}</button>`;
    } else if (p.multi) {
      h += p.o.map(([e, v], i) => `<button class="opcion" data-i="${i}">${esc(e)}</button>`).join("") + `<button class="btn" id="sig">Continuar →</button>`;
    } else {
      h += p.o.map(([e], i) => `<button class="opcion" data-i="${i}">${esc(e)}</button>`).join("");
    }
    if (paso > 0) h += `<br><button class="atras" id="atras">← Atrás</button>`;
    view.innerHTML = h;
    if (p.form) {
      $("#sig").onclick = () => responder({ altura: parseInt($("#alt").value, 10) || 175, peso: parseFloat($("#peso").value) || 75 });
    } else if (p.multi) {
      view.querySelectorAll(".opcion").forEach((b) => (b.onclick = () => b.classList.toggle("on")));
      $("#sig").onclick = () => responder([...view.querySelectorAll(".opcion.on")].map((b) => p.o[+b.dataset.i][1]));
    } else {
      view.querySelectorAll(".opcion").forEach((b) => (b.onclick = () => responder(p.o[+b.dataset.i][1])));
    }
    if (paso > 0) $("#atras").onclick = () => { paso--; mostrarPregunta(); };
  }

  function responder(v) {
    resp[preguntas[paso].k] = v;
    if (paso + 1 < preguntas.length) { paso++; mostrarPregunta(); } else iniciarCarga();
  }

  function iniciarCarga() {
    view.innerHTML = `<div class="centro" style="padding:60px 0"><div class="pregunta" id="lt">🔎 Analizando tus respuestas…</div>
      <div class="barra"><i id="lb" style="width:0"></i></div></div>`;
    const fases = [[25, "🧮 Calculando tu nivel…"], [55, "🔗 Eligiendo ejercicios…"], [85, "📅 Organizando tus semanas…"], [100, "🎉 ¡Plan listo!"]];
    const id = setInterval(() => {
      const [pct, txt] = fases.shift();
      $("#lb").style.width = pct + "%"; $("#lt").textContent = txt;
      if (!fases.length) { clearInterval(id); setTimeout(terminarCarga, 500); }
    }, 650);
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
    const p = modo === "gym" ? L.generarPlanGym(todo) : L.generarPlan(todo);
    p.creado = L.hoy();
    datos[modo] = { plan: p, log: {} };
    guardar();
    mostrarPlan();
  }

  // ------------------------------------------------------------ plan
  function mostrarPlan() {
    plan = sec().plan; r = plan.resumen; esGym = plan.tipo === "gym";
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
    let h = "<h3>Tu semana tipo</h3>";
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
      h += `<p><i>En cada fase: semanas 1-3 cada vez más cerca del límite (menos repeticiones en reserva, RIR) y la semana 4 de descarga con menos series y un 10% menos de peso.</i></p>
        <p><b>Doble progresión:</b> cuando hagas el máximo de repeticiones en todas las series con buena técnica, sube el peso (1-2 kg en tren superior, 2-5 kg en pierna).</p>`;
    } else {
      h += "<p><i>Semanas 1-3: sube reps o tiempo cada semana. Semana 4: descarga. Cuando llegues al tope de reps en todas las series, pasa al siguiente ejercicio de la progresión.</i></p>";
    }
    return h;
  }

  // ---- sesiones
  function htmlSesiones() {
    const semanas = [];
    for (let i = 1; i <= plan.semanas; i++) semanas.push(`<option value="${i}">${esGym ? L.tituloSemana(i) : "Semana " + i + (i === 4 ? " · descarga" : "")}</option>`);
    const dias = D.NOMBRES_DIAS.filter((d) => plan.calendario[d]).map((d) => `<option>${d}</option>`);
    return `<div class="fila"><select id="selSem" style="flex:3">${semanas.join("")}</select><select id="selDia" style="flex:2">${dias.join("")}</select></div>
      <div class="ses"><ul class="lista" id="lista"></ul>
      <div class="der"><canvas class="anim" id="cv"></canvas><div class="caja" id="det"></div></div></div>`;
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

  function elegir(i) {
    $("#lista").querySelectorAll("li.ex").forEach((li) => li.classList.toggle("on", +li.dataset.i === i));
    const [, , e, tipo, presc] = entradasAct[i];
    const clave = L.animPara(e.nombre);
    anim.setAnim(clave);
    let h = `<h3>${esc(e.nombre)}</h3><p><i>${esc(tipo)}</i></p>`;
    if (presc) h += `<p><b>${esc(presc)}</b></p>`;
    if (clave) h += `<p><b>Cómo se hace:</b> ${esc(D.ANIMS[clave].texto)}</p>`;
    h += `<p>💡 ${esc(e.nota)}</p>`;
    $("#det").innerHTML = h;
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
      <button class="btn" id="bPar">🔁 Cambiar solo días y tiempo (mantengo mi perfil)</button>
      <button class="btn" id="bTodo">🔄 Rehacer el quiz completo</button>
      <button class="btn" id="bUsu">👤 Cambiar de usuario</button>
      <p class="hint msg" id="msgMas"></p></div>`;
    $("#bMd").onclick = () => {
      const md = [`# Plan de ${D.MODOS[modo].label} (${plan.creado})`];
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
