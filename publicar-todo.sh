#!/usr/bin/env bash
# Publica un cambio en TODAS las versiones: ./publicar-todo.sh "mensaje del commit"
#   1) regenera docs/data.js desde los datos de Python
#   2) sube la web a GitHub (GitHub Pages: https://nandorro.github.io/entrenamientorro/)
#   3) recompila el APK privado (../Entrenamientorro.apk, lleva el token de Drive: no se sube a GitHub)
set -euo pipefail
cd "$(dirname "$0")"
MSG="${1:-Actualización}"
QT_QPA_PLATFORM=offscreen python export_datos.py
git add -A
git diff --cached --quiet || git commit -q -m "$MSG

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
git push -q origin main
(cd apk && ./compilar.sh)
echo "Publicado: web + APK"
