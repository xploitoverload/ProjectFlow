/**
 * Jira Service Desk Module
 * Features: Queues, Customers, Change Calendar, SLA Management, Request Types,
 * Agent View, Customer Portal
 */

class ServiceDesk {
    constructor(projectKey = 'SUP') {
        this.projectKey = projectKey;
        this.currentView = 'queues'; // queues, customers, calendar
        this.queues = [];
        this.customers = [];
        this.events = [];
        this.requestTypes = [];
        this.slas = [];
        
        this.init();
    }

    async init() {
        await this.loadData();
        this.createServiceDeskUI();
        this.setupEventListeners();
    }

    async loadData() {
        try {
            const [queues, customers, events, requestTypes, slas] = await Promise.all([
                fetch('/api/service-desk/queues').then(r => r.json()),
                fetch('/api/service-desk/customers').then(r => r.json()),
                fetch('/api/service-desk/events').then(r => r.json()),
                fetch('/api/service-desk/request-types').then(r => r.json()),
                fetch('/api/service-desk/slas').then(r => r.json())
            ]);
            
            this.queues = queues;
            this.customers = customers;
            this.events = events;
            this.requestTypes = requestTypes;
            this.slas = slas;
        } catch (error) {
            console.error('Failed to load service desk data:', error);
            this.loadMockData();
        }
    }

    loadMockData() {
        this.queues = [
            { id: 1, name: 'All open requests', count: 45, color: '#0052cc', filter: 'status != Done' },
            { id: 2, name: 'High priority', count: 12, color: '#ff5630', filter: 'priority = High' },
            { id: 3, name: 'Waiting for customer', count: 8, color: '#ffab00', filter: 'status = "Waiting for customer"' },
            { id: 4, name: 'Escalated', count: 3, color: '#de350b', filter: 'labels = escalated' }
        ];

        this.customers = [
            { id: 1, name: 'Alice Johnson', email: 'alice@example.com', company: 'Acme Corp', requests: 12, satisfaction: 4.5, status: 'active' },
            { id: 2, name: 'Bob Smith', email: 'bob@example.com', company: 'Tech Inc', requests: 8, satisfaction: 4.8, status: 'active' },
            { id: 3, name: 'Carol White', email: 'carol@example.com', company: 'Global Ltd', requests: 15, satisfaction: 3.9, status: 'inactive' }
        ];

        this.events = [
            { id: 1, type: 'freeze', title: 'Code Freeze', start: '2026-01-25', end: '2026-01-27', description: 'No deployments allowed' },
            { id: 2, type: 'maintenance', title: 'Database Maintenance', start: '2026-01-30', end: '2026-01-30', description: 'System downtime expected' },
            { id: 3, type: 'release', title: 'Version 2.0 Release', start: '2026-02-01', end: '2026-02-01', description: 'Major release deployment' }
        ];

        this.requestTypes = [
            { id: 1, name: 'Get IT help', icon: 'help-circle', description: 'Request IT support', fields: ['summary', 'description', 'priority'] },
            { id: 2, name: 'Report a system problem', icon: 'alert-triangle', description: 'Report technical issues', fields: ['summary', 'description', 'priority', 'affected-systems'] },
            { id: 3, name: 'Request access', icon: 'key', description: 'Request system access', fields: ['summary', 'description', 'system', 'access-level'] },
            { id: 4, name: 'Ask a question', icon: 'message-circle', description: 'General inquiries', fields: ['summary', 'description'] }
        ];

        this.slas = [
            { id: 1, name: 'Time to first response', target: '4h', achieved: '95%', breached: 2 },
            { id: 2, name: 'Time to resolution', target: '24h', achieved: '88%', breached: 5 }
        ];
    }

