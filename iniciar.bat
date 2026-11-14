@echo off
chcp 65001 >nul
title Calistenia Plan
cd /d "%~dp0"

rem --- Buscar Python (py launcher o python)
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY (
  echo No se encuentra Python. Instalalo desde https://www.python.org/downloads/
  echo Marca la casilla "Add Python to PATH" al instalar.
  pause
  exit /b 1
)

rem --- Instalar PySide6 si falta
%PY% -c "import PySide6.QtWidgets" >nul 2>&1
if errorlevel 1 (
  echo Instalando PySide6 ^(solo la primera vez^)...
  %PY% -m pip install PySide6
  if errorlevel 1 (
    echo No se pudo instalar PySide6.
    pause
    exit /b 1
  )
)

rem --- Borrar error anterior y lanzar sin ventana de consola
if exist error.log del error.log
set "PYW=%PY%w"
if "%PY%"=="py" set "PYW=pyw"
start "" %PYW% calistenia.py

rem --- Si fallo al arrancar, error.log aparece enseguida: mostrarlo
timeout /t 3 /nobreak >nul
if exist error.log (
  echo La app ha fallado:
  echo.
  type error.log
  echo.
  pause
)
exit /b 0
