"""
Punto de entrada principal para la ejecución de algoritmos de multiplicación
de matrices en Python.

Equivalente a Main.java. Lee los mismos casos de prueba JSON generados por Java,
ejecuta los 15 algoritmos y exporta resultados CSV en formato compatible.

Uso:
    python -m python.main [--mode sequential|concurrent]
"""

import os
import sys
import json
import time
from datetime import datetime

# Forzar UTF-8 en la consola de Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from python.utils.timer import Timer
from python.algorithms.naive import naiv_on_array, naiv_loop_unrolling_two, naiv_loop_unrolling_four
from python.algorithms.winograd import winograd_original, winograd_scaled
from python.algorithms.strassen import strassen_naiv, strassen_winograd
from python.algorithms.column_column import cc_sequential_block, cc_parallel_block
from python.algorithms.row_column import rc_sequential_block, rc_parallel_block, rc_enhanced_parallel_block
from python.algorithms.row_row import rr_sequential_block, rr_parallel_block, rr_enhanced_parallel_block


# ===================== CONFIGURACIÓN =====================
MATRIX_SIZES = [16, 32, 64, 128]
NUM_CASES = 2
BLOCK_SIZE = 16
NUM_ALGORITHMS = 15
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEST_CASES_DIR = os.path.join(BASE_DIR, "data", "test_cases")
RESULTS_DIR = os.path.join(BASE_DIR, "data", "results")
# =========================================================


