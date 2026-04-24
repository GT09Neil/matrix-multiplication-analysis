package main;

import main.utils.MatrixGenerator;
import main.utils.Timer;
import main.persistence.TestCaseRepository;
import main.persistence.ExecutionResultRepository;
import main.persistence.ChartDataExporter;

// Algoritmos naive
import main.algorithms.naive.NaivOnArray;
import main.algorithms.naive.NaivLoopUnrollingTwo;
import main.algorithms.naive.NaivLoopUnrollingFour;

// Algoritmos Strassen
import main.algorithms.strassen.StrassenNaiv;
import main.algorithms.strassen.StrassenWinograd;

// Algoritmos Winograd
import main.algorithms.winograd.WinogradOriginal;
import main.algorithms.winograd.WinogradScaled;

import java.util.Locale;

/**
 * Clase principal que ejecuta todos los algoritmos de multiplicación de matrices,
 * mide sus tiempos y guarda los resultados.
 *
 * Genera 2 casos de prueba por cada tamaño de matriz y ejecuta los 15 algoritmos
 * con los mismos datos para garantizar una comparación justa.
 *
 * Algoritmos evaluados:
 * - 3 Naive: OnArray, LoopUnrolling×2, LoopUnrolling×4
 * - 2 Winograd: Original, Scaled
 * - 2 Strassen: Naiv, Winograd
 * - 2 Column-Column: SequentialBlock, ParallelBlock
 * - 3 Row-Column: SequentialBlock, ParallelBlock, EnhancedParallelBlock
 * - 3 Row-Row: SequentialBlock, ParallelBlock, EnhancedParallelBlock
 */
public class Main {

    // ===================== CONFIGURACIÓN =====================
    // Tamaños de matrices a evaluar (deben ser potencias de 2 para Strassen)
    private static final int[] MATRIX_SIZES = { 16, 32, 64, 128 };

    // Número de casos de prueba por tamaño
    private static final int NUM_CASES = 2;

    // Tamaño de bloque para algoritmos de bloque
    private static final int BLOCK_SIZE = 16;

    // Número total de algoritmos
    private static final int NUM_ALGORITHMS = 15;

    // =========================================================

