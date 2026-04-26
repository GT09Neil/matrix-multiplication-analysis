/**
 * app.js — Dashboard interactivo para Matrix Multiplication Analytics
 *
 * Flujo:
 * 1. Usuario selecciona modo (Java / Python / Comparación)
 * 2. Presiona "Ejecutar" → POST /api/execute
 * 3. Servidor ejecuta algoritmos y devuelve datos
 * 4. Gráfica y estadísticas se renderizan automáticamente
 *
 * También permite cargar resultados históricos desde /api/results
 */

// ── Estado global ──
let rawData = [];
let chartInstance = null;
let currentMode = 'java';
let currentSize = null;
let currentView = 'cases';
let selectedMatrixSize = null;  // null = all default sizes
let isExecuting = false;

// ── Referencias DOM ──
const btnExecute = document.getElementById('btnExecute');
const statusText = document.getElementById('statusText');
const sizeFilter = document.getElementById('sizeFilter');
const ctx = document.getElementById('resultsChart').getContext('2d');

// ══════════════════════════════════════════════════════
//  INICIALIZACIÓN
// ══════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    // Mode card selection
    document.querySelectorAll('.mode-card').forEach(card => {
        card.addEventListener('click', () => {
            if (isExecuting) return;
            document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            currentMode = card.dataset.mode;
        });
    });

    // Execute button
    btnExecute.addEventListener('click', executeAnalysis);

    // Matrix size selector
    const matrixSizeSelect = document.getElementById('matrixSize');
    const sizeWarning = document.getElementById('sizeWarning');
    matrixSizeSelect.addEventListener('change', () => {
        const val = matrixSizeSelect.value;
        selectedMatrixSize = val ? parseInt(val) : null;
        // Show warning for large sizes
        if (selectedMatrixSize && selectedMatrixSize >= 512) {
            sizeWarning.classList.remove('hidden');
        } else {
            sizeWarning.classList.add('hidden');
        }
    });

    // Size filter
    sizeFilter.addEventListener('change', () => {
        currentSize = parseInt(sizeFilter.value);
        renderCurrentView();
    });

    // View tabs
    document.querySelectorAll('.tab-btn[data-view]').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn[data-view]').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentView = tab.dataset.view;
            renderCurrentView();
        });
    });

    // Load historical results
    loadHistory();
});


// ══════════════════════════════════════════════════════
//  EJECUCIÓN DE ALGORITMOS
// ══════════════════════════════════════════════════════

async function executeAnalysis() {
    if (isExecuting) return;
    isExecuting = true;

    btnExecute.disabled = true;
    const sizeLabel = selectedMatrixSize ? `${selectedMatrixSize}×${selectedMatrixSize}` : 'todos los tamaños';
    setStatus('loading', `Ejecutando ${currentMode} (${sizeLabel})... Esto puede tomar unos segundos.`);

    try {
        const body = { mode: currentMode };
        if (selectedMatrixSize) body.size = selectedMatrixSize;

        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const result = await response.json();

        if (result.success && result.data && result.data.length > 0) {
            rawData = parseServerData(result.data);

            const filesStr = result.files.join(', ');
            const timingStr = Object.entries(result.timings || {})
                .map(([lang, secs]) => `${lang}: ${secs}s`)
                .join(' · ');

            setStatus('success', `✓ ${rawData.length} resultados cargados (${filesStr}) · ${timingStr}`);
            showResults();
        } else {
            const errMsg = (result.errors || []).join('; ') || 'Sin datos generados';
            setStatus('error', `Error: ${errMsg}`);
        }
    } catch (err) {
        setStatus('error', `Error de conexión: ${err.message}. ¿Está corriendo el servidor?`);
    }

    isExecuting = false;
    btnExecute.disabled = false;
    loadHistory();
}


// ══════════════════════════════════════════════════════
//  HISTORIAL DE RESULTADOS
// ══════════════════════════════════════════════════════

