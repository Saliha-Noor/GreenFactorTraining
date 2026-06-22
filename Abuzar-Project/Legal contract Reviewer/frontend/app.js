/**
 * LegalLens — Premium Frontend Application
 * Dark glassmorphism UI with CUAD integration, search, and animated pipeline.
 */

const API = '';

// ─── Stats Bar ─────────────────────────────────────────────
async function loadStats() {
    try {
        const res = await fetch(`${API}/api/stats`);
        const data = await res.json();
        animateCounter('stat-clauses', data.total_clause_types || 0);
        animateCounter('stat-examples', data.total_examples || 0);
        animateCounter('stat-contracts', data.total_contracts || 0);
    } catch (e) {
        document.getElementById('stat-clauses').textContent = '41';
        document.getElementById('stat-examples').textContent = '—';
        document.getElementById('stat-contracts').textContent = '0';
    }
}

function animateCounter(id, target) {
    const el = document.getElementById(id);
    if (!el || target === 0) { el.textContent = target; return; }
    let current = 0;
    const step = Math.max(1, Math.floor(target / 40));
    const interval = setInterval(() => {
        current += step;
        if (current >= target) { current = target; clearInterval(interval); }
        el.textContent = current.toLocaleString();
    }, 30);
}

loadStats();

// ─── Navigation ────────────────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.view').forEach(v => {
            v.classList.remove('active');
            v.style.display = 'none';
        });
        const target = document.getElementById(`view-${view}`);
        if (target) {
            target.style.display = 'block';
            target.classList.add('active');
        }
        if (view === 'history') loadHistory();
        if (view === 'clause-db') loadClauseTypes();
    });
});

document.getElementById('view-upload').style.display = 'block';

// ─── File Upload ───────────────────────────────────────────
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.name.toLowerCase().endsWith('.pdf')) uploadFile(file);
    else showError('Please upload a PDF file.');
});
fileInput.addEventListener('change', () => { if (fileInput.files[0]) uploadFile(fileInput.files[0]); });

async function uploadFile(file) {
    const progress = document.getElementById('pipeline-progress');
    const reportContainer = document.getElementById('report-container');
    progress.style.display = 'block';
    reportContainer.style.display = 'none';

    const steps = ['step-parser', 'step-classifier', 'step-risk', 'step-report'];
    const statusTexts = {
        'parser': 'Agent 1: Extracting contract text from PDF...',
        'classifier': 'Agent 2: Running CUAD clause classifications...',
        'risk_analyzer': 'Agent 3: Calculating risk scores and rationales...',
        'report_generator': 'Agent 4: Compiling executive summary and Word report...'
    };

    // Reset progress UI
    steps.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.remove('active', 'done');
            el.querySelector('.step-status').textContent = 'Waiting...';
            el.querySelector('.step-fill').style.width = '0%';
        }
    });

    // Make parser active on start
    const parserEl = document.getElementById('step-parser');
    if (parserEl) {
        parserEl.classList.add('active');
        parserEl.querySelector('.step-status').textContent = statusTexts['parser'];
        parserEl.querySelector('.step-fill').style.width = '50%';
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        // 1. Upload contract to get task_id
        const res = await fetch(`${API}/api/upload`, { method: 'POST', body: formData });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(err.detail || 'Upload failed');
        }

        const uploadData = await res.json();
        const taskId = uploadData.task_id;

        // 2. Poll status endpoint until completed or failed
        let pollCount = 0;
        const maxPolls = 300; // 5 minutes max
        const pollInterval = 1500; // poll every 1.5 seconds

        const pollStatus = async () => {
            if (pollCount >= maxPolls) {
                throw new Error('Pipeline analysis timed out. Please try again.');
            }
            pollCount++;

            const statusRes = await fetch(`${API}/api/pipeline/status/${taskId}`);
            if (!statusRes.ok) {
                throw new Error('Failed to fetch pipeline status.');
            }

            const task = await statusRes.json();

            if (task.status === 'running') {
                const currentAgent = task.current_agent; // e.g., 'parser', 'classifier', 'risk_analyzer', 'report_generator'
                updateProgressUI(currentAgent);
                setTimeout(pollStatus, pollInterval);
            } else if (task.status === 'complete') {
                // Complete all steps in UI
                steps.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) {
                        el.classList.remove('active');
                        el.classList.add('done');
                        el.querySelector('.step-status').textContent = 'Complete ✓';
                        el.querySelector('.step-fill').style.width = '100%';
                    }
                });

                window._lastReportId = task.id;
                setTimeout(() => {
                    progress.style.display = 'none';
                    renderReport(task.report, task.id);
                    loadStats();
                }, 600);
            } else if (task.status === 'failed') {
                const errorMsg = (task.errors && task.errors.length) ? task.errors[0] : 'Pipeline analysis failed';
                throw new Error(errorMsg);
            }
        };

        // Start polling
        setTimeout(pollStatus, pollInterval);

    } catch (err) {
        showError(err.message);
        progress.style.display = 'none';
    }
}

