
package main.algorithms.naive;

public class NaivLoopUnrollingTwo {

    public static double[][] naivLoopUnrollingTwo(double[][] A, double[][] B, int size) {
        double[][] C = new double[size][size];

        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                int k;
                for (k = 0; k <= size - 2; k += 2) {
                    C[i][j] += A[i][k] * B[k][j]
                            + A[i][k + 1] * B[k + 1][j];
                }
                for (; k < size; k++) {
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }

        return C;
    }
    
}
