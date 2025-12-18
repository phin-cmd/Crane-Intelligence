/**
 * Turnaround Timer Component
 * Displays real-time countdown timer for FMV report turnaround deadlines
 */

class TurnaroundTimer {
    constructor(containerId, reportData) {
        this.containerId = containerId;
        this.reportData = reportData;
        this.container = document.getElementById(containerId);
        this.intervalId = null;
        this.deadline = null;
        
        if (reportData.turnaround_deadline) {
            this.deadline = new Date(reportData.turnaround_deadline);
        }
    }
    
    init() {
        if (!this.container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }
        
        if (!this.deadline) {
            this.container.innerHTML = '<span class="timer-unavailable">Deadline not set</span>';
            return;
        }
        
        this.update();
        this.intervalId = setInterval(() => this.update(), 1000);
    }
    
    update() {
        if (!this.deadline) return;
        
        const now = new Date();
        const timeRemaining = this.deadline - now;
        
        if (timeRemaining <= 0) {
            this.renderOverdue();
            if (this.intervalId) {
                clearInterval(this.intervalId);
                this.intervalId = null;
            }
            return;
        }
        
        const hours = Math.floor(timeRemaining / (1000 * 60 * 60));
        const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
        
        this.renderTimer(hours, minutes, seconds, timeRemaining);
    }
    
    renderTimer(hours, minutes, seconds, totalMs) {
        const totalHours = Math.floor(totalMs / (1000 * 60 * 60));
        const isUrgent = totalHours < 6;
        const isWarning = totalHours < 12;
        
        let className = 'turnaround-timer';
        if (isUrgent) {
            className += ' timer-urgent';
        } else if (isWarning) {
            className += ' timer-warning';
        }
        
        const hoursStr = String(hours).padStart(2, '0');
        const minutesStr = String(minutes).padStart(2, '0');
        const secondsStr = String(seconds).padStart(2, '0');
        
        this.container.innerHTML = `
            <div class="${className}">
                <div class="timer-label">Time Remaining</div>
                <div class="timer-display">
                    <span class="timer-value">${hoursStr}:${minutesStr}:${secondsStr}</span>
                </div>
                <div class="timer-status">${this.getStatusText(totalHours)}</div>
            </div>
        `;
    }
    
    renderOverdue() {
        this.container.innerHTML = `
            <div class="turnaround-timer timer-overdue">
                <div class="timer-label">Status</div>
                <div class="timer-display">
                    <span class="timer-value overdue">OVERDUE</span>
                </div>
                <div class="timer-status">Report is past deadline</div>
            </div>
        `;
    }
    
    getStatusText(totalHours) {
        if (totalHours < 1) {
            return 'Less than 1 hour remaining';
        } else if (totalHours < 6) {
            return 'Urgent - Less than 6 hours remaining';
        } else if (totalHours < 12) {
            return 'Warning - Less than 12 hours remaining';
        } else if (totalHours < 24) {
            return 'Due within 24 hours';
        } else {
            return 'On track';
        }
    }
    
    destroy() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
}

// Auto-initialize timers on page load
document.addEventListener('DOMContentLoaded', function() {
    // Find all timer containers
    const timerContainers = document.querySelectorAll('[data-turnaround-timer]');
    
    timerContainers.forEach(container => {
        const reportId = container.getAttribute('data-report-id');
        const deadline = container.getAttribute('data-deadline');
        
        if (deadline) {
            const timer = new TurnaroundTimer(container.id, {
                turnaround_deadline: deadline
            });
            timer.init();
        }
    });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TurnaroundTimer;
}