async function loadHistory() {
    const list = document.getElementById('historyList');
    try {
        const res = await fetch('/api/results');
        const data = await res.json();

        if (data.files.length === 0) {
            list.innerHTML = '<div style="color:var(--text-muted);font-size:0.85rem;text-align:center;padding:1rem;">No hay resultados anteriores</div>';
            return;
        }

        list.innerHTML = data.files.map(f => {
            const badge = getBadgeClass(f.name);
            return `<div class="history-item" onclick="loadHistoryFile('${f.name}')">
                <span class="history-name">${f.name}</span>
                <span class="history-badge ${badge.cls}">${badge.label}</span>
            </div>`;
        }).join('');
    } catch {
        list.innerHTML = '<div style="color:var(--text-muted);font-size:0.85rem;text-align:center;padding:1rem;">Servidor no disponible</div>';
    }
}

function getBadgeClass(name) {
    if (name.startsWith('java')) return { cls: 'java', label: 'Java' };
    if (name.startsWith('python')) return { cls: 'python', label: 'Python' };
    if (name.includes('results_java')) return { cls: 'java', label: 'Java' };
    if (name.includes('results_python')) return { cls: 'python', label: 'Python' };
    return { cls: 'other', label: 'Otro' };
}

async function loadHistoryFile(filename) {
    setStatus('loading', `Cargando ${filename}...`);
    try {
        const res = await fetch(`/api/results/${filename}`);
        const text = await res.text();

        rawData = parseCSVText(text);
        if (rawData.length > 0) {
            setStatus('success', `✓ ${rawData.length} resultados cargados desde ${filename}`);
            showResults();
        } else {
            setStatus('error', 'El archivo no contiene datos válidos');
        }
    } catch (err) {
        setStatus('error', `Error cargando archivo: ${err.message}`);
    }
}


// ══════════════════════════════════════════════════════
//  PARSING DE DATOS
// ══════════════════════════════════════════════════════

function parseServerData(serverData) {
    return serverData.map(row => ({
        algoritmo: row['algoritmo'] || '',
        tamano: parseInt(row['tamaño'] || row['tamano'] || '0'),
        caso: row['caso'] || '',
        tiempo_ns: parseInt(row['tiempo_ns'] || '0'),
        tiempo_ms: parseFloat(row['tiempo_ms'] || '0'),
        lenguaje: row['lenguaje'] || 'Java',
        tipo_ejecucion: row['tipo_ejecucion'] || 'secuencial'
    })).filter(r => !isNaN(r.tiempo_ms) && r.tiempo_ms > 0);
}

function parseCSVText(text) {
    const lines = text.trim().split('\n');
    if (lines.length < 2) return [];

    const header = lines[0].replace(/\r/g, '').split(',');
    const hasLang = header.includes('lenguaje');
    const hasExec = header.includes('tipo_ejecucion');
    const data = [];

    for (let i = 1; i < lines.length; i++) {
        const vals = lines[i].replace(/\r/g, '').split(',');
        if (vals.length < 5) continue;

        const row = {
            algoritmo: vals[0].trim(),
            tamano: parseInt(vals[1]),
            caso: vals[2].trim(),
            tiempo_ns: parseInt(vals[3]),
            tiempo_ms: parseFloat(vals[4]),
            lenguaje: hasLang && vals[5] ? vals[5].trim() : 'Java',
            tipo_ejecucion: hasExec && vals[6] ? vals[6].trim() : 'secuencial'
        };

        if (!isNaN(row.tiempo_ms) && row.tiempo_ms > 0) data.push(row);
    }
    return data;
}


// ══════════════════════════════════════════════════════
//  MOSTRAR RESULTADOS
// ══════════════════════════════════════════════════════

function showResults() {
    // Mostrar paneles
    document.getElementById('filtersCard').classList.remove('hidden');
    document.getElementById('chartCard').classList.remove('hidden');
    document.getElementById('statsCard').classList.remove('hidden');
    document.getElementById('chartPlaceholder').classList.add('hidden');

    // Popular tamaños
    const sizes = [...new Set(rawData.map(d => d.tamano))].sort((a, b) => a - b);
    sizeFilter.innerHTML = sizes.map(s => `<option value="${s}">${s} × ${s}</option>`).join('');
    currentSize = sizes[0];

    // Determinar si mostrar tab comparación
    const langs = [...new Set(rawData.map(d => d.lenguaje))];
    const compareTab = document.getElementById('viewCompare');
    if (langs.length >= 2) {
        compareTab.classList.remove('hidden');
    } else {
        compareTab.classList.add('hidden');
        if (currentView === 'compare') {
            currentView = 'cases';
            document.querySelectorAll('.tab-btn[data-view]').forEach(t => t.classList.remove('active'));
            document.getElementById('viewCases').classList.add('active');
        }
    }

    renderCurrentView();
}

