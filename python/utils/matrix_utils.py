"""
Utilidades para operaciones con matrices.

Replica las funciones de MatrixUtils.java:
- add: suma de matrices
- subtract: resta de matrices
- split: dividir matriz en 4 cuadrantes
- join: unir 4 cuadrantes en una matriz
"""


def add(A, B):
    """Suma dos matrices cuadradas."""
    n = len(A)
    C = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            C[i][j] = A[i][j] + B[i][j]
    return C


def subtract(A, B):
    """Resta dos matrices cuadradas (A - B)."""
    n = len(A)
    C = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            C[i][j] = A[i][j] - B[i][j]
    return C


def split(matrix, new_size):
    """
    Divide una matriz en 4 cuadrantes.

    Retorna (A11, A12, A21, A22) donde cada cuadrante es de tamaño new_size x new_size.
    """
    A11 = [[0.0] * new_size for _ in range(new_size)]
    A12 = [[0.0] * new_size for _ in range(new_size)]
    A21 = [[0.0] * new_size for _ in range(new_size)]
    A22 = [[0.0] * new_size for _ in range(new_size)]

    for i in range(new_size):
        for j in range(new_size):
            A11[i][j] = matrix[i][j]
            A12[i][j] = matrix[i][j + new_size]
            A21[i][j] = matrix[i + new_size][j]
            A22[i][j] = matrix[i + new_size][j + new_size]

    return A11, A12, A21, A22


def join(C11, C12, C21, C22, n):
    """
    Une 4 cuadrantes en una sola matriz de tamaño n x n.
    """
    C = [[0.0] * n for _ in range(n)]
    new_size = n // 2

    for i in range(new_size):
        for j in range(new_size):
            C[i][j] = C11[i][j]
            C[i][j + new_size] = C12[i][j]
            C[i + new_size][j] = C21[i][j]
            C[i + new_size][j + new_size] = C22[i][j]

    return C
