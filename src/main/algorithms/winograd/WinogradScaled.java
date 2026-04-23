package main.algorithms.winograd;

/**
 * Implementación del algoritmo de Winograd con escalamiento (Scaled).
 *
 * Escala las matrices A y B por su norma infinito antes de aplicar
 * el algoritmo de Winograd Original. Esto mejora la estabilidad numérica
 * al normalizar los valores, especialmente con números grandes (6+ dígitos).
 *
 * El resultado se des-escala al final para obtener el producto correcto.
 */
public class WinogradScaled {

    /**
     * Multiplica dos matrices usando el algoritmo de Winograd con escalamiento.
     *
     * @param A    primera matriz
     * @param B    segunda matriz
     * @param size tamaño de las matrices (n x n)
     * @return resultado de A × B
     */
    public static double[][] winogradScaled(double[][] A, double[][] B, int size) {
        // Calcular factores de escala (norma infinito)
        double normA = infinityNorm(A, size);
        double normB = infinityNorm(B, size);

        // Evitar división por cero
        if (normA == 0 || normB == 0) {
            return new double[size][size];
        }

        // Crear copias escaladas de las matrices
        double[][] scaledA = new double[size][size];
        double[][] scaledB = new double[size][size];

        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                scaledA[i][j] = A[i][j] / normA;
                scaledB[i][j] = B[i][j] / normB;
            }
        }

        // Aplicar Winograd Original a las matrices escaladas
        double[][] scaledResult = WinogradOriginal.winogradOriginal(scaledA, scaledB, size);

        // Des-escalar el resultado: C = (normA * normB) * scaledResult
        double scaleFactor = normA * normB;
        double[][] result = new double[size][size];
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                result[i][j] = scaledResult[i][j] * scaleFactor;
            }
        }

        return result;
    }

    /**
     * Calcula la norma infinito de una matriz (máximo de las sumas absolutas por fila).
     *
     * @param matrix la matriz
     * @param size   tamaño de la matriz
     * @return norma infinito
     */
    private static double infinityNorm(double[][] matrix, int size) {
        double maxRowSum = 0;
        for (int i = 0; i < size; i++) {
            double rowSum = 0;
            for (int j = 0; j < size; j++) {
                rowSum += Math.abs(matrix[i][j]);
            }
            if (rowSum > maxRowSum) {
                maxRowSum = rowSum;
            }
        }
        return maxRowSum;
    }

}
