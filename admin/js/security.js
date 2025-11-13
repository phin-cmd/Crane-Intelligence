/**
 * Security & Access Control JavaScript
 * Handles security events, role management, and access control
 */

class SecurityManager {
    constructor() {
        this.currentTab = 'events';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSecurityData();
    }

    bindEvents() {
        // Tab navigation
        document.querySelectorAll('.security-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Event filters
        document.getElementById('eventSeverityFilter').addEventListener('change', () => this.loadSecurityEvents());
        document.getElementById('refreshEvents').addEventListener('click', () => this.loadSecurityEvents());
        
        // Role management
        document.getElementById('createRoleBtn').addEventListener('click', () => this.showRoleModal());
        
        // Session management
        document.getElementById('terminateAllSessions').addEventListener('click', () => this.terminateAllSessions());
        
        // Audit logs
        document.getElementById('auditActionFilter').addEventListener('change', () => this.loadAuditLogs());
        document.getElementById('exportAuditLogs').addEventListener('click', () => this.exportAuditLogs());
    }

    switchTab(tabName) {
        // Hide all panels
        document.querySelectorAll('.security-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.security-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected panel
        document.getElementById(`${tabName}-panel`).classList.add('active');
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        this.currentTab = tabName;
        
        // Load data for the selected tab
        switch(tabName) {
            case 'events':
                this.loadSecurityEvents();
                break;
            case 'sessions':
                this.loadActiveSessions();
                break;
            case 'audit':
                this.loadAuditLogs();
                break;
        }
    }

    async loadSecurityData() {
        try {
            this.showLoadingState();
            const api = new AdminAPI();
            const data = await api.getSecurityData();
            this.updateSecurityOverview(data);
            this.hideLoadingState();
        } catch (error) {
            console.error('Error loading security data:', error);
            this.hideLoadingState();
            this.showError('Failed to load security data');
        }
    }

    showLoadingState() {
        // Show loading indicators
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(el => el.style.display = 'block');
        
        // Hide error messages
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(el => el.style.display = 'none');
    }

    hideLoadingState() {
        // Hide loading indicators
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(el => el.style.display = 'none');
    }

    updateSecurityOverview(data) {
        document.getElementById('securityScore').textContent = data.security_score || 85;
        document.getElementById('activeThreats').textContent = data.active_threats || 0;
        document.getElementById('blockedIPs').textContent = data.blocked_ips || 0;
        document.getElementById('activeSessions').textContent = data.active_sessions || 0;
    }

    async loadSecurityEvents() {
        try {
            const severity = document.getElementById('eventSeverityFilter').value;
            const api = new AdminAPI();
            const events = await api.getSecurityEvents({ severity });
            this.renderSecurityEvents(events);
        } catch (error) {
            console.error('Error loading security events:', error);
            this.showError('Failed to load security events');
        }
    }

    renderSecurityEvents(events) {
        const tbody = document.getElementById('eventsTableBody');
        tbody.innerHTML = '';

        if (events.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center">No security events found</td></tr>';
            return;
        }

        events.forEach(event => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.formatDate(event.timestamp)}</td>
                <td><span class="event-type">${event.event_type}</span></td>
                <td><span class="severity-badge ${event.severity}">${event.severity}</span></td>
                <td>${event.description}</td>
                <td>${event.ip_address || 'N/A'}</td>
                <td>${event.user_name || 'N/A'}</td>
                <td><span class="status-badge ${event.is_resolved ? 'resolved' : 'pending'}">${event.is_resolved ? 'Resolved' : 'Pending'}</span></td>
                <td>
                    <div class="action-buttons">
                        ${!event.is_resolved ? `<button class="btn btn-sm btn-primary" onclick="securityManager.resolveEvent(${event.id})">Resolve</button>` : ''}
                        <button class="btn btn-sm btn-secondary" onclick="securityManager.viewEventDetails(${event.id})">Details</button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadActiveSessions() {
        try {
            const sessions = await AdminAPI.getActiveSessions();
            this.renderActiveSessions(sessions);
        } catch (error) {
            console.error('Error loading active sessions:', error);
            this.showError('Failed to load active sessions');
        }
    }

    renderActiveSessions(sessions) {
        const tbody = document.getElementById('sessionsTableBody');
        tbody.innerHTML = '';

        if (sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No active sessions</td></tr>';
            return;
        }

        sessions.forEach(session => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div class="user-info">
                        <strong>${session.user_name}</strong>
                        <div class="user-email">${session.user_email}</div>
                    </div>
                </td>
                <td>${session.ip_address}</td>
                <td>${session.location || 'Unknown'}</td>
                <td>${session.device || 'Unknown'}</td>
                <td>${this.formatDate(session.last_activity)}</td>
                <td><span class="status-badge active">Active</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-danger" onclick="securityManager.terminateSession('${session.session_id}')">Terminate</button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadAuditLogs() {
        try {
            const action = document.getElementById('auditActionFilter').value;
            const logs = await AdminAPI.getAuditLogs({ action });
            this.renderAuditLogs(logs);
        } catch (error) {
            console.error('Error loading audit logs:', error);
            this.showError('Failed to load audit logs');
        }
    }

    renderAuditLogs(logs) {
        const tbody = document.getElementById('auditTableBody');
        tbody.innerHTML = '';

        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No audit logs found</td></tr>';
            return;
        }

        logs.forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.formatDate(log.timestamp)}</td>
                <td>${log.user_name || 'System'}</td>
                <td><span class="action-badge ${log.action}">${log.action}</span></td>
                <td>${log.resource_type}</td>
                <td>${log.ip_address || 'N/A'}</td>
                <td>${log.description || 'N/A'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    async resolveEvent(eventId) {
        try {
            await AdminAPI.resolveSecurityEvent(eventId);
            this.showSuccess('Security event resolved');
            this.loadSecurityEvents();
        } catch (error) {
            console.error('Error resolving event:', error);
            this.showError('Failed to resolve security event');
        }
    }

    async viewEventDetails(eventId) {
        try {
            const event = await AdminAPI.getSecurityEvent(eventId);
            this.showEventDetailsModal(event);
        } catch (error) {
            console.error('Error loading event details:', error);
            this.showError('Failed to load event details');
        }
    }

    showEventDetailsModal(event) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Security Event Details</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="event-details">
                        <div class="detail-row">
                            <label>Event Type:</label>
                            <span>${event.event_type}</span>
                        </div>
                        <div class="detail-row">
                            <label>Severity:</label>
                            <span class="severity-badge ${event.severity}">${event.severity}</span>
                        </div>
                        <div class="detail-row">
                            <label>Description:</label>
                            <span>${event.description}</span>
                        </div>
                        <div class="detail-row">
                            <label>IP Address:</label>
                            <span>${event.ip_address || 'N/A'}</span>
                        </div>
                        <div class="detail-row">
                            <label>User Agent:</label>
                            <span>${event.user_agent || 'N/A'}</span>
                        </div>
                        <div class="detail-row">
                            <label>Timestamp:</label>
                            <span>${this.formatDate(event.timestamp)}</span>
                        </div>
                        <div class="detail-row">
                            <label>Status:</label>
                            <span class="status-badge ${event.is_resolved ? 'resolved' : 'pending'}">${event.is_resolved ? 'Resolved' : 'Pending'}</span>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
                    ${!event.is_resolved ? `<button type="button" class="btn btn-primary" onclick="securityManager.resolveEvent(${event.id}); this.closest('.modal').remove();">Resolve Event</button>` : ''}
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    showRoleModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Create New Role</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="roleForm">
                        <div class="form-group">
                            <label for="roleName">Role Name</label>
                            <input type="text" id="roleName" name="role_name" required>
                        </div>
                        <div class="form-group">
                            <label for="roleDescription">Description</label>
                            <textarea id="roleDescription" name="role_description" rows="3"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Permissions</label>
                            <div class="permissions-grid">
                                <label class="permission-item">
                                    <input type="checkbox" name="permissions" value="user_management">
                                    <span>User Management</span>
                                </label>
                                <label class="permission-item">
                                    <input type="checkbox" name="permissions" value="content_management">
                                    <span>Content Management</span>
                                </label>
                                <label class="permission-item">
                                    <input type="checkbox" name="permissions" value="analytics">
                                    <span>Analytics</span>
                                </label>
                                <label class="permission-item">
                                    <input type="checkbox" name="permissions" value="settings">
                                    <span>Settings</span>
                                </label>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="securityManager.createRole()">Create Role</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    async createRole() {
        try {
            const form = document.getElementById('roleForm');
            const formData = new FormData(form);
            const data = {
                role_name: formData.get('role_name'),
                role_description: formData.get('role_description'),
                permissions: formData.getAll('permissions')
            };
            
            await AdminAPI.createRole(data);
            this.showSuccess('Role created successfully');
            document.querySelector('.modal').remove();
            this.loadRoles();
        } catch (error) {
            console.error('Error creating role:', error);
            this.showError('Failed to create role');
        }
    }

    async terminateSession(sessionId) {
        if (!confirm('Are you sure you want to terminate this session?')) {
            return;
        }
        
        try {
            await AdminAPI.terminateSession(sessionId);
            this.showSuccess('Session terminated');
            this.loadActiveSessions();
        } catch (error) {
            console.error('Error terminating session:', error);
            this.showError('Failed to terminate session');
        }
    }

    async terminateAllSessions() {
        if (!confirm('Are you sure you want to terminate all active sessions? This will log out all users.')) {
            return;
        }
        
        try {
            await AdminAPI.terminateAllSessions();
            this.showSuccess('All sessions terminated');
            this.loadActiveSessions();
        } catch (error) {
            console.error('Error terminating sessions:', error);
            this.showError('Failed to terminate sessions');
        }
    }

    async exportAuditLogs() {
        try {
            const action = document.getElementById('auditActionFilter').value;
            const response = await AdminAPI.exportAuditLogs({ action });
            
            if (response.download_url) {
                window.open(response.download_url, '_blank');
            }
            this.showSuccess('Audit logs exported successfully');
        } catch (error) {
            console.error('Error exporting audit logs:', error);
            this.showError('Failed to export audit logs');
        }
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleString();
    }

    showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }
}

// Initialize security manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.securityManager = new SecurityManager();
});
