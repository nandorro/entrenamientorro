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
    let nPier = { nunca: 0, poco: 1, medio: 2, avanzado: 3 }[resp.experiencia];
    if (resp.sentadillas) nPier = D.SENTADILLAS[resp.sentadillas];
    const prio = new Set((resp.zonas || []).flatMap((z) => D.ZONA_PATRONES[z] || []));
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
    for (const [nombre, patrones0] of D.ESTRUCTURA_CALIS[String(dias)]) {
      const patrones = patrones0.slice().sort((a, b) => (prio.has(a) ? 0 : 1) - (prio.has(b) ? 0 : 1));
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
    const zonas = resp.zonas || [];
    const prio = new Set(zonas.flatMap((z) => D.ZONA_SLOTS[z] || []));
    const sesiones = [];
    D.ESTRUCTURA_GYM[obj][String(dias)].forEach(([clave, conAbs, cardio], i) => {
      let tAbs = conAbs ? 10 : 0, tCardio;
      if (clave === null) { tCardio = Math.max(20, Math.min(45, minutos - 5 - 12)); tAbs = 12; }
      else tCardio = cardio ? 12 : 0;
      const tFuerza = minutos - 5 - tAbs - tCardio;
      const bloques = [];
      if (clave) {
        const n = Math.max((tAbs || tCardio) ? 2 : 3, Math.min(8, Math.floor(tFuerza / 9)));
        bloques.push({ tipo: "Musculación", titulo: D.NOMBRES_SLOTS[clave], ejercicios: bloqueFuerza(D.SLOTS[clave].slice().sort((a, b) => (prio.has(a) ? 0 : 1) - (prio.has(b) ? 0 : 1)), n, expOff, lim) });
      }
      if (conAbs) bloques.push({ tipo: "Abdominales", titulo: "Abdominales y core", ejercicios: bloqueAbs((tAbs >= 12 || zonas.includes("abdomen")) ? 4 : 3, expOff, lim) });
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

  // ------------------------------------------------------------ perfil (port de plan.resumen_perfil)
  L.resumenPerfil = function (r) {
    const out = [];
    const imc = r.peso / Math.pow(r.altura / 100, 2);
    const cat = imc < 18.5 ? "bajo peso" : imc < 25 ? "peso normal" : imc < 30 ? "sobrepeso" : "obesidad";
    out.push(`IMC ${(Math.floor(imc * 10 + 0.5) / 10).toFixed(1)} (${cat})`);
    const po = r.peso_obj;
    if (po && Math.abs(po - r.peso) >= 1) {
      const diff = po - r.peso, a = Math.abs(diff);
      const lo = Math.round(a / 0.5), hi = Math.round(a / 0.25);
      const g = (n) => String(+n.toFixed(2)).replace(".", ",");
      out.push(`Meta: ${g(po)} kg (${diff > 0 ? "+" : "−"}${g(a)} kg). A un ritmo saludable de 0,25-0,5 kg/semana (${diff < 0 ? "perder" : "ganar"}) son unas ${lo}-${hi} semanas.`);
    }
    out.push("Nivel de partida: " + { nunca: "principiante", poco: "principiante", medio: "intermedio", avanzado: "avanzado" }[r.experiencia]);
    if (r.zonas && r.zonas.length) out.push("Zonas prioritarias: " + r.zonas.join(", "));
    if (r.sueno === "<6") out.push("Duermes poco (<6 h): es cuando más se recupera el músculo; intenta llegar a 7-8 h.");
    if (r.dia === "sedentario") out.push("Tu día es sedentario: suma 8.000-10.000 pasos diarios además de entrenar.");
    const dias = r.dias !== undefined ? r.dias : (r.gym_dias || 0);
    if (r.actual === "nunca" && dias >= 5) out.push("Empiezas desde cero con muchos días: si te cuesta, empieza con 3 y sube poco a poco.");
    return out;
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

  // ------------------------------------------------------------ nutrición (port de nutricion.py)
  const rd = (x, nd) => { const f = Math.pow(10, nd || 0); return Math.floor(x * f + 0.5) / f; };
  L.rd = rd;
  const hora = (h) => {
    let m = rd((h - Math.floor(h)) * 60), hh = Math.floor(h);
    if (m === 60) { hh += 1; m = 0; }
    return String(hh).padStart(2, "0") + ":" + String(m).padStart(2, "0");
  };

  L.generarPlanNutricion = function (r) {
    const N = D.NUTRI;
    const sexo = r.sexo || "otro";
    const peso = r.peso, altura = r.altura, edad = r.edad, obj = r.objetivo;
    const dieta = r.dieta || "omnivora";
    const n = parseInt(r.comidas === undefined ? 4 : r.comidas, 10);
    const fr = N.FRECUENCIA[r.actual === undefined ? "3-4" : r.actual];
    const diasEnt = Math.max(fr === undefined ? 3 : fr, r.dias || 0, r.gym_dias || 0);
    const basal = 10 * peso + 6.25 * altura - 5 * edad + N.BASAL_SEXO[sexo];
    let mant = basal * N.FACTOR_DIA[r.dia || "moderado"] + diasEnt * 250 / 7;
    const ajuste = edad < 18 ? 0.0 : N.AJUSTE[obj];
    let kcal = mant * (1 + ajuste), limitado = false;
    if (ajuste < 0) {
      const suelo = Math.max(mant * 0.75, N.MINIMO_KCAL[sexo]);
      if (kcal < suelo) { kcal = suelo; limitado = true; }
    }
    kcal = rd(kcal / 10) * 10;
    mant = rd(mant / 10) * 10;
    let prot = rd(peso * N.PROTEINA_GKG[obj]);
    prot = Math.min(prot, rd(kcal * 0.35 / 4));
    const grasa = rd(Math.max(peso * 0.6, kcal * 0.25 / 9));
    const hidr = Math.max(0, rd((kcal - prot * 4 - grasa * 9) / 4));
    const agua = Math.min(4.0, Math.max(1.5, rd((peso * 35 + (diasEnt > 0 ? 500 : 0)) / 100) / 10));
    const inicio = N.HORA_DESAYUNO[r.desayuno || "7-9"];
    const comidas = [];
    for (const [nombre, pct, tipo, desfase] of N.COMIDAS[String(n)]) {
      const k = rd(kcal * pct);
      const opciones = N.MENUS[dieta][tipo].map(([on, ok, op, oc, og]) => {
        const racion = Math.min(2.0, Math.max(0.5, rd(k / ok * 4) / 4));
        return { nombre: on, racion, kcal: rd(ok * racion), p: rd(op * racion), c: rd(oc * racion), g: rd(og * racion) };
      });
      comidas.push({ nombre, hora: hora(inicio + desfase), kcal: k, opciones });
    }
    const consejos = [
      "Pon una fuente de proteína en cada comida (huevo, legumbres, pescado, lácteos, tofu…): sacia y protege el músculo.",
      "La mitad del plato, verduras; un cuarto proteína y un cuarto hidratos integrales.",
    ];
    if (r.agua === "<3" || r.agua === "3-5") {
      consejos.push(`Hoy bebes poco: sube hasta ${String(agua).replace(".", ",")} L al día (vasos de 250 ml). Un vaso al levantarte y otro antes de cada comida.`);
    }
    for (const a of r.antojos || []) if (N.ANTOJOS[a]) consejos.push(N.ANTOJOS[a]);
    if (r.registro === "no") consejos.push("Apunta lo que comes durante 7 días (cuaderno o app): ver los datos suele corregir más que cualquier regla.");
    if (r.sueno === "<6") consejos.push("Dormir menos de 6 h aumenta el hambre y los antojos; mejorar el sueño ayuda tanto como la dieta.");
    if (dieta === "vegana") consejos.push("Dieta vegana: la vitamina B12 hay que suplementarla (consúltalo con tu médico) y combina legumbres con cereales.");
    else if (dieta === "vegetariana") consejos.push("Dieta vegetariana: cuida hierro y B12; toma las legumbres con algo de vitamina C (cítricos, pimiento).");
    if (limitado) consejos.push("Hemos limitado el déficit para que no baje de un mínimo saludable; es mejor perder grasa despacio y mantener el músculo.");
    if (edad < 18) consejos.push("Eres menor de 18: no recomendamos déficit calórico; este plan es de mantenimiento. Consulta con tu pediatra o médico.");
    const delta = kcal - mant;
    return {
      tipo: "nutricion",
      resumen: Object.assign({}, r, { dias: diasEnt, duracion: 0, comidas: n, dieta }),
      kcal, mantenimiento: mant, basal: rd(basal), macros: { p: prot, c: hidr, g: grasa },
      agua, ritmo_kg_sem: rd(Math.abs(delta) * 7 / 7700, 2), delta, comidas, consejos, aviso: N.AVISO, semanas: 1,
      calendario: {}, sesiones: [], calentamiento: [], enfriamiento: [],
    };
  };

  // ------------------------------------------------------------ gráficas finales (port de progreso.py)
  const r1 = (x) => Math.floor(x * 10 + 0.5) / 10;
  L.proyeccionPeso = function (r, ritmo) {
    const po = r.peso_obj, peso = r.peso;
    if (!po || Math.abs(po - peso) < 1) return null;
    const diff = po - peso;
    if (!ritmo) ritmo = diff < 0 ? 0.5 : 0.25;
    const semanas = Math.min(52, Math.max(4, Math.ceil(Math.abs(diff) / ritmo)));
    const f = Math.min(1.0, semanas * ritmo / Math.abs(diff));
    const puntos = [];
    for (let i = 0; i < 7; i++) {
      const u = i / 6;
      puntos.push([Math.floor(semanas * u + 0.5), r1(peso + diff * f * (1 - Math.pow(1 - u, 1.5)))]);
    }
    return { semanas, alcanza: f >= 1.0, inicio: peso, meta: po, puntos };
  };
  const series = (t) => { const m = /^\s*(\d+)/.exec(t); return m ? parseInt(m[1], 10) : 0; };
  L.cargaSemanal = function (plan) {
    const r = plan.resumen, out = [];
    for (let sem = 1; sem <= plan.semanas; sem++) {
      let total = 0;
      for (const s of plan.sesiones) {
        if (plan.tipo === "gym") {
          for (const b of s.bloques) {
            if (b.tipo === "Cardio") continue;
            for (const ej of b.ejercicios) total += series(L.prescripcionGym(r, b, ej, L.ejercicioEn(ej, sem), sem)[0]);
          }
        } else for (const e of s.ejercicios) total += series(L.prescripcion(r, e, sem));
      }
      out.push(total);
    }
    return out;
  };

  root.LOGIC = L;
  if (typeof module !== "undefined") module.exports = L;
})(typeof window !== "undefined" ? window : globalThis);
