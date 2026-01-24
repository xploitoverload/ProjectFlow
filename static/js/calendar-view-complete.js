/**
 * Complete Calendar View System
 * Month/Week/Day/Agenda views, Drag-drop reschedule, Color coding, Mini calendar, iCal export
 */

class CalendarViewSystem {
    constructor() {
        this.viewMode = 'month'; // month, week, day, agenda
        this.currentDate = new Date();
        this.selectedDate = new Date();
        this.colorBy = 'priority'; // priority, assignee, type, status
        
        this.events = [
            { id: 'e1', title: 'TEST-123: Fix login bug', start: new Date(2026, 0, 23, 10, 0), end: new Date(2026, 0, 23, 12, 0), type: 'Bug', priority: 'High', assignee: 'John Doe', status: 'In Progress' },
            { id: 'e2', title: 'TEST-124: Design review', start: new Date(2026, 0, 24, 14, 0), end: new Date(2026, 0, 24, 15, 0), type: 'Task', priority: 'Medium', assignee: 'Jane Smith', status: 'To Do' },
            { id: 'e3', title: 'TEST-125: Sprint planning', start: new Date(2026, 0, 27, 9, 0), end: new Date(2026, 0, 27, 11, 0), type: 'Story', priority: 'High', assignee: 'Bob Johnson', status: 'Done' }
        ];
        
        this.colorSchemes = {
            priority: {
                'Critical': '#cf222e',
                'High': '#fb8500',
                'Medium': '#0969da',
                'Low': '#1a7f37'
            },
            assignee: {
                'John Doe': '#8250df',
                'Jane Smith': '#0969da',
                'Bob Johnson': '#1a7f37'
            },
            type: {
                'Bug': '#cf222e',
                'Task': '#0969da',
                'Story': '#8250df',
                'Epic': '#fb8500'
            },
            status: {
                'To Do': '#57606a',
                'In Progress': '#0969da',
                'In Review': '#8250df',
                'Done': '#1a7f37'
            }
        };
        
        this.init();
    }
    
    init() {
        console.log('Calendar View System initialized');
    }
    
    render(container) {
        container.innerHTML = `
            <div class="calendar-view-container">
                ${this.renderHeader()}
                <div class="calendar-main">
                    ${this.renderMiniCalendar()}
                    ${this.renderCalendarContent()}
                </div>
            </div>
        `;
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        this.setupDragDrop();
    }
    
    renderHeader() {
        const monthYear = this.currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        const weekRange = this.getWeekRange();
        const dayDate = this.currentDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
        
        return `
            <div class="calendar-header">
                <div class="calendar-nav">
                    <button class="btn-icon" onclick="calendarViewSystem.previousPeriod()">
                        <i data-lucide="chevron-left"></i>
                    </button>
                    <button class="btn btn-secondary" onclick="calendarViewSystem.goToToday()">Today</button>
                    <button class="btn-icon" onclick="calendarViewSystem.nextPeriod()">
                        <i data-lucide="chevron-right"></i>
                    </button>
                    <h2 class="calendar-title">
                        ${this.viewMode === 'month' ? monthYear : this.viewMode === 'week' ? weekRange : dayDate}
                    </h2>
                </div>
                
                <div class="calendar-controls">
                    <div class="view-mode-buttons">
                        <button class="view-btn ${this.viewMode === 'month' ? 'active' : ''}" onclick="calendarViewSystem.setViewMode('month')">Month</button>
                        <button class="view-btn ${this.viewMode === 'week' ? 'active' : ''}" onclick="calendarViewSystem.setViewMode('week')">Week</button>
                        <button class="view-btn ${this.viewMode === 'day' ? 'active' : ''}" onclick="calendarViewSystem.setViewMode('day')">Day</button>
                        <button class="view-btn ${this.viewMode === 'agenda' ? 'active' : ''}" onclick="calendarViewSystem.setViewMode('agenda')">Agenda</button>
                    </div>
                    
                    <div class="color-by-selector">
                        <label>Color by:</label>
                        <select onchange="calendarViewSystem.setColorBy(this.value)">
                            <option value="priority" ${this.colorBy === 'priority' ? 'selected' : ''}>Priority</option>
                            <option value="assignee" ${this.colorBy === 'assignee' ? 'selected' : ''}>Assignee</option>
                            <option value="type" ${this.colorBy === 'type' ? 'selected' : ''}>Type</option>
                            <option value="status" ${this.colorBy === 'status' ? 'selected' : ''}>Status</option>
                        </select>
                    </div>
                    
                    <button class="btn btn-secondary" onclick="calendarViewSystem.exportICalendar()">
                        <i data-lucide="download"></i>
                        Export iCal
                    </button>
                    
                    <button class="btn btn-primary" onclick="calendarViewSystem.createEvent()">
                        <i data-lucide="plus"></i>
                        Create Event
                    </button>
                </div>
            </div>
        `;
    }
    