    createServiceDeskUI() {
        const html = `
            <div class="service-desk-container" id="serviceDeskContainer">
                <!-- Service Desk Header -->
                <div class="sd-header">
                    <div class="sd-title">
                        <i data-lucide="headphones"></i>
                        <h1>Service Desk</h1>
                        <span class="project-key">${this.projectKey}</span>
                    </div>
                    <div class="sd-actions">
                        <button class="btn-secondary" onclick="serviceDesk.openPortal()">
                            <i data-lucide="external-link"></i>
                            Customer portal
                        </button>
                        <button class="btn-primary" onclick="serviceDesk.createRequest()">
                            <i data-lucide="plus"></i>
                            Create request
                        </button>
                    </div>
                </div>

                <!-- Service Desk Navigation -->
                <div class="sd-nav">
                    <button class="sd-nav-item ${this.currentView === 'queues' ? 'active' : ''}" 
                            onclick="serviceDesk.switchView('queues')">
                        <i data-lucide="inbox"></i>
                        <span>Queues</span>
                    </button>
                    <button class="sd-nav-item ${this.currentView === 'customers' ? 'active' : ''}" 
                            onclick="serviceDesk.switchView('customers')">
                        <i data-lucide="users"></i>
                        <span>Customers</span>
                    </button>
                    <button class="sd-nav-item ${this.currentView === 'calendar' ? 'active' : ''}" 
                            onclick="serviceDesk.switchView('calendar')">
                        <i data-lucide="calendar"></i>
                        <span>Change calendar</span>
                    </button>
                    <button class="sd-nav-item" onclick="serviceDesk.openRequestTypes()">
                        <i data-lucide="file-check"></i>
                        <span>Request types</span>
                    </button>
                    <button class="sd-nav-item" onclick="serviceDesk.openSLAs()">
                        <i data-lucide="clock"></i>
                        <span>SLAs</span>
                    </button>
                </div>

                <!-- Service Desk Content -->
                <div class="sd-content" id="sdContent">
                    ${this.renderCurrentView()}
                </div>
            </div>

            <!-- SLA Dashboard Modal -->
            <div class="modal" id="slaDashboardModal" style="display: none;">
                <div class="modal-overlay" onclick="serviceDesk.closeModal('slaDashboardModal')"></div>
                <div class="modal-content modal-large">
                    <div class="modal-header">
                        <h2>SLA Dashboard</h2>
                        <button class="btn-icon" onclick="serviceDesk.closeModal('slaDashboardModal')">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="sla-metrics">
                            ${this.slas.map(sla => `
                                <div class="sla-card">
                                    <h3>${sla.name}</h3>
                                    <div class="sla-stats">
                                        <div class="sla-stat">
                                            <label>Target</label>
                                            <span class="stat-value">${sla.target}</span>
                                        </div>
                                        <div class="sla-stat">
                                            <label>Achievement</label>
                                            <span class="stat-value stat-success">${sla.achieved}</span>
                                        </div>
                                        <div class="sla-stat">
                                            <label>Breached</label>
                                            <span class="stat-value stat-danger">${sla.breached}</span>
                                        </div>
                                    </div>
                                    <div class="sla-progress">
                                        <div class="progress-bar">
                                            <div class="progress-fill" style="width: ${sla.achieved}"></div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Request Types Modal -->
            <div class="modal" id="requestTypesModal" style="display: none;">
                <div class="modal-overlay" onclick="serviceDesk.closeModal('requestTypesModal')"></div>
                <div class="modal-content modal-medium">
                    <div class="modal-header">
                        <h2>Request Types</h2>
                        <button class="btn-icon" onclick="serviceDesk.closeModal('requestTypesModal')">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="request-types-grid">
                            ${this.requestTypes.map(type => `
                                <div class="request-type-card" onclick="serviceDesk.selectRequestType(${type.id})">
                                    <i data-lucide="${type.icon}"></i>
                                    <h3>${type.name}</h3>
                                    <p>${type.description}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;

        const container = document.getElementById('serviceDeskRoot') || document.body;
        container.innerHTML = html;

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderCurrentView() {
        switch (this.currentView) {
            case 'queues':
                return this.renderQueuesView();
            case 'customers':
                return this.renderCustomersView();
            case 'calendar':
                return this.renderCalendarView();
            default:
                return '<div class="empty-state">Select a view</div>';
        }
    }

    renderQueuesView() {
        return `
            <div class="queues-view">
                <div class="queues-header">
                    <h2>Queues</h2>
                    <button class="btn-secondary" onclick="serviceDesk.createQueue()">
                        <i data-lucide="plus"></i>
                        Create queue
                    </button>
                </div>
                <div class="queues-grid">
                    ${this.queues.map(queue => `
                        <div class="queue-card" onclick="serviceDesk.openQueue(${queue.id})">
                            <div class="queue-header">
                                <div class="queue-icon" style="background: ${queue.color}">
                                    <i data-lucide="inbox"></i>
                                </div>
                                <button class="btn-icon-sm" onclick="event.stopPropagation(); serviceDesk.editQueue(${queue.id})">
                                    <i data-lucide="more-vertical"></i>
                                </button>
                            </div>
                            <h3>${queue.name}</h3>
                            <div class="queue-count">${queue.count} requests</div>
                            <div class="queue-filter">${queue.filter}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderCustomersView() {
        return `
            <div class="customers-view">
                <div class="customers-header">
                    <h2>Customers</h2>
                    <div class="customers-actions">
                        <input type="text" class="search-input" placeholder="Search customers..." 
                               oninput="serviceDesk.searchCustomers(this.value)">
                        <button class="btn-secondary" onclick="serviceDesk.inviteCustomer()">
                            <i data-lucide="user-plus"></i>
                            Invite customer
                        </button>
                    </div>
                </div>
                <div class="customers-table-container">
                    <table class="customers-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Company</th>
                                <th>Requests</th>
                                <th>Satisfaction</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.customers.map(customer => `
                                <tr class="customer-row">
                                    <td>
                                        <div class="customer-name">
                                            <div class="avatar-sm">${this.getInitials(customer.name)}</div>
                                            <span>${customer.name}</span>
                                        </div>
                                    </td>
                                    <td>${customer.email}</td>
                                    <td>${customer.company}</td>
                                    <td>${customer.requests}</td>
                                    <td>
                                        <div class="satisfaction-rating">
                                            <i data-lucide="star" class="star-filled"></i>
                                            <span>${customer.satisfaction}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="status-badge status-${customer.status}">
                                            ${customer.status}
                                        </span>
                                    </td>
                                    <td>
                                        <button class="btn-icon-sm" onclick="serviceDesk.viewCustomer(${customer.id})">
                                            <i data-lucide="eye"></i>
                                        </button>
                                        <button class="btn-icon-sm" onclick="serviceDesk.editCustomer(${customer.id})">
                                            <i data-lucide="edit-2"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    renderCalendarView() {
        const currentMonth = new Date(2026, 0); // January 2026
        const daysInMonth = new Date(2026, 1, 0).getDate();
        const firstDay = new Date(2026, 0, 1).getDay();

        return `
            <div class="calendar-view">
                <div class="calendar-header">
                    <h2>Change Calendar</h2>
                    <div class="calendar-controls">
                        <button class="btn-secondary" onclick="serviceDesk.createEvent()">
                            <i data-lucide="plus"></i>
                            Create event
                        </button>
                        <div class="calendar-nav">
                            <button class="btn-icon" onclick="serviceDesk.prevMonth()">
                                <i data-lucide="chevron-left"></i>
                            </button>
                            <span class="calendar-month">January 2026</span>
                            <button class="btn-icon" onclick="serviceDesk.nextMonth()">
                                <i data-lucide="chevron-right"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="calendar-legend">
                    <div class="legend-item">
                        <span class="legend-dot freeze"></span>
                        <span>Code Freeze</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-dot maintenance"></span>
                        <span>Maintenance</span>
                    </div>
                    <div class="legend-item">
                        <span class="legend-dot release"></span>
                        <span>Release</span>
                    </div>
                </div>

                <div class="calendar-grid">
                    <div class="calendar-days">
                        <div class="day-header">Sun</div>
                        <div class="day-header">Mon</div>
                        <div class="day-header">Tue</div>
                        <div class="day-header">Wed</div>
                        <div class="day-header">Thu</div>
                        <div class="day-header">Fri</div>
                        <div class="day-header">Sat</div>
                    </div>
                    <div class="calendar-dates">
                        ${this.renderCalendarDates(firstDay, daysInMonth)}
                    </div>
                </div>

                <div class="events-list">
                    <h3>Upcoming Events</h3>
                    ${this.events.map(event => `
                        <div class="event-item event-${event.type}">
                            <div class="event-icon">
                                <i data-lucide="${this.getEventIcon(event.type)}"></i>
                            </div>
                            <div class="event-details">
                                <h4>${event.title}</h4>
                                <p>${event.description}</p>
                                <div class="event-date">
                                    ${this.formatDateRange(event.start, event.end)}
                                </div>
                            </div>
                            <button class="btn-icon-sm" onclick="serviceDesk.editEvent(${event.id})">
                                <i data-lucide="more-vertical"></i>
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderCalendarDates(firstDay, daysInMonth) {
        let html = '';
        
        // Empty cells before first day
        for (let i = 0; i < firstDay; i++) {
            html += '<div class="calendar-date empty"></div>';
        }

        // Days of month
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `2026-01-${day.toString().padStart(2, '0')}`;
            const eventsOnDay = this.events.filter(e => 
                dateStr >= e.start && dateStr <= e.end
            );
            
            const isToday = day === 23;

            html += `
                <div class="calendar-date ${isToday ? 'today' : ''}" onclick="serviceDesk.selectDate('${dateStr}')">
                    <span class="date-number">${day}</span>
                    ${eventsOnDay.map(e => `
                        <div class="date-event event-${e.type}" title="${e.title}"></div>
                    `).join('')}
                </div>
            `;
        }

        return html;
    }

    switchView(view) {
        this.currentView = view;
        
        document.querySelectorAll('.sd-nav-item').forEach(item => {
            item.classList.remove('active');
        });
        event.target.closest('.sd-nav-item').classList.add('active');

        document.getElementById('sdContent').innerHTML = this.renderCurrentView();
        
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal').forEach(modal => {
                    modal.style.display = 'none';
                });
            }
        });
    }

    // Queues
    openQueue(queueId) {
        const queue = this.queues.find(q => q.id === queueId);
        if (queue) {
            window.location.href = `/issues?jql=${encodeURIComponent(queue.filter)}`;
        }
    }

    createQueue() { alert('Create queue'); }
    editQueue(id) { alert(`Edit queue ${id}`); }

    // Customers
    searchCustomers(query) {
        // Filter customers
        console.log('Search customers:', query);
    }

    inviteCustomer() { alert('Invite customer'); }
    viewCustomer(id) { alert(`View customer ${id}`); }
    editCustomer(id) { alert(`Edit customer ${id}`); }

    // Calendar
    createEvent() { alert('Create event'); }
    editEvent(id) { alert(`Edit event ${id}`); }
    selectDate(date) { console.log('Selected date:', date); }
    prevMonth() { alert('Previous month'); }
    nextMonth() { alert('Next month'); }

    // Request Types
    openRequestTypes() {
        document.getElementById('requestTypesModal').style.display = 'flex';
        if (window.lucide) lucide.createIcons();
    }

    selectRequestType(typeId) {
        const type = this.requestTypes.find(t => t.id === typeId);
        if (type) {
            this.closeModal('requestTypesModal');
            alert(`Create request: ${type.name}`);
        }
    }

    // SLAs
    openSLAs() {
        document.getElementById('slaDashboardModal').style.display = 'flex';
        if (window.lucide) lucide.createIcons();
    }

    // Portal
    openPortal() {
        window.open('/portal', '_blank');
    }

    createRequest() {
        this.openRequestTypes();
    }

    // Utilities
    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    getInitials(name) {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }

    getEventIcon(type) {
        const icons = {
            freeze: 'snowflake',
            maintenance: 'tool',
            release: 'rocket'
        };
        return icons[type] || 'calendar';
    }

    formatDateRange(start, end) {
        const startDate = new Date(start);
        const endDate = new Date(end);
        
        if (start === end) {
            return startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        }
        
        return `${startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.serviceDesk = new ServiceDesk();
});
