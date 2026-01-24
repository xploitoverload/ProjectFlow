/**
 * Epic Management Enhancements
 * Enhanced epic features with hierarchy and roadmap
 */

class EpicManagement {
    constructor() {
        this.epics = [];
        this.selectedEpic = null;
        this.view = 'board'; // board, list, roadmap
        
        this.init();
    }

    async init() {
        await this.loadEpics();
        this.createModal();
    }

    createModal() {
        const modalHTML = `
            <div id="epicManagementModal" class="epic-modal" style="display: none;">
                <div class="epic-backdrop"></div>
                <div class="epic-container">
                    <div class="epic-header">
                        <div class="header-left">
                            <h2>Epic Management</h2>
                            <div class="epic-view-switcher">
                                <button class="view-btn active" data-view="board" onclick="epicManagement.switchView('board')">
                                    <i data-lucide="layout-grid"></i>
                                    Board
                                </button>
                                <button class="view-btn" data-view="list" onclick="epicManagement.switchView('list')">
                                    <i data-lucide="list"></i>
                                    List
                                </button>
                                <button class="view-btn" data-view="roadmap" onclick="epicManagement.switchView('roadmap')">
                                    <i data-lucide="gantt-chart"></i>
                                    Roadmap
                                </button>
                            </div>
                        </div>
                        <div class="header-right">
                            <button class="btn-primary" onclick="epicManagement.createEpic()">
                                <i data-lucide="plus"></i>
                                Create Epic
                            </button>
                            <button class="btn-icon-sm" onclick="epicManagement.closeModal()">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    </div>

                    <div class="epic-content" id="epicContent">
                        <!-- Populated by JS -->
                    </div>
                </div>
            </div>

            <!-- Epic Detail Panel -->
            <div id="epicDetailPanel" class="epic-detail-panel" style="display: none;">
                <div class="panel-header">
                    <button class="btn-icon-sm" onclick="epicManagement.closeDetailPanel()">
                        <i data-lucide="arrow-left"></i>
                    </button>
                    <h3 id="epicDetailTitle">Epic Title</h3>
                    <button class="btn-icon-sm" onclick="epicManagement.editEpic()">
                        <i data-lucide="edit-2"></i>
                    </button>
                </div>

                <div class="panel-content" id="epicDetailContent">
                    <!-- Populated by JS -->
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    async loadEpics() {
        try {
            const response = await fetch('/api/epics');
            this.epics = await response.json();
        } catch (error) {
            console.error('Failed to load epics:', error);
            this.epics = this.getMockEpics();
        }
    }

    getMockEpics() {
        return [
            {
                id: 1,
                key: 'EPIC-1',
                name: 'User Authentication System',
                description: 'Complete overhaul of authentication',
                status: 'In Progress',
                color: '#3B82F6',
                progress: 65,
                startDate: '2026-01-01',
                endDate: '2026-03-31',
                owner: 'John Doe',
                childIssues: 15,
                completedIssues: 10,
                storyPoints: 89,
                completedPoints: 58
            },
            {
                id: 2,
                key: 'EPIC-2',
                name: 'Mobile App Development',
                description: 'Build iOS and Android apps',
                status: 'To Do',
                color: '#10B981',
                progress: 20,
                startDate: '2026-02-01',
                endDate: '2026-06-30',
                owner: 'Jane Smith',
                childIssues: 32,
                completedIssues: 6,
                storyPoints: 144,
                completedPoints: 29
            },
            {
                id: 3,
                key: 'EPIC-3',
                name: 'Performance Optimization',
                description: 'Improve system performance',
                status: 'In Progress',
                color: '#F59E0B',
                progress: 45,
                startDate: '2026-01-15',
                endDate: '2026-02-28',
                owner: 'Bob Johnson',
                childIssues: 12,
                completedIssues: 5,
                storyPoints: 55,
                completedPoints: 25
            },
            {
                id: 4,
                key: 'EPIC-4',
                name: 'API v2 Development',
                description: 'New REST API version',
                status: 'Done',
                color: '#8B5CF6',
                progress: 100,
                startDate: '2025-11-01',
                endDate: '2026-01-15',
                owner: 'Alice Williams',
                childIssues: 24,
                completedIssues: 24,
                storyPoints: 98,
                completedPoints: 98
            }
        ];
    }

    openModal() {
        document.getElementById('epicManagementModal').style.display = 'flex';
        this.renderView();
        
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    closeModal() {
        document.getElementById('epicManagementModal').style.display = 'none';
        this.closeDetailPanel();
    }

    switchView(view) {
        this.view = view;
        
        // Update buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`)?.classList.add('active');
        
