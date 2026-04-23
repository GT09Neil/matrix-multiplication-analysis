package main.algorithms.strassen;

import main.utils.MatrixUtils;
import main.algorithms.naive.NaivOnArray;

public class StrassenNaiv {

    public static double[][] strassenNaiv(double[][] A, double[][] B) {
        int n = A.length;

        if (n <= 2) {
            return NaivOnArray.naivOnArray(A, B, n);
        }

        int newSize = n / 2;

        double[][] A11 = new double[newSize][newSize];
        double[][] A12 = new double[newSize][newSize];
        double[][] A21 = new double[newSize][newSize];
        double[][] A22 = new double[newSize][newSize];

        double[][] B11 = new double[newSize][newSize];
        double[][] B12 = new double[newSize][newSize];
        double[][] B21 = new double[newSize][newSize];
        double[][] B22 = new double[newSize][newSize];

        MatrixUtils.split(A, A11, 0 , 0);
        MatrixUtils.split(A, A12, 0 , newSize);
        MatrixUtils.split(A, A21, newSize, 0);
        MatrixUtils.split(A, A22, newSize, newSize);

        MatrixUtils.split(B, B11, 0 , 0);
        MatrixUtils.split(B, B12, 0 , newSize);
        MatrixUtils.split(B, B21, newSize, 0);
        MatrixUtils.split(B, B22, newSize, newSize);

        double[][] M1 = strassenNaiv(MatrixUtils.add(A11, A22), MatrixUtils.add(B11, B22));
        double[][] M2 = strassenNaiv(MatrixUtils.add(A21, A22), B11);
        double[][] M3 = strassenNaiv(A11, MatrixUtils.subtract(B12, B22));
        double[][] M4 = strassenNaiv(A22, MatrixUtils.subtract(B21, B11));
        double[][] M5 = strassenNaiv(MatrixUtils.add(A11, A12), B22);
        double[][] M6 = strassenNaiv(MatrixUtils.subtract(A21, A11), MatrixUtils.add(B11, B12));
        double[][] M7 = strassenNaiv(MatrixUtils.subtract(A12, A22), MatrixUtils.add(B21, B22));

        double[][] C11 = MatrixUtils.add(MatrixUtils.subtract(MatrixUtils.add(M1, M4), M5), M7);
        double[][] C12 = MatrixUtils.add(M3, M5);
        double[][] C21 = MatrixUtils.add(M2, M4);
        double[][] C22 = MatrixUtils.add(MatrixUtils.subtract(MatrixUtils.add(M1, M3), M2), M6);

        double[][] C = new double[n][n];

        MatrixUtils.join(C11, C, 0 , 0);
        MatrixUtils.join(C12, C, 0 , newSize);
        MatrixUtils.join(C21, C, newSize, 0);
        MatrixUtils.join(C22, C, newSize, newSize);

        return C;
    }
    
}
