package main.persistence;

import java.io.*;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Exportador de datos listos para graficar.
 * Genera archivos CSV optimizados para importar en herramientas de gráficos
 * como Excel, Google Sheets, Python (matplotlib/pandas), o R.
 *
 * Formatos de exportación:
 * 1. Tabla pivote: columnas = algoritmos, filas = tamaños (promedios)
 * 2. Resumen estadístico: promedio, mínimo, máximo por algoritmo y tamaño
 *
 * NOTA: Usa Locale.US para forzar punto decimal en CSV.
 */
public class ChartDataExporter {

    private static final String BASE_DIR = "data/results";

    /**
     * Representa un resultado individual de ejecución.
     */
    public static class Result {
        public final String algorithm;
        public final int size;
        public final String caseId;
        public final long nanos;
        public final double millis;

        public Result(String algorithm, int size, String caseId, long nanos) {
            this.algorithm = algorithm;
            this.size = size;
            this.caseId = caseId;
            this.nanos = nanos;
            this.millis = nanos / 1_000_000.0;
        }
    }

    private final List<Result> results = new ArrayList<>();

    /**
     * Agrega un resultado de ejecución.
     *
     * @param algorithm nombre del algoritmo
     * @param size      tamaño de la matriz
     * @param caseId    identificador del caso
     * @param nanos     tiempo en nanosegundos
     */
    public void addResult(String algorithm, int size, String caseId, long nanos) {
        results.add(new Result(algorithm, size, caseId, nanos));
    }

    /**
     * Exporta una tabla pivote donde:
     * - Filas = tamaños de matriz
     * - Columnas = algoritmos
     * - Valores = tiempo promedio en milisegundos
     *
     * Ideal para graficar en Excel/Google Sheets con gráficos de líneas.
     */
    public void exportPivotTable() {
        if (results.isEmpty()) {
            System.out.println("No hay resultados para exportar.");
            return;
        }

        // Obtener algoritmos y tamaños únicos (ordenados)
        TreeSet<String> algorithms = new TreeSet<>();
        TreeSet<Integer> sizes = new TreeSet<>();
        Map<String, List<Double>> groupedData = new HashMap<>();

        for (Result r : results) {
            algorithms.add(r.algorithm);
            sizes.add(r.size);
            String key = r.algorithm + "_" + r.size;
            groupedData.computeIfAbsent(key, k -> new ArrayList<>()).add(r.millis);
        }

        // Generar archivo
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss"));
        String filename = BASE_DIR + "/chart_pivot_" + timestamp + ".csv";

        try (PrintWriter writer = new PrintWriter(new FileWriter(filename))) {
            // Header
            writer.print("tamaño");
            for (String algo : algorithms) {
                writer.print("," + algo);
            }
            writer.println();

            // Datos (promedio por tamaño y algoritmo)
            for (int size : sizes) {
                writer.print(size);
                for (String algo : algorithms) {
                    String key = algo + "_" + size;
                    List<Double> times = groupedData.get(key);
                    if (times != null && !times.isEmpty()) {
                        double avg = times.stream().mapToDouble(Double::doubleValue).average().orElse(0);
                        writer.print(String.format(Locale.US, ",%.4f", avg));
                    } else {
                        writer.print(",");
                    }
                }
                writer.println();
            }

            System.out.println("[OK] Tabla pivote exportada: " + filename);
        } catch (IOException e) {
            System.err.println("Error exportando tabla pivote: " + e.getMessage());
        }
    }

    /**
     * Exporta un resumen con estadísticas por algoritmo y tamaño.
     * Formato: algoritmo, tamaño, promedio_ms, min_ms, max_ms, num_ejecuciones
     *
     * Ideal para análisis estadístico y reportes.
     */
    public void exportSummary() {
        if (results.isEmpty()) {
            System.out.println("No hay resultados para exportar.");
            return;
        }

        Map<String, List<Double>> groupedData = new LinkedHashMap<>();
        for (Result r : results) {
            String key = r.algorithm + "," + r.size;
            groupedData.computeIfAbsent(key, k -> new ArrayList<>()).add(r.millis);
        }

        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss"));
        String filename = BASE_DIR + "/chart_summary_" + timestamp + ".csv";

        try (PrintWriter writer = new PrintWriter(new FileWriter(filename))) {
            writer.println("algoritmo,tamaño,promedio_ms,min_ms,max_ms,num_ejecuciones");

            for (Map.Entry<String, List<Double>> entry : groupedData.entrySet()) {
                String key = entry.getKey();
                List<Double> times = entry.getValue();

                double avg = times.stream().mapToDouble(Double::doubleValue).average().orElse(0);
                double min = times.stream().mapToDouble(Double::doubleValue).min().orElse(0);
                double max = times.stream().mapToDouble(Double::doubleValue).max().orElse(0);

                // Locale.US para punto decimal
                writer.printf(Locale.US, "%s,%.4f,%.4f,%.4f,%d%n", key, avg, min, max, times.size());
            }

            System.out.println("[OK] Resumen estadístico exportado: " + filename);
        } catch (IOException e) {
            System.err.println("Error exportando resumen: " + e.getMessage());
        }
    }

}