        this.renderView();
    }

    renderView() {
        switch (this.view) {
            case 'board':
                this.renderBoardView();
                break;
            case 'list':
                this.renderListView();
                break;
            case 'roadmap':
                this.renderRoadmapView();
                break;
        }

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderBoardView() {
        const grouped = {
            'To Do': this.epics.filter(e => e.status === 'To Do'),
            'In Progress': this.epics.filter(e => e.status === 'In Progress'),
            'Done': this.epics.filter(e => e.status === 'Done')
        };

        document.getElementById('epicContent').innerHTML = `
            <div class="epic-board">
                ${Object.entries(grouped).map(([status, epics]) => `
                    <div class="epic-column">
                        <div class="column-header">
                            <h3>${status}</h3>
                            <span class="count">${epics.length}</span>
                        </div>
                        <div class="epic-cards">
                            ${epics.map(epic => this.renderEpicCard(epic)).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderEpicCard(epic) {
        return `
            <div class="epic-card" 
                 style="border-left: 4px solid ${epic.color}"
                 onclick="epicManagement.showEpicDetail(${epic.id})">
                <div class="epic-card-header">
                    <span class="epic-key">${epic.key}</span>
                    <button class="btn-icon-xs" onclick="event.stopPropagation(); epicManagement.openEpicMenu(${epic.id})">
                        <i data-lucide="more-horizontal"></i>
                    </button>
                </div>
                
                <h4 class="epic-name">${epic.name}</h4>
                <p class="epic-description">${epic.description}</p>
                
                <div class="epic-progress">
                    <div class="progress-header">
                        <span class="progress-label">Progress</span>
                        <span class="progress-value">${epic.progress}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${epic.progress}%; background: ${epic.color}"></div>
                    </div>
                </div>
                
                <div class="epic-stats">
                    <div class="stat">
                        <i data-lucide="check-circle"></i>
                        <span>${epic.completedIssues}/${epic.childIssues} issues</span>
                    </div>
                    <div class="stat">
                        <i data-lucide="zap"></i>
                        <span>${epic.completedPoints}/${epic.storyPoints} pts</span>
                    </div>
                </div>
                
                <div class="epic-footer">
                    <div class="epic-owner">
                        <div class="avatar-sm">${this.getInitials(epic.owner)}</div>
                        <span>${epic.owner}</span>
                    </div>
                    <span class="epic-date">${this.formatDateRange(epic.startDate, epic.endDate)}</span>
                </div>
            </div>
        `;
    }

    renderListView() {
        document.getElementById('epicContent').innerHTML = `
            <div class="epic-list">
                <table class="epic-table">
                    <thead>
                        <tr>
                            <th style="width: 100px">Key</th>
                            <th>Name</th>
                            <th style="width: 120px">Status</th>
                            <th style="width: 150px">Progress</th>
                            <th style="width: 100px">Issues</th>
                            <th style="width: 100px">Points</th>
                            <th style="width: 150px">Owner</th>
                            <th style="width: 200px">Timeline</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.epics.map(epic => `
                            <tr class="epic-row" onclick="epicManagement.showEpicDetail(${epic.id})">
                                <td>
                                    <span class="epic-key" style="color: ${epic.color}">${epic.key}</span>
                                </td>
                                <td>
                                    <div class="epic-name-cell">
                                        <div class="color-indicator" style="background: ${epic.color}"></div>
                                        <strong>${epic.name}</strong>
                                    </div>
                                </td>
                                <td>
                                    <span class="status-badge status-${epic.status.toLowerCase().replace(' ', '-')}">${epic.status}</span>
                                </td>
                                <td>
                                    <div class="progress-cell">
                                        <div class="progress-bar-sm">
                                            <div class="progress-fill" style="width: ${epic.progress}%; background: ${epic.color}"></div>
                                        </div>
                                        <span class="progress-text">${epic.progress}%</span>
                                    </div>
                                </td>
                                <td>${epic.completedIssues}/${epic.childIssues}</td>
                                <td>${epic.completedPoints}/${epic.storyPoints}</td>
                                <td>
                                    <div class="owner-cell">
                                        <div class="avatar-xs">${this.getInitials(epic.owner)}</div>
                                        <span>${epic.owner}</span>
                                    </div>
                                </td>
                                <td>${this.formatDateRange(epic.startDate, epic.endDate)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    renderRoadmapView() {
        // Calculate timeline scale
        const allDates = this.epics.flatMap(e => [new Date(e.startDate), new Date(e.endDate)]);
        const minDate = new Date(Math.min(...allDates));
        const maxDate = new Date(Math.max(...allDates));
        
        // Generate months
        const months = [];
        let current = new Date(minDate.getFullYear(), minDate.getMonth(), 1);
        while (current <= maxDate) {
            months.push(new Date(current));
            current.setMonth(current.getMonth() + 1);
        }

        document.getElementById('epicContent').innerHTML = `
            <div class="epic-roadmap">
                <div class="roadmap-timeline">
                    <div class="timeline-header">
                        <div class="timeline-label">Epic</div>
                        <div class="timeline-months">
                            ${months.map(month => `
                                <div class="month-col">
                                    ${month.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="timeline-body">
                        ${this.epics.map(epic => {
                            const start = new Date(epic.startDate);
                            const end = new Date(epic.endDate);
                            const totalDays = (maxDate - minDate) / (1000 * 60 * 60 * 24);
                            const startOffset = ((start - minDate) / (1000 * 60 * 60 * 24)) / totalDays * 100;
                            const duration = ((end - start) / (1000 * 60 * 60 * 24)) / totalDays * 100;
                            
                            return `
                                <div class="timeline-row">
                                    <div class="row-label">
                                        <div class="color-indicator" style="background: ${epic.color}"></div>
                                        <div>
                                            <div class="epic-key">${epic.key}</div>
                                            <div class="epic-name-small">${epic.name}</div>
                                        </div>
                                    </div>
                                    <div class="row-timeline">
                                        <div class="timeline-bar" 
                                             style="left: ${startOffset}%; width: ${duration}%; background: ${epic.color}"
                                             onclick="epicManagement.showEpicDetail(${epic.id})">
                                            <span class="bar-label">${epic.progress}%</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    showEpicDetail(epicId) {
        const epic = this.epics.find(e => e.id === epicId);
        if (!epic) return;

        this.selectedEpic = epic;

        document.getElementById('epicDetailTitle').textContent = epic.name;
        document.getElementById('epicDetailContent').innerHTML = `
            <div class="detail-section">
                <div class="detail-header">
                    <span class="epic-key" style="color: ${epic.color}">${epic.key}</span>
                    <span class="status-badge status-${epic.status.toLowerCase().replace(' ', '-')}">${epic.status}</span>
                </div>
                
                <p class="epic-description-full">${epic.description}</p>
            </div>

            <div class="detail-section">
                <h4>Progress Overview</h4>
                <div class="progress-overview">
                    <div class="progress-stat">
                        <div class="stat-label">Issues Completed</div>
                        <div class="stat-value">${epic.completedIssues} / ${epic.childIssues}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${(epic.completedIssues / epic.childIssues) * 100}%; background: ${epic.color}"></div>
                        </div>
                    </div>
                    <div class="progress-stat">
                        <div class="stat-label">Story Points</div>
                        <div class="stat-value">${epic.completedPoints} / ${epic.storyPoints}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${(epic.completedPoints / epic.storyPoints) * 100}%; background: ${epic.color}"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h4>Timeline</h4>
                <div class="timeline-info">
                    <div class="timeline-item">
                        <i data-lucide="calendar"></i>
                        <div>
                            <div class="label">Start Date</div>
                            <div class="value">${new Date(epic.startDate).toLocaleDateString()}</div>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <i data-lucide="flag"></i>
                        <div>
                            <div class="label">End Date</div>
                            <div class="value">${new Date(epic.endDate).toLocaleDateString()}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h4>Owner</h4>
                <div class="owner-info">
                    <div class="avatar-lg">${this.getInitials(epic.owner)}</div>
                    <div>
                        <div class="owner-name">${epic.owner}</div>
                        <div class="owner-role">Epic Owner</div>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h4>Child Issues</h4>
                <div class="child-issues-placeholder">
                    <i data-lucide="list"></i>
                    <p>View all ${epic.childIssues} issues in this epic</p>
                    <button class="btn-secondary">View Issues</button>
                </div>
            </div>
        `;

        document.getElementById('epicDetailPanel').style.display = 'flex';

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    closeDetailPanel() {
        document.getElementById('epicDetailPanel').style.display = 'none';
        this.selectedEpic = null;
    }

    createEpic() {
        alert('Create Epic - Integration point for form dialog');
    }

    editEpic() {
        alert('Edit Epic - Integration point');
    }

    openEpicMenu(epicId) {
        alert(`Epic menu for ${epicId}`);
    }

    getInitials(name) {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }

    formatDateRange(start, end) {
        const startDate = new Date(start);
        const endDate = new Date(end);
        return `${startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.epicManagement = new EpicManagement();
});
