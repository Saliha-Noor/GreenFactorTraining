const API = '';

// Run warning screen countdown on page load
function startWarningCountdown() {
    const warningScreen = document.getElementById('warning-screen');
    const timerEl = document.getElementById('countdown-timer');
    const progressEl = document.getElementById('countdown-progress');
    if (!warningScreen || !timerEl || !progressEl) return;

    let timeLeft = 7;
    timerEl.textContent = timeLeft;

    const dismissWarning = () => {
        clearInterval(interval);
        warningScreen.classList.add('hidden');
        setTimeout(() => {
            warningScreen.style.display = 'none';
        }, 500);
    };

    const skipBtn = document.getElementById('skip-warning-btn');
    if (skipBtn) {
        skipBtn.addEventListener('click', dismissWarning);
    }

    const interval = setInterval(() => {
        timeLeft--;
        timerEl.textContent = timeLeft;
        progressEl.style.width = `${((7 - timeLeft) / 7) * 100}%`;

        if (timeLeft <= 0) {
            dismissWarning();
        }
    }, 1000);
}

// Start countdown
startWarningCountdown();

// Load statistics from database
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

// Animate numbers counting up
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

// Initialize stats loader
loadStats();

// Set up page navigation buttons
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

// Set default view on load
document.getElementById('view-upload').style.display = 'block';

// Get elements for drag and drop
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

// Handle click trigger for file upload
dropZone.addEventListener('click', () => fileInput.click());

// Handle dragover hover effect
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });

// Handle dragleave hover removal
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

// Handle dropped files
dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.name.toLowerCase().endsWith('.pdf')) uploadFile(file);
    else showError('Please upload a PDF file.');
});

// Handle file input selection change
fileInput.addEventListener('change', () => { if (fileInput.files[0]) uploadFile(fileInput.files[0]); });

// Upload selected contract PDF file to server
async function uploadFile(file) {
    const progress = document.getElementById('pipeline-progress');
    const reportContainer = document.getElementById('report-container');
    progress.style.display = 'block';
    reportContainer.style.display = 'none';

    const steps = ['step-parser', 'step-classifier', 'step-risk', 'step-missing', 'step-conflict', 'step-report'];
    const statusTexts = {
        'parser': 'Agent 1: Extracting contract text from PDF...',
        'classifier': 'Agent 2: Running CUAD clause classifications...',
        'risk_analyzer': 'Agent 3: Calculating risk scores and rationales...',
        'missing_clause_detector': 'Agent 4: Detecting missing and weak clauses...',
        'conflict_detector': 'Agent 5: Detecting logical conflicts and contradictions...',
        'report_generator': 'Agent 6: Compiling executive summary and Word report...'
    };

    // Reset progress items in UI
    steps.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.remove('active', 'done');
            el.querySelector('.step-status').textContent = 'Waiting...';
            el.querySelector('.step-fill').style.width = '0%';
        }
    });

    // Make first agent step active
    const parserEl = document.getElementById('step-parser');
    if (parserEl) {
        parserEl.classList.add('active');
        parserEl.querySelector('.step-status').textContent = statusTexts['parser'];
        parserEl.querySelector('.step-fill').style.width = '50%';
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Send file upload POST request
        const res = await fetch(`${API}/api/upload`, { method: 'POST', body: formData });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(err.detail || 'Upload failed');
        }

        const uploadData = await res.json();
        const taskId = uploadData.task_id;

        let pollCount = 0;
        const maxPolls = 300;
        const pollInterval = 1500;

        // Poll pipeline status in a loop
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
                const currentAgent = task.current_agent;
                updateProgressUI(currentAgent);
                setTimeout(pollStatus, pollInterval);
            } else if (task.status === 'complete') {
                // Mark all steps complete
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

        // Start polling task progress
        setTimeout(pollStatus, pollInterval);

    } catch (err) {
        showError(err.message);
        progress.style.display = 'none';
    }
}

// Update pipeline step progress indicators in UI
function updateProgressUI(currentAgent) {
    const steps = ['step-parser', 'step-classifier', 'step-risk', 'step-missing', 'step-conflict', 'step-report'];
    const agentMap = {
        'starting': 0,
        'parser': 0,
        'classifier': 1,
        'risk_analyzer': 2,
        'missing_clause_detector': 3,
        'conflict_detector': 4,
        'report_generator': 5
    };

    const activeIdx = agentMap[currentAgent] !== undefined ? agentMap[currentAgent] : 0;

    for (let i = 0; i < steps.length; i++) {
        const el = document.getElementById(steps[i]);
        if (!el) continue;

        if (i < activeIdx) {
            // Update completed steps
            el.classList.remove('active');
            el.classList.add('done');
            el.querySelector('.step-status').textContent = 'Complete ✓';
            el.querySelector('.step-fill').style.width = '100%';
        } else if (i === activeIdx) {
            // Update active step
            el.classList.remove('done');
            el.classList.add('active');
            
            const statusTexts = {
                'step-parser': 'Agent 1: Extracting contract text from PDF...',
                'step-classifier': 'Agent 2: Running CUAD clause classifications...',
                'step-risk': 'Agent 3: Calculating risk scores and rationales...',
                'step-missing': 'Agent 4: Detecting missing and weak clauses...',
                'step-conflict': 'Agent 5: Detecting logical conflicts and contradictions...',
                'step-report': 'Agent 6: Compiling executive summary and Word report...'
            };
            
            el.querySelector('.step-status').textContent = statusTexts[steps[i]];
            el.querySelector('.step-fill').style.width = '50%';
        } else {
            // Update waiting steps
            el.classList.remove('active', 'done');
            el.querySelector('.step-status').textContent = 'Waiting...';
            el.querySelector('.step-fill').style.width = '0%';
        }
    }
}

