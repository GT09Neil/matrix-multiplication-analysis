package main.persistence;

import java.io.*;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Repositorio para guardar resultados de ejecución de algoritmos en formato CSV.
 *
 * Formato: algoritmo, tamaño, caso, tiempo_ns, tiempo_ms, lenguaje, tipo_ejecucion
 * Los archivos se guardan en data/results/.
 *
 * NOTA: Usa Locale.US para evitar problemas con separadores decimales
 * en locales que usan coma (ej: español), ya que la coma es el delimitador CSV.
 */
public class ExecutionResultRepository {

    private static final String BASE_DIR = "data/results";
    private static final String CSV_HEADER = "algoritmo,tamaño,caso,tiempo_ns,tiempo_ms,lenguaje,tipo_ejecucion";

    private final String filename;
    private final List<String> results;
    private final String executionType;

    public ExecutionResultRepository() {
        this("secuencial");
    }

    public ExecutionResultRepository(String executionType) {
        this.executionType = executionType;

        // Crear directorio si no existe
        try {
            Files.createDirectories(Paths.get(BASE_DIR));
        } catch (IOException e) {
            System.err.println("Error creando directorio de resultados: " + e.getMessage());
        }

        // Generar nombre de archivo con timestamp
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss"));
        this.filename = BASE_DIR + "/results_java_" + timestamp + ".csv";
        this.results = new ArrayList<>();
    }

    /**
     * Constructor con ruta de archivo personalizada.
     * Usado por el servidor para controlar la nomenclatura de los archivos.
     *
     * @param executionType tipo de ejecución
     * @param customPath    ruta completa del archivo de salida
     */
    public ExecutionResultRepository(String executionType, String customPath) {
        this.executionType = executionType;
        this.filename = customPath;
        this.results = new ArrayList<>();

        try {
            Path parent = Paths.get(customPath).getParent();
            if (parent != null) {
                Files.createDirectories(parent);
            }
        } catch (IOException e) {
            System.err.println("Error creando directorio de resultados: " + e.getMessage());
        }
    }

    /**
     * Agrega un resultado de ejecución.
     *
     * @param algorithm nombre del algoritmo
     * @param size      tamaño de la matriz
     * @param caseId    identificador del caso de prueba
     * @param nanos     tiempo de ejecución en nanosegundos
     */
    public void addResult(String algorithm, int size, String caseId, long nanos) {
        double millis = nanos / 1_000_000.0;
        // Locale.US para forzar punto decimal (no coma) en el CSV
        String line = String.format(Locale.US, "%s,%d,%s,%d,%.4f,Java,%s",
                algorithm, size, caseId, nanos, millis, executionType);
        results.add(line);
    }

    /**
     * Guarda todos los resultados acumulados en el archivo CSV.
     */
    public void saveAll() {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filename))) {
            writer.println(CSV_HEADER);
            for (String line : results) {
                writer.println(line);
            }
            System.out.println("\n[OK] Resultados guardados en: " + filename);
        } catch (IOException e) {
            System.err.println("Error guardando resultados: " + e.getMessage());
        }
    }

    /**
     * Obtiene la ruta del archivo de resultados.
     */
    public String getFilename() {
        return filename;
    }

    /**
     * Obtiene la cantidad de resultados registrados.
     */
    public int getResultCount() {
        return results.size();
    }

}
