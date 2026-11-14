"""Sincronización con Google Drive (carpeta «entrenamientorro») usando rclone.

Cada usuario guarda un archivo  gdrive:entrenamientorro/<nombre>.json  con su perfil, planes y progreso.
El mismo formato y el mismo nombre de archivo los usa la versión APK, así comparten datos.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path

REMOTO = "gdrive:entrenamientorro"
NOFLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def buscar_rclone():
    ruta = shutil.which("rclone")
    if ruta:
        return ruta
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    if base.exists():
        for p in base.rglob("rclone.exe"):
            return str(p)
    return None


def codigo_vinculacion() -> str:
    """Código para vincular la web/APK con tu Drive (base64 de client_id, client_secret y refresh_token).

    Sale del remoto «gdrive» de rclone. Si ese remoto usa el cliente compartido de rclone (client_id vacío),
    las credenciales públicas de rclone se toman de apk/www/drive-config.js (archivo local, nunca en git).
    ATENCIÓN: el código da acceso a todo tu Drive; no lo compartas ni lo publiques.
    """
    import base64
    import json
    exe = buscar_rclone()
    if not exe:
        raise RuntimeError("No encuentro rclone.")
    r = subprocess.run([exe, "config", "dump"], capture_output=True, text=True, encoding="utf8",
                       creationflags=NOFLAGS, timeout=60)
    g = json.loads(r.stdout).get("gdrive")
    if not g:
        raise RuntimeError("No existe el remoto «gdrive» en rclone.")
    cid, sec = g.get("client_id"), g.get("client_secret")
    if not (cid and sec):
        local = Path(__file__).resolve().parent / "apk" / "www" / "drive-config.js"
        if not local.exists():
            raise RuntimeError("Tu rclone usa el cliente compartido y falta apk/www/drive-config.js "
                               "(ejecuta apk/compilar.sh una vez).")
        cfg = json.loads(local.read_text(encoding="utf8").split("=", 1)[1].strip().rstrip(";"))
        cid, sec = cfg["client_id"], cfg["client_secret"]
    conf = {"client_id": cid, "client_secret": sec, "refresh_token": json.loads(g["token"])["refresh_token"]}
    return base64.b64encode(json.dumps(conf).encode()).decode()


def slug(nombre: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", nombre.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "usuario"


def ruta_remota(nombre: str) -> str:
    return f"{REMOTO}/{slug(nombre)}.json"


def _rclone(*args, timeout=60):
    exe = buscar_rclone()
    if not exe:
        return None
    return subprocess.run([exe, *args], capture_output=True, text=True, timeout=timeout,
                          creationflags=NOFLAGS, encoding="utf8", errors="replace")


def descargar(nombre: str):
    """Devuelve (estado, texto): estado = 'ok' | 'no_existe' | 'error' ('error' = sin rclone o sin conexión)."""
    tmp = Path(tempfile.mkdtemp()) / "datos.json"
    try:
        r = _rclone("copyto", ruta_remota(nombre), str(tmp))
        if r is None:
            return "error", None
        if r.returncode == 0 and tmp.exists():
            return "ok", tmp.read_text(encoding="utf8")
        err = (r.stderr or "").lower()
        if "not found" in err or "directory not found" in err or r.returncode in (3, 4):
            return "no_existe", None
        return "error", None
    except Exception:
        return "error", None
    finally:
        shutil.rmtree(tmp.parent, ignore_errors=True)


def subir(nombre: str, texto: str) -> bool:
    tmp = Path(tempfile.mkdtemp()) / "datos.json"
    try:
        tmp.write_text(texto, encoding="utf8")
        r = _rclone("copyto", str(tmp), ruta_remota(nombre))
        return bool(r and r.returncode == 0)
    except Exception:
        return False
    finally:
        shutil.rmtree(tmp.parent, ignore_errors=True)
