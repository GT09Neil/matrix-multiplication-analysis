package main.utils;

import java.util.Random;

/**
 * Generador de matrices cuadradas n x n con valores aleatorios.
 * Los valores generados tienen al menos 6 dígitos (entre 100000 y 999999).
 *
 * Soporta generación reproducible mediante semilla (seed).
 */
public class MatrixGenerator {

    private static final int MIN_VALUE = 100000;  // 6 dígitos mínimo
    private static final int MAX_VALUE = 999999;  // 6 dígitos máximo

    private final Random random;

    /**
     * Constructor con semilla aleatoria.
     */
    public MatrixGenerator() {
        this.random = new Random();
    }

    /**
     * Constructor con semilla fija para reproducibilidad.
     *
     * @param seed semilla para el generador aleatorio
     */
    public MatrixGenerator(long seed) {
        this.random = new Random(seed);
    }

    /**
     * Genera una matriz n x n con valores aleatorios de al menos 6 dígitos.
     * Los valores pueden ser positivos o negativos.
     *
     * @param n tamaño de la matriz (n x n), debe ser mayor a 0
     * @return matriz generada
     * @throws IllegalArgumentException si n es menor o igual a 0
     */
    public double[][] generate(int n) {
        if (n <= 0) {
            throw new IllegalArgumentException("El tamaño de la matriz debe ser mayor a 0. Recibido: " + n);
        }

        double[][] matrix = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                int value = MIN_VALUE + random.nextInt(MAX_VALUE - MIN_VALUE + 1);
                // Asignar signo aleatorio
                matrix[i][j] = random.nextBoolean() ? value : -value;
            }
        }
        return matrix;
    }

    /**
     * Genera un par de matrices A y B del mismo tamaño.
     *
     * @param n tamaño de las matrices (n x n)
     * @return arreglo con [A, B]
     * @throws IllegalArgumentException si n es menor o igual a 0
     */
    public double[][][] generatePair(int n) {
        return new double[][][] { generate(n), generate(n) };
    }

    /**
     * Imprime información sobre una matriz generada (para depuración).
     *
     * @param matrix la matriz a describir
     * @param name   nombre identificador de la matriz
     */
    public static void printInfo(double[][] matrix, String name) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        System.out.printf("  Matriz %s: %d x %d | Muestra [0][0] = %.0f%n",
                name, rows, cols, matrix[0][0]);
    }

}