function updateProgressUI(currentAgent) {
    const steps = ['step-parser', 'step-classifier', 'step-risk', 'step-report'];
    const agentMap = {
        'starting': 0,
        'parser': 0,
        'classifier': 1,
        'risk_analyzer': 2,
        'report_generator': 3
    };

    const activeIdx = agentMap[currentAgent] !== undefined ? agentMap[currentAgent] : 0;

    for (let i = 0; i < steps.length; i++) {
        const el = document.getElementById(steps[i]);
        if (!el) continue;

        if (i < activeIdx) {
            // Completed steps
            el.classList.remove('active');
            el.classList.add('done');
            el.querySelector('.step-status').textContent = 'Complete ✓';
            el.querySelector('.step-fill').style.width = '100%';
        } else if (i === activeIdx) {
            // Currently active step
            el.classList.remove('done');
            el.classList.add('active');
            
            const statusTexts = {
                'step-parser': 'Agent 1: Extracting contract text from PDF...',
                'step-classifier': 'Agent 2: Running CUAD clause classifications...',
                'step-risk': 'Agent 3: Calculating risk scores and rationales...',
                'step-report': 'Agent 4: Compiling executive summary and Word report...'
            };
            
            el.querySelector('.step-status').textContent = statusTexts[steps[i]];
            el.querySelector('.step-fill').style.width = '50%';
        } else {
            // Pending steps
            el.classList.remove('active', 'done');
            el.querySelector('.step-status').textContent = 'Waiting...';
            el.querySelector('.step-fill').style.width = '0%';
        }
    }
}

