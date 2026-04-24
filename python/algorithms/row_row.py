"""
Algoritmos de bloque Row-Row de multiplicación de matrices.

Replica exactamente la lógica de los algoritmos Java:
- RR_SequentialBlock
- RR_ParallelBlock
- RR_EnhancedParallelBlock

Nota: El acceso a la matriz resultante es A[i][k] += B[i][j] * C[j][k]
(orden row-row).
"""

import threading


def rr_sequential_block(B, C, size, bsize):
    """Multiplicación por bloques row-row secuencial."""
    A = [[0.0] * size for _ in range(size)]

    for i1 in range(0, size, bsize):
        for j1 in range(0, size, bsize):
            for k1 in range(0, size, bsize):
                for i in range(i1, min(i1 + bsize, size)):
                    for j in range(j1, min(j1 + bsize, size)):
                        for k in range(k1, min(k1 + bsize, size)):
                            A[i][k] += B[i][j] * C[j][k]

    return A


def rr_parallel_block(B, C, size, bsize):
    """Multiplicación por bloques row-row con paralelismo."""
    A = [[0.0] * size for _ in range(size)]
    num_blocks = size // bsize

    def _worker(block_i):
        i1 = block_i * bsize
        for j1 in range(0, size, bsize):
            for k1 in range(0, size, bsize):
                for i in range(i1, min(i1 + bsize, size)):
                    for j in range(j1, min(j1 + bsize, size)):
                        for k in range(k1, min(k1 + bsize, size)):
                            A[i][k] += B[i][j] * C[j][k]

    threads = []
    for bi in range(num_blocks):
        t = threading.Thread(target=_worker, args=(bi,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    return A


def rr_enhanced_parallel_block(B, C, size, bsize):
    """Multiplicación por bloques row-row con 2 hilos (mitad superior/inferior)."""
    A = [[0.0] * size for _ in range(size)]

    def _worker_half(start_row, end_row):
        for i1 in range(start_row, end_row, bsize):
            for j1 in range(0, size, bsize):
                for k1 in range(0, size, bsize):
                    for i in range(i1, min(i1 + bsize, size)):
                        for j in range(j1, min(j1 + bsize, size)):
                            for k in range(k1, min(k1 + bsize, size)):
                                A[i][k] += B[i][j] * C[j][k]

    half = size // 2
    t1 = threading.Thread(target=_worker_half, args=(0, half))
    t2 = threading.Thread(target=_worker_half, args=(half, size))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    return A
