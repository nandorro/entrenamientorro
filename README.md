# Entrenamientorro 💪🥦

Planes de entrenamiento personalizados con un quiz y **animaciones de cada ejercicio**:

- **💪 Calistenia**: plan de 4 semanas según tu nivel, material, días y tiempo.
- **🥦 GymBrocoli**: plan de gimnasio de 12 semanas en 3 fases (adaptación → construcción → intensificación),
  con semana de descarga cada 4 y sesiones separadas en **musculación, abdominales y cardio**.

Si ya hiciste el test de una modalidad, la otra solo te pregunta lo que le falta (días y tiempo).

## Versiones

| Versión | Cómo se usa | Datos |
|---|---|---|
| **Web** (GitHub Pages) | Abre la web desde el móvil o el PC. Se puede instalar como app (PWA). | En el dispositivo; botones para exportar/importar `.json`. |
| **PC** (Python + PySide6) | `iniciar.bat` (o `python calistenia.py`). | En `datos.json` y en Google Drive (`entrenamientorro/<nombre>.json`) con rclone. |
| **APK** (Android) | Instalable privado, no incluido en el repositorio. | En Google Drive, en la misma carpeta que el PC. |

Al empezar te pregunta tu **nombre y edad**; con ellos se nombra y se encuentra tu archivo en Drive.

## Estructura

```
calistenia.py       app de escritorio (interfaz)
plan.py  gym.py     generadores de los planes (calistenia / gimnasio)
ejercicios.py       catálogo de calistenia y progresiones
animaciones*.py     muñecos animados de cada ejercicio
drive.py            sincronización con Drive (rclone)
export_datos.py     genera docs/data.js a partir de los datos de Python
docs/               versión web (la que publica GitHub Pages)
```

La versión web usa exactamente los mismos datos que Python: tras cambiar ejercicios, animaciones o textos, ejecuta

```
python export_datos.py
```

y la lógica de `docs/logic.js` genera los mismos planes que `plan.py` / `gym.py`.
