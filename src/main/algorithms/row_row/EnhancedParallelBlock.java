package main.algorithms.row_row;

public class EnhancedParallelBlock {

    public static double[][] rowRowEnhancedParallelBlock(double[][] B, double[][] C, int size, int bsize) {
        double[][] A = new double[size][size];

        Thread t1 = new Thread(() -> {
            for (int i1 = 0; i1 < size / 2; i1 += bsize) {
                for (int j1 = 0; j1 < size; j1 += bsize) {
                    for (int k1 = 0; k1 < size; k1 += bsize) {
                        for (int i = i1; i < i1 + bsize && i < size; i++) {
                            for (int j = j1; j < j1 + bsize && j < size; j++) {
                                for (int k = k1; k < k1 + bsize && k < size; k++) {
                                    A[i][k] += B[i][j] * C[j][k];
                                }
                            }
                        }
                    }
                }
            }
        });

        Thread t2 = new Thread(() -> {
            for (int i1 = size / 2; i1 < size; i1 += bsize) {
                for (int j1 = 0; j1 < size; j1 += bsize) {
                    for (int k1 = 0; k1 < size; k1 += bsize) {
                        for (int i = i1; i < i1 + bsize && i < size; i++) {
                            for (int j = j1; j < j1 + bsize && j < size; j++) {
                                for (int k = k1; k < k1 + bsize && k < size; k++) {
                                    A[i][k] += B[i][j] * C[j][k];
                                }
                            }
                        }
                    }
                }
            }
        });

        t1.start();
        t2.start();

        try {
            t1.join();
            t2.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        return A;
    }
    
}
