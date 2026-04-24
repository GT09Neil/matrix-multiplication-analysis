"""
Algoritmos Naive de multiplicación de matrices.

Replica exactamente la lógica de los algoritmos Java:
- NaivOnArray
- NaivLoopUnrollingTwo
- NaivLoopUnrollingFour
"""


def naiv_on_array(A, B, size):
    """Multiplicación naive estándar O(n³)."""
    C = [[0.0] * size for _ in range(size)]

    for i in range(size):
        for j in range(size):
            for k in range(size):
                C[i][j] += A[i][k] * B[k][j]

    return C


def naiv_loop_unrolling_two(A, B, size):
    """Multiplicación naive con loop unrolling de factor 2."""
    C = [[0.0] * size for _ in range(size)]

    for i in range(size):
        for j in range(size):
            k = 0
            while k <= size - 2:
                C[i][j] += (A[i][k] * B[k][j]
                            + A[i][k + 1] * B[k + 1][j])
                k += 2
            while k < size:
                C[i][j] += A[i][k] * B[k][j]
                k += 1

    return C


def naiv_loop_unrolling_four(A, B, size):
    """Multiplicación naive con loop unrolling de factor 4."""
    C = [[0.0] * size for _ in range(size)]

    for i in range(size):
        for j in range(size):
            k = 0
            while k <= size - 4:
                C[i][j] += (A[i][k] * B[k][j]
                            + A[i][k + 1] * B[k + 1][j]
                            + A[i][k + 2] * B[k + 2][j]
                            + A[i][k + 3] * B[k + 3][j])
                k += 4
            while k < size:
                C[i][j] += A[i][k] * B[k][j]
                k += 1

    return C
