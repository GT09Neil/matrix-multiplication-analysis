package main.utils;

/**
 * Clase para medir el tiempo de ejecución de algoritmos.
 * Utiliza System.nanoTime() para máxima precisión.
 *
 * Uso típico:
 * <pre>
 *   Timer timer = new Timer();
 *   timer.start();
 *   // ... ejecutar algoritmo ...
 *   timer.stop();
 *   System.out.println("Tiempo: " + timer.getElapsedMillis() + " ms");
 * </pre>
 */
public class Timer {

    private long startTime;
    private long endTime;
    private boolean running;

    /**
     * Inicia la medición de tiempo.
     * Si el timer ya estaba corriendo, reinicia la medición.
     */
    public void start() {
        this.startTime = System.nanoTime();
        this.running = true;
    }

    /**
     * Detiene la medición de tiempo.
     *
     * @throws IllegalStateException si el timer no estaba corriendo
     */
    public void stop() {
        if (!running) {
            throw new IllegalStateException("El timer no está corriendo. Llame start() primero.");
        }
        this.endTime = System.nanoTime();
        this.running = false;
    }

    /**
     * Obtiene el tiempo transcurrido en nanosegundos.
     *
     * @return tiempo en nanosegundos
     */
    public long getElapsedNanos() {
        if (running) {
            return System.nanoTime() - startTime;
        }
        return endTime - startTime;
    }

    /**
     * Obtiene el tiempo transcurrido en milisegundos.
     *
     * @return tiempo en milisegundos (con precisión de nanosegundos)
     */
    public double getElapsedMillis() {
        return getElapsedNanos() / 1_000_000.0;
    }

    /**
     * Obtiene el tiempo transcurrido en segundos.
     *
     * @return tiempo en segundos
     */
    public double getElapsedSeconds() {
        return getElapsedNanos() / 1_000_000_000.0;
    }

    /**
     * Reinicia el timer a su estado inicial.
     */
    public void reset() {
        this.startTime = 0;
        this.endTime = 0;
        this.running = false;
    }

    /**
     * Mide el tiempo de ejecución de un Runnable.
     * Método de conveniencia para medir cualquier bloque de código.
     *
     * @param task la tarea a medir
     * @return tiempo en nanosegundos
     */
    public long measure(Runnable task) {
        reset();
        start();
        task.run();
        stop();
        return getElapsedNanos();
    }

    @Override
    public String toString() {
        return String.format("%.4f ms (%.2f s)", getElapsedMillis(), getElapsedSeconds());
    }

}
