// API Configuration
const API_BASE_URL = 'http://localhost:8000';

let currentCandidates = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    const searchForm = document.getElementById('searchForm');
    searchForm.addEventListener('submit', handleSearch);
}

// Load Statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const stats = await response.json();
        
        document.getElementById('totalCandidates').textContent = stats.total_candidates;
        document.getElementById('openToWork').textContent = stats.candidates_open_to_work;
        document.getElementById('totalJobs').textContent = stats.total_jobs;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Handle Search Form
async function handleSearch(event) {
    event.preventDefault();
    
    const jobDescription = document.getElementById('jobDescription').value;
    const location = document.getElementById('location').value;
    const limit = parseInt(document.getElementById('limit').value);
    
    // Show loading
    const loading = document.getElementById('loading');
    const resultsSection = document.getElementById('resultsSection');
    const searchBtn = document.getElementById('searchBtn');
    
    loading.classList.remove('hidden');
    resultsSection.style.display = 'none';
    searchBtn.disabled = true;
    searchBtn.textContent = '🔍 Searching...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                job_description: jobDescription,
                location: location,
                limit: limit
            })
        });
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const candidates = await response.json();
        currentCandidates = candidates;
        
        displayCandidates(candidates);
        loadStats(); // Refresh stats
        
    } catch (error) {
        console.error('Error during search:', error);
        alert('Search failed. Please try again. Make sure the backend server is running.');
    } finally {
        loading.classList.add('hidden');
        resultsSection.style.display = 'block';
        searchBtn.disabled = false;
        searchBtn.textContent = '🚀 Find Candidates';
    }
}

// Display Candidates
function displayCandidates(candidates) {
    const candidatesList = document.getElementById('candidatesList');
    
    if (!candidates || candidates.length === 0) {
        candidatesList.innerHTML = '<p class="empty-state">No candidates found. Try adjusting your search criteria.</p>';
        return;
    }
    
    candidatesList.innerHTML = candidates.map(candidate => {
        // Parse skills if it's a string
        let skills = candidate.skills;
        if (typeof skills === 'string') {
            try {
                skills = JSON.parse(skills);
            } catch {
                skills = [];
            }
        }
        
        return `
            <div class="candidate-card">
                <div class="candidate-header">
                    <div class="candidate-info">
                        <h3>${candidate.name || 'Unknown'}</h3>
                        ${candidate.email ? `<p class="candidate-email">📧 ${candidate.email}</p>` : ''}
                    </div>
                    <div class="match-score">${candidate.match_score || 0}%</div>
                </div>
                
                <div class="candidate-details">
                    ${candidate.location ? `
                        <div class="detail-row">
                            <span class="detail-label">📍 Location:</span>
                            <span class="detail-value">${candidate.location}</span>
                        </div>
                    ` : ''}
                    
                    ${candidate.experience_years ? `
                        <div class="detail-row">
                            <span class="detail-label">💼 Experience:</span>
                            <span class="detail-value">${candidate.experience_years} years</span>
                        </div>
                    ` : ''}
                    
                    ${candidate.open_to_work ? `
                        <div class="detail-row">
                            <span class="detail-label">Status:</span>
                            <span class="badge badge-success">✅ Open to Work</span>
                        </div>
                    ` : ''}
                    
                    ${candidate.bio ? `
                        <div class="detail-row">
                            <span class="detail-label">📝 Bio:</span>
                            <span class="detail-value">${candidate.bio.substring(0, 200)}${candidate.bio.length > 200 ? '...' : ''}</span>
                        </div>
                    ` : ''}
                </div>
                
                ${skills && skills.length > 0 ? `
                    <div class="skills-container">
                        ${skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                    </div>
                ` : ''}
                
                <div class="candidate-links">
                    ${candidate.github_url ? `
                        <a href="${candidate.github_url}" target="_blank" class="link-btn">
                            🐙 GitHub
                        </a>
                    ` : ''}
                    ${candidate.linkedin_url ? `
                        <a href="${candidate.linkedin_url}" target="_blank" class="link-btn">
                            💼 LinkedIn
                        </a>
                    ` : ''}
                    ${candidate.portfolio_url ? `
                        <a href="${candidate.portfolio_url}" target="_blank" class="link-btn">
                            🌐 Portfolio
                        </a>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Load All Candidates
async function loadAllCandidates() {
    const loading = document.getElementById('loading');
    const resultsSection = document.getElementById('resultsSection');
    
    loading.classList.remove('hidden');
    resultsSection.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/candidates?limit=100`);
        const candidates = await response.json();
        currentCandidates = candidates;
        
        displayCandidates(candidates);
    } catch (error) {
        console.error('Error loading candidates:', error);
        alert('Failed to load candidates');
    } finally {
        loading.classList.add('hidden');
        resultsSection.style.display = 'block';
    }
}

// Export to CSV
function exportToCSV() {
    if (!currentCandidates || currentCandidates.length === 0) {
        alert('No candidates to export');
        return;
    }
    
    // Create CSV content
    const headers = ['Name', 'Email', 'Location', 'Skills', 'Match Score', 'Experience Years', 'Open to Work', 'GitHub', 'LinkedIn', 'Bio'];
    const csvRows = [headers.join(',')];
    
    currentCandidates.forEach(candidate => {
        let skills = candidate.skills;
        if (typeof skills === 'string') {
            try {
                skills = JSON.parse(skills);
            } catch {
                skills = [];
            }
        }
        
        const row = [
            `"${candidate.name || ''}"`,
            `"${candidate.email || ''}"`,
            `"${candidate.location || ''}"`,
            `"${Array.isArray(skills) ? skills.join('; ') : ''}"`,
            candidate.match_score || 0,
            candidate.experience_years || 0,
            candidate.open_to_work ? 'Yes' : 'No',
            `"${candidate.github_url || ''}"`,
            `"${candidate.linkedin_url || ''}"`,
            `"${(candidate.bio || '').replace(/"/g, '""')}"` // Escape quotes
        ];
        csvRows.push(row.join(','));
    });
    
    const csvContent = csvRows.join('\n');
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `talentradar_candidates_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
