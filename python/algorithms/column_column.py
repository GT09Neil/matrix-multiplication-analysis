"""
Algoritmos de bloque Column-Column de multiplicación de matrices.

Replica exactamente la lógica de los algoritmos Java:
- CC_SequentialBlock
- CC_ParallelBlock

Nota: El acceso a la matriz resultante es A[k][i] += B[k][j] * C[j][i]
(orden column-column).
"""

import threading


def cc_sequential_block(B, C, size, bsize):
    """Multiplicación por bloques column-column secuencial."""
    A = [[0.0] * size for _ in range(size)]

    for i1 in range(0, size, bsize):
        for j1 in range(0, size, bsize):
            for k1 in range(0, size, bsize):
                for i in range(i1, min(i1 + bsize, size)):
                    for j in range(j1, min(j1 + bsize, size)):
                        for k in range(k1, min(k1 + bsize, size)):
                            A[k][i] += B[k][j] * C[j][i]

    return A


def cc_parallel_block(B, C, size, bsize):
    """Multiplicación por bloques column-column con paralelismo."""
    A = [[0.0] * size for _ in range(size)]
    num_blocks = size // bsize

    def _worker(block_i):
        i1 = block_i * bsize
        for j1 in range(0, size, bsize):
            for k1 in range(0, size, bsize):
                for i in range(i1, min(i1 + bsize, size)):
                    for j in range(j1, min(j1 + bsize, size)):
                        for k in range(k1, min(k1 + bsize, size)):
                            A[k][i] += B[k][j] * C[j][i]

    # Ejecución secuencial de los bloques (en Python puro, sin multiprocessing
    # para esta variante, ya que compartir la matriz A entre procesos es costoso)
    # Se usa threading que, aunque limitado por GIL, replica el comportamiento
    # de parallel streams de Java para tareas de este tipo.
    threads = []
    for bi in range(num_blocks):
        t = threading.Thread(target=_worker, args=(bi,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    return A
