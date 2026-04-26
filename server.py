"""
Servidor HTTP integrado para el proyecto de Multiplicación de Matrices.

Sirve la interfaz HTML y proporciona una API REST para ejecutar los algoritmos
en Java y/o Python, generando automáticamente archivos CSV con nombres claros.

Uso:
    python server.py              # Inicia en http://localhost:8080
    python server.py --port 3000  # Puerto personalizado

Endpoints:
    GET  /                    → Dashboard HTML
    GET  /app.js              → JavaScript del dashboard
    GET  /api/results         → Lista archivos CSV disponibles
    GET  /api/results/<file>  → Contenido de un archivo CSV
    POST /api/execute         → Ejecuta algoritmos según modo seleccionado
"""

import http.server
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from urllib.parse import urlparse

# Forzar UTF-8 en la consola de Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(PROJECT_DIR, "data", "results")
JAVA_OUT_DIR = os.path.join(PROJECT_DIR, "out")
PORT = 8080

# Tipos MIME para archivos estáticos
MIME_TYPES = {
    '.html': 'text/html',
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.csv': 'text/csv',
    '.json': 'application/json',
}


class APIHandler(http.server.BaseHTTPRequestHandler):
    """Manejador HTTP para la API REST y archivos estáticos."""

    def log_message(self, format, *args):
        """Override: log compacto."""
        print(f"  [{self.command}] {self.path} → {args[0]}")

    # ── Helpers ──

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_text_file(self, filepath, content_type):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            body = content.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', f'{content_type}; charset=utf-8')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_json({"error": "Archivo no encontrado"}, 404)

    # ── Routing ──

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path in ('/', '/index.html'):
            self.send_text_file(os.path.join(PROJECT_DIR, 'index.html'), 'text/html')
        elif path == '/app.js':
            self.send_text_file(os.path.join(PROJECT_DIR, 'app.js'), 'application/javascript')
        elif path == '/api/results':
            self._handle_list_results()
        elif path.startswith('/api/results/'):
            filename = os.path.basename(path[len('/api/results/'):])
            self._handle_get_result(filename)
        else:
            self.send_json({"error": "Ruta no encontrada"}, 404)

    def do_POST(self):
        if self.path == '/api/execute':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                params = json.loads(body) if body else {}
            except json.JSONDecodeError:
                params = {}
            self._handle_execute(params)
        else:
            self.send_json({"error": "Ruta no encontrada"}, 404)

    # ── API: Listar resultados ──

    def _handle_list_results(self):
        os.makedirs(RESULTS_DIR, exist_ok=True)
        files = []
        for fname in sorted(os.listdir(RESULTS_DIR), reverse=True):
            if fname.endswith('.csv'):
                fpath = os.path.join(RESULTS_DIR, fname)
                files.append({
                    "name": fname,
                    "size": os.path.getsize(fpath),
                    "modified": os.path.getmtime(fpath)
                })
        self.send_json({"files": files})

    # ── API: Obtener archivo CSV ──

    def _handle_get_result(self, filename):
        filepath = os.path.join(RESULTS_DIR, filename)
        if os.path.exists(filepath):
            self.send_text_file(filepath, 'text/csv')
        else:
            self.send_json({"error": f"Archivo '{filename}' no encontrado"}, 404)

    # ── API: Ejecutar algoritmos ──

    def _handle_execute(self, params):
        """
        Ejecuta algoritmos según el modo seleccionado.

        Parámetros del request body:
            mode: 'java' | 'python' | 'comparacion'
            size: tamaño de la matriz (potencia de 2). Si no se envía, usa los predeterminados.
        """
        mode = params.get('mode', 'java')
        size = params.get('size', None)  # None = usar todos los predeterminados
        timestamp = datetime.now().strftime("%H-%M-%S")
        os.makedirs(RESULTS_DIR, exist_ok=True)

        # Construir prefijo de nombre con tamaño si se especificó
        size_tag = f"_{size}" if size else ""

        response = {
            "success": True,
            "mode": mode,
            "size": size,
            "timestamp": timestamp,
            "files": [],
            "data": [],
            "errors": [],
            "timings": {}
        }

        if mode == 'comparacion':
            self._execute_comparison(timestamp, size_tag, size, response)
        elif mode == 'java':
            self._execute_java(timestamp, size_tag, size, response)
        elif mode == 'python':
            self._execute_python(timestamp, size_tag, size, response)
        else:
            response["success"] = False
            response["errors"].append(f"Modo desconocido: {mode}")

        if response["errors"]:
            response["success"] = False

        self.send_json(response)

    def _build_java_cmd(self, filepath, size):
        """Construye el comando para ejecutar Java."""
        cmd = ["java", "-cp", JAVA_OUT_DIR, "main.Main", "--output", filepath]
        if size:
            cmd.extend(["--size", str(size)])
        return cmd

    def _build_python_cmd(self, filepath, size):
        """Construye el comando para ejecutar Python."""
        cmd = [sys.executable, "-m", "python.main", "--output", filepath]
        if size:
            cmd.extend(["--size", str(size)])
        return cmd

    def _execute_java(self, timestamp, size_tag, size, response):
        filename = f"java{size_tag}_{timestamp}.csv"
        filepath = os.path.join(RESULTS_DIR, filename)

        size_info = f" (tamaño {size})" if size else ""
        print(f"  → Ejecutando Java{size_info}...")
        start = time.perf_counter()
        success, stdout, stderr = self._run_process(self._build_java_cmd(filepath, size))
        elapsed = time.perf_counter() - start
        response["timings"]["java"] = round(elapsed, 2)

        if success and os.path.exists(filepath):
            response["files"].append(filename)
            response["data"].extend(self._parse_csv(filepath))
            print(f"  ✓ Java completado en {elapsed:.2f}s → {filename}")
        else:
            response["errors"].append(f"Java falló: {stderr[:500]}")
            print(f"  ✗ Java falló: {stderr[:200]}")

    def _execute_python(self, timestamp, size_tag, size, response):
        filename = f"python{size_tag}_{timestamp}.csv"
        filepath = os.path.join(RESULTS_DIR, filename)

        size_info = f" (tamaño {size})" if size else ""
        print(f"  → Ejecutando Python{size_info}...")
        start = time.perf_counter()
        success, stdout, stderr = self._run_process(self._build_python_cmd(filepath, size))
        elapsed = time.perf_counter() - start
        response["timings"]["python"] = round(elapsed, 2)

        if success and os.path.exists(filepath):
            response["files"].append(filename)
            response["data"].extend(self._parse_csv(filepath))
            print(f"  ✓ Python completado en {elapsed:.2f}s → {filename}")
        else:
            response["errors"].append(f"Python falló: {stderr[:500]}")
            print(f"  ✗ Python falló: {stderr[:200]}")

    def _execute_comparison(self, timestamp, size_tag, size, response):
        """Ejecuta Java y Python concurrentemente para comparación justa."""
        java_filename = f"java{size_tag}_{timestamp}.csv"
        python_filename = f"python{size_tag}_{timestamp}.csv"
        java_path = os.path.join(RESULTS_DIR, java_filename)
        python_path = os.path.join(RESULTS_DIR, python_filename)

        results_holder = {"java": None, "python": None}

        def run_java():
            size_info = f" (tamaño {size})" if size else ""
            print(f"  → Ejecutando Java (comparación){size_info}...")
            start = time.perf_counter()
            success, stdout, stderr = self._run_process(self._build_java_cmd(java_path, size))
            elapsed = time.perf_counter() - start
            results_holder["java"] = (success, stdout, stderr, elapsed)

        def run_python():
            size_info = f" (tamaño {size})" if size else ""
            print(f"  → Ejecutando Python (comparación){size_info}...")
            start = time.perf_counter()
            success, stdout, stderr = self._run_process(self._build_python_cmd(python_path, size))
            elapsed = time.perf_counter() - start
            results_holder["python"] = (success, stdout, stderr, elapsed)

        # Lanzar ambos procesos en paralelo
        t_java = threading.Thread(target=run_java)
        t_python = threading.Thread(target=run_python)
        t_java.start()
        t_python.start()
        t_java.join()
        t_python.join()

        # Procesar resultado Java
        j_success, _, j_stderr, j_elapsed = results_holder["java"]
        response["timings"]["java"] = round(j_elapsed, 2)
        if j_success and os.path.exists(java_path):
            response["files"].append(java_filename)
            response["data"].extend(self._parse_csv(java_path))
            print(f"  ✓ Java completado en {j_elapsed:.2f}s → {java_filename}")
        else:
            response["errors"].append(f"Java falló: {j_stderr[:500]}")

        # Procesar resultado Python
        p_success, _, p_stderr, p_elapsed = results_holder["python"]
        response["timings"]["python"] = round(p_elapsed, 2)
        if p_success and os.path.exists(python_path):
            response["files"].append(python_filename)
            response["data"].extend(self._parse_csv(python_path))
            print(f"  ✓ Python completado en {p_elapsed:.2f}s → {python_filename}")
        else:
            response["errors"].append(f"Python falló: {p_stderr[:500]}")

    # ── Utilidades ──

    def _run_process(self, cmd):
        """Ejecuta un subproceso y retorna (success, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd, cwd=PROJECT_DIR,
                capture_output=True, text=True,
                encoding='utf-8', errors='replace',
                timeout=1800
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Timeout: el proceso excedió 30 minutos"
        except Exception as e:
            return False, "", str(e)

    def _parse_csv(self, filepath):
        """Lee un CSV y lo convierte a lista de diccionarios."""
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if len(lines) < 2:
                return data
            header = lines[0].strip().split(',')
            for line in lines[1:]:
                values = line.strip().split(',')
                if len(values) >= len(header):
                    row = {}
                    for idx, col in enumerate(header):
                        row[col] = values[idx]
                    data.append(row)
        except Exception:
            pass
        return data


def main():
    port = PORT
    if '--port' in sys.argv:
        idx = sys.argv.index('--port')
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   Matrix Multiplication Analytics — Server                  ║")
    print(f"║   http://localhost:{port:<43} ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║   Endpoints:                                                ║")
    print("║     GET  /              → Dashboard                         ║")
    print("║     POST /api/execute   → Ejecutar algoritmos               ║")
    print("║     GET  /api/results   → Listar archivos CSV               ║")
    print("║   Presiona Ctrl+C para detener el servidor                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    server = http.server.HTTPServer(('', port), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor detenido.")
        server.server_close()


if __name__ == '__main__':
    main()
