"""
Timer de alta precisión para medir tiempos de ejecución.

Equivalente a la clase Timer.java, usa time.perf_counter_ns()
que es el equivalente más preciso a System.nanoTime() en Python.
"""

import time


class Timer:
    """Clase para medir el tiempo de ejecución de algoritmos."""

    def __init__(self):
        self._start_time = 0
        self._end_time = 0
        self._running = False

    def start(self):
        """Inicia la medición de tiempo."""
        self._start_time = time.perf_counter_ns()
        self._running = True

    def stop(self):
        """Detiene la medición de tiempo."""
        if not self._running:
            raise RuntimeError("El timer no está corriendo. Llame start() primero.")
        self._end_time = time.perf_counter_ns()
        self._running = False

    def get_elapsed_nanos(self):
        """Obtiene el tiempo transcurrido en nanosegundos."""
        if self._running:
            return time.perf_counter_ns() - self._start_time
        return self._end_time - self._start_time

    def get_elapsed_millis(self):
        """Obtiene el tiempo transcurrido en milisegundos."""
        return self.get_elapsed_nanos() / 1_000_000.0

    def get_elapsed_seconds(self):
        """Obtiene el tiempo transcurrido en segundos."""
        return self.get_elapsed_nanos() / 1_000_000_000.0

    def reset(self):
        """Reinicia el timer a su estado inicial."""
        self._start_time = 0
        self._end_time = 0
        self._running = False

    def measure(self, task):
        """
        Mide el tiempo de ejecución de una función (callable).

        Args:
            task: función sin argumentos a medir
        Returns:
            tiempo en nanosegundos
        """
        self.reset()
        self.start()
        task()
        self.stop()
        return self.get_elapsed_nanos()

    def __str__(self):
        return f"{self.get_elapsed_millis():.4f} ms ({self.get_elapsed_seconds():.2f} s)"
