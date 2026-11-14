/* Lógica de planes: port de plan.py y gym.py. Usa window.DATA (generado por export_datos.py). */
(function (root) {
  const D = root.DATA;
  const L = {};

  L.norm = (s) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  const REGLAS_TODAS = () => D.REGLAS_GYM.concat(D.REGLAS);
  L.animPara = function (nombre) {
    const n = L.norm(nombre);
    for (const [k, a] of REGLAS_TODAS()) if (n.includes(k)) return a;
    return null;
  };
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const sum = (a) => a.reduce((x, y) => x + y, 0);

  // ------------------------------------------------------------ calistenia (plan.py)
  function ejCalis(patron, nivel) {
    const c = D.PATRONES[patron];
    return c[clamp(nivel, 0, c.length - 1)].concat([patron]);
  }

  L.generarPlan = function (resp, semanas = 4) {
    const obj = D.OBJETIVOS[resp.objetivo];
    const dias = resp.dias, minutos = resp.duracion;
    const barra = resp.equipo !== "nada", paralelas = resp.equipo === "completo";
    const exp = { nunca: 0, poco: 0, medio: 1, avanzado: 2 }[resp.experiencia];
    const nEmp = D.NIVEL_EMPUJE[resp.flexiones];
    const nTra = barra ? D.NIVEL_TRACCION[resp.dominadas] : Math.min(2, exp + (resp.dominadas !== "0" ? 1 : 0));
    const nPier = { nunca: 0, poco: 1, medio: 2, avanzado: 3 }[resp.experiencia];
    const nCore = { nunca: 0, poco: 0, medio: 2, avanzado: 4 }[resp.experiencia];
    const niveles = {
      empuje: nEmp, empuje_vertical: Math.max(0, nEmp - 2), fondos: Math.max(0, nEmp - 1),
      traccion: nTra, traccion_sin_barra: nTra, piernas: nPier, gluteo_isquio: Math.max(0, nPier - 1),
      gemelos: Math.min(1, Math.floor(nPier / 2)), core: nCore, core_colgado: Math.max(0, nCore - 2),
      core_rotacion: Math.max(0, Math.floor(nCore / 2)),
    };
    const nEj = { 20: 3, 30: 4, 45: 5, 60: 6 }[minutos];
    const lesion = resp.limitaciones || [];

    const sesiones = [];
    for (const [nombre, patrones] of D.ESTRUCTURA_CALIS[String(dias)]) {
      const ejercicios = [];
      const usados = new Set();
      for (const p of patrones) {
        if (ejercicios.length >= nEj) break;
        let nivel = niveles[p !== "traccion" || barra ? p : "traccion_sin_barra"];
        let patron = p;
        if (p === "traccion" && !barra) patron = "traccion_sin_barra";
        if (p === "fondos" && !paralelas) nivel = Math.min(nivel, 1);
        if (lesion.includes("muñecas") && (p === "empuje" || p === "empuje_vertical")) nivel = Math.min(nivel, 0);
        if (lesion.includes("rodillas") && p === "piernas") nivel = Math.min(nivel, 0);
        if (lesion.includes("hombros") && p === "empuje_vertical") continue;
        if (usados.has(patron)) nivel = Math.max(0, nivel - 1);
        const ej = ejCalis(patron, nivel);
        if (ejercicios.some((e) => e.nombre === ej[0])) continue;
        usados.add(patron);
        ejercicios.push({ nombre: ej[0], tipo: ej[1], nota: ej[2], patron });
      }
      sesiones.push({ nombre, ejercicios });
    }
    const mini = (e) => ({ nombre: e[0], tipo: e[1], nota: e[2] });
    if (obj.cardio) {
      for (const s of sesiones) s.finisher = [D.PATRONES.cardio[1], D.PATRONES.cardio[2], D.PATRONES.cardio[0]].map(mini);
    }
    const calendario = {};
    D.DISTRIBUCION[String(dias)].forEach((d, k) => { calendario[D.NOMBRES_DIAS[d]] = sesiones[k]; });
    return {
      resumen: Object.assign({}, resp, { series: obj.series, descanso: obj.descanso }),
      semanas, sesiones, calendario,
      calentamiento: [D.PATRONES.movilidad[0], D.PATRONES.movilidad[3], D.PATRONES.cardio[0]].map(mini),
      enfriamiento: [D.PATRONES.movilidad[1], D.PATRONES.movilidad[2]].map(mini),
    };
  };

  L.prescripcion = function (resp, ej, semana) {
    const obj = D.OBJETIVOS[resp.objetivo];
    const [lo, hi] = obj.reps;
    let series = obj.series, extra;
    if (resp.duracion <= 20) series = Math.max(2, series - 1);
    if (semana === 4) { series = Math.max(2, series - 1); extra = 0; }
    else extra = (semana - 1) * (hi >= 10 ? 2 : 1);
    if (ej.tipo === "seg") {
      const base = { fuerza: 20, musculo: 25, grasa: 30, general: 25 }[resp.objetivo];
      return `${series} × ${semana < 4 ? base + (semana - 1) * 5 : base} s`;
    }
    return `${series} × ${lo + extra}-${hi + extra} reps` + (semana === 4 ? " (RIR 2: deja 2 en reserva)" : "");
  };

  // ------------------------------------------------------------ gym (gym.py)
  L.faseDe = (semana) => Math.floor((semana - 1) / 4);
  L.esDescarga = (semana) => semana % 4 === 0;
  L.tituloSemana = (semana) => `Semana ${semana} · ${D.FASES[L.faseDe(semana)][0]}` + (L.esDescarga(semana) ? " · descarga" : "");

  function nivelGym(patron, fase, expOff, lim) {
    const base = patron.endsWith("_b") ? patron.slice(0, -2) : patron;
    const delta = patron.endsWith("_b") ? -1 : 0;
    const cadena = D.GYM[base];
    let lvl = fase + expOff + delta;
    if (base === "peso_muerto" && fase + expOff < 1) return null;
    if (lim.includes("hombros") && base === "hombro_press") return null;
    if (lim.includes("hombros") && (base === "pecho_press" || base === "espalda_vert"))
      lvl = Math.min(lvl, base === "espalda_vert" ? 0 : 1);
    if (lim.includes("muñecas") && (base === "pecho_press" || base === "hombro_press"))
      lvl = base === "pecho_press" ? 0 : lvl;
    if (lim.includes("muñecas") && base === "biceps") lvl = Math.min(lvl, 1);
    if (lim.includes("muñecas") && base === "abs_core") lvl = 0;
    if (lim.includes("rodillas") && (base === "unilateral" || base === "cuad_acc")) return null;
    if (lim.includes("rodillas") && base === "cuadriceps") lvl = 0;
    return cadena[clamp(lvl, 0, cadena.length - 1)];
  }

  const ejGym = (patron, items) => ({ patron, niveles: items.map(([nombre, nota, tipo]) => ({ nombre, nota, tipo })) });

  function bloqueFuerza(slots, n, expOff, lim) {
    const ejercicios = [], vistos = new Set();
    for (const patron of slots) {
      if (ejercicios.length >= n) break;
      const orig = [0, 1, 2].map((f) => nivelGym(patron, f, expOff, lim));
      if (!orig[0] && !orig[1] && !orig[2]) continue;
      const first = orig.find((x) => x);
      const porfase = orig.map((p) => p || first);
      if (vistos.has(porfase[0][0])) continue;
      vistos.add(porfase[0][0]);
      ejercicios.push(ejGym(patron, porfase));
    }
    return ejercicios;
  }

  function bloqueAbs(n, expOff, lim) {
    return ["abs_flex", "abs_core", "abs_piernas", "abs_rot"].slice(0, n).map((patron) =>
      ejGym(patron, [0, 1, 2].map((f) => nivelGym(patron, f, expOff, lim))));
  }

  function bloqueCardio(modo, lim, k) {
    let lista = modo === "LISS" ? D.CARDIO_LISS : D.CARDIO_HIIT;
    if (lim.includes("rodillas")) lista = lista.filter((e) => !D.CARDIO_SUAVE_RODILLAS.includes(e[0]));
    const r = k % lista.length;
    const rot = lista.slice(r).concat(lista.slice(0, r));
    return [{ patron: "cardio", modo, opciones: rot.slice(0, 4).map(([nombre, nota, tipo]) => ({ nombre, nota, tipo })) }];
  }

  L.generarPlanGym = function (resp) {
    const dias = resp.gym_dias, minutos = resp.gym_duracion, obj = resp.objetivo;
    const lim = resp.limitaciones || [];
    const expOff = { nunca: 0, poco: 0, medio: 1, avanzado: 2 }[resp.experiencia];
    const sesiones = [];
    D.ESTRUCTURA_GYM[obj][String(dias)].forEach(([clave, conAbs, cardio], i) => {
      let tAbs = conAbs ? 10 : 0, tCardio;
      if (clave === null) { tCardio = Math.max(20, Math.min(45, minutos - 5 - 12)); tAbs = 12; }
      else tCardio = cardio ? 12 : 0;
      const tFuerza = minutos - 5 - tAbs - tCardio;
      const bloques = [];
      if (clave) {
        const n = Math.max((tAbs || tCardio) ? 2 : 3, Math.min(8, Math.floor(tFuerza / 9)));
        bloques.push({ tipo: "Musculación", titulo: D.NOMBRES_SLOTS[clave], ejercicios: bloqueFuerza(D.SLOTS[clave], n, expOff, lim) });
      }
      if (conAbs) bloques.push({ tipo: "Abdominales", titulo: "Abdominales y core", ejercicios: bloqueAbs(tAbs >= 12 ? 4 : 3, expOff, lim) });
      if (cardio) bloques.push({ tipo: "Cardio", titulo: `Cardio ${cardio}`, modo: cardio, minutos: tCardio, ejercicios: bloqueCardio(cardio, lim, i) });
      sesiones.push({ nombre: clave ? D.NOMBRES_SLOTS[clave] : "Cardio y abdominales", bloques });
    });
    const calendario = {};
    D.DISTRIBUCION[String(dias)].forEach((d, k) => { calendario[D.NOMBRES_DIAS[d]] = sesiones[k]; });
    const mv = D.PATRONES.movilidad;
    return {
      tipo: "gym",
      resumen: Object.assign({}, resp, { dias, duracion: minutos }),
      semanas: D.SEMANAS_GYM, sesiones, calendario,
      calentamiento: [
        { nombre: "Caminata en cinta inclinada (5 min suaves)", nota: "Sube el pulso y calienta articulaciones.", tipo: "min" },
        { nombre: mv[0][0], nota: mv[0][2], tipo: "reps" },
        { nombre: mv[3][0], nota: mv[3][2], tipo: "reps" },
      ],
      enfriamiento: [
        { nombre: mv[1][0], nota: mv[1][2], tipo: "seg" },
        { nombre: mv[2][0], nota: mv[2][2], tipo: "seg" },
      ],
    };
  };

  L.ejercicioEn = (ej, semana) => ej.niveles ? ej.niveles[L.faseDe(semana)] : ej.opciones[(semana - 1) % ej.opciones.length];

  L.prescripcionGym = function (resp, bloque, ej, ejReal, semana) {
    const f = L.faseDe(semana), desc = L.esDescarga(semana), w = (semana - 1) % 4;
    const tipo = bloque.tipo;
    if (tipo === "Cardio") {
      const k = semana;
      if (bloque.modo === "LISS") {
        let m = Math.min(bloque.minutos === undefined ? 30 : bloque.minutos, 12 + 2 * k);
        if (desc) m = Math.floor(m * 0.8);
        return [`${m} min a ritmo suave (podrías hablar; 60-70% de tu FC máxima)`, 0];
      }
      const rondas = Math.min(12, 5 + Math.floor(k / 2) + (desc ? -2 : 0));
      return [`${rondas} rondas de 30 s fuerte (RPE 8-9) / 60 s suave + 3 min de vuelta a la calma`, 0];
    }
    if (tipo === "Abdominales") {
      const series = desc ? 2 : 3;
      if (ejReal.tipo === "seg") return [`${series} × ${30 + 10 * f + (desc ? 0 : 5 * Math.min(w, 2))} s`, 45];
      const [lo, hi] = f === 0 ? [12, 15] : [15, 20];
      return [`${series} × ${lo}-${hi} reps` + (f === 2 ? " · añade lastre/lentitud cuando sobren" : ""), 45];
    }
    const compuesto = D.COMPUESTOS.includes(ej.patron);
    const [lo, hi] = D.REPS_GYM[resp.objetivo][f][compuesto ? 0 : 1];
    let series = compuesto ? D.SERIES_GYM[resp.objetivo][f] : Math.max(2, D.SERIES_GYM[resp.objetivo][f] - 1);
    let rir;
    if (desc) { series = Math.max(2, series - 1); rir = "RIR 4 · baja el peso un 10%"; }
    else rir = D.RIR_GYM[f][w] ? `RIR ${D.RIR_GYM[f][w]}` : "al fallo técnico (última serie)";
    const descanso = compuesto ? { musculo: 90, fuerza: 150, grasa: 60, general: 90 }[resp.objetivo] : 60;
    return [`${series} × ${lo}-${hi} reps · ${rir}`, descanso];
  };

  // ------------------------------------------------------------ utilidades de datos
  L.slug = function (nombre) {
    const s = L.norm(nombre).replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
    return s || "usuario";
  };
  L.ahora = function () {
    const d = new Date(), p = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
  };
  L.hoy = () => L.ahora().slice(0, 10);

  root.LOGIC = L;
  if (typeof module !== "undefined") module.exports = L;
})(typeof window !== "undefined" ? window : globalThis);