// ─── Report Rendering ──────────────────────────────────────
function renderReport(report, reportId) {
    const container = document.getElementById('report-container');
    container.style.display = 'block';
    if (reportId) window._lastReportId = reportId;
    const riskClass = report.overall_risk_score >= 7 ? 'high' : report.overall_risk_score >= 4 ? 'medium' : 'low';

    let clauseRows = '';
    (report.identified_clauses || []).forEach(cl => {
        const excerpt = cl.text_excerpt.length > 200 ? cl.text_excerpt.slice(0, 200) + '...' : cl.text_excerpt;
        clauseRows += `
            <tr>
                <td><span class="clause-type-tag">${esc(cl.clause_type)}</span></td>
                <td class="text-excerpt">${esc(excerpt)}</td>
                <td>Page ${cl.page_number}</td>
                <td>${(cl.confidence * 100).toFixed(0)}%</td>
            </tr>`;
    });

    let riskCards = '';
    const sortedRisks = [...(report.risk_assessments || [])].sort((a, b) => b.risk_score - a.risk_score);
    sortedRisks.forEach(r => {
        const rc = r.risk_score >= 7 ? 'high' : r.risk_score >= 4 ? 'medium' : 'low';
        const src = r.source_text
            ? `<div class="risk-source">"${esc(r.source_text.slice(0, 200))}${r.source_text.length > 200 ? '...' : ''}"</div>`
            : '';
        riskCards += `
            <div class="risk-card ${rc}">
                <div class="risk-card-header">
                    <span class="risk-card-type">${esc(r.clause_type)}</span>
                    <span class="risk-score-pill ${rc}">${r.risk_score}/10</span>
                </div>
                <p class="risk-rationale">${esc(r.risk_rationale)}</p>
                ${src}
                <div class="risk-tip">
                    <strong>💡 Negotiation Tip</strong>
                    ${esc(r.negotiation_tip)}
                </div>
            </div>`;
    });

    let recItems = '';
    (report.recommendations || []).forEach(r => { recItems += `<li>${esc(r)}</li>`; });

    container.innerHTML = `
        <div class="report-header">
            <h2 class="report-title">📋 ${esc(report.document_name || 'Contract Analysis Report')}</h2>
            <div class="report-meta">
                <span>📄 ${report.page_count || 0} pages</span>
                <span>🔍 ${report.total_clauses_found || 0} clauses</span>
                <span>🕐 ${report.analysis_timestamp ? new Date(report.analysis_timestamp).toLocaleString() : 'Just now'}</span>
                ${report.governing_law ? `<span>⚖ ${esc(report.governing_law).slice(0, 60)}</span>` : ''}
            </div>
            ${report.parties && report.parties.length
                ? `<div class="report-meta"><span>👥 ${report.parties.map(p => esc(p).slice(0, 80)).join(' · ')}</span></div>`
                : ''}
            <div class="risk-gauge">
                <div class="gauge-circle ${riskClass}">${report.overall_risk_score.toFixed(1)}</div>
                <div class="gauge-info">
                    <h4>Overall Risk Score</h4>
                    <p>${esc(report.risk_summary || '')}</p>
                    <div class="risk-counts">
                        <span class="risk-badge high">🔴 ${report.high_risk_count || 0} High</span>
                        <span class="risk-badge medium">🟡 ${report.medium_risk_count || 0} Medium</span>
                        <span class="risk-badge low">🟢 ${report.low_risk_count || 0} Low</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="report-section">
            <h3>📝 Executive Summary</h3>
            <p class="executive-summary">${esc(report.executive_summary || 'No summary available.')}</p>
        </div>
        ${riskCards ? `
        <div class="report-section">
            <h3>⚠️ Risk Assessments (${sortedRisks.length})</h3>
            <div class="risk-cards">${riskCards}</div>
        </div>` : ''}
        ${clauseRows ? `
        <div class="report-section">
            <h3>🔍 Identified Clauses (${report.total_clauses_found || 0})</h3>
            <div style="overflow-x:auto">
                <table class="clause-table">
                    <thead><tr><th>Clause Type</th><th>Text Excerpt</th><th>Location</th><th>Confidence</th></tr></thead>
                    <tbody>${clauseRows}</tbody>
                </table>
            </div>
        </div>` : ''}
        ${recItems ? `
        <div class="report-section">
            <h3>✅ Recommendations</h3>
            <ul class="rec-list">${recItems}</ul>
        </div>` : ''}
        <button class="btn-download" onclick="downloadReport()">📥 Download Word Report (.docx)</button>
    `;
    window._lastReport = report;
}

function downloadReport() {
    const id = window._lastReportId;
    if (!id) { showError('No report to download.'); return; }
    const a = document.createElement('a');
    a.href = `${API}/api/reports/${id}/download`;
    a.download = 'report.docx';
    a.click();
}

// ─── History ───────────────────────────────────────────────
async function loadHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = '<p class="empty-state">Loading...</p>';
    try {
        const res = await fetch(`${API}/api/reports`);
        const data = await res.json();
        if (!data.length) {
            list.innerHTML = '<p class="empty-state">No contracts analyzed yet. Upload one to get started!</p>';
            return;
        }
        list.innerHTML = data.map(r => {
            const rc = (r.overall_risk_score || 0) >= 7 ? 'high' : (r.overall_risk_score || 0) >= 4 ? 'medium' : 'low';
            const date = r.upload_date ? new Date(r.upload_date).toLocaleDateString() : '';
            return `
                <div class="history-card" onclick="loadHistoryReport(${r.id})">
                    <div class="history-info">
                        <h4>${esc(r.filename)}</h4>
                        <span>📄 ${r.page_count || 0} pages · ${date}</span>
                    </div>
                    <div class="history-score risk-badge ${rc}">${(r.overall_risk_score || 0).toFixed(1)}/10</div>
                </div>`;
        }).join('');
    } catch (e) {
        list.innerHTML = '<p class="empty-state">Failed to load history. Is the server running?</p>';
    }
}

