/**
 * app.js - Lógica de parsing y graficación
 */

let rawData = [];
let chartInstance = null;

const fileInput = document.getElementById('csvFile');
const sizeFilter = document.getElementById('sizeFilter');
const ctx = document.getElementById('resultsChart').getContext('2d');

// Escuchar carga de archivo
fileInput.addEventListener('change', handleFile);

// Escuchar cambios en el filtro
sizeFilter.addEventListener('change', updateChart);

function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(event) {
        parseCSV(event.target.result);
    };
    reader.readAsText(file);
}

/**
 * Parsea el CSV considerando que los números pueden venir con punto decimal
 * @param {string} text Contenido del archivo
 */
function parseCSV(text) {
    const lines = text.trim().split('\n');
    if (lines.length < 2) return;

    rawData = [];
    const sizes = new Set();

    // Procesar líneas
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        if (values.length < 5) continue;

        // Limpiar valores y convertir a tipos correctos
        const row = {
            algoritmo: values[0].trim(),
            tamano: parseInt(values[1]),
            caso: values[2].trim(),
            tiempo_ms: parseFloat(values[4])
        };

        // Validar que el tiempo sea un número válido
        if (!isNaN(row.tiempo_ms)) {
            rawData.push(row);
            sizes.add(row.tamano);
        }
    }

    if (rawData.length === 0) {
        alert("El archivo no contiene datos válidos o el formato es incorrecto.");
        return;
    }

    // Actualizar selector de tamaños
    const sortedSizes = Array.from(sizes).sort((a, b) => a - b);
    sizeFilter.innerHTML = sortedSizes.map(s => `<option value="${s}">${s} x ${s}</option>`).join('');
    
    // Auto-seleccionar el primer tamaño y mostrar estadísticas
    sizeFilter.value = sortedSizes[0];
    document.getElementById('summary').style.display = 'grid';
    updateChart();
}

/**
 * Actualiza la gráfica basada en el filtro de tamaño seleccionado
 */
function updateChart() {
    const selectedSize = parseInt(sizeFilter.value);
    const filtered = rawData.filter(d => d.tamano === selectedSize);

    // Obtener lista única de algoritmos para el eje X
    const algos = [...new Set(filtered.map(d => d.algoritmo))];
    
    // Preparar datasets para Caso 1 y Caso 2
    const dataCase1 = algos.map(a => {
        const entry = filtered.find(d => d.algoritmo === a && d.caso === "1");
        return entry ? entry.tiempo_ms : 0;
    });

    const dataCase2 = algos.map(a => {
        const entry = filtered.find(d => d.algoritmo === a && d.caso === "2");
        return entry ? entry.tiempo_ms : 0;
    });

    renderChart(algos, dataCase1, dataCase2);
    updateStats(filtered);
}

/**
 * Renderiza la gráfica usando Chart.js
 */
function renderChart(labels, case1, case2) {
    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Caso 1 (Matriz A)',
                    data: case1,
                    backgroundColor: 'rgba(56, 189, 248, 0.8)',
                    borderColor: '#38bdf8',
                    borderWidth: 1,
                    borderRadius: 4,
                    hoverBackgroundColor: '#38bdf8',
                },
                {
                    label: 'Caso 2 (Matriz B)',
                    data: case2,
                    backgroundColor: 'rgba(251, 113, 133, 0.8)',
                    borderColor: '#fb7185',
                    borderWidth: 1,
                    borderRadius: 4,
                    hoverBackgroundColor: '#fb7185',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)', drawBorder: false },
                    ticks: { 
                        color: '#94a3b8', 
                        font: { size: 11 },
                        callback: v => v + ' ms' 
                    },
                    title: { display: true, text: 'Tiempo de ejecución (ms)', color: '#64748b' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { size: 10, weight: '500' }, maxRotation: 45, minRotation: 45 }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end',
                    labels: { 
                        color: '#f1f5f9', 
                        font: { family: 'Outfit', size: 12, weight: '600' },
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleFont: { size: 13, family: 'Outfit' },
                    bodyFont: { size: 12, family: 'Outfit' },
                    padding: 12,
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw.toFixed(4)} ms`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Actualiza las tarjetas de estadísticas rápidas
 */
function updateStats(data) {
    if (data.length === 0) return;

    // Encontrar el mejor tiempo absoluto en este tamaño
    const sorted = [...data].sort((a, b) => a.tiempo_ms - b.tiempo_ms);
    const best = sorted[0];

    const fastestEl = document.getElementById('fastestAlgo');
    const bestTimeEl = document.getElementById('bestTime');
    const totalAlgosEl = document.getElementById('totalAlgos');

    // Animación simple de actualización
    fastestEl.innerText = best.algoritmo;
    bestTimeEl.innerText = best.tiempo_ms.toFixed(4);
    totalAlgosEl.innerText = [...new Set(data.map(d => d.algoritmo))].length;
}
