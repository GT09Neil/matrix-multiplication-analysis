# 🏗️ Arquitectura del Proyecto

> Documento técnico que describe la estructura, componentes y decisiones de diseño del sistema de análisis de multiplicación de matrices.

---

## 📁 Estructura General

```
matrix-multiplication/
│
├── server.py                  ← Servidor HTTP con API REST
├── orchestrator.py            ← Orquestador CLI (alternativa sin web)
├── index.html                 ← Dashboard HTML interactivo
├── app.js                     ← Lógica del frontend (fetch API + Chart.js)
├── README.md                  ← Documentación principal
│
├── src/main/                  ← Código fuente Java
│   ├── Main.java              ← Punto de entrada
│   ├── algorithms/            ← 15 algoritmos de multiplicación
│   ├── persistence/           ← Exportación de datos (CSV, JSON)
│   └── utils/                 ← Utilidades (Timer, MatrixGenerator, MatrixUtils)
│
├── python/                    ← Código fuente Python
│   ├── main.py                ← Punto de entrada
│   ├── algorithms/            ← 15 algoritmos (réplica de Java)
│   └── utils/                 ← Utilidades (Timer, MatrixUtils)
│
├── data/
│   ├── test_cases/            ← Casos de prueba compartidos (JSON)
│   └── results/               ← Archivos CSV de resultados
│
├── out/                       ← Clases Java compiladas
│
└── docs/                      ← Documentación adicional
    └── ARCHITECTURE.md        ← Este archivo
```

---

## 🔍 Descripción de Componentes

### `server.py` — Servidor HTTP integrado

**Propósito:** Punto central del sistema. Sirve el dashboard HTML y proporciona una API REST para ejecutar algoritmos y consultar resultados.

**Tecnología:** `http.server` (biblioteca estándar de Python, sin dependencias externas).

**Endpoints:**

| Método | Ruta | Función |
|--------|------|---------|
| `GET` | `/` | Sirve `index.html` |
| `GET` | `/app.js` | Sirve el JavaScript del dashboard |
| `GET` | `/api/results` | Lista archivos CSV en `data/results/` |
| `GET` | `/api/results/<archivo>` | Devuelve contenido de un CSV específico |
| `POST` | `/api/execute` | Ejecuta algoritmos según el modo seleccionado |

**Modos de ejecución (`POST /api/execute`):**

Request body: `{ mode: "java"|"python"|"comparacion", size: 256 }`

| Modo | Acción | Archivos generados |
|------|--------|---------|
| `java` | Ejecuta `java -cp out main.Main --output <path> [--size N]` | `java_256_HH-MM-SS.csv` |
| `python` | Ejecuta `python -m python.main --output <path> [--size N]` | `python_256_HH-MM-SS.csv` |
| `comparacion` | Ejecuta ambos **en paralelo** (2 hilos) | `java_256_HH-MM-SS.csv` + `python_256_HH-MM-SS.csv` |

> Si no se envía `size`, ambos lenguajes ejecutan con los tamaños predeterminados (16, 32, 64, 128) y el nombre del archivo omite el tamaño.

**Decisión de diseño:** Se eligió `http.server` de la biblioteca estándar para evitar dependencias externas (no se requiere instalar Flask, Django, etc.), manteniendo el proyecto autocontenido y fácil de ejecutar en cualquier máquina con Python.

---

### `orchestrator.py` — Orquestador de línea de comandos

**Propósito:** Alternativa al servidor web para ejecución desde terminal. Lanza Java y Python como subprocesos, mide tiempos globales y genera un reporte comparativo.

**Uso:**

```bash
python orchestrator.py                     # Modo concurrente (por defecto)
python orchestrator.py --mode sequential   # Modo secuencial
```

**Diferencia con `server.py`:** El orquestador es una herramienta CLI para ejecución directa, mientras que el servidor es una interfaz web interactiva. Ambos invocan los mismos programas Java y Python internamente.

---

### `index.html` — Dashboard interactivo

**Propósito:** Interfaz web del usuario. Permite seleccionar el modo de ejecución, ejecutar análisis y visualizar resultados sin intervención manual.

**Componentes del UI:**

| Sección | Función |
|---------|---------|
| Panel de ejecución | 3 tarjetas (Java / Python / Comparación) + botón ejecutar |
| Filtros | Selector de tamaño de matriz y vista (Por Caso / Comparativa) |
| Gráfica | Canvas de Chart.js con barras agrupadas |
| Estadísticas | 4 tarjetas: mejor algoritmo, mejor Java, mejor Python, total |
| Panel comparativo | Promedios, mínimos, máximos por lenguaje |
| Historial | Lista de archivos CSV anteriores con carga por clic |

