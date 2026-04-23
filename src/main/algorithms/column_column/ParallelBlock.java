package main.algorithms.column_column;

import java.util.stream.IntStream;

public class ParallelBlock {

    public static double[][] columnColumnParallelBlock(double[][] B, double[][] C, int size, int bsize) {
        double[][] A = new double[size][size];

        IntStream.range(0, size / bsize).parallel().forEach(blockI -> {
            int i1 = blockI * bsize;

            for (int j1 = 0; j1 < size; j1 += bsize) {
                for (int k1 = 0; k1 < size; k1 += bsize) {
                    for (int i = i1; i < i1 + bsize && i < size; i++) {
                        for (int j = j1; j < j1 + bsize && j < size; j++) {
                            for (int k = k1; k < k1 + bsize && k < size; k++) {
                                A[k][i] += B[k][j] * C[j][i];
                            }
                        }
                    }
                }
            }
        });

        return A;
    }

}
