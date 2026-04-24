"""
Algoritmos de Strassen de multiplicación de matrices.

Replica exactamente la lógica de los algoritmos Java:
- StrassenNaiv
- StrassenWinograd

Usa las utilidades de MatrixUtils para operaciones auxiliares.
"""

from python.utils.matrix_utils import add, subtract, split, join


def strassen_naiv(A, B):
    """Algoritmo de Strassen con base naive."""
    n = len(A)

    if n <= 2:
        from python.algorithms.naive import naiv_on_array
        return naiv_on_array(A, B, n)

    new_size = n // 2

    A11, A12, A21, A22 = split(A, new_size)
    B11, B12, B21, B22 = split(B, new_size)

    M1 = strassen_naiv(add(A11, A22), add(B11, B22))
    M2 = strassen_naiv(add(A21, A22), B11)
    M3 = strassen_naiv(A11, subtract(B12, B22))
    M4 = strassen_naiv(A22, subtract(B21, B11))
    M5 = strassen_naiv(add(A11, A12), B22)
    M6 = strassen_naiv(subtract(A21, A11), add(B11, B12))
    M7 = strassen_naiv(subtract(A12, A22), add(B21, B22))

    C11 = add(subtract(add(M1, M4), M5), M7)
    C12 = add(M3, M5)
    C21 = add(M2, M4)
    C22 = add(subtract(add(M1, M3), M2), M6)

    return join(C11, C12, C21, C22, n)


def strassen_winograd(A, B):
    """Algoritmo de Strassen con variante Winograd."""
    n = len(A)

    if n <= 2:
        return strassen_naiv(A, B)

    new_size = n // 2

    A11, A12, A21, A22 = split(A, new_size)
    B11, B12, B21, B22 = split(B, new_size)

    # Variantes tipo Winograd (menos operaciones)
    S1 = subtract(B12, B22)
    S2 = add(A11, A12)
    S3 = add(A21, A22)
    S4 = subtract(B21, B11)
    S5 = add(A11, A22)
    S6 = add(B11, B22)
    S7 = subtract(A12, A22)
    S8 = add(B21, B22)
    S9 = subtract(A11, A21)
    S10 = add(B11, B12)

    P1 = strassen_winograd(A11, S1)
    P2 = strassen_winograd(S2, B22)
    P3 = strassen_winograd(S3, B11)
    P4 = strassen_winograd(A22, S4)
    P5 = strassen_winograd(S5, S6)
    P6 = strassen_winograd(S7, S8)
    P7 = strassen_winograd(S9, S10)

    C11 = add(subtract(add(P5, P4), P2), P6)
    C12 = add(P1, P2)
    C21 = add(P3, P4)
    C22 = subtract(subtract(add(P5, P1), P3), P7)

    return join(C11, C12, C21, C22, n)
