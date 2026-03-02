const API_URL = ''; // Same origin
const API_KEY = 'testkey'; // Dynamic key for authentication

// State
let currentPage = 1;
const pageSize = 10;

// DOM Elements
const recordsBody = document.getElementById('records-body');
const insightsContent = document.getElementById('insights-content');
const statsRow = document.getElementById('stats-row');
const uploadStatus = document.getElementById('upload-status');
const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const filterCompany = document.getElementById('filter-company');
const filterYear = document.getElementById('filter-year');
const prevPageBtn = document.getElementById('prev-page');
const nextPageBtn = document.getElementById('next-page');
const pageInfo = document.getElementById('page-info');

// Modal Elements
const modal = document.getElementById('detail-modal');
const modalBody = document.getElementById('modal-body');
const closeModal = document.querySelector('.close-modal');

/**
 * Initialize
 */
document.addEventListener('DOMContentLoaded', () => {
    fetchRecords();
    fetchInsights();
    setupEventListeners();
});

function setupEventListeners() {
    // Buttons
    document.getElementById('refresh-btn').addEventListener('click', () => {
        fetchRecords();
        fetchInsights();
    });

    document.getElementById('generate-insights-btn').addEventListener('click', fetchInsights);
    
    document.getElementById('browse-btn').addEventListener('click', () => fileInput.click());

    // File Upload
    fileInput.addEventListener('change', (e) => handleFileUpload(e.target.files[0]));

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFileUpload(e.dataTransfer.files[0]);
    });

    // Filters
    filterCompany.addEventListener('input', debounce(() => {
        currentPage = 1;
        fetchRecords();
    }, 500));

    filterYear.addEventListener('change', () => {
        currentPage = 1;
        fetchRecords();
    });

    // Pagination
    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchRecords();
        }
    });

    nextPageBtn.addEventListener('click', () => {
        currentPage++;
        fetchRecords();
    });

    // Modal
    closeModal.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });
}

/**
 * API Calls
 */

async function fetchRecords() {
    toggleLoading('records-section', true);
    
    let url = `/records?page=${currentPage}&page_size=${pageSize}`;
    if (filterCompany.value) url += `&company_name=${encodeURIComponent(filterCompany.value)}`;
    if (filterYear.value) url += `&report_year=${filterYear.value}`;

    try {
        const response = await fetch(url, {
            headers: { 'X-API-Key': API_KEY }
        });
        
        if (!response.ok) throw new Error('Failed to fetch records');
        
        const data = await response.json();
        renderRecords(data.results);
        updatePagination(data.total);
    } catch (error) {
        console.error(error);
        recordsBody.innerHTML = `<tr><td colspan="7" class="placeholder-text">Error loading records.</td></tr>`;
    } finally {
        toggleLoading('records-section', false);
    }
}

async function fetchInsights() {
    toggleLoading('insights-section', true);
    insightsContent.innerHTML = `<p class="placeholder-text">Analyzing data with Gemini...</p>`;

    try {
        const response = await fetch('/insights', {
            headers: { 'X-API-Key': API_KEY }
        });
        
        if (!response.ok) throw new Error('Failed to fetch insights');
        
        const data = await response.json();
        renderInsights(data);
    } catch (error) {
        console.error(error);
        insightsContent.innerHTML = `<p class="placeholder-text" style="color:var(--danger)">Error generating insights.</p>`;
    } finally {
        toggleLoading('insights-section', false);
    }
}

async function handleFileUpload(file) {
    if (!file) return;

    uploadStatus.textContent = `Uploading ${file.name}...`;
    uploadStatus.className = 'status-message';
    toggleLoading('upload-section', true);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            headers: { 'X-API-Key': API_KEY },
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            uploadStatus.textContent = 'Upload successful!';
            uploadStatus.classList.add('success');
            fetchRecords();
            fetchInsights();
        } else {
            uploadStatus.textContent = result.detail || 'Upload failed.';
            uploadStatus.classList.add('danger');
        }
    } catch (error) {
        uploadStatus.textContent = 'Network error.';
        uploadStatus.classList.add('danger');
    } finally {
        toggleLoading('upload-section', false);
        setTimeout(() => { uploadStatus.textContent = ''; }, 5000);
    }
}

