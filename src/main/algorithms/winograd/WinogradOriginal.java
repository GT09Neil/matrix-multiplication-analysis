package main.algorithms.winograd;

public class WinogradOriginal {

    public static double[][] winogradOriginal(double[][] A, double[][] B, int size) {
        double[][] C = new double[size][size];
        double[] rowFactor = new double[size];
        double[] colFactor = new double[size];

        for (int i = 0; i < size; i++) {
            for (int k = 0; k < size / 2; k++) {
                rowFactor[i] += A[i][2 * k] * A[i][2 * k + 1];
            }
        }

        for (int j = 0; j < size; j++) {
            for (int k = 0; k < size / 2; k++) {
                colFactor[j] += B[2 * k][j] * B[2 * k + 1][j];
            }
        }

        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                C[i][j] = -rowFactor[i] - colFactor[j];

                for (int k = 0; k < size / 2; k++) {
                    C[i][j] += (A[i][2 * k] + B[2 * k + 1][j]) *
                            (A[i][2 * k + 1] + B[2 * k][j]);
                }
            }
        }

        if (size % 2 == 1) {
            for (int i = 0; i < size; i++) {
                for (int j = 0; j < size; j++) {
                    C[i][j] += A[i][size - 1] * B[size - 1][j];
                }
            }
        }

        return C;
    }
    
}