**Decisión de diseño:** Se eliminó la carga manual de archivos CSV. La selección del usuario (Java/Python/Comparación) controla todo el flujo: ejecución → generación → carga → visualización.

---

### `app.js` — Lógica del frontend

**Propósito:** Gestiona la comunicación con la API, el parseo de datos, el renderizado de gráficas y la actualización de estadísticas.

**Flujo principal:**

```
Usuario selecciona modo → Click "Ejecutar"
    → fetch('POST /api/execute', {mode: 'java'})
    → Servidor ejecuta algoritmos
    → Respuesta JSON con datos CSV parseados
    → renderCasesChart() o renderCompareChart()
    → updateStats() + updateComparison()
```

**Funciones clave:**

| Función | Responsabilidad |
|---------|-----------------|
| `executeAnalysis()` | POST a la API, procesa respuesta |
| `loadHistory()` | GET archivos históricos, renderiza lista |
| `loadHistoryFile()` | GET contenido de un CSV, parsea y grafica |
| `parseServerData()` | Convierte respuesta JSON a formato interno |
| `parseCSVText()` | Convierte texto CSV a formato interno |
| `renderCasesChart()` | Gráfica de barras agrupadas por caso |
| `renderCompareChart()` | Gráfica comparativa Java vs Python |
| `updateStats()` | Actualiza tarjetas de estadísticas |
| `updateComparison()` | Actualiza panel de comparación por lenguaje |

---

### `src/main/` — Implementación Java

#### `Main.java`

**Propósito:** Punto de entrada que ejecuta los 15 algoritmos con matrices cargadas desde JSON, mide tiempos y exporta CSV.

**Parámetros CLI:**

```bash
java -cp out main.Main                                               # Tamaños predeterminados
java -cp out main.Main --size 256                                    # Solo tamaño 256
java -cp out main.Main --output data/results/java_256_18-09-00.csv   # Nombre controlado
java -cp out main.Main --output ... --size 256                       # Ambos parámetros
```

#### `algorithms/` — 15 algoritmos

| Paquete | Clases | Descripción |
|---------|--------|-------------|
| `naive/` | `NaivOnArray`, `NaivLoopUnrollingTwo`, `NaivLoopUnrollingFour` | Multiplicación directa O(n³) con optimización de loop unrolling |
| `winograd/` | `WinogradOriginal`, `WinogradScaled` | Optimización algebraica que reduce multiplicaciones. La variante Scaled normaliza por norma infinito |
| `strassen/` | `StrassenNaiv`, `StrassenWinograd` | Divide y vencerás recursivo O(n^2.807). Caso base: naive o Winograd |
| `column_column/` | `SequentialBlock`, `ParallelBlock` | Multiplicación por bloques con acceso column-column (A[k][i] += B[k][j] * C[j][i]) |
| `row_column/` | `SequentialBlock`, `ParallelBlock`, `EnhancedParallelBlock` | Multiplicación por bloques con acceso row-column estándar (A[i][j] += B[i][k] * C[k][j]) |
| `row_row/` | `SequentialBlock`, `ParallelBlock`, `EnhancedParallelBlock` | Multiplicación por bloques con acceso row-row (A[i][k] += B[i][j] * C[j][k]) |

#### `persistence/` — Exportación de datos

| Clase | Función |
|-------|---------|
| `ExecutionResultRepository` | Guarda resultados detallados en CSV (7 columnas). Acepta nombre de archivo personalizado via constructor |
| `ChartDataExporter` | Genera tabla pivote y resumen estadístico para análisis externos |
| `TestCaseRepository` | Persiste y carga pares de matrices (A, B) en formato JSON |

#### `utils/` — Utilidades

| Clase | Función |
|-------|---------|
| `Timer` | Medición de alta precisión con `System.nanoTime()` |
| `MatrixGenerator` | Genera pares de matrices aleatorias (valores de 6 dígitos) |
| `MatrixUtils` | Operaciones auxiliares: add, subtract, split, join (para Strassen) |

---

### `python/` — Implementación Python

#### `main.py`

**Propósito:** Equivalente exacto de `Main.java`. Ejecuta los 15 algoritmos, mide tiempos con `time.perf_counter_ns()` y exporta CSV.

**Parámetros CLI:**

```bash
python -m python.main                                                  # Tamaños predeterminados
python -m python.main --size 512                                       # Solo tamaño 512
python -m python.main --output data/results/python_512_18-09-00.csv    # Nombre controlado
python -m python.main --mode concurrente                               # Tipo de ejecución
python -m python.main --output ... --size 256 --mode secuencial        # Todos los parámetros
```