    public static void main(String[] args) {
        // Parsear argumentos opcionales
        String outputFile = null;
        for (int i = 0; i < args.length; i++) {
            if ("--output".equals(args[i]) && i + 1 < args.length) {
                outputFile = args[i + 1];
            }
        }

        System.out.println("╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║   ANÁLISIS DE ALGORITMOS DE MULTIPLICACIÓN DE MATRICES      ║");
        System.out.println("╠══════════════════════════════════════════════════════════════╣");
        System.out.printf( "║   Tamaños: %-49s ║%n", java.util.Arrays.toString(MATRIX_SIZES));
        System.out.printf( "║   Casos por tamaño: %-40d ║%n", NUM_CASES);
        System.out.printf( "║   Algoritmos: %-46d ║%n", NUM_ALGORITHMS);
        System.out.printf( "║   Total de ejecuciones: %-36d ║%n",
                MATRIX_SIZES.length * NUM_CASES * NUM_ALGORITHMS);
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        System.out.println();

        MatrixGenerator generator = new MatrixGenerator();
        TestCaseRepository testCaseRepo = new TestCaseRepository();
        ExecutionResultRepository resultRepo = outputFile != null
                ? new ExecutionResultRepository("secuencial", outputFile)
                : new ExecutionResultRepository();
        ChartDataExporter chartExporter = new ChartDataExporter();
        Timer timer = new Timer();

        long globalStart = System.nanoTime();

        for (int size : MATRIX_SIZES) {
            System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            System.out.printf("  TAMAÑO DE MATRIZ: %d x %d%n", size, size);
            System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

            for (int caseNum = 1; caseNum <= NUM_CASES; caseNum++) {
                String caseId = String.valueOf(caseNum);
                System.out.printf("%n  ▶ Caso de prueba #%d (tamaño %d)%n", caseNum, size);

                // Generar o cargar matrices
                double[][] A, B;
                if (testCaseRepo.exists(size, caseId)) {
                    System.out.println("    Cargando caso existente...");
                    double[][][] matrices = testCaseRepo.load(size, caseId);
                    A = matrices[0];
                    B = matrices[1];
                } else {
                    System.out.println("    Generando matrices nuevas...");
                    double[][][] pair = generator.generatePair(size);
                    A = pair[0];
                    B = pair[1];
                    testCaseRepo.save(A, B, size, caseId);
                }

                System.out.println("    Ejecutando algoritmos...\n");

                // ============ ALGORITMOS NAIVE ============
                runAlgorithm("NaivOnArray", size, caseId, timer, resultRepo, chartExporter,
                    () -> NaivOnArray.naivOnArray(A, B, size));

                runAlgorithm("NaivLoopUnrollingTwo", size, caseId, timer, resultRepo, chartExporter,
                    () -> NaivLoopUnrollingTwo.naivLoopUnrollingTwo(A, B, size));

                runAlgorithm("NaivLoopUnrollingFour", size, caseId, timer, resultRepo, chartExporter,
                    () -> NaivLoopUnrollingFour.naivLoopUnrollingFour(A, B, size));

                // ============ ALGORITMOS WINOGRAD ============
                runAlgorithm("WinogradOriginal", size, caseId, timer, resultRepo, chartExporter,
                    () -> WinogradOriginal.winogradOriginal(A, B, size));

                runAlgorithm("WinogradScaled", size, caseId, timer, resultRepo, chartExporter,
                    () -> WinogradScaled.winogradScaled(A, B, size));

                // ============ ALGORITMOS STRASSEN ============
                runAlgorithm("StrassenNaiv", size, caseId, timer, resultRepo, chartExporter,
                    () -> StrassenNaiv.strassenNaiv(A, B));

                runAlgorithm("StrassenWinograd", size, caseId, timer, resultRepo, chartExporter,
                    () -> StrassenWinograd.strassenWinograd(A, B));

                // ============ BLOCK COLUMN-COLUMN ============
                runAlgorithm("CC_SequentialBlock", size, caseId, timer, resultRepo, chartExporter,
                    () -> main.algorithms.column_column.SequentialBlock.columnColumnSequentialBlock(A, B, size, BLOCK_SIZE));

                runAlgorithm("CC_ParallelBlock", size, caseId, timer, resultRepo, chartExporter,
                    () -> main.algorithms.column_column.ParallelBlock.columnColumnParallelBlock(A, B, size, BLOCK_SIZE));

                // ============ BLOCK ROW-COLUMN ============
                runAlgorithm("RC_SequentialBlock", size, caseId, timer, resultRepo, chartExporter,
                    () -> main.algorithms.row_column.SequentialBlock.rowColumnSequentialBlock(A, B, size, BLOCK_SIZE));

                runAlgorithm("RC_ParallelBlock", size, caseId, timer, resultRepo, chartExporter,
                    () -> main.algorithms.row_column.ParallelBlock.rowColumnParallelBlock(A, B, size, BLOCK_SIZE));

                runAlgorithm("RC_EnhancedParallelBlock", size, caseId, timer, resultRepo, chartExporter,
                    () -> main.algorithms.row_column.EnhancedParallelBlock.rowColumnEnhancedParallelBlock(A, B, size, BLOCK_SIZE));

                // ============ BLOCK ROW-ROW ============
                runAlgorithm("RR_SequentialBlock", size, caseId, timer, resultRepo, chartExporter,
                    () -> main.algorithms.row_row.SequentialBlock.rowRowSequentialBlock(A, B, size, BLOCK_SIZE));

                runAlgorithm("RR_ParallelBlock", size, caseId, timer, resultRepo, chartExporter,
                    () -> main.algorithms.row_row.ParallelBlock.rowRowParallelBlock(A, B, size, BLOCK_SIZE));

                runAlgorithm("RR_EnhancedParallelBlock", size, caseId, timer, resultRepo, chartExporter,
                    () -> main.algorithms.row_row.EnhancedParallelBlock.rowRowEnhancedParallelBlock(A, B, size, BLOCK_SIZE));
            }
        }

        // Guardar resultados
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("  GUARDANDO RESULTADOS");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        resultRepo.saveAll();
        chartExporter.exportPivotTable();
        chartExporter.exportSummary();

        long globalEnd = System.nanoTime();
        double totalSeconds = (globalEnd - globalStart) / 1_000_000_000.0;

        System.out.println("\n╔══════════════════════════════════════════════════════════════╗");
        System.out.printf("║   Total de ejecuciones registradas: %-24d ║%n", resultRepo.getResultCount());
        System.out.printf(Locale.US, "║   Tiempo total de ejecución: %-31.2f s ║%n", totalSeconds);
        System.out.println("║   Archivos generados en: data/results/                      ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
    }

    /**
     * Ejecuta un algoritmo, mide su tiempo y registra el resultado.
     *
     * @param name        nombre del algoritmo
     * @param size        tamaño de las matrices
     * @param caseId      identificador del caso de prueba
     * @param timer       instancia de Timer para medir tiempo
     * @param resultRepo  repositorio de resultados CSV
     * @param chartExporter exportador de datos para gráficos
     * @param algorithm   algoritmo a ejecutar (como Runnable)
     */
    private static void runAlgorithm(
            String name,
            int size,
            String caseId,
            Timer timer,
            ExecutionResultRepository resultRepo,
            ChartDataExporter chartExporter,
            Runnable algorithm) {

        timer.reset();
        timer.start();
        algorithm.run();
        timer.stop();

        long nanos = timer.getElapsedNanos();
        double millis = timer.getElapsedMillis();

        resultRepo.addResult(name, size, caseId, nanos);
        chartExporter.addResult(name, size, caseId, nanos);

        System.out.printf(Locale.US, "    %-30s → %12.4f ms%n", name, millis);
    }

}
