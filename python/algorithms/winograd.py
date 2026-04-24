"""
Algoritmos de Winograd de multiplicación de matrices.

Replica exactamente la lógica de los algoritmos Java:
- WinogradOriginal
- WinogradScaled
"""


def winograd_original(A, B, size):
    """Algoritmo de Winograd original."""
    C = [[0.0] * size for _ in range(size)]
    row_factor = [0.0] * size
    col_factor = [0.0] * size

    for i in range(size):
        for k in range(size // 2):
            row_factor[i] += A[i][2 * k] * A[i][2 * k + 1]

    for j in range(size):
        for k in range(size // 2):
            col_factor[j] += B[2 * k][j] * B[2 * k + 1][j]

    for i in range(size):
        for j in range(size):
            C[i][j] = -row_factor[i] - col_factor[j]

            for k in range(size // 2):
                C[i][j] += ((A[i][2 * k] + B[2 * k + 1][j])
                            * (A[i][2 * k + 1] + B[2 * k][j]))

    if size % 2 == 1:
        for i in range(size):
            for j in range(size):
                C[i][j] += A[i][size - 1] * B[size - 1][j]

    return C


def winograd_scaled(A, B, size):
    """
    Algoritmo de Winograd con escalamiento.

    Escala las matrices por su norma infinito antes de aplicar Winograd Original.
    Des-escala el resultado al final.
    """
    norm_a = _infinity_norm(A, size)
    norm_b = _infinity_norm(B, size)

    if norm_a == 0 or norm_b == 0:
        return [[0.0] * size for _ in range(size)]

    # Crear copias escaladas
    scaled_a = [[A[i][j] / norm_a for j in range(size)] for i in range(size)]
    scaled_b = [[B[i][j] / norm_b for j in range(size)] for i in range(size)]

    # Aplicar Winograd Original a las matrices escaladas
    scaled_result = winograd_original(scaled_a, scaled_b, size)

    # Des-escalar el resultado
    scale_factor = norm_a * norm_b
    result = [[scaled_result[i][j] * scale_factor for j in range(size)] for i in range(size)]

    return result


def _infinity_norm(matrix, size):
    """Calcula la norma infinito de una matriz (máximo de sumas absolutas por fila)."""
    max_row_sum = 0.0
    for i in range(size):
        row_sum = 0.0
        for j in range(size):
            row_sum += abs(matrix[i][j])
        if row_sum > max_row_sum:
            max_row_sum = row_sum
    return max_row_sum
