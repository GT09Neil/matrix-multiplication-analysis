package main.algorithms.naive;

public class NaivOnArray {
    
    public static double[][] naivOnArray(double[][] A, double[][] B, int size) {
        double[][] C = new double[size][size];

        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                for (int k = 0; k < size; k++) {
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }

        return C;
    }

}