class ResultCollector:
    """Recolector de resultados de ejecución para exportar a CSV."""

    def __init__(self, execution_type="secuencial", custom_path=None):
        self.results = []
        self.execution_type = execution_type
        os.makedirs(RESULTS_DIR, exist_ok=True)
        if custom_path:
            self.filename = custom_path
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.filename = os.path.join(RESULTS_DIR, f"results_python_{timestamp}.csv")

    def add_result(self, algorithm, size, case_id, nanos):
        millis = nanos / 1_000_000.0
        self.results.append({
            "algorithm": algorithm,
            "size": size,
            "case_id": case_id,
            "nanos": nanos,
            "millis": millis,
        })

    def save_all(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("algoritmo,tamaño,caso,tiempo_ns,tiempo_ms,lenguaje,tipo_ejecucion\n")
            for r in self.results:
                f.write(f"{r['algorithm']},{r['size']},{r['case_id']},"
                        f"{r['nanos']},{r['millis']:.4f},"
                        f"Python,{self.execution_type}\n")
        print(f"\n[OK] Resultados guardados en: {self.filename}")

    def get_result_count(self):
        return len(self.results)


def load_test_case(size, case_id):
    """
    Carga un caso de prueba (par de matrices A y B) desde un archivo JSON.
    Usa los mismos archivos generados por Java para garantizar comparabilidad.
    """
    filename = os.path.join(TEST_CASES_DIR, f"case_{case_id}_size_{size}.json")
    if not os.path.exists(filename):
        return None

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    data = json.loads(content)
    A = data["matrixA"]
    B = data["matrixB"]

    # Convertir a float (por si vienen como int)
    A = [[float(val) for val in row] for row in A]
    B = [[float(val) for val in row] for row in B]

    return A, B


def generate_and_save_matrices(size, case_id):
    """Genera matrices aleatorias y las guarda en JSON (compatibles con Java)."""
    import random

    MIN_VALUE = 100000
    MAX_VALUE = 999999

    def generate_matrix(n):
        matrix = []
        for _ in range(n):
            row = []
            for _ in range(n):
                value = random.randint(MIN_VALUE, MAX_VALUE)
                if random.random() < 0.5:
                    value = -value
                row.append(float(value))
            matrix.append(row)
        return matrix

    A = generate_matrix(size)
    B = generate_matrix(size)

    # Guardar en JSON
    os.makedirs(TEST_CASES_DIR, exist_ok=True)
    filename = os.path.join(TEST_CASES_DIR, f"case_{case_id}_size_{size}.json")
    data = {
        "size": size,
        "caseId": case_id,
        "matrixA": A,
        "matrixB": B
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"  [OK] Caso guardado: {filename}")
    return A, B


def run_algorithm(name, size, case_id, timer, collector, algorithm_fn):
    """Ejecuta un algoritmo, mide su tiempo y registra el resultado."""
    timer.reset()
    timer.start()
    algorithm_fn()
    timer.stop()

    nanos = timer.get_elapsed_nanos()
    millis = timer.get_elapsed_millis()

    collector.add_result(name, size, case_id, nanos)
    print(f"    {name:<30} → {millis:>12.4f} ms")


def main(execution_type="secuencial", output_path=None):
    """Función principal que ejecuta todos los algoritmos."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   ANÁLISIS DE ALGORITMOS — PYTHON                          ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print(f"║   Tamaños: {str(MATRIX_SIZES):<49} ║")
    print(f"║   Casos por tamaño: {NUM_CASES:<40} ║")
    print(f"║   Algoritmos: {NUM_ALGORITHMS:<46} ║")
    total_exec = len(MATRIX_SIZES) * NUM_CASES * NUM_ALGORITHMS
    print(f"║   Total de ejecuciones: {total_exec:<36} ║")
    print(f"║   Tipo de ejecución: {execution_type:<39} ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    timer = Timer()
    collector = ResultCollector(execution_type, output_path)
    global_start = time.perf_counter_ns()

    for size in MATRIX_SIZES:
        print("━" * 62)
        print(f"  TAMAÑO DE MATRIZ: {size} x {size}")
        print("━" * 62)

        for case_num in range(1, NUM_CASES + 1):
            case_id = str(case_num)
            print(f"\n  ▶ Caso de prueba #{case_num} (tamaño {size})")

            # Cargar o generar matrices
            result = load_test_case(size, case_id)
            if result:
                print("    Cargando caso existente...")
                A, B = result
            else:
                print("    Generando matrices nuevas...")
                A, B = generate_and_save_matrices(size, case_id)

            print("    Ejecutando algoritmos...\n")

            # ============ ALGORITMOS NAIVE ============
            run_algorithm("NaivOnArray", size, case_id, timer, collector,
                          lambda: naiv_on_array(A, B, size))

            run_algorithm("NaivLoopUnrollingTwo", size, case_id, timer, collector,
                          lambda: naiv_loop_unrolling_two(A, B, size))

            run_algorithm("NaivLoopUnrollingFour", size, case_id, timer, collector,
                          lambda: naiv_loop_unrolling_four(A, B, size))

            # ============ ALGORITMOS WINOGRAD ============
            run_algorithm("WinogradOriginal", size, case_id, timer, collector,
                          lambda: winograd_original(A, B, size))

            run_algorithm("WinogradScaled", size, case_id, timer, collector,
                          lambda: winograd_scaled(A, B, size))

            # ============ ALGORITMOS STRASSEN ============
            run_algorithm("StrassenNaiv", size, case_id, timer, collector,
                          lambda: strassen_naiv(A, B))

            run_algorithm("StrassenWinograd", size, case_id, timer, collector,
                          lambda: strassen_winograd(A, B))

            # ============ BLOCK COLUMN-COLUMN ============
            run_algorithm("CC_SequentialBlock", size, case_id, timer, collector,
                          lambda: cc_sequential_block(A, B, size, BLOCK_SIZE))

            run_algorithm("CC_ParallelBlock", size, case_id, timer, collector,
                          lambda: cc_parallel_block(A, B, size, BLOCK_SIZE))

            # ============ BLOCK ROW-COLUMN ============
            run_algorithm("RC_SequentialBlock", size, case_id, timer, collector,
                          lambda: rc_sequential_block(A, B, size, BLOCK_SIZE))

            run_algorithm("RC_ParallelBlock", size, case_id, timer, collector,
                          lambda: rc_parallel_block(A, B, size, BLOCK_SIZE))

            run_algorithm("RC_EnhancedParallelBlock", size, case_id, timer, collector,
                          lambda: rc_enhanced_parallel_block(A, B, size, BLOCK_SIZE))

            # ============ BLOCK ROW-ROW ============
            run_algorithm("RR_SequentialBlock", size, case_id, timer, collector,
                          lambda: rr_sequential_block(A, B, size, BLOCK_SIZE))

            run_algorithm("RR_ParallelBlock", size, case_id, timer, collector,
                          lambda: rr_parallel_block(A, B, size, BLOCK_SIZE))

            run_algorithm("RR_EnhancedParallelBlock", size, case_id, timer, collector,
                          lambda: rr_enhanced_parallel_block(A, B, size, BLOCK_SIZE))

    # Guardar resultados
    print("\n" + "━" * 62)
    print("  GUARDANDO RESULTADOS")
    print("━" * 62)

    collector.save_all()

    global_end = time.perf_counter_ns()
    total_seconds = (global_end - global_start) / 1_000_000_000.0

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print(f"║   Total de ejecuciones registradas: {collector.get_result_count():<24} ║")
    print(f"║   Tiempo total de ejecución: {total_seconds:<31.2f} s ║")
    print(f"║   Archivos generados en: data/results/                      ║")
    print("╚══════════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    exec_type = "secuencial"
    out_path = None
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--mode" and i + 1 < len(sys.argv):
            exec_type = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            out_path = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    main(exec_type, out_path)
