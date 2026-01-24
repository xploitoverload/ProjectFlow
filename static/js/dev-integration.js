/**
 * Development Integration Panel
 * Commits, PRs, Branches, Builds, Deployments tracking
 */

class DevelopmentIntegration {
    constructor() {
        this.repos = [];
        this.commits = [];
        this.pullRequests = [];
        this.branches = [];
        this.builds = [];
        this.deployments = [];
        
        this.init();
    }

    async init() {
        await this.loadRepositories();
        await this.loadDevelopmentData();
        console.log('DevelopmentIntegration initialized');
    }

    async loadRepositories() {
        this.repos = [
            { id: 1, name: 'frontend-app', provider: 'github', url: 'https://github.com/company/frontend-app' },
            { id: 2, name: 'backend-api', provider: 'github', url: 'https://github.com/company/backend-api' }
        ];
    }

    async loadDevelopmentData() {
        this.commits = [
            {
                id: 1,
                hash: 'a1b2c3d',
                message: 'Fix authentication bug',
                author: 'John Doe',
                date: '2026-01-23 10:30',
                filesChanged: 3,
                additions: 45,
                deletions: 12
            },
            {
                id: 2,
                hash: 'e4f5g6h',
                message: 'Add user profile feature',
                author: 'Jane Smith',
                date: '2026-01-22 15:45',
                filesChanged: 8,
                additions: 234,
                deletions: 23
            }
        ];

        this.pullRequests = [
            {
                id: 1,
                number: 142,
                title: 'Feature: User authentication',
                status: 'open',
                author: 'John Doe',
                reviewers: ['Jane Smith', 'Bob Johnson'],
                approvals: 1,
                requiredApprovals: 2,
                checks: { passed: 3, failed: 0, pending: 1 },
                created: '2026-01-22',
                branch: 'feature/auth'
            },
            {
                id: 2,
                number: 141,
                title: 'Fix: Memory leak in cache',
                status: 'merged',
                author: 'Jane Smith',
                reviewers: ['John Doe'],
                approvals: 1,
                requiredApprovals: 1,
                checks: { passed: 4, failed: 0, pending: 0 },
                created: '2026-01-20',
                merged: '2026-01-21',
                branch: 'bugfix/cache-leak'
            }
        ];

        this.branches = [
            { name: 'main', type: 'main', lastCommit: '2 hours ago', ahead: 0, behind: 0 },
            { name: 'develop', type: 'develop', lastCommit: '1 day ago', ahead: 5, behind: 2 },
            { name: 'feature/auth', type: 'feature', lastCommit: '3 hours ago', ahead: 12, behind: 0 },
            { name: 'bugfix/cache-leak', type: 'bugfix', lastCommit: '2 days ago', ahead: 0, behind: 0, merged: true }
        ];

        this.builds = [
            {
                id: 1,
                number: 245,
                status: 'success',
                branch: 'main',
                commit: 'a1b2c3d',
                duration: '3m 42s',
                started: '2026-01-23 10:35',
                stages: [
                    { name: 'Build', status: 'success', duration: '1m 20s' },
                    { name: 'Test', status: 'success', duration: '2m 15s' },
                    { name: 'Deploy', status: 'success', duration: '7s' }
                ]
            },
            {
                id: 2,
                number: 244,
                status: 'failed',
                branch: 'feature/auth',
                commit: 'e4f5g6h',
                duration: '2m 18s',
                started: '2026-01-22 16:20',
                stages: [
                    { name: 'Build', status: 'success', duration: '1m 15s' },
                    { name: 'Test', status: 'failed', duration: '1m 3s' }
                ]
            }
        ];

        this.deployments = [
            {
                id: 1,
                environment: 'production',
                version: 'v2.3.1',
                status: 'deployed',
                deployedAt: '2026-01-23 11:00',
                deployedBy: 'John Doe',
                commit: 'a1b2c3d'
            },
            {
                id: 2,
                environment: 'staging',
                version: 'v2.4.0-beta',
                status: 'deployed',
                deployedAt: '2026-01-23 09:30',
                deployedBy: 'Jane Smith',
                commit: 'e4f5g6h'
            },
            {
                id: 3,
                environment: 'development',
                version: 'v2.4.0-alpha',
                status: 'deploying',
                deployedAt: '2026-01-23 12:15',
                deployedBy: 'Bob Johnson',
                commit: 'i7j8k9l'
            }
        ];
    }

