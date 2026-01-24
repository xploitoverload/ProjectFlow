/**
 * Version/Release Management System
 * Version planning, release notes, burndown chart
 */

class VersionManagement {
    constructor() {
        this.versions = [];
        this.selectedVersion = null;
        this.burndownChart = null;
        
        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
    }

    createModal() {
        const modalHTML = `
            <div id="versionModal" class="version-modal" style="display: none;">
                <div class="version-modal-backdrop"></div>
                <div class="version-modal-container">
                    <div class="version-modal-header">
                        <h2>Versions & Releases</h2>
                        <div class="header-actions">
                            <button class="btn btn-primary btn-sm" id="createVersionBtn">
                                <i data-lucide="plus"></i>
                                Create Version
                            </button>
                            <button class="btn-icon" id="closeVersionModal">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    </div>

                    <div class="version-modal-body">
                        <!-- Versions Sidebar -->
                        <div class="versions-sidebar">
                            <div class="sidebar-tabs">
                                <button class="sidebar-tab active" data-tab="unreleased">Unreleased</button>
                                <button class="sidebar-tab" data-tab="released">Released</button>
                            </div>
                            <div class="versions-list" id="versionsList">
                                <!-- Populated by JS -->
                            </div>
                        </div>

                        <!-- Version Details -->
                        <div class="version-content" id="versionContent">
                            <div class="empty-state">
                                <i data-lucide="package"></i>
                                <p>Select a version to view details</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Create/Edit Version Dialog -->
            <div id="versionDialog" class="version-dialog" style="display: none;">
                <div class="version-dialog-backdrop"></div>
                <div class="version-dialog-container">
                    <div class="version-dialog-header">
                        <h3 id="versionDialogTitle">Create Version</h3>
                        <button class="btn-icon-sm" onclick="versionManagement.closeVersionDialog()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="version-dialog-body">
                        <div class="form-group">
                            <label>Version Name</label>
                            <input type="text" class="form-input" id="versionName" placeholder="e.g., v1.0.0">
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea class="form-input" id="versionDescription" rows="3" 
                                      placeholder="Brief description of this release"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Release Date</label>
                            <input type="date" class="form-input" id="versionReleaseDate">
                        </div>
                    </div>
                    <div class="version-dialog-footer">
                        <button class="btn btn-ghost" onclick="versionManagement.closeVersionDialog()">Cancel</button>
                        <button class="btn btn-primary" id="saveVersionBtn">Save Version</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        document.getElementById('closeVersionModal')?.addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('createVersionBtn')?.addEventListener('click', () => {
            this.openVersionDialog();
        });

        document.getElementById('saveVersionBtn')?.addEventListener('click', () => {
            this.saveVersion();
        });

        // Sidebar tabs
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.sidebar-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                this.filterVersions(e.target.dataset.tab);
            });
        });
    }

    openModal() {
        document.getElementById('versionModal').style.display = 'block';
        this.loadVersions();
    }

    closeModal() {
        document.getElementById('versionModal').style.display = 'none';
        this.destroyChart();
    }

    async loadVersions() {
        try {
            const response = await fetch('/api/versions');
            if (response.ok) {
                this.versions = await response.json();
                this.renderVersionsList();
                
                if (this.versions.length > 0 && !this.selectedVersion) {
                    this.selectVersion(this.versions[0].id);
                }
            }
        } catch (error) {
            console.error('Failed to load versions:', error);
        }
    }

    filterVersions(filter) {
        // Filter and re-render based on released status
        this.renderVersionsList(filter);
    }

    renderVersionsList(filter = 'unreleased') {
        const container = document.getElementById('versionsList');
        const filtered = this.versions.filter(v => 
            filter === 'released' ? v.released : !v.released
        );

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-sidebar">
                    <p>No ${filter} versions</p>
                </div>
            `;
            return;
        }