async function loadHistoryReport(id) {
    try {
        const res = await fetch(`${API}/api/reports/${id}`);
        const report = await res.json();
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('nav-upload').classList.add('active');
        document.querySelectorAll('.view').forEach(v => { v.classList.remove('active'); v.style.display = 'none'; });
        const uploadView = document.getElementById('view-upload');
        uploadView.style.display = 'block';
        uploadView.classList.add('active');
        document.getElementById('pipeline-progress').style.display = 'none';
        renderReport(report, id);
    } catch (e) {
        showError('Failed to load report.');
    }
}

// ─── Clause Types (CUAD Database) ──────────────────────────
let _clauseData = [];

async function loadClauseTypes() {
    const grid = document.getElementById('clause-grid');
    grid.innerHTML = '<p class="empty-state">Loading CUAD clause types...</p>';
    try {
        const res = await fetch(`${API}/api/clause-types`);
        const data = await res.json();
        _clauseData = data;
        if (!data.length) {
            grid.innerHTML = '<p class="empty-state">No clause types found. Run <code>python setup_cuad.py</code> first.</p>';
            return;
        }
        renderClauseGrid(data);
    } catch (e) {
        grid.innerHTML = '<p class="empty-state">Failed to load clause types. Is the server running?</p>';
    }
}

function renderClauseGrid(data) {
    const grid = document.getElementById('clause-grid');
    grid.innerHTML = data.map(ct => `
        <div class="clause-db-card" onclick="toggleExamples(this, ${ct.id})" data-name="${esc(ct.name).toLowerCase()}">
            <h4>
                ${esc(ct.name)}
                <span class="risk-tag ${ct.risk_category}">${ct.risk_category}</span>
            </h4>
            <p>${esc(ct.description)}</p>
            <div class="example-count">📚 ${ct.example_count || 0} training examples · Click to expand</div>
            <div class="clause-examples" id="examples-${ct.id}"></div>
        </div>
    `).join('');
}

async function toggleExamples(card, clauseId) {
    const container = document.getElementById(`examples-${clauseId}`);
    if (container.classList.contains('open')) {
        container.classList.remove('open');
        return;
    }
    if (container.innerHTML === '') {
        container.innerHTML = '<p>Loading examples...</p>';
        try {
            const res = await fetch(`${API}/api/clause-examples/${clauseId}?limit=5`);
            const data = await res.json();
            if (data.examples && data.examples.length) {
                container.innerHTML = data.examples.map(ex => `
                    <p>"${esc(ex.text_span)}"<span class="ex-source">— ${esc(ex.source_contract)}</span></p>
                `).join('');
            } else {
                container.innerHTML = '<p>No examples available. Run setup_cuad.py to seed the dataset.</p>';
            }
        } catch (e) {
            container.innerHTML = '<p>Failed to load examples.</p>';
        }
    }
    container.classList.add('open');
}

// Clause search
const searchInput = document.getElementById('clause-search');
if (searchInput) {
    searchInput.addEventListener('input', () => {
        const q = searchInput.value.toLowerCase().trim();
        if (!q) { renderClauseGrid(_clauseData); return; }
        const filtered = _clauseData.filter(ct =>
            ct.name.toLowerCase().includes(q) ||
            ct.description.toLowerCase().includes(q) ||
            ct.risk_category.toLowerCase().includes(q)
        );
        renderClauseGrid(filtered);
    });
}

// ─── Utilities ─────────────────────────────────────────────
function esc(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function showError(msg) {
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}
