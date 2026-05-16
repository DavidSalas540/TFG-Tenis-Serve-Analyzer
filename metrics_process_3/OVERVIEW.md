# metrics_process_3 — Overview

Este módulo toma los CSVs de landmarks generados por `video_process_2` y produce
el dataset de entrenamiento con métricas biomecánicas por vídeo.

---

## Flujo de datos

```
data_csv/*.csv  (landmarks MediaPipe)
      │
      ▼
 event_detector.py   →  detecta los 4 frames clave del saque
      │
      ▼
 tennis_metrics.py   →  calcula métricas crudas (distancias, ángulos, salto)
      │
      ▼
 features_extractor.py  →  agrupa métricas en dicts para stance y effect
      │
      ▼
 batch_metrics.py    →  itera todos los CSVs y exporta train_dataset.csv
```

---

## Archivos

### `config.py`
Define las rutas de entrada y salida del módulo.
- `FOLDER_CSVS` → carpeta con los CSVs de landmarks
- `OUTPUT_DATASET` → ruta del CSV de entrenamiento generado

---

### `geometry.py`
Utilidades matemáticas básicas. No depende de ningún otro módulo del proyecto.

| Función | Qué hace |
|---|---|
| `calculate_angle(a, b, c)` | Ángulo en B formado por los puntos A-B-C (grados) |
| `calculate_distance(a, b)` | Distancia euclídea entre dos puntos |

---

### `quality_checks.py`
Valida que las métricas extraídas sean biomecánicamente plausibles.
Si un valor es imposible (e.g. rodilla en 5°), descarta ese vídeo.

| Función | Qué valida | Retorna |
|---|---|---|
| `validate_effect_metrics(data)` | jump, lateral_offset, arm_extension dentro de rangos | `(bool, msg)` |
| `validate_knee_integrity(angles, min_f, path)` | Ángulo de rodilla en mínimo ≥ 45° | `bool` |
| `validate_non_dominant_arm_angle(angle, path)` | Ángulo brazo no dominante entre 155°-190° | `bool` |

---

### `event_detector.py`
Detecta los 4 frames clave del saque usando la trayectoria del ángulo de rodilla.

| Frame | Significado biomecánico |
|---|---|
| `start` | Posición erguida inicial antes del movimiento |
| `best_min` | Máxima flexión de rodilla (fase de carga) |
| `best_max` | Máxima extensión de rodilla (despegue) |
| `target` | 32.5% del recorrido min→max (punto de máxima inercia) |

| Función | Qué hace |
|---|---|
| `detect_serve_phases(angles)` | Algoritmo principal: peaks/valleys → selección ROM → refinado local |
| `calculate_knee_frames(df)` | Wrapper: extrae ángulos del df y llama a `detect_serve_phases` |

---

### `tennis_metrics.py`
Calcula las métricas biomecánicas crudas a partir del DataFrame de landmarks.
Es el módulo más grande y centraliza todos los cálculos sobre el cuerpo.

**Utilidades:**

| Función | Qué devuelve |
|---|---|
| `get_hip_width(df, frame)` | Distancia entre caderas en un frame |
| `get_ankles_distance(df, frame)` | Distancia entre tobillos en un frame |
| `get_knee_angles_series(df)` | Lista de ángulos de rodilla para todos los frames |
| `get_hip_center_series(df)` | Lista de coordenadas X del centro de caderas |
| `get_non_dominant_arm_angles(df)` | Lista de ángulos del brazo no dominante por frame |

**Métricas de stance:**

| Función | Qué mide |
|---|---|
| `get_ankle_drag(df, start_f, target_f, hip_width)` | Desplazamiento acumulado del tobillo derecho, normalizado por ancho de caderas |
| `get_hip_tilt_data(df, target_f)` | Diferencia vertical entre caderas dividida por ancho de caderas |

**Métricas de effect:**

| Función | Qué mide |
|---|---|
| `calculate_max_jump(df, start_f, max_f, hip_width)` | Desplazamiento máximo hacia arriba del centro de caderas, normalizado |
| `extract_impact_metrics(df, start_f, max_f)` | Frame de impacto (mínimo Y de muñeca), lateral_offset y arm_extension |

---

### `features_extractor.py`
Capa de orquestación entre los cálculos de `tennis_metrics` y el pipeline batch.
Agrupa las métricas en diccionarios listos para construir el dataset.

| Función | Qué devuelve |
|---|---|
| `get_stance_label(video_id)` | 0 (pinpoint) / 1 (platform) / -1 (desconocido) |
| `get_effect_label(video_id)` | 0 (flat) / 1 (kick) / 2 (slice) / -1 (desconocido) |
| `calculate_stance_metrics(df, start_f, target_f)` | Dict con `ankle_drag`, `ankle_min_dist`, `hip_tilt` |
| `calculate_effect_metrics(df, start_f, max_f, hip_width, path)` | Dict con `jump`, `impact_frame`, `lateral_offset`, `arm_extension` |
| `get_non_dominant_arm_angle(df, min_f, target_f, path)` | Máximo ángulo del brazo no dominante en ventana ±5 frames alrededor de min_f |

---

### `batch_metrics.py`
Punto de entrada del módulo. Itera todos los CSVs y construye el dataset de entrenamiento.

| Función | Qué hace |
|---|---|
| `process_single_csv(csv_path)` | Procesa un CSV: detecta fases → extrae métricas → valida → retorna fila |
| `main_batch_process()` | Itera `FOLDER_CSVS`, llama a `process_single_csv` y exporta `train_dataset.csv` |

---

## Notebooks (carpeta `notebooks/`)

| Notebook | Propósito |
|---|---|
| `analyze_stance_metrics.ipynb` | Valida que ankle_drag y ankle_min_dist discriminan pinpoint vs platform |
| `analyze_effect.ipynb` | Valida que jump, lateral_offset e hip_tilt discriminan flat/kick/slice |
| `analyze_bio_feedback.ipynb` | Analiza métricas de feedback: extensión brazo no dominante y hip drive |

---

## Bugs conocidos (pendientes de corregir)

| Bug | Ubicación | Impacto |
|---|---|---|
| `validate_knee_integrity` chequeado con `is None` pero retorna `bool` | `batch_metrics.py:15` | El filtro de calidad de rodilla nunca descarta nada |
| Imports circulares: `tennis_metrics ↔ features_extractor ↔ event_detector` | Varios archivos | Puede fallar según orden de importación |
| `detectar_fases_saque` nombre en español | `event_detector.py` | Inconsistencia de idioma |
| `train_dataset.csv` guardado en directorio de trabajo, no en ruta fija | `batch_metrics.py:75` | Resuelto por `config.py` |
