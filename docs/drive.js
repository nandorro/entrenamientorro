/* Sincronización con Google Drive (carpeta «entrenamientorro») para la versión APK.
 *
 * Solo está activa si existe window.DRIVE_CONFIG (lo genera apk/preparar_config.py y NUNCA se sube a GitHub).
 * En la web pública no hay credenciales: Sync.activo = false y los datos quedan en el dispositivo.
 * El archivo de cada usuario es  entrenamientorro/<nombre>.json  (mismo nombre que usa la versión de PC).
 */
(function (root) {
  const cfg = root.DRIVE_CONFIG;
  const Sync = { activo: !!(cfg && cfg.refresh_token) };
  const API = "https://www.googleapis.com/drive/v3/files";
  const UP = "https://www.googleapis.com/upload/drive/v3/files";
  let tok = null, tokHasta = 0, carpetaId = null;

  async function token() {
    if (tok && Date.now() < tokHasta) return tok;
    const r = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: cfg.client_id, client_secret: cfg.client_secret,
        refresh_token: cfg.refresh_token, grant_type: "refresh_token",
      }).toString(),
    });
    if (!r.ok) throw new Error("token " + r.status);
    const j = await r.json();
    tok = j.access_token;
    tokHasta = Date.now() + (j.expires_in - 60) * 1000;
    return tok;
  }

  const espera = (ms) => new Promise((ok) => setTimeout(ok, ms));
  // Drive responde 403/429/5xx cuando se agota la cuota por minuto del proyecto (pasa con el cliente compartido
  // de rclone): se reintenta con espera creciente, igual que hace rclone.
  async function api(url, opts) {
    opts = opts || {};
    for (let intento = 0; ; intento++) {
      const t = await token();
      const r = await fetch(url, Object.assign({}, opts, { headers: Object.assign({ Authorization: "Bearer " + t }, opts.headers || {}) }));
      if (r.ok || r.status === 404) return r;
      const reintentable = r.status === 403 || r.status === 429 || r.status >= 500;
      if (!reintentable || intento >= 7) throw new Error("drive " + r.status);
      if (r.status === 401) tok = null;
      await espera(Math.min(20000, 800 * Math.pow(2, intento)) + Math.random() * 500);
    }
  }

  async function buscar(q) {
    const r = await api(API + "?q=" + encodeURIComponent(q) + "&fields=files(id,name)&pageSize=5");
    return (await r.json()).files || [];
  }

  async function carpeta() {
    if (carpetaId) return carpetaId;
    const f = await buscar("name='entrenamientorro' and mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false");
    if (f.length) return (carpetaId = f[0].id);
    const r = await api(API, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "entrenamientorro", mimeType: "application/vnd.google-apps.folder", parents: ["root"] }),
    });
    return (carpetaId = (await r.json()).id);
  }

  async function archivo(nombre) {
    const c = await carpeta();
    const f = await buscar(`name='${root.LOGIC.slug(nombre)}.json' and '${c}' in parents and trashed=false`);
    return f.length ? f[0].id : null;
  }

  /** @returns {Promise<{estado: 'ok'|'no_existe'|'error', texto: string|null}>} */
  Sync.descargar = async function (nombre) {
    try {
      const id = await archivo(nombre);
      if (!id) return { estado: "no_existe", texto: null };
      const r = await api(API + "/" + id + "?alt=media");
      return { estado: "ok", texto: await r.text() };
    } catch (e) {
      return { estado: "error", texto: null };
    }
  };

  Sync.subir = async function (nombre, texto) {
    try {
      let id = await archivo(nombre);
      if (!id) {
        const c = await carpeta();
        const r = await api(API, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: root.LOGIC.slug(nombre) + ".json", mimeType: "application/json", parents: [c] }),
        });
        id = (await r.json()).id;
      }
      await api(UP + "/" + id + "?uploadType=media", {
        method: "PATCH", headers: { "Content-Type": "application/json; charset=UTF-8" }, body: texto,
      });
      return true;
    } catch (e) {
      return false;
    }
  };

  root.DriveSync = Sync;
})(window);
