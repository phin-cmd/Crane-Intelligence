// Browser-compatible notification system
(function() {
    'use strict';
    
    const NotificationSystem = {
        showSuccess: function(title, message) {
            this.showNotification('success', title, message);
        },
        
        showError: function(title, message) {
            this.showNotification('error', title, message);
        },
        
        showWarning: function(title, message) {
            this.showNotification('warning', title, message);
        },
        
        showNotification: function(type, title, message) {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.innerHTML = `
                <strong>${title}</strong><br>
                ${message}
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => notification.classList.add('show'), 100);
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }, 5000);
        }
    };
    
    // Make it globally available
    window.NotificationSystem = NotificationSystem;
    
    console.log('Notification system initialized successfully');
})();