async function showRecordDetail(id) {
    try {
        const response = await fetch(`/records/${id}`, {
            headers: { 'X-API-Key': API_KEY }
        });
        const data = await response.json();
        renderDetailModal(data);
        modal.style.display = 'flex';
    } catch (error) {
        alert('Could not load details');
    }
}

/**
 * Rendering
 */

function renderRecords(records) {
    recordsBody.innerHTML = '';
    
    if (records.length === 0) {
        recordsBody.innerHTML = `<tr><td colspan="7" class="placeholder-text">No records found.</td></tr>`;
        return;
    }

    records.forEach(rec => {
        const tr = document.createElement('tr');
        const confClass = rec.confidence_score >= 0.8 ? 'conf-high' : (rec.confidence_score >= 0.5 ? 'conf-med' : 'conf-low');
        
        tr.innerHTML = `
            <td>${rec.company_name || 'N/A'}</td>
            <td>${rec.report_year || 'N/A'}</td>
            <td>${rec.emissions_co2_tonnes?.toLocaleString() || 'N/A'}</td>
            <td>${rec.energy_usage_mwh?.toLocaleString() || 'N/A'}</td>
            <td>${rec.water_usage_m3?.toLocaleString() || 'N/A'}</td>
            <td><span class="confidence-badge ${confClass}">${(rec.confidence_score * 100).toFixed(0)}%</span></td>
            <td><button class="btn-secondary btn-small" onclick="showRecordDetail(${rec.id})">View</button></td>
        `;
        recordsBody.appendChild(tr);
    });
}

function renderInsights(data) {
    insightsContent.innerHTML = `<p>${data.summary}</p>`;
    
    statsRow.innerHTML = `
        <div class="stat-item">
            <span class="stat-label">Total Records</span>
            <span class="stat-value">${data.record_count}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Avg CO2 (tonnes)</span>
            <span class="stat-value">${data.avg_emissions_co2_tonnes?.toLocaleString() || '0'}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Avg Energy (MWh)</span>
            <span class="stat-value">${data.avg_energy_usage_mwh?.toLocaleString() || '0'}</span>
        </div>
    `;
}

function renderDetailModal(data) {
    modalBody.innerHTML = `
        <div class="detail-grid">
            <div class="detail-item">
                <h4>Company</h4>
                <p>${data.company_name || 'N/A'}</p>
            </div>
            <div class="detail-item">
                <h4>Report Year</h4>
                <p>${data.report_year || 'N/A'}</p>
            </div>
            <div class="detail-item">
                <h4>Carbon Emissions</h4>
                <p>${data.emissions_co2_tonnes?.toLocaleString() || 'N/A'} tCO2e</p>
            </div>
            <div class="detail-item">
                <h4>Energy Usage</h4>
                <p>${data.energy_usage_mwh?.toLocaleString() || 'N/A'} MWh</p>
            </div>
            <div class="detail-item">
                <h4>Water Consumption</h4>
                <p>${data.water_usage_m3?.toLocaleString() || 'N/A'} m3</p>
            </div>
            <div class="detail-item">
                <h4>Confidence Score</h4>
                <p>${(data.confidence_score * 100).toFixed(1)}%</p>
            </div>
            <div class="detail-full">
                <h4>Sustainability Targets</h4>
                <p>${data.sustainability_targets || 'No targets specified.'}</p>
            </div>
            <div class="detail-full">
                <h4>Raw Text Excerpt</h4>
                <div class="raw-text">${data.raw_text_excerpt || 'N/A'}</div>
            </div>
        </div>
    `;
}

/**
 * Utilities
 */

function toggleLoading(sectionId, isLoading) {
    const el = document.getElementById(sectionId);
    if (isLoading) el.classList.add('loading');
    else el.classList.remove('loading');
}

function updatePagination(total) {
    const totalPages = Math.ceil(total / pageSize);
    pageInfo.textContent = `Page ${currentPage} of ${totalPages || 1}`;
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage >= totalPages || total === 0;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