function renderCurrentView() {
    if (rawData.length === 0) return;

    const filtered = rawData.filter(d => d.tamano === currentSize);
    if (filtered.length === 0) return;

    if (currentView === 'compare') {
        renderCompareChart(filtered);
    } else {
        renderCasesChart(filtered);
    }

    updateStats(filtered);
    updateComparison(filtered);
}


// ══════════════════════════════════════════════════════
//  GRÁFICAS
// ══════════════════════════════════════════════════════

function renderCasesChart(filtered) {
    const algos = [...new Set(filtered.map(d => d.algoritmo))];
    const langs = [...new Set(filtered.map(d => d.lenguaje))];
    const datasets = [];

    const colors = {
        'Java':   { bgs: ['rgba(249,115,22,0.7)', 'rgba(249,115,22,0.45)'], border: '#f97316' },
        'Python': { bgs: ['rgba(56,189,248,0.7)', 'rgba(56,189,248,0.45)'], border: '#38bdf8' }
    };
    const fallbackColors = [
        { bg: 'rgba(74,222,128,0.7)', border: '#4ade80' },
        { bg: 'rgba(251,191,36,0.7)', border: '#fbbf24' }
    ];

    langs.forEach(lang => {
        const langData = filtered.filter(d => d.lenguaje === lang);
        const cases = [...new Set(langData.map(d => d.caso))].sort();
        const c = colors[lang] || { bgs: [fallbackColors[0].bg, fallbackColors[1].bg], border: fallbackColors[0].border };

        cases.forEach((cas, idx) => {
            datasets.push({
                label: langs.length > 1 ? `${lang} — Caso ${cas}` : `Caso ${cas}`,
                data: algos.map(a => {
                    const entry = langData.find(d => d.algoritmo === a && d.caso === cas);
                    return entry ? entry.tiempo_ms : 0;
                }),
                backgroundColor: c.bgs[idx % c.bgs.length],
                borderColor: c.border,
                borderWidth: 1,
                borderRadius: 4
            });
        });
    });

    const langLabel = langs.length > 1 ? 'Java + Python' : langs[0];
    document.getElementById('chartTitle').textContent =
        `Rendimiento por algoritmo — ${langLabel} (${currentSize}×${currentSize})`;
    drawChart(algos, datasets);
}

function renderCompareChart(filtered) {
    const algos = [...new Set(filtered.map(d => d.algoritmo))];

    const avgByAlgo = (lang) => algos.map(a => {
        const entries = filtered.filter(d => d.algoritmo === a && d.lenguaje === lang);
        if (entries.length === 0) return 0;
        return entries.reduce((s, e) => s + e.tiempo_ms, 0) / entries.length;
    });

    const datasets = [
        {
            label: 'Java (promedio)',
            data: avgByAlgo('Java'),
            backgroundColor: 'rgba(249,115,22,0.75)',
            borderColor: '#f97316',
            borderWidth: 1, borderRadius: 4
        },
        {
            label: 'Python (promedio)',
            data: avgByAlgo('Python'),
            backgroundColor: 'rgba(56,189,248,0.75)',
            borderColor: '#38bdf8',
            borderWidth: 1, borderRadius: 4
        }
    ];

    document.getElementById('chartTitle').textContent =
        `Java vs Python — Comparación de rendimiento (${currentSize}×${currentSize})`;
    drawChart(algos, datasets);
}

