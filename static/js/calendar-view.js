/**
 * Calendar View Manager - JIRA-style calendar with Month/Week/Day/Agenda views
 * Supports drag-and-drop event scheduling, event creation, and multi-view navigation
 */

class CalendarView {
    constructor() {
        this.currentView = 'month'; // month, week, day, agenda
        this.currentDate = new Date();
        this.events = [];
        this.selectedEvent = null;
        this.draggedEvent = null;
        this.isCreatingEvent = false;
        this.createStartCell = null;
        
        this.container = document.getElementById('calendarContainer');
        
        this.init();
    }

    init() {
        if (!this.container) return;
        
        this.loadEvents();
        this.createControls();
        this.render();
        this.setupDragAndDrop();
        this.setupKeyboardShortcuts();
    }

    loadEvents() {
        // Load events from DOM or API
        const eventElements = document.querySelectorAll('[data-calendar-event]');
        this.events = Array.from(eventElements).map(el => ({
            id: el.dataset.eventId,
            title: el.dataset.eventTitle,
            start: new Date(el.dataset.eventStart),
            end: new Date(el.dataset.eventEnd),
            type: el.dataset.eventType || 'issue', // issue, sprint, release, meeting
            color: el.dataset.eventColor || '#0052CC',
            allDay: el.dataset.allDay === 'true',
            attendees: el.dataset.attendees?.split(',') || [],
            location: el.dataset.location || '',
            description: el.dataset.description || '',
            issueKey: el.dataset.issueKey || null
        }));

        // Also fetch from API if available
        this.fetchEventsFromAPI();
    }

    async fetchEventsFromAPI() {
        try {
            const projectId = this.getProjectId();
            if (!projectId) return;

            const response = await fetch(`/api/projects/${projectId}/calendar/events`);
            if (response.ok) {
                const data = await response.json();
                this.events = data.events.map(e => ({
                    ...e,
                    start: new Date(e.start),
                    end: new Date(e.end)
                }));
                this.render();
            }
        } catch (error) {
            console.error('Failed to fetch calendar events:', error);
        }
    }

