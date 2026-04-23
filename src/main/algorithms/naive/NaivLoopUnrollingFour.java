package main.algorithms.naive;

public class NaivLoopUnrollingFour {

    public static double[][] naivLoopUnrollingFour(double[][] A, double[][] B, int size) {
        double[][] C = new double[size][size];

        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                int k;
                for (k = 0; k <= size - 4; k += 4) {
                    C[i][j] += A[i][k] * B[k][j]
                            + A[i][k + 1] * B[k + 1][j]
                            + A[i][k + 2] * B[k + 2][j]
                            + A[i][k + 3] * B[k + 3][j];
                }
                for (; k < size; k++) {
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }

        return C;
    }
    
}