function drawChart(labels, datasets) {
    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 700, easing: 'easeOutQuart' },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
                    ticks: { color: '#94a3b8', font: { size: 11, family: 'Outfit' }, callback: v => v + ' ms' },
                    title: { display: true, text: 'Tiempo (ms)', color: '#64748b', font: { family: 'Outfit' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { size: 9, weight: '500', family: 'Outfit' }, maxRotation: 45, minRotation: 45 }
                }
            },
            plugins: {
                legend: {
                    position: 'top', align: 'end',
                    labels: { color: '#f1f5f9', font: { family: 'Outfit', size: 11, weight: '600' }, usePointStyle: true, pointStyle: 'circle', padding: 14, boxWidth: 8 }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleFont: { size: 13, family: 'Outfit', weight: '600' },
                    bodyFont: { size: 12, family: 'Outfit' },
                    padding: 10, borderColor: 'rgba(255,255,255,0.08)', borderWidth: 1,
                    callbacks: { label: c => `${c.dataset.label}: ${c.raw.toFixed(4)} ms` }
                }
            }
        }
    });
}


// ══════════════════════════════════════════════════════
//  ESTADÍSTICAS
// ══════════════════════════════════════════════════════

function updateStats(data) {
    const sorted = [...data].sort((a, b) => a.tiempo_ms - b.tiempo_ms);
    const best = sorted[0];

    document.getElementById('bestAlgo').textContent = best.algoritmo;
    document.getElementById('bestAlgoSub').textContent = `${best.lenguaje} — ${best.tiempo_ms.toFixed(4)} ms`;

    // Java
    const jd = data.filter(d => d.lenguaje === 'Java');
    if (jd.length > 0) {
        const bj = jd.sort((a, b) => a.tiempo_ms - b.tiempo_ms)[0];
        document.getElementById('bestJava').textContent = bj.tiempo_ms.toFixed(4) + ' ms';
        document.getElementById('bestJavaSub').textContent = bj.algoritmo;
    } else {
        document.getElementById('bestJava').textContent = 'N/A';
        document.getElementById('bestJavaSub').textContent = 'Sin datos';
    }

    // Python
    const pd = data.filter(d => d.lenguaje === 'Python');
    if (pd.length > 0) {
        const bp = pd.sort((a, b) => a.tiempo_ms - b.tiempo_ms)[0];
        document.getElementById('bestPython').textContent = bp.tiempo_ms.toFixed(4) + ' ms';
        document.getElementById('bestPythonSub').textContent = bp.algoritmo;
    } else {
        document.getElementById('bestPython').textContent = 'N/A';
        document.getElementById('bestPythonSub').textContent = 'Sin datos';
    }

    document.getElementById('totalExecs').textContent = data.length;
    document.getElementById('totalExecsSub').textContent = `${[...new Set(data.map(d => d.algoritmo))].length} algoritmos`;
}

function updateComparison(data) {
    const card = document.getElementById('compareCard');
    const jd = data.filter(d => d.lenguaje === 'Java');
    const pd = data.filter(d => d.lenguaje === 'Python');

    if (jd.length > 0 && pd.length > 0) {
        card.classList.remove('hidden');
        const avg = arr => arr.reduce((a, b) => a + b, 0) / arr.length;

        const jt = jd.map(d => d.tiempo_ms);
        document.getElementById('cmpJavaAvg').textContent = avg(jt).toFixed(4) + ' ms';
        document.getElementById('cmpJavaMin').textContent = Math.min(...jt).toFixed(4) + ' ms';
        document.getElementById('cmpJavaMax').textContent = Math.max(...jt).toFixed(4) + ' ms';
        document.getElementById('cmpJavaCount').textContent = jd.length;

        const pt = pd.map(d => d.tiempo_ms);
        document.getElementById('cmpPythonAvg').textContent = avg(pt).toFixed(4) + ' ms';
        document.getElementById('cmpPythonMin').textContent = Math.min(...pt).toFixed(4) + ' ms';
        document.getElementById('cmpPythonMax').textContent = Math.max(...pt).toFixed(4) + ' ms';
        document.getElementById('cmpPythonCount').textContent = pd.length;
    } else {
        card.classList.add('hidden');
    }
}


// ══════════════════════════════════════════════════════
//  UTILIDADES
// ══════════════════════════════════════════════════════

function setStatus(type, msg) {
    statusText.className = 'status-text';
    if (type === 'loading') {
        statusText.innerHTML = `<span class="spinner"></span>${msg}`;
    } else if (type === 'error') {
        statusText.classList.add('error');
        statusText.textContent = msg;
    } else if (type === 'success') {
        statusText.classList.add('success');
        statusText.textContent = msg;
    } else {
        statusText.textContent = msg;
    }
}