    createControls() {
        if (document.getElementById('calendarControls')) return;

        const controlsHTML = `
            <div id="calendarControls" class="calendar-controls">
                <div class="calendar-nav">
                    <button class="btn btn-ghost btn-sm" id="calendarPrevBtn" title="Previous">
                        <i data-lucide="chevron-left"></i>
                    </button>
                    <button class="btn btn-ghost btn-sm" id="calendarTodayBtn">
                        Today
                    </button>
                    <button class="btn btn-ghost btn-sm" id="calendarNextBtn" title="Next">
                        <i data-lucide="chevron-right"></i>
                    </button>
                    <h2 id="calendarTitle" class="calendar-title"></h2>
                </div>
                
                <div class="calendar-view-switcher">
                    <div class="btn-group">
                        <button class="btn btn-sm ${this.currentView === 'month' ? 'active' : ''}" data-view="month">Month</button>
                        <button class="btn btn-sm ${this.currentView === 'week' ? 'active' : ''}" data-view="week">Week</button>
                        <button class="btn btn-sm ${this.currentView === 'day' ? 'active' : ''}" data-view="day">Day</button>
                        <button class="btn btn-sm ${this.currentView === 'agenda' ? 'active' : ''}" data-view="agenda">Agenda</button>
                    </div>
                </div>
                
                <div class="calendar-actions">
                    <button class="btn btn-primary btn-sm" id="createEventBtn">
                        <i data-lucide="plus"></i>
                        Create Event
                    </button>
                </div>
            </div>
        `;

        const toolbar = document.querySelector('.calendar-toolbar') || 
                       document.querySelector('.kanban-toolbar');
        
        if (toolbar) {
            toolbar.insertAdjacentHTML('afterend', controlsHTML);
        } else {
            this.container.insertAdjacentHTML('beforebegin', controlsHTML);
        }

        this.setupControlListeners();
        this.updateTitle();

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupControlListeners() {
        document.getElementById('calendarPrevBtn')?.addEventListener('click', () => {
            this.navigatePrevious();
        });

        document.getElementById('calendarNextBtn')?.addEventListener('click', () => {
            this.navigateNext();
        });

        document.getElementById('calendarTodayBtn')?.addEventListener('click', () => {
            this.goToToday();
        });

        document.querySelectorAll('[data-view]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.dataset.view);
            });
        });

        document.getElementById('createEventBtn')?.addEventListener('click', () => {
            this.openCreateEventModal();
        });
    }

    navigatePrevious() {
        if (this.currentView === 'month') {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        } else if (this.currentView === 'week') {
            this.currentDate.setDate(this.currentDate.getDate() - 7);
        } else if (this.currentView === 'day') {
            this.currentDate.setDate(this.currentDate.getDate() - 1);
        } else if (this.currentView === 'agenda') {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        }
        this.updateTitle();
        this.render();
    }

    navigateNext() {
        if (this.currentView === 'month') {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        } else if (this.currentView === 'week') {
            this.currentDate.setDate(this.currentDate.getDate() + 7);
        } else if (this.currentView === 'day') {
            this.currentDate.setDate(this.currentDate.getDate() + 1);
        } else if (this.currentView === 'agenda') {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        }
        this.updateTitle();
        this.render();
    }

    goToToday() {
        this.currentDate = new Date();
        this.updateTitle();
        this.render();
    }

    switchView(view) {
        this.currentView = view;
        
        // Update active button
        document.querySelectorAll('[data-view]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });
        
        this.updateTitle();
        this.render();
    }

    updateTitle() {
        const titleEl = document.getElementById('calendarTitle');
        if (!titleEl) return;

        let title = '';
        if (this.currentView === 'month') {
            title = this.currentDate.toLocaleDateString('en-US', { 
                month: 'long', 
                year: 'numeric' 
            });
        } else if (this.currentView === 'week') {
            const weekStart = this.getWeekStart(this.currentDate);
            const weekEnd = new Date(weekStart);
            weekEnd.setDate(weekEnd.getDate() + 6);
            
            title = `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
        } else if (this.currentView === 'day') {
            title = this.currentDate.toLocaleDateString('en-US', { 
                weekday: 'long',
                month: 'long', 
                day: 'numeric',
                year: 'numeric' 
            });
        } else if (this.currentView === 'agenda') {
            title = 'Agenda';
        }

        titleEl.textContent = title;
    }

    render() {
        this.container.innerHTML = '';

        switch (this.currentView) {
            case 'month':
                this.renderMonthView();
                break;
            case 'week':
                this.renderWeekView();
                break;
            case 'day':
                this.renderDayView();
                break;
            case 'agenda':
                this.renderAgendaView();
                break;
        }
    }

    renderMonthView() {
        const monthGrid = document.createElement('div');
        monthGrid.className = 'calendar-month-grid';

        // Add day headers
        const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const headerRow = document.createElement('div');
        headerRow.className = 'calendar-header-row';
        
        daysOfWeek.forEach(day => {
            const headerCell = document.createElement('div');
            headerCell.className = 'calendar-header-cell';
            headerCell.textContent = day;
            headerRow.appendChild(headerCell);
        });
        
        monthGrid.appendChild(headerRow);

        // Get first and last day of month
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        // Start from the previous Sunday
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - startDate.getDay());
        
        // End at the next Saturday
        const endDate = new Date(lastDay);
        endDate.setDate(endDate.getDate() + (6 - endDate.getDay()));

        // Create calendar cells
        const currentDate = new Date(startDate);
        
        while (currentDate <= endDate) {
            const weekRow = document.createElement('div');
            weekRow.className = 'calendar-week-row';
            
            for (let i = 0; i < 7; i++) {
                const dayCell = this.createMonthDayCell(new Date(currentDate), month);
                weekRow.appendChild(dayCell);
                currentDate.setDate(currentDate.getDate() + 1);
            }
            
            monthGrid.appendChild(weekRow);
        }

        this.container.appendChild(monthGrid);
    }

    createMonthDayCell(date, currentMonth) {
        const cell = document.createElement('div');
        cell.className = 'calendar-day-cell';
        cell.dataset.date = date.toISOString().split('T')[0];
        
        const isToday = this.isToday(date);
        const isCurrentMonth = date.getMonth() === currentMonth;
        const isWeekend = date.getDay() === 0 || date.getDay() === 6;
        
        if (isToday) cell.classList.add('today');
        if (!isCurrentMonth) cell.classList.add('other-month');
        if (isWeekend) cell.classList.add('weekend');

        // Day number
        const dayNumber = document.createElement('div');
        dayNumber.className = 'calendar-day-number';
        dayNumber.textContent = date.getDate();
        cell.appendChild(dayNumber);

        // Events for this day
        const dayEvents = this.getEventsForDay(date);
        const eventsContainer = document.createElement('div');
        eventsContainer.className = 'calendar-day-events';
        
        dayEvents.slice(0, 3).forEach(event => {
            const eventEl = this.createMonthEventElement(event);
            eventsContainer.appendChild(eventEl);
        });

        if (dayEvents.length > 3) {
            const moreEl = document.createElement('div');
            moreEl.className = 'calendar-event-more';
            moreEl.textContent = `+${dayEvents.length - 3} more`;
            moreEl.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showDayEventsModal(date, dayEvents);
            });
            eventsContainer.appendChild(moreEl);
        }

        cell.appendChild(eventsContainer);

        // Click to create event
        cell.addEventListener('click', (e) => {
            if (!e.target.closest('.calendar-event, .calendar-event-more')) {
                this.handleDayCellClick(date);
            }
        });

        return cell;
    }

    createMonthEventElement(event) {
        const eventEl = document.createElement('div');
        eventEl.className = 'calendar-event calendar-event-month';
        eventEl.style.backgroundColor = event.color;
        eventEl.dataset.eventId = event.id;
        
        const timeStr = event.allDay ? 'All day' : 
            event.start.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        
        eventEl.innerHTML = `
            <span class="calendar-event-time">${timeStr}</span>
            <span class="calendar-event-title">${event.title}</span>
        `;

        eventEl.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showEventDetails(event);
        });

        return eventEl;
    }

    renderWeekView() {
        const weekGrid = document.createElement('div');
        weekGrid.className = 'calendar-week-grid';

        // Time column + 7 day columns
        const weekStart = this.getWeekStart(this.currentDate);
        
        // Header row with dates
        const headerRow = document.createElement('div');
        headerRow.className = 'calendar-week-header';
        
        // Empty cell for time column
        const timeHeader = document.createElement('div');
        timeHeader.className = 'calendar-time-header';
        headerRow.appendChild(timeHeader);

        // Day headers
        for (let i = 0; i < 7; i++) {
            const date = new Date(weekStart);
            date.setDate(date.getDate() + i);
            
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            if (this.isToday(date)) dayHeader.classList.add('today');
            
            dayHeader.innerHTML = `
                <div class="day-name">${date.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                <div class="day-number">${date.getDate()}</div>
            `;
            
            headerRow.appendChild(dayHeader);
        }
        
        weekGrid.appendChild(headerRow);

        // Time slots (7am to 7pm)
        const gridBody = document.createElement('div');
        gridBody.className = 'calendar-week-body';
        
        for (let hour = 7; hour <= 19; hour++) {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'calendar-week-row';
            
            // Time label
            const timeLabel = document.createElement('div');
            timeLabel.className = 'calendar-time-label';
            timeLabel.textContent = this.formatHour(hour);
            rowDiv.appendChild(timeLabel);
            
            // Day cells
            for (let day = 0; day < 7; day++) {
                const date = new Date(weekStart);
                date.setDate(date.getDate() + day);
                date.setHours(hour, 0, 0, 0);
                
                const cell = document.createElement('div');
                cell.className = 'calendar-time-cell';
                cell.dataset.datetime = date.toISOString();
                
                if (this.isNow(date)) {
                    cell.classList.add('current-hour');
                }
                
                rowDiv.appendChild(cell);
            }
            
            gridBody.appendChild(rowDiv);
        }
        
        weekGrid.appendChild(gridBody);
        this.container.appendChild(weekGrid);

        // Render events as overlay
        this.renderWeekEvents(weekStart);
    }

    renderWeekEvents(weekStart) {
        const weekEvents = this.events.filter(event => {
            const weekEnd = new Date(weekStart);
            weekEnd.setDate(weekEnd.getDate() + 7);
            return event.start < weekEnd && event.end >= weekStart;
        });

        weekEvents.forEach(event => {
            // Calculate position and size
            const eventEl = this.createWeekEventElement(event, weekStart);
            if (eventEl) {
                this.container.querySelector('.calendar-week-body').appendChild(eventEl);
            }
        });
    }

    createWeekEventElement(event, weekStart) {
        // Calculate column (day of week)
        const daysDiff = Math.floor((event.start - weekStart) / (1000 * 60 * 60 * 24));
        if (daysDiff < 0 || daysDiff >= 7) return null;

        const eventEl = document.createElement('div');
        eventEl.className = 'calendar-event calendar-event-week';
        eventEl.style.backgroundColor = event.color;
        eventEl.dataset.eventId = event.id;

        // Calculate row position (time of day)
        const startHour = event.start.getHours();
        const startMin = event.start.getMinutes();
        const duration = (event.end - event.start) / (1000 * 60); // minutes

        const topPercent = ((startHour - 7) * 60 + startMin) / (13 * 60) * 100; // 7am-8pm = 13 hours
        const heightPercent = (duration / (13 * 60)) * 100;

        eventEl.style.position = 'absolute';
        eventEl.style.left = `calc(${(daysDiff / 7) * 100}% + 60px)`;
        eventEl.style.width = `calc(${100 / 7}% - 4px)`;
        eventEl.style.top = `${topPercent}%`;
        eventEl.style.height = `${Math.max(heightPercent, 5)}%`;

        eventEl.innerHTML = `
            <div class="calendar-event-content">
                <div class="calendar-event-title">${event.title}</div>
                <div class="calendar-event-time">
                    ${event.start.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })} - 
                    ${event.end.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
                </div>
            </div>
        `;

        eventEl.addEventListener('click', () => {
            this.showEventDetails(event);
        });

        return eventEl;
    }

    renderDayView() {
        const dayGrid = document.createElement('div');
        dayGrid.className = 'calendar-day-grid';

        // Time slots for the day (7am to 7pm)
        for (let hour = 7; hour <= 19; hour++) {
            const hourRow = document.createElement('div');
            hourRow.className = 'calendar-hour-row';
            
            const timeLabel = document.createElement('div');
            timeLabel.className = 'calendar-time-label';
            timeLabel.textContent = this.formatHour(hour);
            
            const hourContent = document.createElement('div');
            hourContent.className = 'calendar-hour-content';
            
            // Check if this is current hour
            const now = new Date();
            if (this.isToday(this.currentDate) && now.getHours() === hour) {
                hourContent.classList.add('current-hour');
            }
            
            hourRow.appendChild(timeLabel);
            hourRow.appendChild(hourContent);
            dayGrid.appendChild(hourRow);
        }

        this.container.appendChild(dayGrid);

        // Render events for this day
        this.renderDayEvents();
    }

    renderDayEvents() {
        const dayEvents = this.getEventsForDay(this.currentDate);
        
        dayEvents.forEach(event => {
            const eventEl = this.createDayEventElement(event);
            if (eventEl) {
                this.container.querySelector('.calendar-day-grid').appendChild(eventEl);
            }
        });
    }

    createDayEventElement(event) {
        const eventEl = document.createElement('div');
        eventEl.className = 'calendar-event calendar-event-day';
        eventEl.style.backgroundColor = event.color;
        eventEl.dataset.eventId = event.id;

        const startHour = event.start.getHours();
        const startMin = event.start.getMinutes();
        const duration = (event.end - event.start) / (1000 * 60);

        const topPercent = ((startHour - 7) * 60 + startMin) / (13 * 60) * 100;
        const heightPercent = (duration / (13 * 60)) * 100;

        eventEl.style.position = 'absolute';
        eventEl.style.left = '60px';
        eventEl.style.right = '10px';
        eventEl.style.top = `${topPercent}%`;
        eventEl.style.height = `${Math.max(heightPercent, 8)}%`;

        eventEl.innerHTML = `
            <div class="calendar-event-content">
                <div class="calendar-event-title">${event.title}</div>
                <div class="calendar-event-time">
                    ${event.start.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })} - 
                    ${event.end.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
                </div>
                ${event.location ? `<div class="calendar-event-location"><i data-lucide="map-pin" style="width: 12px; height: 12px;"></i> ${event.location}</div>` : ''}
            </div>
        `;

        eventEl.addEventListener('click', () => {
            this.showEventDetails(event);
        });

        if (window.lucide) {
            lucide.createIcons();
        }

        return eventEl;
    }

    renderAgendaView() {
        const agendaList = document.createElement('div');
        agendaList.className = 'calendar-agenda-list';

        // Get next 30 days of events
        const endDate = new Date(this.currentDate);
        endDate.setDate(endDate.getDate() + 30);

        const upcomingEvents = this.events.filter(e => 
            e.start >= this.currentDate && e.start <= endDate
        ).sort((a, b) => a.start - b.start);

        if (upcomingEvents.length === 0) {
            agendaList.innerHTML = '<div class="calendar-empty-state">No upcoming events</div>';
        } else {
            let currentDate = null;
            
            upcomingEvents.forEach(event => {
                const eventDate = event.start.toLocaleDateString();
                
                // Add date header if new date
                if (eventDate !== currentDate) {
                    currentDate = eventDate;
                    const dateHeader = document.createElement('div');
                    dateHeader.className = 'calendar-agenda-date';
                    dateHeader.textContent = event.start.toLocaleDateString('en-US', {
                        weekday: 'long',
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric'
                    });
                    agendaList.appendChild(dateHeader);
                }
                
                // Add event
                const eventItem = this.createAgendaEventItem(event);
                agendaList.appendChild(eventItem);
            });
        }

        this.container.appendChild(agendaList);
    }

    createAgendaEventItem(event) {
        const item = document.createElement('div');
        item.className = 'calendar-agenda-item';
        item.style.borderLeftColor = event.color;
        
        item.innerHTML = `
            <div class="calendar-agenda-time">
                ${event.allDay ? 'All day' : event.start.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
            </div>
            <div class="calendar-agenda-content">
                <div class="calendar-agenda-title">${event.title}</div>
                ${event.location ? `<div class="calendar-agenda-location"><i data-lucide="map-pin" style="width: 14px; height: 14px;"></i> ${event.location}</div>` : ''}
                ${event.description ? `<div class="calendar-agenda-description">${event.description}</div>` : ''}
            </div>
        `;

        item.addEventListener('click', () => {
            this.showEventDetails(event);
        });

        if (window.lucide) {
            lucide.createIcons();
        }

        return item;
    }

    // Helper methods
    getEventsForDay(date) {
        const dayStart = new Date(date);
        dayStart.setHours(0, 0, 0, 0);
        const dayEnd = new Date(date);
        dayEnd.setHours(23, 59, 59, 999);

        return this.events.filter(event => {
            return event.start < dayEnd && event.end >= dayStart;
        });
    }

    getWeekStart(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day;
        return new Date(d.setDate(diff));
    }

    isToday(date) {
        const today = new Date();
        return date.toDateString() === today.toDateString();
    }

    isNow(date) {
        const now = new Date();
        return date.toDateString() === now.toDateString() && 
               date.getHours() === now.getHours();
    }

    formatHour(hour) {
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour > 12 ? hour - 12 : (hour === 0 ? 12 : hour);
        return `${displayHour} ${ampm}`;
    }

    // Event handling
    handleDayCellClick(date) {
        this.openCreateEventModal(date);
    }

    showEventDetails(event) {
        // Create event details modal
        alert(`Event: ${event.title}\nStart: ${event.start}\nEnd: ${event.end}`);
        // TODO: Implement proper modal
    }

    showDayEventsModal(date, events) {
        // Show all events for a specific day
        alert(`${events.length} events on ${date.toLocaleDateString()}`);
        // TODO: Implement proper modal
    }

    openCreateEventModal(date = null) {
        alert('Create Event Modal - Coming soon!');
        // TODO: Implement event creation modal
    }

    // Drag and drop
    setupDragAndDrop() {
        // Implemented in next section
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // T - Today
            if (e.key === 't' || e.key === 'T') {
                if (!e.target.matches('input, textarea')) {
                    this.goToToday();
                }
            }
            // Arrow keys for navigation
            if (!e.target.matches('input, textarea')) {
                if (e.key === 'ArrowLeft') {
                    this.navigatePrevious();
                } else if (e.key === 'ArrowRight') {
                    this.navigateNext();
                }
            }
        });
    }

    getProjectId() {
        const match = window.location.pathname.match(/projects\/(\d+)/);
        return match ? match[1] : null;
    }
}

// Initialize calendar view
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('calendarContainer')) {
        window.calendarView = new CalendarView();
    }
});