    renderMiniCalendar() {
        const today = new Date();
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startingDayOfWeek = firstDay.getDay();
        const monthLength = lastDay.getDate();
        
        let html = `
            <div class="mini-calendar">
                <div class="mini-calendar-header">
                    <button class="btn-icon-sm" onclick="calendarViewSystem.miniPrevMonth()">
                        <i data-lucide="chevron-left"></i>
                    </button>
                    <span>${firstDay.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</span>
                    <button class="btn-icon-sm" onclick="calendarViewSystem.miniNextMonth()">
                        <i data-lucide="chevron-right"></i>
                    </button>
                </div>
                <div class="mini-calendar-grid">
                    <div class="mini-day-header">Su</div>
                    <div class="mini-day-header">Mo</div>
                    <div class="mini-day-header">Tu</div>
                    <div class="mini-day-header">We</div>
                    <div class="mini-day-header">Th</div>
                    <div class="mini-day-header">Fr</div>
                    <div class="mini-day-header">Sa</div>
        `;
        
        // Empty cells before first day
        for (let i = 0; i < startingDayOfWeek; i++) {
            html += '<div class="mini-day empty"></div>';
        }
        
        // Days of month
        for (let day = 1; day <= monthLength; day++) {
            const date = new Date(year, month, day);
            const isToday = date.toDateString() === today.toDateString();
            const isSelected = date.toDateString() === this.selectedDate.toDateString();
            const hasEvents = this.getEventsForDate(date).length > 0;
            
            html += `
                <div class="mini-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''} ${hasEvents ? 'has-events' : ''}" 
                    onclick="calendarViewSystem.selectDate(new Date(${year}, ${month}, ${day}))">
                    ${day}
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }
    
    renderCalendarContent() {
        switch(this.viewMode) {
            case 'month':
                return this.renderMonthView();
            case 'week':
                return this.renderWeekView();
            case 'day':
                return this.renderDayView();
            case 'agenda':
                return this.renderAgendaView();
            default:
                return '';
        }
    }
    
    renderMonthView() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startingDayOfWeek = firstDay.getDay();
        const monthLength = lastDay.getDate();
        
        let html = `
            <div class="month-view">
                <div class="month-header">
                    <div class="day-header">Sunday</div>
                    <div class="day-header">Monday</div>
                    <div class="day-header">Tuesday</div>
                    <div class="day-header">Wednesday</div>
                    <div class="day-header">Thursday</div>
                    <div class="day-header">Friday</div>
                    <div class="day-header">Saturday</div>
                </div>
                <div class="month-grid">
        `;
        
        // Empty cells
        for (let i = 0; i < startingDayOfWeek; i++) {
            html += '<div class="day-cell empty"></div>';
        }
        
        // Days with events
        for (let day = 1; day <= monthLength; day++) {
            const date = new Date(year, month, day);
            const isToday = date.toDateString() === new Date().toDateString();
            const weekNumber = this.getWeekNumber(date);
            const events = this.getEventsForDate(date);
            
            html += `
                <div class="day-cell ${isToday ? 'today' : ''}" data-date="${date.toISOString()}" 
                    ondrop="calendarViewSystem.handleDrop(event)" ondragover="calendarViewSystem.handleDragOver(event)">
                    <div class="day-number">
                        ${day}
                        <span class="week-number" title="Week ${weekNumber}">W${weekNumber}</span>
                    </div>
                    <div class="day-events">
                        ${events.map(event => this.renderMonthEvent(event)).join('')}
                    </div>
                </div>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }
    
    renderMonthEvent(event) {
        const color = this.getEventColor(event);
        return `
            <div class="month-event" 
                style="background-color: ${color}; border-left: 3px solid ${color};" 
                draggable="true" 
                data-event-id="${event.id}"
                ondragstart="calendarViewSystem.handleDragStart(event)"
                onclick="calendarViewSystem.viewEvent('${event.id}')">
                <span class="event-time">${this.formatTime(event.start)}</span>
                <span class="event-title">${event.title}</span>
            </div>
        `;
    }
    
    renderWeekView() {
        const weekDays = this.getWeekDays(this.currentDate);
        const hours = Array.from({ length: 24 }, (_, i) => i);
        
        let html = `
            <div class="week-view">
                <div class="week-header">
                    <div class="time-column-header">Time</div>
                    ${weekDays.map(day => `
                        <div class="week-day-header ${this.isToday(day) ? 'today' : ''}">
                            <div class="day-name">${day.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                            <div class="day-number">${day.getDate()}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="week-grid">
                    <div class="time-column">
                        ${hours.map(hour => `
                            <div class="time-slot">${this.formatHour(hour)}</div>
                        `).join('')}
                    </div>
                    ${weekDays.map(day => this.renderWeekDay(day, hours)).join('')}
                </div>
            </div>
        `;
        
        return html;
    }
    
    renderWeekDay(day, hours) {
        const events = this.getEventsForDate(day);
        
        return `
            <div class="week-day" data-date="${day.toISOString()}" 
                ondrop="calendarViewSystem.handleDrop(event)" ondragover="calendarViewSystem.handleDragOver(event)">
                ${hours.map(hour => `
                    <div class="week-time-slot" data-hour="${hour}"></div>
                `).join('')}
                ${events.map(event => this.renderWeekEvent(event)).join('')}
            </div>
        `;
    }
    
    renderWeekEvent(event) {
        const color = this.getEventColor(event);
        const startHour = event.start.getHours() + event.start.getMinutes() / 60;
        const duration = (event.end - event.start) / (1000 * 60 * 60);
        const top = (startHour / 24) * 100;
        const height = (duration / 24) * 100;
        
        return `
            <div class="week-event" 
                style="background-color: ${color}; top: ${top}%; height: ${height}%;" 
                draggable="true" 
                data-event-id="${event.id}"
                ondragstart="calendarViewSystem.handleDragStart(event)"
                onclick="calendarViewSystem.viewEvent('${event.id}')">
                <div class="event-title">${event.title}</div>
                <div class="event-time">${this.formatTime(event.start)} - ${this.formatTime(event.end)}</div>
            </div>
        `;
    }
    
    renderDayView() {
        const hours = Array.from({ length: 24 }, (_, i) => i);
        const events = this.getEventsForDate(this.currentDate);
        
        return `
            <div class="day-view">
                <div class="day-timeline">
                    ${hours.map(hour => `
                        <div class="day-hour">
                            <div class="hour-label">${this.formatHour(hour)}</div>
                            <div class="hour-slot" data-hour="${hour}" 
                                ondrop="calendarViewSystem.handleDrop(event)" 
                                ondragover="calendarViewSystem.handleDragOver(event)">
                                ${events.filter(e => e.start.getHours() === hour).map(event => this.renderDayEvent(event)).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderDayEvent(event) {
        const color = this.getEventColor(event);
        return `
            <div class="day-event" 
                style="background-color: ${color};" 
                draggable="true" 
                data-event-id="${event.id}"
                ondragstart="calendarViewSystem.handleDragStart(event)"
                onclick="calendarViewSystem.viewEvent('${event.id}')">
                <div class="event-title">${event.title}</div>
                <div class="event-time">${this.formatTime(event.start)} - ${this.formatTime(event.end)}</div>
                <div class="event-meta">${event[this.colorBy]}</div>
            </div>
        `;
    }
    
    renderAgendaView() {
        const nextDays = 30;
        const agendaEvents = [];
        
        for (let i = 0; i < nextDays; i++) {
            const date = new Date(this.currentDate);
            date.setDate(date.getDate() + i);
            const events = this.getEventsForDate(date);
            
            if (events.length > 0) {
                agendaEvents.push({ date, events });
            }
        }
        
        return `
            <div class="agenda-view">
                ${agendaEvents.length === 0 ? `
                    <div class="agenda-empty">
                        <i data-lucide="calendar"></i>
                        <p>No upcoming events</p>
                    </div>
                ` : agendaEvents.map(({ date, events }) => `
                    <div class="agenda-day">
                        <div class="agenda-date">
                            <div class="agenda-day-number">${date.getDate()}</div>
                            <div class="agenda-day-name">
                                <div>${date.toLocaleDateString('en-US', { weekday: 'long' })}</div>
                                <div class="agenda-month">${date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</div>
                            </div>
                        </div>
                        <div class="agenda-events">
                            ${events.map(event => this.renderAgendaEvent(event)).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    renderAgendaEvent(event) {
        const color = this.getEventColor(event);
        return `
            <div class="agenda-event" onclick="calendarViewSystem.viewEvent('${event.id}')">
                <div class="event-color-indicator" style="background-color: ${color};"></div>
                <div class="event-details">
                    <div class="event-title">${event.title}</div>
                    <div class="event-time">${this.formatTime(event.start)} - ${this.formatTime(event.end)}</div>
                    <div class="event-meta">
                        <span class="event-type">${event.type}</span>
                        <span class="event-priority">${event.priority}</span>
                        <span class="event-assignee">${event.assignee}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Drag & Drop
    setupDragDrop() {
        this.draggedEvent = null;
    }
    
    handleDragStart(e) {
        this.draggedEvent = e.target.dataset.eventId;
        e.dataTransfer.effectAllowed = 'move';
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }
    
    handleDrop(e) {
        e.preventDefault();
        if (!this.draggedEvent) return;
        
        const targetDate = e.currentTarget.dataset.date;
        const targetHour = e.currentTarget.dataset.hour;
        
        if (targetDate) {
            this.rescheduleEvent(this.draggedEvent, new Date(targetDate), targetHour);
        }
        
        this.draggedEvent = null;
    }
    
    rescheduleEvent(eventId, newDate, newHour) {
        const event = this.events.find(e => e.id === eventId);
        if (event) {
            const duration = event.end - event.start;
            event.start = new Date(newDate);
            if (newHour !== undefined) {
                event.start.setHours(parseInt(newHour), 0, 0, 0);
            }
            event.end = new Date(event.start.getTime() + duration);
            
            this.showToast('Event rescheduled');
            const container = document.querySelector('.calendar-view-container').parentElement;
            this.render(container);
        }
    }
    
    // Helper methods
    getEventsForDate(date) {
        return this.events.filter(event => {
            const eventDate = new Date(event.start);
            return eventDate.toDateString() === date.toDateString();
        });
    }
    
    getEventColor(event) {
        const scheme = this.colorSchemes[this.colorBy];
        return scheme[event[this.colorBy]] || '#57606a';
    }
    
    getWeekDays(date) {
        const days = [];
        const sunday = new Date(date);
        sunday.setDate(date.getDate() - date.getDay());
        
        for (let i = 0; i < 7; i++) {
            const day = new Date(sunday);
            day.setDate(sunday.getDate() + i);
            days.push(day);
        }
        
        return days;
    }
    
    getWeekNumber(date) {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        const dayNum = d.getUTCDay() || 7;
        d.setUTCDate(d.getUTCDate() + 4 - dayNum);
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    }
    
    getWeekRange() {
        const weekDays = this.getWeekDays(this.currentDate);
        const start = weekDays[0].toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const end = weekDays[6].toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        return `${start} - ${end}`;
    }
    
    isToday(date) {
        return date.toDateString() === new Date().toDateString();
    }
    
    formatTime(date) {
        return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    }
    
    formatHour(hour) {
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        return `${displayHour}:00 ${ampm}`;
    }
    
    // Actions
    setViewMode(mode) {
        this.viewMode = mode;
        const container = document.querySelector('.calendar-view-container').parentElement;
        this.render(container);
    }
    
    setColorBy(colorBy) {
        this.colorBy = colorBy;
        const container = document.querySelector('.calendar-view-container').parentElement;
        this.render(container);
    }
    
    previousPeriod() {
        if (this.viewMode === 'month') {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        } else if (this.viewMode === 'week') {
            this.currentDate.setDate(this.currentDate.getDate() - 7);
        } else if (this.viewMode === 'day') {
            this.currentDate.setDate(this.currentDate.getDate() - 1);
        }
        const container = document.querySelector('.calendar-view-container').parentElement;
        this.render(container);
    }
    
    nextPeriod() {
        if (this.viewMode === 'month') {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        } else if (this.viewMode === 'week') {
            this.currentDate.setDate(this.currentDate.getDate() + 7);
        } else if (this.viewMode === 'day') {
            this.currentDate.setDate(this.currentDate.getDate() + 1);
        }
        const container = document.querySelector('.calendar-view-container').parentElement;
        this.render(container);
    }
    
    goToToday() {
        this.currentDate = new Date();
        const container = document.querySelector('.calendar-view-container').parentElement;
        this.render(container);
    }
    
    miniPrevMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        const container = document.querySelector('.calendar-view-container').parentElement;
        this.render(container);
    }
    
    miniNextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        const container = document.querySelector('.calendar-view-container').parentElement;
        this.render(container);
    }
    
    selectDate(date) {
        this.selectedDate = date;
        this.currentDate = new Date(date);
        this.setViewMode('day');
    }
    
    exportICalendar() {
        let ical = 'BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ProjectFlow//Calendar//EN\n';
        
        this.events.forEach(event => {
            ical += `BEGIN:VEVENT\n`;
            ical += `UID:${event.id}\n`;
            ical += `SUMMARY:${event.title}\n`;
            ical += `DTSTART:${this.formatICalDate(event.start)}\n`;
            ical += `DTEND:${this.formatICalDate(event.end)}\n`;
            ical += `END:VEVENT\n`;
        });
        
        ical += 'END:VCALENDAR';
        
        const blob = new Blob([ical], { type: 'text/calendar' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'calendar.ics';
        a.click();
        
        this.showToast('Calendar exported as iCal');
    }
    
    formatICalDate(date) {
        return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    }
    
    createEvent() {
        this.showToast('Create event dialog');
    }
    
    viewEvent(eventId) {
        this.showToast('View event ' + eventId);
    }
    
    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        toast.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #36b37e; color: white; padding: 12px 20px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); z-index: 10000;';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }
}

// Initialize
const calendarViewSystem = new CalendarViewSystem();
