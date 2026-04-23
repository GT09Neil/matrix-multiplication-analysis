package main.algorithms.strassen;

import main.utils.MatrixUtils;

public class StrassenWinograd {

    public static double[][] strassenWinograd(double[][] A, double[][] B) {
        
        int n = A.length;

        if (n <= 2) {
            return StrassenNaiv.strassenNaiv(A, B);
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

        MatrixUtils.split(A, A11, 0, 0);
        MatrixUtils.split(A, A12, 0, newSize);
        MatrixUtils.split(A, A21, newSize, 0);
        MatrixUtils.split(A, A22, newSize, newSize);

        MatrixUtils.split(B, B11, 0, 0);
        MatrixUtils.split(B, B12, 0, newSize);
        MatrixUtils.split(B, B21, newSize, 0);
        MatrixUtils.split(B, B22, newSize, newSize);

        // Variantes tipo Winograd (menos operaciones)
        double[][] S1 = MatrixUtils.subtract(B12, B22);
        double[][] S2 = MatrixUtils.add(A11, A12);
        double[][] S3 = MatrixUtils.add(A21, A22);
        double[][] S4 = MatrixUtils.subtract(B21, B11);
        double[][] S5 = MatrixUtils.add(A11, A22);
        double[][] S6 = MatrixUtils.add(B11, B22);
        double[][] S7 = MatrixUtils.subtract(A12, A22);
        double[][] S8 = MatrixUtils.add(B21, B22);
        double[][] S9 = MatrixUtils.subtract(A11, A21);
        double[][] S10 = MatrixUtils.add(B11, B12);

        double[][] P1 = strassenWinograd(A11, S1);
        double[][] P2 = strassenWinograd(S2, B22);
        double[][] P3 = strassenWinograd(S3, B11);
        double[][] P4 = strassenWinograd(A22, S4);
        double[][] P5 = strassenWinograd(S5, S6);
        double[][] P6 = strassenWinograd(S7, S8);
        double[][] P7 = strassenWinograd(S9, S10);

        double[][] C11 = MatrixUtils.add(MatrixUtils.subtract(MatrixUtils.add(P5, P4), P2), P6);
        double[][] C12 = MatrixUtils.add(P1, P2);
        double[][] C21 = MatrixUtils.add(P3, P4);
        double[][] C22 = MatrixUtils.subtract(MatrixUtils.subtract(MatrixUtils.add(P5, P1), P3), P7);

        double[][] C = new double[n][n];

        MatrixUtils.join(C11, C, 0, 0);
        MatrixUtils.join(C12, C, 0, newSize);
        MatrixUtils.join(C21, C, newSize, 0);
        MatrixUtils.join(C22, C, newSize, newSize);

        return C;
    }
    
}
