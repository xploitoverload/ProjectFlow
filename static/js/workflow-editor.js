/**
 * Workflow Editor - JIRA-style visual workflow designer
 * Features: Drag-drop states, transition configuration, conditions, validators
 */

class WorkflowEditor {
    constructor() {
        this.workflow = null;
        this.states = [];
        this.transitions = [];
        this.selectedState = null;
        this.selectedTransition = null;
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        this.canvas = null;
        this.ctx = null;
        this.zoom = 1;
        this.pan = { x: 0, y: 0 };
        
        this.init();
    }

    init() {
        this.createEditorModal();
        this.setupEventListeners();
    }

    createEditorModal() {
        const modalHTML = `
            <div id="workflowEditorModal" class="workflow-modal" style="display: none;">
                <div class="workflow-modal-backdrop"></div>
                <div class="workflow-modal-container">
                    <div class="workflow-modal-header">
                        <div class="workflow-header-left">
                            <h2 id="workflowTitle">Workflow Editor</h2>
                            <select id="workflowSelector" class="workflow-select">
                                <option value="">Select workflow...</option>
                            </select>
                        </div>
                        <div class="workflow-header-right">
                            <button class="btn btn-ghost btn-sm" id="newWorkflowBtn">
                                <i data-lucide="plus"></i>
                                New Workflow
                            </button>
                            <button class="btn btn-ghost btn-sm" id="publishWorkflowBtn">
                                <i data-lucide="upload"></i>
                                Publish
                            </button>
                            <button class="btn-icon" id="closeWorkflowModal">
                                <i data-lucide="x"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="workflow-modal-body">
                        <!-- Toolbar -->
                        <div class="workflow-toolbar">
                            <div class="toolbar-group">
                                <button class="tool-btn" id="addStateBtn" title="Add State">
                                    <i data-lucide="circle"></i>
                                    <span>Add State</span>
                                </button>
                                <button class="tool-btn" id="addTransitionBtn" title="Add Transition">
                                    <i data-lucide="arrow-right"></i>
                                    <span>Add Transition</span>
                                </button>
                            </div>
                            
                            <div class="toolbar-group">
                                <button class="tool-btn" id="zoomInBtn" title="Zoom In">
                                    <i data-lucide="zoom-in"></i>
                                </button>
                                <span class="zoom-level">100%</span>
                                <button class="tool-btn" id="zoomOutBtn" title="Zoom Out">
                                    <i data-lucide="zoom-out"></i>
                                </button>
                                <button class="tool-btn" id="fitToScreenBtn" title="Fit to Screen">
                                    <i data-lucide="maximize"></i>
                                </button>
                            </div>
                            
                            <div class="toolbar-group">
                                <button class="tool-btn" id="autoLayoutBtn" title="Auto Layout">
                                    <i data-lucide="layout"></i>
                                    <span>Auto Layout</span>
                                </button>
                            </div>
                        </div>

                        <!-- Canvas and Properties -->
                        <div class="workflow-content">
                            <!-- Canvas -->
                            <div class="workflow-canvas-container">
                                <canvas id="workflowCanvas"></canvas>
                                <div class="canvas-hint" id="canvasHint">
                                    Click "Add State" to start building your workflow
                                </div>
                            </div>

                            <!-- Properties Panel -->
                            <div class="workflow-properties" id="workflowProperties">
                                <div class="properties-header">
                                    <h3>Properties</h3>
                                </div>
                                <div class="properties-content" id="propertiesContent">
                                    <p class="properties-empty">Select a state or transition to edit properties</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        this.canvas = document.getElementById('workflowCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        // Modal controls
        document.getElementById('closeWorkflowModal')?.addEventListener('click', () => {
            this.closeModal();
        });

        // Workflow selector
        document.getElementById('workflowSelector')?.addEventListener('change', (e) => {
            this.loadWorkflow(e.target.value);
        });

        // Toolbar actions
        document.getElementById('addStateBtn')?.addEventListener('click', () => {
            this.addState();
        });

        document.getElementById('addTransitionBtn')?.addEventListener('click', () => {
            this.startAddingTransition();
        });

        document.getElementById('zoomInBtn')?.addEventListener('click', () => {
            this.zoomIn();
        });

        document.getElementById('zoomOutBtn')?.addEventListener('click', () => {
            this.zoomOut();
        });

        document.getElementById('fitToScreenBtn')?.addEventListener('click', () => {
            this.fitToScreen();
        });

        document.getElementById('autoLayoutBtn')?.addEventListener('click', () => {
            this.autoLayout();
        });

        document.getElementById('newWorkflowBtn')?.addEventListener('click', () => {
            this.createNewWorkflow();
        });

        document.getElementById('publishWorkflowBtn')?.addEventListener('click', () => {
            this.publishWorkflow();
        });

        // Canvas interactions
        this.canvas.addEventListener('mousedown', (e) => this.handleCanvasMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleCanvasMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleCanvasMouseUp(e));
        this.canvas.addEventListener('wheel', (e) => this.handleCanvasWheel(e));
        this.canvas.addEventListener('dblclick', (e) => this.handleCanvasDoubleClick(e));

        // Resize canvas
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    openModal() {
        document.getElementById('workflowEditorModal').style.display = 'block';
        this.resizeCanvas();
        this.render();
    }

    closeModal() {
        document.getElementById('workflowEditorModal').style.display = 'none';
    }

    resizeCanvas() {
        const container = document.querySelector('.workflow-canvas-container');
        if (!container) return;

        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight;
        this.render();
    }

    addState(x = null, y = null) {
        const state = {
            id: `state-${Date.now()}`,
            name: `State ${this.states.length + 1}`,
            x: x !== null ? x : this.canvas.width / 2 + Math.random() * 100 - 50,
            y: y !== null ? y : this.canvas.height / 2 + Math.random() * 100 - 50,
            color: this.getRandomColor(),
            isInitial: this.states.length === 0,
            isFinal: false
        };

        this.states.push(state);
        this.render();
        this.selectState(state);
        
        document.getElementById('canvasHint').style.display = 'none';
    }

    startAddingTransition() {
        if (this.states.length < 2) {
            alert('Add at least 2 states before creating transitions');
            return;
        }
        
        alert('Click on a source state, then click on a target state to create a transition');
        this.addingTransition = { source: null };
    }

    addTransition(sourceId, targetId) {
        const transition = {
            id: `transition-${Date.now()}`,
            name: 'Transition',
            source: sourceId,
            target: targetId,
            conditions: [],
            validators: [],
            postFunctions: []
        };

        this.transitions.push(transition);
        this.render();
        this.selectTransition(transition);
    }

    selectState(state) {
        this.selectedState = state;
        this.selectedTransition = null;
        this.renderStateProperties(state);
        this.render();
    }

    selectTransition(transition) {
        this.selectedTransition = transition;
        this.selectedState = null;
        this.renderTransitionProperties(transition);
        this.render();
    }

    renderStateProperties(state) {
        const content = document.getElementById('propertiesContent');
        content.innerHTML = `
            <div class="property-section">
                <h4>State Properties</h4>
                
                <div class="form-group">
                    <label>State Name</label>
                    <input type="text" class="form-input" value="${state.name}" 
                           onchange="window.workflowEditor.updateStateName('${state.id}', this.value)">
                </div>

                <div class="form-group">
                    <label>State Type</label>
                    <div class="state-type-options">
                        <label class="checkbox-label">
                            <input type="checkbox" ${state.isInitial ? 'checked' : ''}
                                   onchange="window.workflowEditor.updateStateType('${state.id}', 'initial', this.checked)">
                            <span>Initial State</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" ${state.isFinal ? 'checked' : ''}
                                   onchange="window.workflowEditor.updateStateType('${state.id}', 'final', this.checked)">
                            <span>Final State</span>
                        </label>
                    </div>
                </div>

                <div class="form-group">
                    <label>Color</label>
                    <input type="color" class="color-input" value="${state.color}"
                           onchange="window.workflowEditor.updateStateColor('${state.id}', this.value)">
                </div>

                <div class="property-actions">
                    <button class="btn btn-ghost btn-sm" onclick="window.workflowEditor.deleteState('${state.id}')">
                        <i data-lucide="trash-2"></i>
                        Delete State
                    </button>
                </div>
            </div>
        `;

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderTransitionProperties(transition) {
        const content = document.getElementById('propertiesContent');
        const sourceState = this.states.find(s => s.id === transition.source);
        const targetState = this.states.find(s => s.id === transition.target);

        content.innerHTML = `
            <div class="property-section">
                <h4>Transition Properties</h4>
                
                <div class="form-group">
                    <label>Transition Name</label>
                    <input type="text" class="form-input" value="${transition.name}"
                           onchange="window.workflowEditor.updateTransitionName('${transition.id}', this.value)">
                </div>

                <div class="transition-flow">
                    <div class="flow-state">
                        <span class="flow-label">From:</span>
                        <span class="flow-value">${sourceState?.name || 'Unknown'}</span>
                    </div>
                    <i data-lucide="arrow-right"></i>
                    <div class="flow-state">
                        <span class="flow-label">To:</span>
                        <span class="flow-value">${targetState?.name || 'Unknown'}</span>
                    </div>
                </div>

                <div class="form-group">
                    <label>Conditions</label>
                    <div class="conditions-list" id="conditionsList">
                        ${transition.conditions.map((c, i) => `
                            <div class="condition-item">
                                <span>${c.name}</span>
                                <button class="btn-icon-sm" onclick="window.workflowEditor.removeCondition('${transition.id}', ${i})">
                                    <i data-lucide="x"></i>
                                </button>
                            </div>
                        `).join('') || '<p class="empty-text">No conditions</p>'}
                    </div>
                    <button class="btn btn-ghost btn-sm" onclick="window.workflowEditor.addCondition('${transition.id}')">
                        <i data-lucide="plus"></i>
                        Add Condition
                    </button>
                </div>

                <div class="form-group">
                    <label>Validators</label>
                    <div class="validators-list">
                        ${transition.validators.length === 0 ? '<p class="empty-text">No validators</p>' : ''}
                    </div>
                    <button class="btn btn-ghost btn-sm" onclick="window.workflowEditor.addValidator('${transition.id}')">
                        <i data-lucide="plus"></i>
                        Add Validator
                    </button>
                </div>

                <div class="form-group">
                    <label>Post Functions</label>
                    <div class="post-functions-list">
                        ${transition.postFunctions.length === 0 ? '<p class="empty-text">No post functions</p>' : ''}
                    </div>
                    <button class="btn btn-ghost btn-sm" onclick="window.workflowEditor.addPostFunction('${transition.id}')">
                        <i data-lucide="plus"></i>
                        Add Post Function
                    </button>
                </div>

                <div class="property-actions">
                    <button class="btn btn-ghost btn-sm" onclick="window.workflowEditor.deleteTransition('${transition.id}')">
                        <i data-lucide="trash-2"></i>
                        Delete Transition
                    </button>
                </div>
            </div>
        `;

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    handleCanvasMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.pan.x) / this.zoom;
        const y = (e.clientY - rect.top - this.pan.y) / this.zoom;

        // Check if clicking on a state
        const clickedState = this.getStateAtPosition(x, y);
        
        if (clickedState) {
            if (this.addingTransition) {
                if (!this.addingTransition.source) {
                    this.addingTransition.source = clickedState.id;
                } else if (this.addingTransition.source !== clickedState.id) {
                    this.addTransition(this.addingTransition.source, clickedState.id);
                    this.addingTransition = null;
                }
            } else {
                this.isDragging = true;
                this.selectedState = clickedState;
                this.dragOffset = { x: x - clickedState.x, y: y - clickedState.y };
                this.selectState(clickedState);
            }
        } else {
            // Check if clicking on a transition
            const clickedTransition = this.getTransitionAtPosition(x, y);
            if (clickedTransition) {
                this.selectTransition(clickedTransition);
            } else {
                this.selectedState = null;
                this.selectedTransition = null;
                document.getElementById('propertiesContent').innerHTML = 
                    '<p class="properties-empty">Select a state or transition to edit properties</p>';
            }
        }

        this.render();
    }

    handleCanvasMouseMove(e) {
        if (this.isDragging && this.selectedState) {
            const rect = this.canvas.getBoundingClientRect();
            const x = (e.clientX - rect.left - this.pan.x) / this.zoom;
            const y = (e.clientY - rect.top - this.pan.y) / this.zoom;

            this.selectedState.x = x - this.dragOffset.x;
            this.selectedState.y = y - this.dragOffset.y;
            this.render();
        }
    }

    handleCanvasMouseUp(e) {
        this.isDragging = false;
    }

    handleCanvasWheel(e) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        this.zoom *= delta;
        this.zoom = Math.max(0.1, Math.min(3, this.zoom));
        this.updateZoomDisplay();
        this.render();
    }

    handleCanvasDoubleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.pan.x) / this.zoom;
        const y = (e.clientY - rect.top - this.pan.y) / this.zoom;

        const clickedState = this.getStateAtPosition(x, y);
        if (!clickedState) {
            this.addState(x, y);
        }
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.save();
        this.ctx.translate(this.pan.x, this.pan.y);
        this.ctx.scale(this.zoom, this.zoom);

        // Draw transitions first (behind states)
        this.transitions.forEach(transition => {
            this.drawTransition(transition);
        });

        // Draw states
        this.states.forEach(state => {
            this.drawState(state);
        });

        this.ctx.restore();
    }

    drawState(state) {
        const radius = 40;
        const isSelected = this.selectedState?.id === state.id;

        // Shadow for selected state
        if (isSelected) {
            this.ctx.shadowColor = 'rgba(59, 130, 246, 0.5)';
            this.ctx.shadowBlur = 20;
        }

        // Draw circle
        this.ctx.beginPath();
        this.ctx.arc(state.x, state.y, radius, 0, Math.PI * 2);
        this.ctx.fillStyle = state.color;
        this.ctx.fill();
        this.ctx.lineWidth = isSelected ? 4 : 2;
        this.ctx.strokeStyle = isSelected ? '#3B82F6' : '#fff';
        this.ctx.stroke();

        this.ctx.shadowBlur = 0;

        // Draw state name
        this.ctx.fillStyle = '#fff';
        this.ctx.font = 'bold 14px Inter';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(state.name, state.x, state.y);

        // Draw initial/final indicators
        if (state.isInitial) {
            this.ctx.fillStyle = '#10B981';
            this.ctx.beginPath();
            this.ctx.arc(state.x - radius - 15, state.y, 8, 0, Math.PI * 2);
            this.ctx.fill();
        }

        if (state.isFinal) {
            this.ctx.strokeStyle = '#EF4444';
            this.ctx.lineWidth = 3;
            this.ctx.beginPath();
            this.ctx.arc(state.x, state.y, radius + 5, 0, Math.PI * 2);
            this.ctx.stroke();
        }
    }

    drawTransition(transition) {
        const source = this.states.find(s => s.id === transition.source);
        const target = this.states.find(s => s.id === transition.target);

        if (!source || !target) return;

        const isSelected = this.selectedTransition?.id === transition.id;

        // Calculate arrow points
        const angle = Math.atan2(target.y - source.y, target.x - source.x);
        const startX = source.x + Math.cos(angle) * 40;
        const startY = source.y + Math.sin(angle) * 40;
        const endX = target.x - Math.cos(angle) * 40;
        const endY = target.y - Math.sin(angle) * 40;

        // Draw line
        this.ctx.beginPath();
        this.ctx.moveTo(startX, startY);
        this.ctx.lineTo(endX, endY);
        this.ctx.strokeStyle = isSelected ? '#3B82F6' : '#64748B';
        this.ctx.lineWidth = isSelected ? 3 : 2;
        this.ctx.stroke();

        // Draw arrowhead
        const arrowSize = 10;
        this.ctx.beginPath();
        this.ctx.moveTo(endX, endY);
        this.ctx.lineTo(
            endX - arrowSize * Math.cos(angle - Math.PI / 6),
            endY - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        this.ctx.lineTo(
            endX - arrowSize * Math.cos(angle + Math.PI / 6),
            endY - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        this.ctx.closePath();
        this.ctx.fillStyle = isSelected ? '#3B82F6' : '#64748B';
        this.ctx.fill();

        // Draw transition label
        const midX = (startX + endX) / 2;
        const midY = (startY + endY) / 2;
        this.ctx.fillStyle = '#1E293B';
        this.ctx.fillRect(midX - 30, midY - 10, 60, 20);
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '11px Inter';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(transition.name, midX, midY);
    }

    getStateAtPosition(x, y) {
        return this.states.find(state => {
            const dx = x - state.x;
            const dy = y - state.y;
            return Math.sqrt(dx * dx + dy * dy) <= 40;
        });
    }

    getTransitionAtPosition(x, y) {
        // Simplified - check if near transition line
        return null;
    }

    getRandomColor() {
        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    zoomIn() {
        this.zoom *= 1.2;
        this.zoom = Math.min(3, this.zoom);
        this.updateZoomDisplay();
        this.render();
    }

    zoomOut() {
        this.zoom /= 1.2;
        this.zoom = Math.max(0.1, this.zoom);
        this.updateZoomDisplay();
        this.render();
    }

    updateZoomDisplay() {
        document.querySelector('.zoom-level').textContent = `${Math.round(this.zoom * 100)}%`;
    }

    fitToScreen() {
        if (this.states.length === 0) return;

        const padding = 50;
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

        this.states.forEach(state => {
            minX = Math.min(minX, state.x);
            minY = Math.min(minY, state.y);
            maxX = Math.max(maxX, state.x);
            maxY = Math.max(maxY, state.y);
        });

        const width = maxX - minX + padding * 2;
        const height = maxY - minY + padding * 2;
        
        this.zoom = Math.min(this.canvas.width / width, this.canvas.height / height);
        this.pan.x = (this.canvas.width - (minX + maxX) * this.zoom) / 2;
        this.pan.y = (this.canvas.height - (minY + maxY) * this.zoom) / 2;
        
        this.updateZoomDisplay();
        this.render();
    }

    autoLayout() {
        if (this.states.length === 0) return;

        // Simple circular layout
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 100;

        this.states.forEach((state, i) => {
            const angle = (i / this.states.length) * Math.PI * 2;
            state.x = centerX + Math.cos(angle) * radius;
            state.y = centerY + Math.sin(angle) * radius;
        });

        this.render();
    }

    // Property update methods
    updateStateName(stateId, name) {
        const state = this.states.find(s => s.id === stateId);
        if (state) {
            state.name = name;
            this.render();
        }
    }

    updateStateType(stateId, type, checked) {
        const state = this.states.find(s => s.id === stateId);
        if (state) {
            if (type === 'initial') {
                if (checked) {
                    this.states.forEach(s => s.isInitial = false);
                }
                state.isInitial = checked;
            } else if (type === 'final') {
                state.isFinal = checked;
            }
            this.render();
        }
    }

    updateStateColor(stateId, color) {
        const state = this.states.find(s => s.id === stateId);
        if (state) {
            state.color = color;
            this.render();
        }
    }

    updateTransitionName(transitionId, name) {
        const transition = this.transitions.find(t => t.id === transitionId);
        if (transition) {
            transition.name = name;
            this.render();
        }
    }

    deleteState(stateId) {
        if (!confirm('Delete this state?')) return;

        this.states = this.states.filter(s => s.id !== stateId);
        this.transitions = this.transitions.filter(t => 
            t.source !== stateId && t.target !== stateId
        );
        this.selectedState = null;
        
        document.getElementById('propertiesContent').innerHTML = 
            '<p class="properties-empty">Select a state or transition to edit properties</p>';
        
        this.render();
    }

    deleteTransition(transitionId) {
        if (!confirm('Delete this transition?')) return;

        this.transitions = this.transitions.filter(t => t.id !== transitionId);
        this.selectedTransition = null;
        
        document.getElementById('propertiesContent').innerHTML = 
            '<p class="properties-empty">Select a state or transition to edit properties</p>';
        
        this.render();
    }

    addCondition(transitionId) {
        const condition = prompt('Enter condition name:');
        if (!condition) return;

        const transition = this.transitions.find(t => t.id === transitionId);
        if (transition) {
            transition.conditions.push({ name: condition });
            this.renderTransitionProperties(transition);
        }
    }

    removeCondition(transitionId, index) {
        const transition = this.transitions.find(t => t.id === transitionId);
        if (transition) {
            transition.conditions.splice(index, 1);
            this.renderTransitionProperties(transition);
        }
    }

    addValidator(transitionId) {
        alert('Add Validator - to be implemented');
    }

    addPostFunction(transitionId) {
        alert('Add Post Function - to be implemented');
    }

    createNewWorkflow() {
        const name = prompt('Enter workflow name:');
        if (!name) return;

        this.workflow = { id: Date.now(), name };
        this.states = [];
        this.transitions = [];
        this.selectedState = null;
        this.selectedTransition = null;
        
        document.getElementById('workflowTitle').textContent = name;
        document.getElementById('canvasHint').style.display = 'block';
        this.render();
    }

    async publishWorkflow() {
        if (!this.workflow) {
            alert('Create a workflow first');
            return;
        }

        if (this.states.length === 0) {
            alert('Add at least one state before publishing');
            return;
        }

        try {
            const response = await fetch('/api/workflows', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    workflow: this.workflow,
                    states: this.states,
                    transitions: this.transitions
                })
            });

            if (response.ok) {
                alert('Workflow published successfully!');
            }
        } catch (error) {
            console.error('Failed to publish workflow:', error);
        }
    }

    async loadWorkflow(workflowId) {
        // Load workflow logic
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.workflowEditor = new WorkflowEditor();
});

// Global function to open workflow editor
function openWorkflowEditor() {
    window.workflowEditor?.openModal();
}
