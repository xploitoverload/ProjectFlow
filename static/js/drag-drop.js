/**
 * Drag and Drop Manager - Kanban board drag-and-drop functionality
 */

class DragDropManager {
    constructor(options = {}) {
        this.onDrop = options.onDrop || null;
        this.draggedElement = null;
        this.sourceColumn = null;
        this.init();
    }
    
    init() {
        this.setupDraggables();
        this.setupDropZones();
    }
    
    setupDraggables() {
        const cards = document.querySelectorAll('.kanban-card, .issue-card');
        
        cards.forEach(card => {
            card.setAttribute('draggable', 'true');
            
            card.addEventListener('dragstart', (e) => {
                this.draggedElement = e.target;
                this.sourceColumn = e.target.closest('.kanban-column');
                e.target.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', e.target.innerHTML);
            });
            
            card.addEventListener('dragend', (e) => {
                e.target.classList.remove('dragging');
                this.draggedElement = null;
                this.sourceColumn = null;
            });
        });
    }
    
    setupDropZones() {
        const columns = document.querySelectorAll('.kanban-column, .kanban-column-content');
        
        columns.forEach(column => {
            column.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                
                const afterElement = this.getDragAfterElement(column, e.clientY);
                const dragging = document.querySelector('.dragging');
                
                if (afterElement == null) {
                    const cardContainer = column.querySelector('.kanban-cards, .kanban-column-content');
                    if (cardContainer && dragging) {
                        cardContainer.appendChild(dragging);
                    }
                } else {
                    if (dragging) {
                        column.insertBefore(dragging, afterElement);
                    }
                }
            });
            
            column.addEventListener('drop', (e) => {
                e.preventDefault();
                
                if (this.draggedElement && this.onDrop) {
                    const targetColumn = e.currentTarget.closest('.kanban-column') || e.currentTarget;
                    const targetStatus = targetColumn.dataset.status;
                    const cardId = this.draggedElement.dataset.issueId || this.draggedElement.dataset.cardId;
                    
                    if (cardId && targetStatus) {
                        this.onDrop({
                            cardId: cardId,
                            sourceStatus: this.sourceColumn?.dataset.status,
                            targetStatus: targetStatus,
                            element: this.draggedElement
                        });
                    }
                }
            });
        });
    }
    
    getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.kanban-card:not(.dragging), .issue-card:not(.dragging)')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
    
    refresh() {
        this.setupDraggables();
    }
}

window.DragDropManager = DragDropManager;