        container.innerHTML = filtered.map(version => `
            <div class="version-item ${this.selectedVersion === version.id ? 'active' : ''}" 
                 onclick="versionManagement.selectVersion('${version.id}')">
                <div class="version-icon">
                    <i data-lucide="${version.released ? 'check-circle' : 'circle'}"></i>
                </div>
                <div class="version-info">
                    <div class="version-name">${version.name}</div>
                    <div class="version-meta">
                        ${version.releaseDate ? new Date(version.releaseDate).toLocaleDateString() : 'No date'}
                    </div>
                </div>
                <div class="version-progress">
                    <div class="progress-ring">
                        <svg width="32" height="32">
                            <circle cx="16" cy="16" r="14" fill="none" stroke="var(--color-bg-subtle)" stroke-width="2"/>
                            <circle cx="16" cy="16" r="14" fill="none" stroke="var(--color-primary)" stroke-width="2"
                                    stroke-dasharray="${(version.progress || 0) * 87.96} 87.96" 
                                    transform="rotate(-90 16 16)"/>
                        </svg>
                        <span class="progress-text">${Math.round((version.progress || 0) * 100)}%</span>
                    </div>
                </div>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    selectVersion(versionId) {
        this.selectedVersion = versionId;
        this.renderVersionsList();
        this.renderVersionDetails();
    }

    renderVersionDetails() {
        const version = this.versions.find(v => v.id === this.selectedVersion);
        if (!version) return;

        const contentHTML = `
            <div class="version-details">
                <div class="version-header">
                    <div class="version-title">
                        <h2>${version.name}</h2>
                        <div class="version-status ${version.released ? 'released' : 'unreleased'}">
                            ${version.released ? 'Released' : 'Unreleased'}
                        </div>
                    </div>
                    <div class="version-actions">
                        <button class="btn btn-ghost btn-sm" onclick="versionManagement.editVersion('${version.id}')">
                            <i data-lucide="edit"></i>
                            Edit
                        </button>
                        ${!version.released ? `
                            <button class="btn btn-primary btn-sm" onclick="versionManagement.releaseVersion('${version.id}')">
                                <i data-lucide="rocket"></i>
                                Release
                            </button>
                        ` : ''}
                    </div>
                </div>

                <!-- Summary Stats -->
                <div class="version-stats">
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i data-lucide="calendar"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Release Date</div>
                            <div class="stat-value">${version.releaseDate ? new Date(version.releaseDate).toLocaleDateString() : 'Not set'}</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i data-lucide="list"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Total Issues</div>
                            <div class="stat-value">${version.totalIssues || 0}</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i data-lucide="check-circle"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Completed</div>
                            <div class="stat-value">${version.completedIssues || 0}</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i data-lucide="trending-up"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Progress</div>
                            <div class="stat-value">${Math.round((version.progress || 0) * 100)}%</div>
                        </div>
                    </div>
                </div>

                <!-- Tabs -->
                <div class="version-tabs">
                    <button class="version-tab active" data-tab="overview">
                        <i data-lucide="info"></i>
                        Overview
                    </button>
                    <button class="version-tab" data-tab="burndown">
                        <i data-lucide="trending-down"></i>
                        Burndown
                    </button>
                    <button class="version-tab" data-tab="notes">
                        <i data-lucide="file-text"></i>
                        Release Notes
                    </button>
                    <button class="version-tab" data-tab="issues">
                        <i data-lucide="list"></i>
                        Issues
                    </button>
                </div>

                <!-- Tab Content -->
                <div class="version-tab-content">
                    <div class="tab-pane active" data-pane="overview">
                        ${this.renderOverviewPane(version)}
                    </div>
                    <div class="tab-pane" data-pane="burndown">
                        ${this.renderBurndownPane(version)}
                    </div>
                    <div class="tab-pane" data-pane="notes">
                        ${this.renderNotesPane(version)}
                    </div>
                    <div class="tab-pane" data-pane="issues">
                        ${this.renderIssuesPane(version)}
                    </div>
                </div>
            </div>
        `;

        document.getElementById('versionContent').innerHTML = contentHTML;

        // Setup tab switching
        document.querySelectorAll('.version-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                this.switchTab(tabName, version);
            });
        });

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderOverviewPane(version) {
        return `
            <div class="overview-content">
                <div class="overview-section">
                    <h3>Description</h3>
                    <p>${version.description || 'No description provided'}</p>
                </div>

                <div class="overview-section">
                    <h3>Issue Breakdown</h3>
                    <div class="issue-breakdown">
                        <div class="breakdown-item">
                            <div class="breakdown-color bug"></div>
                            <div class="breakdown-label">Bug</div>
                            <div class="breakdown-count">${version.issuesByType?.bug || 0}</div>
                        </div>
                        <div class="breakdown-item">
                            <div class="breakdown-color feature"></div>
                            <div class="breakdown-label">Feature</div>
                            <div class="breakdown-count">${version.issuesByType?.feature || 0}</div>
                        </div>
                        <div class="breakdown-item">
                            <div class="breakdown-color task"></div>
                            <div class="breakdown-label">Task</div>
                            <div class="breakdown-count">${version.issuesByType?.task || 0}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderBurndownPane(version) {
        // Render burndown chart after DOM is ready
        setTimeout(() => {
            this.renderBurndownChart(version);
        }, 100);

        return `
            <div class="burndown-content">
                <div class="chart-container">
                    <canvas id="burndownChart"></canvas>
                </div>
            </div>
        `;
    }

    renderNotesPane(version) {
        return `
            <div class="notes-content">
                <div class="notes-editor">
                    <textarea class="form-input" id="releaseNotes" rows="15" 
                              placeholder="# Release Notes\n\n## New Features\n\n## Bug Fixes\n\n## Known Issues">${version.releaseNotes || ''}</textarea>
                    <button class="btn btn-primary" onclick="versionManagement.saveReleaseNotes('${version.id}')">
                        <i data-lucide="save"></i>
                        Save Notes
                    </button>
                </div>
            </div>
        `;
    }

    renderIssuesPane(version) {
        const issues = version.issues || [];
        
        return `
            <div class="issues-content">
                <div class="issues-header">
                    <h3>${issues.length} Issues</h3>
                    <button class="btn btn-ghost btn-sm" onclick="versionManagement.assignIssues('${version.id}')">
                        <i data-lucide="plus"></i>
                        Assign Issues
                    </button>
                </div>

                <div class="issues-list">
                    ${issues.length === 0 ? `
                        <div class="empty-state-small">
                            <i data-lucide="list"></i>
                            <p>No issues assigned to this version</p>
                        </div>
                    ` : issues.map(issue => `
                        <div class="issue-item">
                            <div class="issue-key">${issue.key}</div>
                            <div class="issue-summary">${issue.summary}</div>
                            <div class="issue-status ${issue.status?.toLowerCase()}">${issue.status}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    switchTab(tabName, version) {
        document.querySelectorAll('.version-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane.dataset.pane === tabName);
        });

        if (tabName === 'burndown') {
            setTimeout(() => this.renderBurndownChart(version), 100);
        }
    }

    renderBurndownChart(version) {
        const ctx = document.getElementById('burndownChart');
        if (!ctx) return;

        this.destroyChart();

        this.burndownChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                datasets: [{
                    label: 'Ideal',
                    data: [28, 24, 20, 16, 12, 8, 4],
                    borderColor: '#9CA3AF',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5]
                }, {
                    label: 'Actual',
                    data: [28, 26, 22, 20, 16, 14, 10],
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Issues Remaining'
                        }
                    }
                }
            }
        });
    }

    destroyChart() {
        if (this.burndownChart) {
            this.burndownChart.destroy();
            this.burndownChart = null;
        }
    }

    openVersionDialog(versionId = null) {
        const dialog = document.getElementById('versionDialog');
        const title = document.getElementById('versionDialogTitle');
        
        if (versionId) {
            const version = this.versions.find(v => v.id === versionId);
            title.textContent = 'Edit Version';
            document.getElementById('versionName').value = version.name;
            document.getElementById('versionDescription').value = version.description || '';
            document.getElementById('versionReleaseDate').value = version.releaseDate || '';
        } else {
            title.textContent = 'Create Version';
            document.getElementById('versionName').value = '';
            document.getElementById('versionDescription').value = '';
            document.getElementById('versionReleaseDate').value = '';
        }

        dialog.style.display = 'block';
        if (window.lucide) lucide.createIcons();
    }

    closeVersionDialog() {
        document.getElementById('versionDialog').style.display = 'none';
    }

    async saveVersion() {
        const name = document.getElementById('versionName').value;
        const description = document.getElementById('versionDescription').value;
        const releaseDate = document.getElementById('versionReleaseDate').value;

        if (!name) return;

        try {
            const response = await fetch('/api/versions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description, releaseDate })
            });

            if (response.ok) {
                this.closeVersionDialog();
                this.loadVersions();
            }
        } catch (error) {
            console.error('Failed to save version:', error);
        }
    }

    editVersion(versionId) {
        this.openVersionDialog(versionId);
    }

    async releaseVersion(versionId) {
        if (!confirm('Release this version? This will mark it as released.')) return;

        try {
            const response = await fetch(`/api/versions/${versionId}/release`, {
                method: 'POST'
            });

            if (response.ok) {
                this.loadVersions();
                this.renderVersionDetails();
            }
        } catch (error) {
            console.error('Failed to release version:', error);
        }
    }

    async saveReleaseNotes(versionId) {
        const notes = document.getElementById('releaseNotes').value;

        try {
            const response = await fetch(`/api/versions/${versionId}/notes`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ releaseNotes: notes })
            });

            if (response.ok) {
                alert('Release notes saved!');
            }
        } catch (error) {
            console.error('Failed to save release notes:', error);
        }
    }

    assignIssues(versionId) {
        alert('Issue assignment dialog would open here');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.versionManagement = new VersionManagement();
});

// Global function
function openVersionManagement() {
    window.versionManagement?.openModal();
}