#### `algorithms/` — 15 algoritmos (réplica de Java)

| Módulo | Funciones |
|--------|-----------|
| `naive.py` | `naiv_on_array()`, `naiv_loop_unrolling_two()`, `naiv_loop_unrolling_four()` |
| `winograd.py` | `winograd_original()`, `winograd_scaled()`, `_infinity_norm()` |
| `strassen.py` | `strassen_naiv()`, `strassen_winograd()` |
| `column_column.py` | `cc_sequential_block()`, `cc_parallel_block()` |
| `row_column.py` | `rc_sequential_block()`, `rc_parallel_block()`, `rc_enhanced_parallel_block()` |
| `row_row.py` | `rr_sequential_block()`, `rr_parallel_block()`, `rr_enhanced_parallel_block()` |

#### `utils/` — Utilidades

| Módulo | Función |
|--------|---------|
| `timer.py` | Clase `Timer` con `time.perf_counter_ns()` (equivalente a `System.nanoTime()`) |
| `matrix_utils.py` | `add()`, `subtract()`, `split()`, `join()` para Strassen |

---

### `data/` — Datos del proyecto

#### `data/test_cases/`

Contiene pares de matrices (A, B) en formato JSON, generados por Java y consumidos por ambos lenguajes para garantizar comparabilidad.

**Formato:** `case_{id}_size_{n}.json`

```json
{
  "size": 64,
  "caseId": "1",
  "matrixA": [[...], ...],
  "matrixB": [[...], ...]
}
```

#### `data/results/`

Contiene todos los archivos CSV de resultados:

| Patrón | Origen | Descripción |
|--------|--------|-------------|
| `java_256_HH-MM-SS.csv` | Servidor | Resultados Java tamaño específico |
| `python_256_HH-MM-SS.csv` | Servidor | Resultados Python tamaño específico |
| `java_HH-MM-SS.csv` | Servidor | Resultados Java todos los tamaños |
| `python_HH-MM-SS.csv` | Servidor | Resultados Python todos los tamaños |
| `chart_pivot_*.csv` | Java (ChartDataExporter) | Tabla pivote para análisis externo |
| `chart_summary_*.csv` | Java (ChartDataExporter) | Resumen estadístico |

---

### `out/` — Clases Java compiladas

Contiene los archivos `.class` generados por `javac`. Estructura de paquetes espejada desde `src/main/`.

---

## 🧩 Decisiones de Diseño

### ¿Por qué dos lenguajes?

El objetivo académico es comparar cómo un mismo algoritmo se comporta en lenguajes con características fundamentalmente diferentes:

- **Java:** Lenguaje compilado a bytecode con JIT, hilos nativos, sin GIL
- **Python:** Lenguaje interpretado con GIL, más lento en cómputo puro pero con sintaxis clara

Esto permite observar los factores que afectan el rendimiento: compilación JIT, gestión de memoria, overhead de interpretación, etc.

### ¿Por qué `threading` y no `multiprocessing` en Python?

1. **Fidelidad conceptual:** Replicar la semántica de hilos de Java
2. **Simplicidad de datos:** La matriz resultado `A` se comparte en memoria sin serialización
3. **Observación del GIL:** Permite demostrar académicamente cómo el GIL afecta el paralelismo CPU-bound
4. **No hay race conditions:** Cada hilo escribe en filas/regiones independientes de la matriz

### ¿Por qué un servidor HTTP y no una app desktop?

1. **Cero dependencias:** `http.server` es parte de la biblioteca estándar de Python
2. **Portabilidad:** Funciona en cualquier navegador, cualquier SO
3. **Separación de responsabilidades:** Backend (Python/Java) separado del frontend (HTML/JS)
4. **Automatización del flujo:** La selección del usuario controla directamente la ejecución

### ¿Por qué potencias de 2 para los tamaños?

El algoritmo de Strassen requiere que las matrices sean de tamaño 2^k para la división recursiva en cuadrantes. Los tamaños configurados (16, 32, 64, 128) cumplen esta restricción y permiten observar el crecimiento del tiempo de ejecución.

### ¿Por qué JSON para los casos de prueba?

1. **Interoperabilidad:** Tanto Java (con `org.json`) como Python (`json` stdlib) lo leen nativamente
2. **Reproducibilidad:** Ambos lenguajes usan exactamente las mismas matrices de entrada
3. **Persistencia:** Los casos se generan una vez y se reutilizan en múltiples ejecuciones
