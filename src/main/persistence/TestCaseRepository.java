package main.persistence;

import java.io.*;
import java.nio.file.*;

/**
 * Repositorio para persistir y cargar casos de prueba (pares de matrices) en formato JSON.
 * Los archivos se guardan en data/test_cases/.
 *
 * Formato JSON: estructura manual sin dependencias externas.
 * Los valores numéricos se formatean sin decimales (son enteros de 6 dígitos).
 */
public class TestCaseRepository {

    private static final String BASE_DIR = "data/test_cases";

    public TestCaseRepository() {
        // Crear directorio si no existe
        try {
            Files.createDirectories(Paths.get(BASE_DIR));
        } catch (IOException e) {
            System.err.println("Error creando directorio de casos de prueba: " + e.getMessage());
        }
    }

    /**
     * Guarda un caso de prueba (par de matrices A y B) en un archivo JSON.
     *
     * @param A      primera matriz
     * @param B      segunda matriz
     * @param size   tamaño de las matrices
     * @param caseId identificador del caso de prueba
     */
    public void save(double[][] A, double[][] B, int size, String caseId) {
        String filename = String.format("%s/case_%s_size_%d.json", BASE_DIR, caseId, size);

        try (PrintWriter writer = new PrintWriter(new FileWriter(filename))) {
            writer.println("{");
            writer.println("  \"size\": " + size + ",");
            writer.println("  \"caseId\": \"" + caseId + "\",");
            writer.println("  \"matrixA\": " + matrixToJson(A, size) + ",");
            writer.println("  \"matrixB\": " + matrixToJson(B, size));
            writer.println("}");

            System.out.println("  [OK] Caso guardado: " + filename);
        } catch (IOException e) {
            System.err.println("Error guardando caso de prueba: " + e.getMessage());
        }
    }

    /**
     * Carga un caso de prueba desde un archivo JSON.
     *
     * @param size   tamaño de las matrices
     * @param caseId identificador del caso de prueba
     * @return arreglo con [A, B] o null si hay error
     */
    public double[][][] load(int size, String caseId) {
        String filename = String.format("%s/case_%s_size_%d.json", BASE_DIR, caseId, size);

        try {
            String content = new String(Files.readAllBytes(Paths.get(filename)));
            double[][] A = parseMatrix(content, "matrixA", size);
            double[][] B = parseMatrix(content, "matrixB", size);

            System.out.println("  [OK] Caso cargado: " + filename);
            return new double[][][] { A, B };
        } catch (IOException e) {
            System.err.println("Error cargando caso de prueba: " + e.getMessage());
            return null;
        }
    }

    /**
     * Verifica si un caso de prueba existe.
     *
     * @param size   tamaño de las matrices
     * @param caseId identificador del caso de prueba
     * @return true si el archivo JSON existe
     */
    public boolean exists(int size, String caseId) {
        String filename = String.format("%s/case_%s_size_%d.json", BASE_DIR, caseId, size);
        return Files.exists(Paths.get(filename));
    }

    /**
     * Elimina un caso de prueba.
     *
     * @param size   tamaño de las matrices
     * @param caseId identificador del caso de prueba
     * @return true si se eliminó correctamente
     */
    public boolean delete(int size, String caseId) {
        String filename = String.format("%s/case_%s_size_%d.json", BASE_DIR, caseId, size);
        try {
            return Files.deleteIfExists(Paths.get(filename));
        } catch (IOException e) {
            System.err.println("Error eliminando caso de prueba: " + e.getMessage());
            return false;
        }
    }

    // ==================== Métodos auxiliares ====================

    /**
     * Convierte una matriz a su representación JSON (arreglo de arreglos).
     */
    private String matrixToJson(double[][] matrix, int size) {
        StringBuilder sb = new StringBuilder();
        sb.append("[\n");
        for (int i = 0; i < size; i++) {
            sb.append("    [");
            for (int j = 0; j < size; j++) {
                sb.append(String.format("%.0f", matrix[i][j]));
                if (j < size - 1) sb.append(", ");
            }
            sb.append("]");
            if (i < size - 1) sb.append(",");
            sb.append("\n");
        }
        sb.append("  ]");
        return sb.toString();
    }

    /**
     * Parsea una matriz desde un string JSON.
     * Implementación manual para evitar dependencias externas.
     */
    private double[][] parseMatrix(String json, String key, int size) {
        double[][] matrix = new double[size][size];

        // Encontrar la clave de la matriz
        int keyIndex = json.indexOf("\"" + key + "\"");
        if (keyIndex == -1) {
            throw new RuntimeException("Clave no encontrada: " + key);
        }

        // Encontrar el inicio del arreglo de la matriz
        int arrayStart = json.indexOf("[", keyIndex);

        int row = 0;
        int col = 0;
        int pos = arrayStart + 1;

        while (row < size && pos < json.length()) {
            char c = json.charAt(pos);

            if (c == '[') {
                // Inicio de una fila
                col = 0;
                pos++;
                continue;
            }

            if (c == ']') {
                pos++;
                if (row < size) {
                    // Verificar si es el cierre de una fila o del arreglo completo
                    if (col > 0) {
                        row++;
                    }
                }
                continue;
            }

            if (c == ',' || c == ' ' || c == '\n' || c == '\r' || c == '\t') {
                pos++;
                continue;
            }

            // Leer un número (puede ser negativo)
            if (c == '-' || Character.isDigit(c)) {
                int numStart = pos;
                pos++;
                while (pos < json.length() && (Character.isDigit(json.charAt(pos)) || json.charAt(pos) == '.')) {
                    pos++;
                }
                String numStr = json.substring(numStart, pos);
                if (row < size && col < size) {
                    matrix[row][col] = Double.parseDouble(numStr);
                    col++;
                }
                continue;
            }

            pos++;
        }

        return matrix;
    }

}
