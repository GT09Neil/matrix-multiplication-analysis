# 📊 Matrix Multiplication Analysis

> Sistema interactivo y automatizado para el análisis comparativo de rendimiento de 15 algoritmos de multiplicación de matrices, implementados en **Java** y **Python**, con dashboard web integrado.

---

## 📋 Descripción del Proyecto

Este proyecto académico implementa y compara el rendimiento de **15 algoritmos distintos** de multiplicación de matrices en dos lenguajes de programación (Java y Python). El sistema incluye:

- Un **servidor web integrado** que automatiza la ejecución y visualización
- Un **dashboard interactivo** donde el usuario selecciona qué ejecutar y los resultados se cargan automáticamente
- **Ejecución concurrente** para comparaciones justas entre lenguajes
- **Exportación CSV** con nomenclatura clara y formato unificado

### ¿Cómo funciona?

```
┌─────────────────────────────────────────────────────────┐
│                    Dashboard HTML                        │
│   Selección: ☕ Java │ 🐍 Python │ ⚡ Comparación       │
│              [ ▶ Ejecutar Análisis ]                     │
└────────────────────────┬────────────────────────────────┘
                         │ POST /api/execute
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   server.py (API)                        │
│   Lanza subprocesos Java y/o Python según selección     │
│   Genera CSVs con nombres: java_HH-MM-SS.csv           │
│   Devuelve datos al dashboard automáticamente           │
└────────────┬───────────────────────────┬────────────────┘
             ▼                           ▼
     ┌──────────────┐           ┌──────────────────┐
     │  java Main   │           │  python main.py  │
     │  15 algos    │           │  15 algos        │
     │  System.nano │           │  perf_counter_ns │
     └──────┬───────┘           └────────┬─────────┘
            ▼                            ▼
     ┌──────────────────────────────────────────┐
     │       data/results/                       │
     │   java_18-09-00.csv                       │
     │   python_18-09-00.csv                     │
     └──────────────────────────────────────────┘
```

---

## 🚀 Cómo Ejecutar el Proyecto

### Prerrequisitos

- **Java** JDK 11+ (`java` y `javac` en PATH)
- **Python** 3.8+ (`python` en PATH)
- No se requieren dependencias externas de Python

### Paso 1: Compilar Java (solo la primera vez)

```bash
javac -d out -encoding UTF-8 src/main/utils/*.java src/main/persistence/*.java src/main/algorithms/naive/*.java src/main/algorithms/winograd/*.java src/main/algorithms/strassen/*.java src/main/algorithms/column_column/*.java src/main/algorithms/row_column/*.java src/main/algorithms/row_row/*.java src/main/Main.java
```

### Paso 2: Iniciar el servidor

```bash
python server.py
```

El servidor se inicia en **http://localhost:8080**.

### Paso 3: Usar el dashboard

1. Abrir **http://localhost:8080** en el navegador
2. Seleccionar el modo de ejecución:
   - **☕ Java** → ejecuta los 15 algoritmos solo en Java
   - **🐍 Python** → ejecuta los 15 algoritmos solo en Python
   - **⚡ Comparación** → ejecuta ambos lenguajes simultáneamente
3. Seleccionar el **tamaño de matriz** (2 a 1024, potencias de 2) o "Todos" para los predeterminados
4. Presionar **▶ Ejecutar Análisis**
5. Los resultados se cargan y grafican **automáticamente**

### Ejecución alternativa (sin servidor)

También puede ejecutarse desde la línea de comandos:

```bash
# Solo Java
java -cp out main.Main
java -cp out main.Main --size 256

# Solo Python
python -m python.main
python -m python.main --size 512

# Ambos (orquestador CLI)
python orchestrator.py                     # Concurrente
python orchestrator.py --mode sequential   # Secuencial
```

---

## 🧮 Algoritmos Implementados (15)

| # | Categoría | Algoritmo | Complejidad | Concurrencia |
|---|---|---|---|---|
| 1 | Naive | `NaivOnArray` | O(n³) | No |
| 2 | Naive | `NaivLoopUnrollingTwo` | O(n³) | No |
| 3 | Naive | `NaivLoopUnrollingFour` | O(n³) | No |
| 4 | Winograd | `WinogradOriginal` | O(n³) optimizado | No |
| 5 | Winograd | `WinogradScaled` | O(n³) optimizado | No |
| 6 | Strassen | `StrassenNaiv` | O(n^2.807) | No |
| 7 | Strassen | `StrassenWinograd` | O(n^2.807) | No |
| 8 | Column-Column | `CC_SequentialBlock` | O(n³) bloques | No |
| 9 | Column-Column | `CC_ParallelBlock` | O(n³) bloques | **Sí** |
| 10 | Row-Column | `RC_SequentialBlock` | O(n³) bloques | No |
| 11 | Row-Column | `RC_ParallelBlock` | O(n³) bloques | **Sí** |
| 12 | Row-Column | `RC_EnhancedParallelBlock` | O(n³) bloques | **Sí** |
| 13 | Row-Row | `RR_SequentialBlock` | O(n³) bloques | No |
| 14 | Row-Row | `RR_ParallelBlock` | O(n³) bloques | **Sí** |
| 15 | Row-Row | `RR_EnhancedParallelBlock` | O(n³) bloques | **Sí** |

