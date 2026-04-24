"""
Orquestador de ejecución simultánea Java + Python.

Lanza ambos procesos en paralelo usando hilos o subprocesos,
permitiendo medir el rendimiento de cada lenguaje bajo condiciones
de ejecución similares (mismos datos de entrada, mismo momento de inicio).

Uso:
    python orchestrator.py                      # Ejecución simultánea (concurrente)
    python orchestrator.py --mode sequential    # Ejecución secuencial (primero Java, luego Python)
    python orchestrator.py --mode concurrent    # Ejecución simultánea (por defecto)
"""

import subprocess
import threading
import time
import os
import sys
from datetime import datetime

# Forzar UTF-8 en la consola de Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


# Directorio raíz del proyecto
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(PROJECT_DIR, "data", "results")

# Comandos para cada lenguaje
JAVA_CMD = ["java", "-cp", os.path.join(PROJECT_DIR, "out"), "main.Main"]
PYTHON_CMD = [sys.executable, "-m", "python.main"]


class LanguageRunner:
    """Ejecuta un proceso de un lenguaje y captura su salida y tiempo."""

    def __init__(self, name, cmd, cwd, exec_type="secuencial"):
        self.name = name
        self.cmd = cmd
        self.cwd = cwd
        self.exec_type = exec_type
        self.elapsed_ns = 0
        self.elapsed_ms = 0.0
        self.return_code = None
        self.output = ""
        self.error = ""

    def run(self):
        """Ejecuta el proceso y mide el tiempo total."""
        print(f"\n  🚀 Iniciando {self.name}...")

        start = time.perf_counter_ns()
        try:
            # Para Python, pasar el modo de ejecución
            cmd = list(self.cmd)
            if self.name == "Python":
                cmd.extend(["--mode", self.exec_type])

            result = subprocess.run(
                cmd,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            self.return_code = result.returncode
            self.output = result.stdout
            self.error = result.stderr
        except Exception as e:
            self.return_code = -1
            self.error = str(e)

        end = time.perf_counter_ns()
        self.elapsed_ns = end - start
        self.elapsed_ms = self.elapsed_ns / 1_000_000.0

        status = "✅" if self.return_code == 0 else "❌"
        print(f"  {status} {self.name} finalizado en {self.elapsed_ms:.2f} ms "
              f"(código: {self.return_code})")


def run_sequential():
    """Ejecuta Java y luego Python de forma secuencial."""
    print("\n" + "═" * 62)
    print("  MODO: SECUENCIAL (Java → Python)")
    print("═" * 62)

    java_runner = LanguageRunner("Java", JAVA_CMD, PROJECT_DIR, "secuencial")
    python_runner = LanguageRunner("Python", PYTHON_CMD, PROJECT_DIR, "secuencial")

    java_runner.run()
    print_output(java_runner)

    python_runner.run()
    print_output(python_runner)

    return java_runner, python_runner


def run_concurrent():
    """Ejecuta Java y Python de forma simultánea usando hilos."""
    print("\n" + "═" * 62)
    print("  MODO: CONCURRENTE (Java ∥ Python)")
    print("═" * 62)

    java_runner = LanguageRunner("Java", JAVA_CMD, PROJECT_DIR, "concurrente")
    python_runner = LanguageRunner("Python", PYTHON_CMD, PROJECT_DIR, "concurrente")

    # Crear hilos para ejecución simultánea
    java_thread = threading.Thread(target=java_runner.run, name="JavaRunner")
    python_thread = threading.Thread(target=python_runner.run, name="PythonRunner")

    # Lanzar ambos al mismo tiempo
    java_thread.start()
    python_thread.start()

    # Esperar a que ambos terminen
    java_thread.join()
    python_thread.join()

    print_output(java_runner)
    print_output(python_runner)

    return java_runner, python_runner


def print_output(runner):
    """Imprime la salida de un runner."""
    if runner.output:
        print(f"\n  ── Salida de {runner.name} ──")
        for line in runner.output.strip().split("\n"):
            print(f"  │ {line}")
    if runner.error and runner.return_code != 0:
        print(f"\n  ── Errores de {runner.name} ──")
        for line in runner.error.strip().split("\n"):
            print(f"  │ ⚠ {line}")


def save_comparison_report(java_runner, python_runner, mode):
    """Genera un CSV comparativo con los tiempos globales de ambos lenguajes."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(RESULTS_DIR, f"comparison_{mode}_{timestamp}.csv")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("lenguaje,tiempo_total_ms,tiempo_total_s,modo,codigo_retorno,timestamp\n")
        for runner in [java_runner, python_runner]:
            seconds = runner.elapsed_ns / 1_000_000_000.0
            f.write(f"{runner.name},{runner.elapsed_ms:.4f},{seconds:.4f},"
                    f"{mode},{runner.return_code},{timestamp}\n")

    print(f"\n  [OK] Reporte comparativo: {filename}")


def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   ORQUESTADOR — MULTIPLICACIÓN DE MATRICES                 ║")
    print("║   Ejecución simultánea Java + Python                       ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    # Determinar modo
    mode = "concurrent"
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]

    global_start = time.perf_counter_ns()

    if mode == "sequential":
        java_runner, python_runner = run_sequential()
    else:
        java_runner, python_runner = run_concurrent()

    global_end = time.perf_counter_ns()
    global_ms = (global_end - global_start) / 1_000_000.0
    global_s = (global_end - global_start) / 1_000_000_000.0

    # Guardar reporte comparativo
    save_comparison_report(java_runner, python_runner, mode)

    # Resumen final
    print("\n" + "═" * 62)
    print("  RESUMEN DE EJECUCIÓN")
    print("═" * 62)
    print(f"  Modo:                {mode}")
    print(f"  Java:                {java_runner.elapsed_ms:.2f} ms ({java_runner.elapsed_ns / 1e9:.2f} s)")
    print(f"  Python:              {python_runner.elapsed_ms:.2f} ms ({python_runner.elapsed_ns / 1e9:.2f} s)")
    print(f"  Tiempo total:        {global_ms:.2f} ms ({global_s:.2f} s)")

    if java_runner.elapsed_ms > 0 and python_runner.elapsed_ms > 0:
        ratio = python_runner.elapsed_ms / java_runner.elapsed_ms
        faster = "Java" if ratio > 1 else "Python"
        print(f"  Ratio Python/Java:   {ratio:.2f}x ({faster} es más rápido)")

    print("═" * 62)


if __name__ == "__main__":
    main()