// Render generated report data inside container
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

    // Build missing clause section HTML
    const missingAnalysis = report.missing_clause_analysis || [];
    const completeness = report.completeness_score || 0;
    const contractType = report.contract_type || 'Unknown';
    const missingItems = missingAnalysis.filter(m => m.status === 'missing');
    const weakItems = missingAnalysis.filter(m => m.status === 'weakly_defined');

    const compClass = completeness >= 80 ? 'comp-high' : completeness >= 50 ? 'comp-medium' : 'comp-low';
    const compLabel = completeness >= 80 ? 'Excellent' : completeness >= 50 ? 'Moderate' : 'Low — Review Required';

    let missingClauseCards = '';
    missingItems.forEach(item => {
        missingClauseCards += `
            <div class="missing-clause-card missing">
                <div class="missing-clause-header">
                    <span class="missing-clause-type">${esc(item.clause_type)}</span>
                    <span class="missing-status-badge badge-missing">MISSING</span>
                </div>
                <div class="missing-clause-body">
                    <div class="missing-detail">
                        <strong>📌 Why It Matters:</strong>
                        <p>${esc(item.importance)}</p>
                    </div>
                    <div class="missing-detail">
                        <strong>⚠️ Legal Risks:</strong>
                        <p>${esc(item.legal_risks)}</p>
                    </div>
                    <div class="missing-detail recommended">
                        <strong>📝 Recommended Clause:</strong>
                        <p class="recommended-text">${esc(item.recommended_clause)}</p>
                    </div>
                </div>
            </div>`;
    });

    let weakClauseCards = '';
    weakItems.forEach(item => {
        weakClauseCards += `
            <div class="missing-clause-card weak">
                <div class="missing-clause-header">
                    <span class="missing-clause-type">${esc(item.clause_type)}</span>
                    <span class="missing-status-badge badge-weak">WEAKLY DEFINED</span>
                </div>
                <div class="missing-clause-body">
                    <div class="missing-detail">
                        <strong>📌 Why It Matters:</strong>
                        <p>${esc(item.importance)}</p>
                    </div>
                    <div class="missing-detail">
                        <strong>⚠️ Legal Risks:</strong>
                        <p>${esc(item.legal_risks)}</p>
                    </div>
                    <div class="missing-detail recommended">
                        <strong>📝 Strengthened Clause:</strong>
                        <p class="recommended-text">${esc(item.recommended_clause)}</p>
                    </div>
                </div>
            </div>`;
    });

    // Build conflict detection section HTML
    const conflictAnalysis = report.conflict_analysis || [];
    const consistencyScore = report.consistency_score !== undefined ? report.consistency_score : 100.0;
    const consistencyExplanation = report.consistency_explanation || '';

    const consistClass = consistencyScore >= 80 ? 'comp-high' : consistencyScore >= 50 ? 'comp-medium' : 'comp-low';
    const consistLabel = consistencyScore >= 80 ? 'High Consistency' : consistencyScore >= 50 ? 'Moderate Conflicts' : 'Highly Contradictory';

    let conflictCards = '';
    conflictAnalysis.forEach(c => {
        const severityClass = (c.severity || 'Medium').toLowerCase();
        let clausesHtml = '';
        (c.original_clauses || []).forEach((cl, i) => {
            const num = (c.clause_numbers && c.clause_numbers[i]) ? c.clause_numbers[i] : '?';
            clausesHtml += `
                <div class="conflict-clause-excerpt">
                    <strong>Clause Excerpt (Clause ${num}):</strong>
                    <p>"${esc(cl)}"</p>
                </div>
            `;
        });
        
        conflictCards += `
            <div class="conflict-card-ui ${severityClass}">
                <div class="conflict-card-ui-header">
                    <span class="conflict-card-ui-category">${esc(c.conflict_category)} Conflict</span>
                    <span class="conflict-severity-badge ${severityClass}">${esc(c.severity.toUpperCase())}</span>
                </div>
                <div class="conflict-card-ui-body">
                    <div class="conflict-clauses-list">
                        ${clausesHtml}
                    </div>
                    <div class="conflict-field">
                        <strong>📌 Why They Conflict:</strong>
                        <p>${esc(c.why_conflict)}</p>
                    </div>
                    <div class="conflict-field">
                        <strong>⚖ Which Clause is Legally Stronger:</strong>
                        <p>${esc(c.stronger_clause)}</p>
                    </div>
                    <div class="conflict-field">
                        <strong>⚠️ Potential Legal Consequences:</strong>
                        <p class="consequences-text">${esc(c.consequences)}</p>
                    </div>
                    <div class="conflict-field harmonized">
                        <strong>📝 Suggested Harmonized Resolution:</strong>
                        <p class="harmonized-text">${esc(c.harmonized_clause)}</p>
                    </div>
                    <div class="conflict-card-ui-footer">
                        <span>Confidence Score: ${c.confidence_score}%</span>
                        <span>ID: ${esc(c.conflict_id)}</span>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = `
        <div class="report-header">
            <h2 class="report-title">📋 ${esc(report.document_name || 'Contract Analysis Report')}</h2>
            <div class="report-meta">
                <span>📄 ${report.page_count || 0} pages</span>
                <span>🔍 ${report.total_clauses_found || 0} clauses</span>
                <span>📑 ${esc(contractType)}</span>
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

        <div class="report-section completeness-section">
            <h3>🧩 Clause Completeness</h3>
            <div class="completeness-overview">
                <div class="completeness-gauge ${compClass}">
                    <div class="completeness-circle">
                        <span class="completeness-value">${completeness.toFixed(1)}%</span>
                        <span class="completeness-label">${compLabel}</span>
                    </div>
                </div>
                <div class="completeness-stats">
                    <div class="comp-stat">
                        <span class="comp-stat-value comp-present">${report.total_clauses_found || 0}</span>
                        <span class="comp-stat-label">Present</span>
                    </div>
                    <div class="comp-stat">
                        <span class="comp-stat-value comp-missing">${missingItems.length}</span>
                        <span class="comp-stat-label">Missing</span>
                    </div>
                    <div class="comp-stat">
                        <span class="comp-stat-value comp-weak">${weakItems.length}</span>
                        <span class="comp-stat-label">Weak</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="report-section consistency-section">
            <h3>⚔️ Contract Consistency Report</h3>
            <div class="completeness-overview">
                <div class="completeness-gauge ${consistClass}">
                    <div class="completeness-circle">
                        <span class="completeness-value">${consistencyScore.toFixed(1)}/100</span>
                        <span class="completeness-label">${consistLabel}</span>
                    </div>
                </div>
                <div class="completeness-stats">
                    <div class="consistency-explanation-box">
                        <p class="consistency-explanation-text"><strong>Analysis:</strong> ${esc(consistencyExplanation)}</p>
                    </div>
                    <div class="comp-stat">
                        <span class="comp-stat-value comp-missing">${conflictAnalysis.length}</span>
                        <span class="comp-stat-label">Conflicts Found</span>
                    </div>
                </div>
            </div>
        </div>

        ${conflictCards ? `
        <div class="report-section">
            <h3>⚠️ Detected Conflicts & Contradictions (${conflictAnalysis.length})</h3>
            <div class="conflict-cards-group">${conflictCards}</div>
        </div>` : ''}

        ${missingClauseCards || weakClauseCards ? `
        <div class="report-section">
            <h3>🚫 Missing & Weakly Defined Clauses (${missingAnalysis.length})</h3>
            ${missingClauseCards ? `<div class="missing-clause-group">${missingClauseCards}</div>` : ''}
            ${weakClauseCards ? `<div class="missing-clause-group">${weakClauseCards}</div>` : ''}
        </div>` : ''}

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
            <div class="confidence-info-box">
                <span class="info-icon">💡</span>
                <div class="info-text">
                    <strong>What is a Confidence Score?</strong> 
                    <span>This represents the AI's mathematical certainty (from 0% to 100%) that the detected clause matches the definition of that clause type under the CUAD standard. High confidence indicates a strong match, while low confidence suggests the text warrants closer human inspection.</span>
                </div>
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

// Download report Word file
function downloadReport() {
    const id = window._lastReportId;
    if (!id) { showError('No report to download.'); return; }
    const a = document.createElement('a');
    a.href = `${API}/api/reports/${id}/download`;
    a.download = 'report.docx';
    a.click();
}

// Load analysis history from backend
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

// Load specific report from history list selection
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

// Track clause data array
let _clauseData = [];

// Load clause types database on request
async function loadClauseTypes() {
    const grid = document.getElementById('clause-grid');
    grid.innerHTML = '<p class="empty-state">Loading CUAD clause types...</p>';
    try {
        const res = await fetch(`${API}/api/clause-types`);
        const data = await res.json();
        _clauseData = data;
        if (!data.length) {
            grid.innerHTML = '<p class="empty-state">No clause types found.</p>';
            return;
        }
        renderClauseGrid(data);
    } catch (e) {
        grid.innerHTML = '<p class="empty-state">Failed to load clause types. Is the server running?</p>';
    }
}

// Render grid layout for CUAD clauses list
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

// Expand or collapse training examples for clause cards
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
                container.innerHTML = '<p>No examples available.</p>';
            }
        } catch (e) {
            container.innerHTML = '<p>Failed to load examples.</p>';
        }
    }
    container.classList.add('open');
}

// Enable filtering of clause list by search query
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

// Escape special characters to prevent HTML injection
function esc(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Show error messages as toast notifications
function showError(msg) {
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}