---

## 📊 Sistema de Archivos CSV

### Nomenclatura automática

Los archivos se generan con nombres claros que identifican el contenido:

| Selección | Tamaño | Archivos generados | Ejemplo |
|---|---|---|---|
| Java | 256 | 1 archivo | `java_256_18-09-00.csv` |
| Python | 512 | 1 archivo | `python_512_18-09-00.csv` |
| Comparación | 64 | 2 archivos (mismo timestamp) | `java_64_18-10-00.csv` + `python_64_18-10-00.csv` |
| Java | Todos | 1 archivo | `java_18-09-00.csv` |
| Comparación | Todos | 2 archivos | `java_18-10-00.csv` + `python_18-10-00.csv` |

### Formato CSV unificado (7 columnas)

```csv
algoritmo,tamaño,caso,tiempo_ns,tiempo_ms,lenguaje,tipo_ejecucion
NaivOnArray,64,1,6067400,6.0674,Java,secuencial
```

| Columna | Tipo | Descripción |
|---|---|---|
| `algoritmo` | String | Nombre del algoritmo |
| `tamaño` | Integer | Dimensión n de la matriz (n×n) |
| `caso` | String | Identificador del caso de prueba |
| `tiempo_ns` | Long | Tiempo en nanosegundos |
| `tiempo_ms` | Double | Tiempo en milisegundos |
| `lenguaje` | String | `Java` o `Python` |
| `tipo_ejecucion` | String | `secuencial` o `concurrente` |

---

## 🔀 Concurrencia

### Dentro de los algoritmos

Los algoritmos paralelos (`ParallelBlock`, `EnhancedParallelBlock`) usan hilos para dividir el trabajo:

| Lenguaje | Mecanismo | Descripción |
|---|---|---|
| Java | `IntStream.parallel()` / `Thread` | Paralelismo real, aprovecha múltiples núcleos |
| Python | `threading.Thread` | Limitado por GIL, pero replica la semántica de hilos de Java |

> **Decisión de diseño:** Se eligió `threading` sobre `multiprocessing` en Python para compartir la matriz resultado sin serialización, replicar fielmente la semántica de Java, y poder observar las diferencias de rendimiento entre lenguajes.

### En el modo Comparación

Cuando el usuario selecciona **Comparación**, el servidor ejecuta Java y Python como **subprocesos independientes en paralelo** usando `threading.Thread` + `subprocess`. Esto logra paralelismo real ya que cada lenguaje corre en su propio proceso del SO.

---

## 🌐 Dashboard Interactivo

### Funcionalidades

| Función | Descripción |
|---|---|
| **Selección de modo** | Tarjetas interactivas para Java, Python o Comparación |
| **Selección de tamaño** | Dropdown con potencias de 2 (2 a 1024) + advertencia para tamaños grandes |
| **Ejecución automática** | Un clic ejecuta los algoritmos y carga los resultados |
| **Filtro por tamaño** | Selector dinámico según los tamaños disponibles |
| **Vista por caso** | Barras agrupadas por caso de prueba |
| **Vista comparativa** | Barras Java vs Python lado a lado (promedio) |
| **Estadísticas** | Algoritmo más eficiente, mejor tiempo por lenguaje |
| **Panel de comparación** | Promedios, mínimos, máximos por lenguaje |
| **Historial** | Lista de archivos CSV anteriores, cargables con un clic |

### Flujo automatizado

1. **Seleccionar** → Java, Python o Comparación
2. **Elegir tamaño** → Potencia de 2 o "Todos" para los predeterminados
3. **Ejecutar** → El servidor lanza los procesos con el tamaño elegido
4. **Visualizar** → Gráficas y estadísticas se muestran automáticamente
5. **No requiere** selección manual de archivos CSV

---

## ⚙️ Configuración

Los parámetros se configuran en los archivos principales:

```java
// src/main/Main.java
private static final int[] MATRIX_SIZES = { 16, 32, 64, 128 };
private static final int NUM_CASES = 2;
private static final int BLOCK_SIZE = 16;
```

```python
# python/main.py
MATRIX_SIZES = [16, 32, 64, 128]
NUM_CASES = 2
BLOCK_SIZE = 16
```

> Ambos archivos deben tener la misma configuración para resultados comparables.

---

## 📐 Casos de Prueba

Las matrices de entrada se almacenan como JSON en `data/test_cases/` y son compartidas entre Java y Python:

- **Formato:** `case_{id}_size_{n}.json`
- **Valores:** Enteros de 6 dígitos (±100,000 a ±999,999)
- **Tamaños:** Potencias de 2 (requerido por Strassen)

---

## 📝 Tecnologías

| Tecnología | Uso |
|---|---|
| Java 11+ | Implementación de algoritmos + concurrencia |
| Python 3.8+ | Implementación de algoritmos + servidor web |
| HTML5/CSS3/JS | Dashboard interactivo |
| Chart.js 4.x | Gráficas de barras |
| http.server (stdlib) | Servidor HTTP (sin dependencias externas) |
| JSON | Persistencia de casos de prueba |
| CSV | Exportación de resultados |

---

## 📖 Documentación Adicional

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — Estructura detallada del proyecto y decisiones de diseño
