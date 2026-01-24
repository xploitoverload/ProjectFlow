/**
 * Sprint Management - JIRA-style sprint board and planning
 * Features: Sprint planning, start/complete sprint, sprint backlog, burndown
 */

class SprintManager {
    constructor() {
        this.activeSprint = null;
        this.sprints = [];
        this.sprintModal = null;
        
        this.init();
    }

    init() {
        this.createSprintModal();
        this.setupEventListeners();
        this.loadSprints();
    }

    createSprintModal() {
        const modalHTML = `
            <div id="sprintModal" class="sprint-modal" style="display: none;">
                <div class="sprint-modal-backdrop"></div>
                <div class="sprint-modal-container">
                    <div class="sprint-modal-header">
                        <h2 id="sprintModalTitle">Create Sprint</h2>
                        <button class="btn-icon" id="closeSprintModal">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    
                    <div class="sprint-modal-body">
                        <form id="sprintForm">
                            <div class="form-group">
                                <label for="sprintName">Sprint Name *</label>
                                <input type="text" id="sprintName" class="form-input" 
                                       placeholder="e.g., Sprint 1" required>
                            </div>

                            <div class="form-group">
                                <label for="sprintGoal">Sprint Goal</label>
                                <textarea id="sprintGoal" class="form-input" rows="3"
                                          placeholder="What is the goal of this sprint?"></textarea>
                            </div>

                            <div class="form-row">
                                <div class="form-group">
                                    <label for="sprintStartDate">Start Date *</label>
                                    <input type="date" id="sprintStartDate" class="form-input" required>
                                </div>

                                <div class="form-group">
                                    <label for="sprintEndDate">End Date *</label>
                                    <input type="date" id="sprintEndDate" class="form-input" required>
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="sprintDuration">Duration (weeks)</label>
                                <select id="sprintDuration" class="form-input">
                                    <option value="1">1 week</option>
                                    <option value="2" selected>2 weeks</option>
                                    <option value="3">3 weeks</option>
                                    <option value="4">4 weeks</option>
                                </select>
                            </div>

                            <div class="form-actions">
                                <button type="button" class="btn btn-ghost" id="cancelSprintBtn">Cancel</button>
                                <button type="submit" class="btn btn-primary" id="saveSprintBtn">Create Sprint</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Start Sprint Confirmation -->
            <div id="startSprintModal" class="sprint-modal" style="display: none;">
                <div class="sprint-modal-backdrop"></div>
                <div class="sprint-modal-container sprint-modal-small">
                    <div class="sprint-modal-header">
                        <h2>Start Sprint</h2>
                        <button class="btn-icon" id="closeStartSprintModal">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    
                    <div class="sprint-modal-body">
                        <p>You are about to start <strong id="startSprintName"></strong>.</p>
                        <p class="text-muted">Sprint Duration: <span id="startSprintDuration"></span></p>
                        <p class="text-muted">Issues in Sprint: <span id="startSprintIssues"></span></p>
                        
                        <div class="form-actions">
                            <button type="button" class="btn btn-ghost" id="cancelStartSprintBtn">Cancel</button>
                            <button type="button" class="btn btn-success" id="confirmStartSprintBtn">
                                <i data-lucide="play"></i>
                                Start Sprint
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Complete Sprint Modal -->
            <div id="completeSprintModal" class="sprint-modal" style="display: none;">
                <div class="sprint-modal-backdrop"></div>
                <div class="sprint-modal-container">
                    <div class="sprint-modal-header">
                        <h2>Complete Sprint</h2>
                        <button class="btn-icon" id="closeCompleteSprintModal">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    
                    <div class="sprint-modal-body">
                        <div class="sprint-summary">
                            <h3 id="completeSprintName"></h3>
                            <div class="sprint-stats">
                                <div class="stat-card">
                                    <div class="stat-value" id="completedIssuesCount">0</div>
                                    <div class="stat-label">Completed</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" id="incompleteIssuesCount">0</div>
                                    <div class="stat-label">Incomplete</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" id="completionPercentage">0%</div>
                                    <div class="stat-label">Completion</div>
                                </div>
                            </div>
                        </div>

                        <div class="form-group">
                            <label>What to do with incomplete issues?</label>
                            <div class="radio-group">
                                <label class="radio-option">
                                    <input type="radio" name="incompleteAction" value="backlog" checked>
                                    <span>Move to Backlog</span>
                                </label>
                                <label class="radio-option">
                                    <input type="radio" name="incompleteAction" value="next-sprint">
                                    <span>Move to Next Sprint</span>
                                </label>
                                <label class="radio-option">
                                    <input type="radio" name="incompleteAction" value="keep">
                                    <span>Keep in Current Sprint</span>
                                </label>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="sprintRetrospective">Retrospective Notes</label>
                            <textarea id="sprintRetrospective" class="form-input" rows="4"
                                      placeholder="What went well? What could be improved?"></textarea>
                        </div>

                        <div class="form-actions">
                            <button type="button" class="btn btn-ghost" id="cancelCompleteSprintBtn">Cancel</button>
                            <button type="button" class="btn btn-primary" id="confirmCompleteSprintBtn">
                                <i data-lucide="check-circle"></i>
                                Complete Sprint
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.sprintModal = document.getElementById('sprintModal');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        // Create Sprint Modal
        document.getElementById('closeSprintModal')?.addEventListener('click', () => {
            this.closeSprintModal();
        });

        document.getElementById('cancelSprintBtn')?.addEventListener('click', () => {
            this.closeSprintModal();
        });

        document.getElementById('sprintForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createSprint();
        });

        // Auto-calculate end date when duration changes
        document.getElementById('sprintDuration')?.addEventListener('change', (e) => {
            const weeks = parseInt(e.target.value);
            const startDate = document.getElementById('sprintStartDate').value;
            if (startDate) {
                const endDate = this.calculateEndDate(startDate, weeks);
                document.getElementById('sprintEndDate').value = endDate;
            }
        });

        document.getElementById('sprintStartDate')?.addEventListener('change', (e) => {
            const weeks = parseInt(document.getElementById('sprintDuration').value);
            const endDate = this.calculateEndDate(e.target.value, weeks);
            document.getElementById('sprintEndDate').value = endDate;
        });

        // Start Sprint Modal
        document.getElementById('closeStartSprintModal')?.addEventListener('click', () => {
            document.getElementById('startSprintModal').style.display = 'none';
        });

        document.getElementById('cancelStartSprintBtn')?.addEventListener('click', () => {
            document.getElementById('startSprintModal').style.display = 'none';
        });

        document.getElementById('confirmStartSprintBtn')?.addEventListener('click', () => {
            this.startSprint();
        });

        // Complete Sprint Modal
        document.getElementById('closeCompleteSprintModal')?.addEventListener('click', () => {
            document.getElementById('completeSprintModal').style.display = 'none';
        });

        document.getElementById('cancelCompleteSprintBtn')?.addEventListener('click', () => {
            document.getElementById('completeSprintModal').style.display = 'none';
        });

        document.getElementById('confirmCompleteSprintBtn')?.addEventListener('click', () => {
            this.completeSprint();
        });
    }

    async loadSprints() {
        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/sprints`);
            if (response.ok) {
                this.sprints = await response.json();
                this.activeSprint = this.sprints.find(s => s.status === 'active');
                this.renderSprints();
            }
        } catch (error) {
            console.error('Failed to load sprints:', error);
        }
    }

    renderSprints() {
        const container = document.getElementById('sprintsList');
        if (!container) return;

        if (this.sprints.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i data-lucide="calendar" style="width: 48px; height: 48px; margin-bottom: 16px;"></i>
                    <h3>No Sprints Yet</h3>
                    <p>Create your first sprint to start planning your work.</p>
                    <button class="btn btn-primary" onclick="window.sprintManager.openCreateSprintModal()">
                        <i data-lucide="plus"></i>
                        Create Sprint
                    </button>
                </div>
            `;
        } else {
            container.innerHTML = this.sprints.map(sprint => this.renderSprintCard(sprint)).join('');
        }

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderSprintCard(sprint) {
        const statusClass = sprint.status === 'active' ? 'sprint-active' :
                          sprint.status === 'completed' ? 'sprint-completed' :
                          'sprint-planned';

        const issueCount = sprint.issues?.length || 0;
        const completedCount = sprint.issues?.filter(i => i.status === 'Done').length || 0;
        const completionRate = issueCount > 0 ? Math.round((completedCount / issueCount) * 100) : 0;

        return `
            <div class="sprint-card ${statusClass}">
                <div class="sprint-card-header">
                    <div class="sprint-info">
                        <h3 class="sprint-name">${sprint.name}</h3>
                        <div class="sprint-meta">
                            <span class="sprint-status">${sprint.status}</span>
                            <span class="sprint-dates">
                                ${this.formatDate(sprint.start_date)} - ${this.formatDate(sprint.end_date)}
                            </span>
                            <span class="sprint-duration">${sprint.duration} weeks</span>
                        </div>
                    </div>
                    
                    <div class="sprint-actions">
                        ${sprint.status === 'planned' ? `
                            <button class="btn btn-success btn-sm" onclick="window.sprintManager.openStartSprintModal(${sprint.id})">
                                <i data-lucide="play"></i>
                                Start Sprint
                            </button>
                            <button class="btn btn-ghost btn-sm" onclick="window.sprintManager.editSprint(${sprint.id})">
                                <i data-lucide="edit-2"></i>
                            </button>
                            <button class="btn btn-ghost btn-sm" onclick="window.sprintManager.deleteSprint(${sprint.id})">
                                <i data-lucide="trash-2"></i>
                            </button>
                        ` : sprint.status === 'active' ? `
                            <button class="btn btn-primary btn-sm" onclick="window.sprintManager.openCompleteSprintModal(${sprint.id})">
                                <i data-lucide="check-circle"></i>
                                Complete Sprint
                            </button>
                            <button class="btn btn-ghost btn-sm" onclick="window.sprintManager.viewSprintReport(${sprint.id})">
                                <i data-lucide="bar-chart-2"></i>
                                Report
                            </button>
                        ` : `
                            <button class="btn btn-ghost btn-sm" onclick="window.sprintManager.viewSprintReport(${sprint.id})">
                                <i data-lucide="bar-chart-2"></i>
                                View Report
                            </button>
                        `}
                    </div>
                </div>

                ${sprint.goal ? `
                    <div class="sprint-goal">
                        <strong>Goal:</strong> ${sprint.goal}
                    </div>
                ` : ''}

                <div class="sprint-progress">
                    <div class="progress-bar">
                        <div class="progress-bar-fill" style="width: ${completionRate}%"></div>
                    </div>
                    <div class="progress-stats">
                        <span>${completedCount} of ${issueCount} issues completed</span>
                        <span>${completionRate}%</span>
                    </div>
                </div>
            </div>
        `;
    }

    openCreateSprintModal() {
        document.getElementById('sprintModalTitle').textContent = 'Create Sprint';
        document.getElementById('saveSprintBtn').textContent = 'Create Sprint';
        document.getElementById('sprintForm').reset();
        
        // Set default start date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('sprintStartDate').value = today;
        
        // Calculate default end date (2 weeks)
        const endDate = this.calculateEndDate(today, 2);
        document.getElementById('sprintEndDate').value = endDate;
        
        this.sprintModal.style.display = 'block';
    }

    closeSprintModal() {
        this.sprintModal.style.display = 'none';
    }

    async createSprint() {
        const formData = {
            name: document.getElementById('sprintName').value,
            goal: document.getElementById('sprintGoal').value,
            start_date: document.getElementById('sprintStartDate').value,
            end_date: document.getElementById('sprintEndDate').value,
            duration: parseInt(document.getElementById('sprintDuration').value),
            status: 'planned'
        };

        try {
            const projectId = this.getCurrentProjectId();
            const response = await fetch(`/api/projects/${projectId}/sprints`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Sprint Created',
                    message: `${formData.name} has been created successfully`,
                    type: 'success'
                });
                
                this.closeSprintModal();
                await this.loadSprints();
            }
        } catch (error) {
            console.error('Failed to create sprint:', error);
            window.notificationManager?.addNotification({
                title: 'Error',
                message: 'Failed to create sprint',
                type: 'error'
            });
        }
    }

    openStartSprintModal(sprintId) {
        const sprint = this.sprints.find(s => s.id === sprintId);
        if (!sprint) return;

        document.getElementById('startSprintName').textContent = sprint.name;
        document.getElementById('startSprintDuration').textContent = 
            `${sprint.duration} ${sprint.duration === 1 ? 'week' : 'weeks'}`;
        document.getElementById('startSprintIssues').textContent = 
            sprint.issues?.length || 0;

        document.getElementById('confirmStartSprintBtn').dataset.sprintId = sprintId;
        document.getElementById('startSprintModal').style.display = 'block';
    }

    async startSprint() {
        const sprintId = document.getElementById('confirmStartSprintBtn').dataset.sprintId;
        
        try {
            const response = await fetch(`/api/sprints/${sprintId}/start`, {
                method: 'POST'
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Sprint Started',
                    message: 'Sprint has been started successfully',
                    type: 'success'
                });
                
                document.getElementById('startSprintModal').style.display = 'none';
                await this.loadSprints();
            }
        } catch (error) {
            console.error('Failed to start sprint:', error);
        }
    }

    openCompleteSprintModal(sprintId) {
        const sprint = this.sprints.find(s => s.id === sprintId);
        if (!sprint) return;

        const completed = sprint.issues?.filter(i => i.status === 'Done').length || 0;
        const incomplete = (sprint.issues?.length || 0) - completed;
        const percentage = sprint.issues?.length > 0 ? 
            Math.round((completed / sprint.issues.length) * 100) : 0;

        document.getElementById('completeSprintName').textContent = sprint.name;
        document.getElementById('completedIssuesCount').textContent = completed;
        document.getElementById('incompleteIssuesCount').textContent = incomplete;
        document.getElementById('completionPercentage').textContent = `${percentage}%`;

        document.getElementById('confirmCompleteSprintBtn').dataset.sprintId = sprintId;
        document.getElementById('completeSprintModal').style.display = 'block';
    }

    async completeSprint() {
        const sprintId = document.getElementById('confirmCompleteSprintBtn').dataset.sprintId;
        const incompleteAction = document.querySelector('input[name="incompleteAction"]:checked').value;
        const retrospective = document.getElementById('sprintRetrospective').value;

        try {
            const response = await fetch(`/api/sprints/${sprintId}/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    incomplete_action: incompleteAction,
                    retrospective: retrospective
                })
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Sprint Completed',
                    message: 'Sprint has been completed successfully',
                    type: 'success'
                });
                
                document.getElementById('completeSprintModal').style.display = 'none';
                await this.loadSprints();
            }
        } catch (error) {
            console.error('Failed to complete sprint:', error);
        }
    }

    calculateEndDate(startDate, weeks) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + (weeks * 7));
        return date.toISOString().split('T')[0];
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    getCurrentProjectId() {
        // Extract project ID from URL or global variable
        const match = window.location.pathname.match(/\/project\/(\d+)/);
        return match ? match[1] : window.currentProjectId;
    }

    async viewSprintReport(sprintId) {
        // Navigate to sprint report page
        window.location.href = `/sprint/${sprintId}/report`;
    }

    async editSprint(sprintId) {
        const sprint = this.sprints.find(s => s.id === sprintId);
        if (!sprint) return;

        document.getElementById('sprintModalTitle').textContent = 'Edit Sprint';
        document.getElementById('saveSprintBtn').textContent = 'Update Sprint';
        document.getElementById('sprintName').value = sprint.name;
        document.getElementById('sprintGoal').value = sprint.goal || '';
        document.getElementById('sprintStartDate').value = sprint.start_date;
        document.getElementById('sprintEndDate').value = sprint.end_date;
        document.getElementById('sprintDuration').value = sprint.duration;

        document.getElementById('saveSprintBtn').dataset.sprintId = sprintId;
        this.sprintModal.style.display = 'block';
    }

    async deleteSprint(sprintId) {
        if (!confirm('Are you sure you want to delete this sprint?')) return;

        try {
            const response = await fetch(`/api/sprints/${sprintId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                window.notificationManager?.addNotification({
                    title: 'Sprint Deleted',
                    message: 'Sprint has been deleted successfully',
                    type: 'success'
                });
                
                await this.loadSprints();
            }
        } catch (error) {
            console.error('Failed to delete sprint:', error);
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.sprintManager = new SprintManager();
});