    // DEVELOPMENT PANEL (for issue detail sidebar)
    renderDevelopmentPanel(container, issueKey) {
        const html = `
            <div class="development-panel">
                <div class="dev-panel-header">
                    <h3>Development</h3>
                    <button class="btn-secondary btn-sm" onclick="devIntegration.linkRepository('${issueKey}')">
                        <i data-lucide="link"></i>
                        Link Repository
                    </button>
                </div>

                <div class="dev-sections">
                    <div class="dev-section">
                        <div class="section-header" onclick="devIntegration.toggleSection(this)">
                            <i data-lucide="git-commit"></i>
                            <span>Commits (${this.commits.length})</span>
                            <i data-lucide="chevron-down" class="toggle-icon"></i>
                        </div>
                        <div class="section-content">
                            ${this.renderCommitsList()}
                        </div>
                    </div>

                    <div class="dev-section">
                        <div class="section-header" onclick="devIntegration.toggleSection(this)">
                            <i data-lucide="git-pull-request"></i>
                            <span>Pull Requests (${this.pullRequests.length})</span>
                            <i data-lucide="chevron-down" class="toggle-icon"></i>
                        </div>
                        <div class="section-content">
                            ${this.renderPullRequestsList()}
                        </div>
                    </div>

                    <div class="dev-section">
                        <div class="section-header" onclick="devIntegration.toggleSection(this)">
                            <i data-lucide="git-branch"></i>
                            <span>Branches (${this.branches.length})</span>
                            <i data-lucide="chevron-down" class="toggle-icon"></i>
                        </div>
                        <div class="section-content">
                            ${this.renderBranchesList()}
                        </div>
                    </div>

                    <div class="dev-section">
                        <div class="section-header" onclick="devIntegration.toggleSection(this)">
                            <i data-lucide="package"></i>
                            <span>Builds (${this.builds.length})</span>
                            <i data-lucide="chevron-down" class="toggle-icon"></i>
                        </div>
                        <div class="section-content">
                            ${this.renderBuildsList()}
                        </div>
                    </div>

                    <div class="dev-section">
                        <div class="section-header" onclick="devIntegration.toggleSection(this)">
                            <i data-lucide="rocket"></i>
                            <span>Deployments (${this.deployments.length})</span>
                            <i data-lucide="chevron-down" class="toggle-icon"></i>
                        </div>
                        <div class="section-content">
                            ${this.renderDeploymentsList()}
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderCommitsList() {
        return this.commits.map(commit => `
            <div class="commit-item" onclick="devIntegration.viewCommit('${commit.hash}')">
                <div class="commit-hash">
                    <code>${commit.hash}</code>
                </div>
                <div class="commit-details">
                    <div class="commit-message">${commit.message}</div>
                    <div class="commit-meta">
                        <span class="commit-author">${commit.author}</span>
                        <span class="commit-date">${commit.date}</span>
                    </div>
                    <div class="commit-stats">
                        <span class="additions">+${commit.additions}</span>
                        <span class="deletions">-${commit.deletions}</span>
                        <span class="files">${commit.filesChanged} files</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderPullRequestsList() {
        return this.pullRequests.map(pr => `
            <div class="pr-item" onclick="devIntegration.viewPullRequest(${pr.number})">
                <div class="pr-header">
                    <span class="pr-number">#${pr.number}</span>
                    <span class="pr-status pr-status-${pr.status}">
                        <i data-lucide="${pr.status === 'open' ? 'git-pull-request' : 'git-merge'}"></i>
                        ${pr.status}
                    </span>
                </div>
                <div class="pr-title">${pr.title}</div>
                <div class="pr-meta">
                    <span>by ${pr.author}</span>
                    <span>•</span>
                    <span>${pr.created}</span>
                </div>
                <div class="pr-reviewers">
                    <label>Reviewers:</label>
                    <div class="reviewers-list">
                        ${pr.reviewers.map(r => `<span class="reviewer-badge">${r}</span>`).join('')}
                    </div>
                    <span class="approvals">${pr.approvals}/${pr.requiredApprovals} approved</span>
                </div>
                <div class="pr-checks">
                    ${pr.checks.passed > 0 ? `<span class="check-passed">${pr.checks.passed} passed</span>` : ''}
                    ${pr.checks.failed > 0 ? `<span class="check-failed">${pr.checks.failed} failed</span>` : ''}
                    ${pr.checks.pending > 0 ? `<span class="check-pending">${pr.checks.pending} pending</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    renderBranchesList() {
        return this.branches.map(branch => `
            <div class="branch-item ${branch.merged ? 'merged' : ''}">
                <div class="branch-info">
                    <i data-lucide="git-branch"></i>
                    <span class="branch-name">${branch.name}</span>
                    ${branch.merged ? '<span class="merged-badge">Merged</span>' : ''}
                </div>
                <div class="branch-meta">
                    <span>${branch.lastCommit}</span>
                    ${!branch.merged && branch.ahead > 0 ? `<span class="ahead">↑${branch.ahead}</span>` : ''}
                    ${!branch.merged && branch.behind > 0 ? `<span class="behind">↓${branch.behind}</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    renderBuildsList() {
        return this.builds.map(build => `
            <div class="build-item" onclick="devIntegration.viewBuild(${build.id})">
                <div class="build-header">
                    <span class="build-number">#${build.number}</span>
                    <span class="build-status build-${build.status}">
                        <i data-lucide="${build.status === 'success' ? 'check-circle' : 'x-circle'}"></i>
                        ${build.status}
                    </span>
                </div>
                <div class="build-info">
                    <span class="build-branch">${build.branch}</span>
                    <span>•</span>
                    <code class="build-commit">${build.commit}</code>
                </div>
                <div class="build-meta">
                    <span>${build.started}</span>
                    <span>•</span>
                    <span>${build.duration}</span>
                </div>
                <div class="build-stages">
                    ${build.stages.map(stage => `
                        <div class="stage-item stage-${stage.status}">
                            <i data-lucide="${stage.status === 'success' ? 'check' : 'x'}"></i>
                            <span>${stage.name}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }

    renderDeploymentsList() {
        return this.deployments.map(deployment => `
            <div class="deployment-item">
                <div class="deployment-header">
                    <span class="env-badge env-${deployment.environment}">
                        ${deployment.environment}
                    </span>
                    <span class="deployment-status deployment-${deployment.status}">
                        ${deployment.status}
                    </span>
                </div>
                <div class="deployment-version">${deployment.version}</div>
                <div class="deployment-meta">
                    <span>by ${deployment.deployedBy}</span>
                    <span>•</span>
                    <span>${deployment.deployedAt}</span>
                </div>
                <div class="deployment-commit">
                    <code>${deployment.commit}</code>
                </div>
            </div>
        `).join('');
    }

    // CODE INTEGRATION MODAL
    linkRepository(issueKey) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay active';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h2>Link Repository</h2>
                    <button class="btn-icon" onclick="devIntegration.closeModal()">
                        <i data-lucide="x"></i>
                    </button>
                </div>

                <div class="modal-body">
                    <div class="repo-provider-selection">
                        <label>Choose Provider</label>
                        <div class="provider-options">
                            <button class="provider-btn" onclick="devIntegration.selectProvider('github')">
                                <i data-lucide="github"></i>
                                GitHub
                            </button>
                            <button class="provider-btn" onclick="devIntegration.selectProvider('gitlab')">
                                <i data-lucide="gitlab"></i>
                                GitLab
                            </button>
                            <button class="provider-btn" onclick="devIntegration.selectProvider('bitbucket')">
                                <i data-lucide="bitbucket"></i>
                                Bitbucket
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Repository URL</label>
                        <input type="text" class="form-input" id="repoUrl" 
                               placeholder="https://github.com/owner/repo">
                    </div>

                    <div class="form-group">
                        <label>Access Token</label>
                        <input type="password" class="form-input" id="accessToken" 
                               placeholder="Enter your personal access token">
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn-secondary" onclick="devIntegration.closeModal()">
                        Cancel
                    </button>
                    <button class="btn-primary" onclick="devIntegration.connectRepository()">
                        Connect Repository
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        if (window.lucide) lucide.createIcons();
    }

    // Helper Methods
    toggleSection(header) {
        const section = header.closest('.dev-section');
        const content = section.querySelector('.section-content');
        const icon = header.querySelector('.toggle-icon');
        
        section.classList.toggle('collapsed');
        if (section.classList.contains('collapsed')) {
            content.style.display = 'none';
            icon.style.transform = 'rotate(-90deg)';
        } else {
            content.style.display = 'block';
            icon.style.transform = 'rotate(0deg)';
        }
    }

    viewCommit(hash) {
        alert(`View commit: ${hash}`);
    }

    viewPullRequest(number) {
        alert(`View PR #${number}`);
    }

    viewBuild(id) {
        alert(`View build #${id}`);
    }

    selectProvider(provider) {
        console.log('Selected provider:', provider);
    }

    connectRepository() {
        const url = document.getElementById('repoUrl')?.value;
        if (!url) {
            alert('Please enter a repository URL');
            return;
        }
        alert(`Repository connected: ${url}`);
        this.closeModal();
    }

    closeModal() {
        const modal = document.querySelector('.modal-overlay');
        if (modal) modal.remove();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.devIntegration = new DevelopmentIntegration();
});
