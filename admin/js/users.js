/**
 * Crane Intelligence User Management JavaScript
 * Handles user management interface functionality
 */

// Generate avatar URL using initials (SVG data URI)
function generateAvatarUrl(name, size = 80) {
    const initial = (name || 'U').charAt(0).toUpperCase();
    const colors = ['007BFF', '00FF85', 'FFD600', 'FF6B6B', '9C27B0', '00BCD4'];
    const colorIndex = initial.charCodeAt(0) % colors.length;
    const color = colors[colorIndex];
    // Use data URI instead of external placeholder service
    return `data:image/svg+xml,${encodeURIComponent(`<svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg"><rect width="${size}" height="${size}" fill="#${color}"/><text x="50%" y="50%" font-family="Arial, sans-serif" font-size="${size * 0.4}" font-weight="bold" fill="#FFFFFF" text-anchor="middle" dominant-baseline="central">${initial}</text></svg>`)}`;
}

class UserManagement {
    constructor() {
        // Use window.adminAPI (created by admin-api.js) or create new instance
        if (typeof window.adminAPI !== 'undefined') {
            this.api = window.adminAPI;
        } else if (typeof AdminAPI !== 'undefined') {
            this.api = new AdminAPI();
        } else {
            console.error('AdminAPI is not available. Make sure admin-api.js is loaded before users.js');
            // Create a fallback API object with error handling
            this.api = {
                request: async () => { throw new Error('AdminAPI not loaded'); },
                getUsers: async () => { throw new Error('AdminAPI not loaded'); }
            };
        }
        this.currentPage = 1;
        this.pageSize = 25;
        this.totalUsers = 0;
        this.users = [];
        this.selectedUsers = new Set();
        this.currentSort = { field: 'created_at', direction: 'desc' };
        this.currentFilters = {};
        this.currentView = 'table';
        this.isLoading = false;
        this.isLoadingUser = null; // Track which user is currently being loaded to prevent duplicate requests
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadUsers();
        this.setupTableSorting();
    }

    setupEventListeners() {
        // Search and filters
        const searchInput = document.getElementById('user-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.debounce(() => this.handleSearch(e.target.value), 300);
            });
        }

        const roleFilter = document.getElementById('role-filter');
        if (roleFilter) {
            roleFilter.addEventListener('change', (e) => {
                this.handleFilterChange('role', e.target.value);
            });
        }

        const statusFilter = document.getElementById('status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.handleFilterChange('status', e.target.value);
            });
        }

        const dateFilter = document.getElementById('date-filter');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                this.handleFilterChange('date_range', e.target.value);
            });
        }

        const filterBtn = document.getElementById('filter-btn');
        if (filterBtn) {
            filterBtn.addEventListener('click', () => {
                this.applyFilters();
            });
        }

        // Bulk action buttons
        const deleteBtn = document.getElementById('delete-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                this.handleBulkAction('delete');
            });
        }

        const suspendBtn = document.getElementById('suspend-btn');
        if (suspendBtn) {
            suspendBtn.addEventListener('click', () => {
                this.handleBulkAction('suspend');
            });
        }

        // Action icons - use setTimeout to ensure DOM is ready
        setTimeout(() => {
            document.querySelectorAll('.action-icon').forEach(icon => {
                icon.addEventListener('click', (e) => {
                    const title = e.currentTarget.getAttribute('title');
                    this.handleActionIcon(title);
                });
            });
        }, 100);

        // Export functionality
        const exportCheckbox = document.getElementById('export-checkbox');
        if (exportCheckbox) {
            exportCheckbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.exportUsers();
                }
            });
        }

        // Bulk action checkbox
        const bulkActionCheckbox = document.getElementById('bulk-action-checkbox');
        if (bulkActionCheckbox) {
            bulkActionCheckbox.addEventListener('change', (e) => {
                this.toggleBulkActions(e.target.checked);
            });
        }

        // Bulk actions
        document.getElementById('select-all')?.addEventListener('change', (e) => {
            this.handleSelectAll(e.target.checked);
        });

        document.getElementById('bulk-activate-btn')?.addEventListener('click', () => {
            this.handleBulkAction('activate');
        });

        document.getElementById('bulk-deactivate-btn')?.addEventListener('click', () => {
            this.handleBulkAction('deactivate');
        });

        document.getElementById('bulk-change-role-btn')?.addEventListener('click', () => {
            this.handleBulkAction('change_role');
        });

        document.getElementById('bulk-delete-btn')?.addEventListener('click', () => {
            this.handleBulkAction('delete');
        });

        // Table actions
        document.getElementById('refresh-table-btn')?.addEventListener('click', () => {
            this.loadUsers();
        });

        document.getElementById('export-users-btn')?.addEventListener('click', () => {
            this.exportUsers();
        });

        document.getElementById('add-user-btn')?.addEventListener('click', () => {
            this.showAddUserModal();
        });

        // View toggle
        document.getElementById('table-view-btn')?.addEventListener('click', () => {
            this.switchView('table');
        });

        document.getElementById('grid-view-btn')?.addEventListener('click', () => {
            this.switchView('grid');
        });

        // Pagination
        document.getElementById('first-page-btn')?.addEventListener('click', () => {
            this.goToPage(1);
        });

        document.getElementById('prev-page-btn')?.addEventListener('click', () => {
            this.goToPage(this.currentPage - 1);
        });

        document.getElementById('next-page-btn')?.addEventListener('click', () => {
            this.goToPage(this.currentPage + 1);
        });

        document.getElementById('last-page-btn')?.addEventListener('click', () => {
            this.goToPage(this.getTotalPages());
        });

        // Modals
        this.setupModalEventListeners();
    }

    setupModalEventListeners() {
        // User modal
        const userModal = document.getElementById('user-modal');
        const modalClose = document.getElementById('modal-close');
        const modalCancel = document.getElementById('modal-cancel');
        const modalSave = document.getElementById('modal-save');

        modalClose?.addEventListener('click', () => {
            this.hideUserModal();
        });

        modalCancel?.addEventListener('click', () => {
            this.hideUserModal();
        });

        modalSave?.addEventListener('click', () => {
            this.saveUser();
        });

        // User details modal
        const userDetailsModal = document.getElementById('user-details-modal');
        const userDetailsClose = document.getElementById('user-details-close');
        const userDetailsCloseBtn = document.getElementById('user-details-close-btn');
        const editUserBtn = document.getElementById('edit-user-btn');

        userDetailsClose?.addEventListener('click', () => {
            this.hideUserDetailsModal();
        });

        userDetailsCloseBtn?.addEventListener('click', () => {
            this.hideUserDetailsModal();
        });

        editUserBtn?.addEventListener('click', () => {
            this.editUser();
        });

        // Close modals when clicking outside
        userModal?.addEventListener('click', (e) => {
            if (e.target === userModal) {
                this.hideUserModal();
            }
        });

        userDetailsModal?.addEventListener('click', (e) => {
            if (e.target === userDetailsModal) {
                this.hideUserDetailsModal();
            }
        });
    }

    setupTableSorting() {
        const sortableHeaders = document.querySelectorAll('.sortable');
        sortableHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const field = header.dataset.sort;
                this.handleSort(field);
            });
        });
    }

    async loadUsers() {
        console.log('Loading users...');
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoadingState();

        try {
            const params = {
                skip: (this.currentPage - 1) * this.pageSize,
                limit: this.pageSize,
                ...this.currentFilters
            };

            console.log('API params:', params);
            const response = await this.api.getUsers(params);
            console.log('API response:', response);
            
            this.users = response.items || response.users || response;
            this.totalUsers = response.total || (response.items ? response.items.length : 0);

            console.log('Users loaded:', this.users.length);
            this.renderUsers();
            this.updatePagination();
            this.updateTableCount();

        } catch (error) {
            console.error('Error loading users:', error);
            // Show error message
            this.showError('Failed to load users. Please refresh the page.');
            this.users = [];
            this.totalUsers = 0;
            this.renderUsers();
            this.updatePagination();
            this.updateTableCount();
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }

    renderUsers() {
        console.log('Rendering users:', this.users.length);
        if (this.currentView === 'table') {
            this.renderTableView();
        } else {
            this.renderGridView();
        }
    }

    renderTableView() {
        const tbody = document.getElementById('users-table-body');
        if (!tbody) {
            console.error('Table body element not found!');
            return;
        }

        console.log('Rendering table view with', this.users.length, 'users');

        if (this.users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center">
                        <div class="empty-state">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                                <circle cx="9" cy="7" r="4"></circle>
                                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                            </svg>
                            <h3>No users found</h3>
                            <p>Try adjusting your search or filter criteria</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        try {
            tbody.innerHTML = this.users.map(user => {
                // Safely get values with fallbacks
                const userId = user.id || 'unknown';
                const userName = user.name || user.full_name || 'N/A';
                const userEmail = user.email || 'N/A';
                const userRole = user.user_role || user.role || 'N/A';
                const lastLogin = user.lastLogin || user.last_login;
                const lastLoginText = lastLogin ? this.formatDate(lastLogin) : 'Never';
                const statusClass = this.getUserStatusClass(user);
                const statusText = this.getUserStatusText(user);
                
                // Generate avatar URL safely
                const avatarUrl = user.avatar || (typeof generateAvatarUrl === 'function' 
                    ? generateAvatarUrl(userName, 32) 
                    : `data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32'><rect width='32' height='32' fill='%2300FF85'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='%23000' font-size='14' font-weight='bold'>${userName.charAt(0).toUpperCase()}</text></svg>`);
                
                return `
                    <tr class="user-row" data-user-id="${userId}">
                        <td>
                            <input type="checkbox" class="user-checkbox" data-user-id="${userId}">
                        </td>
                        <td>
                            <img src="${avatarUrl}" 
                                 alt="${userName}" class="user-avatar-small">
                        </td>
                        <td>
                            <div class="user-name">${userName}</div>
                        </td>
                        <td>
                            <div class="user-email">${userEmail}</div>
                        </td>
                        <td>
                            <span class="user-role">${userRole}</span>
                        </td>
                        <td>
                            <span class="status-badge ${statusClass}">
                                ${statusText}
                            </span>
                        </td>
                        <td>
                            <div class="last-login">${lastLoginText}</div>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-secondary" onclick="userManagement.viewUser('${userId}')" title="Edit">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                </svg>
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
            
            console.log('Table rendered successfully with', this.users.length, 'rows');
        } catch (error) {
            console.error('Error rendering table:', error);
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center">
                        <div class="error-state">
                            <p>Error rendering users: ${error.message}</p>
                        </div>
                    </td>
                </tr>
            `;
        }

        // Add event listeners for checkboxes
        tbody.querySelectorAll('.user-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const userId = parseInt(e.target.dataset.userId);
                if (e.target.checked) {
                    this.selectedUsers.add(userId);
                } else {
                    this.selectedUsers.delete(userId);
                }
                this.updateBulkActions();
            });
        });

        // Add row click handlers - show full user details modal on row click
        tbody.querySelectorAll('.user-row').forEach(row => {
            row.addEventListener('click', (e) => {
                if (e.target.type === 'checkbox' || e.target.closest('button')) return;
                
                const userId = parseInt(row.dataset.userId);
                // Prevent duplicate calls if already loading this user
                if (this.isLoadingUser === userId) return;
                
                // Show full user details modal on row click
                this.viewUser(userId);
            });
        });
    }

    selectUser(user) {
        // Update the right panel with selected user details
        document.getElementById('selected-user-name').textContent = user.name || user.full_name || 'N/A';
        document.getElementById('selected-user-email').textContent = user.email;
        const avatarEl = document.getElementById('selected-user-avatar');
        if (avatarEl) {
            avatarEl.src = user.avatar || generateAvatarUrl(user.name || user.full_name || 'U', 80);
        }
        
        // Update role selection
        const roleRadios = document.querySelectorAll('input[name="user-role"]');
        roleRadios.forEach(radio => {
            radio.checked = radio.value === (user.role || user.user_role || 'user').toLowerCase();
        });
        
        // Highlight selected row
        document.querySelectorAll('.user-row').forEach(row => {
            row.classList.remove('selected');
        });
        const selectedRow = document.querySelector(`[data-user-id="${user.id}"]`);
        if (selectedRow) {
            selectedRow.classList.add('selected');
        }
    }

    renderGridView() {
        const grid = document.getElementById('users-grid');
        if (!grid) return;

        if (this.users.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="9" cy="7" r="4"></circle>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                    <h3>No users found</h3>
                    <p>Try adjusting your search or filter criteria</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.users.map(user => `
            <div class="user-card" data-user-id="${user.id}">
                <div class="user-card-header">
                    <div class="user-avatar">
                        <img src="${generateAvatarUrl(user.full_name, 48)}" alt="${user.full_name}">
                    </div>
                    <div class="user-info">
                        <div class="user-name">${user.full_name}</div>
                        <div class="user-username">@${user.username}</div>
                    </div>
                    <div class="user-actions">
                        <input type="checkbox" class="user-checkbox" value="${user.id}">
                    </div>
                </div>
                <div class="user-card-body">
                    <div class="user-detail">
                        <label>Email:</label>
                        <span>${user.email}</span>
                    </div>
                    <div class="user-detail">
                        <label>Company:</label>
                        <span>${user.company_name}</span>
                    </div>
                    <div class="user-detail">
                        <label>Role:</label>
                        <span class="role-badge role-${user.user_role}">${this.formatRole(user.user_role)}</span>
                    </div>
                    <!-- Subscription tier removed - using user role instead -->
                    <div class="user-detail">
                        <label>Status:</label>
                        <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                            ${user.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                    <div class="user-detail">
                        <label>Created:</label>
                        <span>${this.formatDate(user.created_at)}</span>
                    </div>
                </div>
                <div class="user-card-footer">
                    <button class="btn btn-secondary btn-sm" onclick="userManagement.viewUser(${user.id})">View</button>
                    <button class="btn btn-primary btn-sm" onclick="userManagement.editUser(${user.id})">Edit</button>
                </div>
            </div>
        `).join('');

        // Add event listeners to checkboxes
        document.querySelectorAll('.user-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.handleUserSelection(e.target.value, e.target.checked);
            });
        });
    }

    handleSearch(query) {
        this.currentFilters.search = query;
        this.currentPage = 1;
        this.loadUsers();
    }

    handleFilterChange(field, value) {
        if (value) {
            this.currentFilters[field] = value;
        } else {
            delete this.currentFilters[field];
        }
    }

    applyFilters() {
        this.currentPage = 1;
        this.loadUsers();
    }

    clearFilters() {
        // Clear all filter inputs
        document.getElementById('user-search').value = '';
        document.getElementById('role-filter').value = '';
        document.getElementById('subscription-filter').value = '';
        document.getElementById('status-filter').value = '';
        document.getElementById('date-filter').value = '';

        // Clear current filters
        this.currentFilters = {};
        this.currentPage = 1;
        this.loadUsers();
    }

    handleSort(field) {
        if (this.currentSort.field === field) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.field = field;
            this.currentSort.direction = 'asc';
        }

        this.currentPage = 1;
        this.loadUsers();
        this.updateSortIndicators();
    }

    updateSortIndicators() {
        document.querySelectorAll('.sortable').forEach(header => {
            const icon = header.querySelector('.sort-icon');
            if (header.dataset.sort === this.currentSort.field) {
                icon.style.transform = this.currentSort.direction === 'asc' ? 'rotate(180deg)' : 'rotate(0deg)';
                icon.style.opacity = '1';
            } else {
                icon.style.opacity = '0.5';
            }
        });
    }

    switchView(view) {
        this.currentView = view;
        
        // Update view buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        const viewBtn = document.getElementById(`${view}-view-btn`);
        if (viewBtn) {
            viewBtn.classList.add('active');
        }

        // Show/hide views
        document.getElementById('table-view').style.display = view === 'table' ? 'block' : 'none';
        document.getElementById('grid-view').style.display = view === 'grid' ? 'block' : 'none';

        this.renderUsers();
    }

    handleSelectAll(checked) {
        this.selectedUsers.clear();
        
        if (checked) {
            this.users.forEach(user => {
                this.selectedUsers.add(user.id);
            });
        }

        // Update checkboxes
        document.querySelectorAll('.user-checkbox').forEach(checkbox => {
            checkbox.checked = checked;
        });

        this.updateBulkActions();
    }

    handleUserSelection(userId, selected) {
        if (selected) {
            this.selectedUsers.add(userId);
        } else {
            this.selectedUsers.delete(userId);
        }

        // Update select all checkbox
        const selectAllCheckbox = document.getElementById('select-all');
        const totalCheckboxes = document.querySelectorAll('.user-checkbox').length;
        const checkedCheckboxes = document.querySelectorAll('.user-checkbox:checked').length;
        
        selectAllCheckbox.checked = checkedCheckboxes === totalCheckboxes;
        selectAllCheckbox.indeterminate = checkedCheckboxes > 0 && checkedCheckboxes < totalCheckboxes;

        this.updateBulkActions();
    }

    updateBulkActions() {
        const bulkActions = document.getElementById('bulk-actions');
        const selectedCount = document.getElementById('selected-count');
        
        if (this.selectedUsers.size > 0) {
            bulkActions.style.display = 'flex';
            selectedCount.textContent = this.selectedUsers.size;
        } else {
            bulkActions.style.display = 'none';
        }
    }

    async handleBulkAction(action) {
        if (this.selectedUsers.size === 0) return;

        const userIds = Array.from(this.selectedUsers);
        
        switch (action) {
            case 'activate':
                await this.bulkActivateUsers(userIds);
                break;
            case 'deactivate':
                await this.bulkDeactivateUsers(userIds);
                break;
            case 'change_role':
                await this.bulkChangeUserRole(userIds);
                break;
            case 'delete':
                await this.bulkDeleteUsers(userIds);
                break;
        }
    }

    async bulkActivateUsers(userIds) {
        try {
            await this.api.bulkUserOperation({
                user_ids: userIds,
                operation: 'activate'
            });
            this.showSuccess(`${userIds.length} users activated successfully`);
            this.selectedUsers.clear();
            this.loadUsers();
        } catch (error) {
            this.showError('Failed to activate users');
        }
    }

    async bulkDeactivateUsers(userIds) {
        try {
            await this.api.bulkUserOperation({
                user_ids: userIds,
                operation: 'deactivate'
            });
            this.showSuccess(`${userIds.length} users deactivated successfully`);
            this.selectedUsers.clear();
            this.loadUsers();
        } catch (error) {
            this.showError('Failed to deactivate users');
        }
    }

    async bulkChangeUserRole(userIds) {
        // Show role selection modal
        const newRole = prompt('Enter new role (crane_rental_company, equipment_dealer, financial_institution, admin):');
        if (!newRole) return;

        try {
            await this.api.bulkUserOperation({
                user_ids: userIds,
                operation: 'change_role',
                parameters: { role: newRole }
            });
            this.showSuccess(`${userIds.length} users role changed successfully`);
            this.selectedUsers.clear();
            this.loadUsers();
        } catch (error) {
            this.showError('Failed to change user roles');
        }
    }

    async bulkDeleteUsers(userIds) {
        if (!confirm(`Are you sure you want to delete ${userIds.length} users? This action cannot be undone.`)) {
            return;
        }

        try {
            await this.api.bulkUserOperation({
                user_ids: userIds,
                operation: 'delete'
            });
            this.showSuccess(`${userIds.length} users deleted successfully`);
            this.selectedUsers.clear();
            this.loadUsers();
        } catch (error) {
            this.showError('Failed to delete users');
        }
    }

    showAddUserModal() {
        const modal = document.getElementById('user-modal');
        const title = document.getElementById('modal-title');
        const form = document.getElementById('user-form');
        
        title.textContent = 'Add User';
        form.reset();
        modal.classList.add('show');
    }

    hideUserModal() {
        const modal = document.getElementById('user-modal');
        modal.classList.remove('show');
    }

    async saveUser() {
        const form = document.getElementById('user-form');
        const formData = new FormData(form);
        
        const userData = {
            full_name: formData.get('full_name'),
            email: formData.get('email'),
            username: formData.get('username'),
            company_name: formData.get('company_name'),
            user_role: formData.get('user_role'),
            password: formData.get('password'),
            is_active: formData.get('is_active') === 'on'
        };

        // Validate password confirmation
        if (userData.password !== formData.get('confirm_password')) {
            this.showError('Passwords do not match');
            return;
        }

        try {
            await this.api.createUser(userData);
            this.showSuccess('User created successfully');
            this.hideUserModal();
            this.loadUsers();
        } catch (error) {
            this.showError('Failed to create user');
        }
    }

    async viewUser(userId) {
        // Prevent multiple simultaneous calls for the same user
        if (this.isLoadingUser === userId) {
            console.log('User details already loading for user:', userId);
            return;
        }
        
        try {
            this.isLoadingUser = userId;
            
            // Get user from API
            const apiUser = await this.api.getUser(userId);
            console.log('API User Response (getUser):', apiUser);
            console.log('API User Response fields:', Object.keys(apiUser));
            console.log('API User - company_name:', apiUser.company_name);
            console.log('API User - phone:', apiUser.phone);
            console.log('API User - address:', apiUser.address);
            console.log('API User - full_name:', apiUser.full_name);
            
            // Try to merge with cached user data (which might have more fields from the list endpoint)
            const cachedUser = this.users.find(u => u.id === userId);
            console.log('Cached User Data (from list):', cachedUser);
            if (cachedUser) {
                console.log('Cached User fields:', Object.keys(cachedUser));
            }
            
            // Merge data sources: API response is most authoritative
            // But we'll merge cached data for any missing fields
            const user = {
                ...cachedUser,    // Start with cached data (might have more fields)
                ...apiUser        // Override with API response (most up-to-date, includes phone/address)
            };
            
            // Ensure we have the latest data from API
            if (apiUser.company_name) user.company_name = apiUser.company_name;
            if (apiUser.phone) user.phone = apiUser.phone;
            if (apiUser.phone_number) user.phone_number = apiUser.phone_number;
            if (apiUser.address) user.address = apiUser.address;
            if (apiUser.street_address) user.street_address = apiUser.street_address;
            if (apiUser.full_address) user.full_address = apiUser.full_address;
            if (apiUser.full_name) user.full_name = apiUser.full_name;
            
            console.log('Final Merged User Data:', user);
            console.log('Final Merged User fields:', Object.keys(user));
            console.log('Final - company_name:', user.company_name);
            console.log('Final - phone:', user.phone);
            console.log('Final - address:', user.address);
            console.log('Final - full_name:', user.full_name);
            this.showUserDetails(user);
        } catch (error) {
            console.error('Failed to load user details:', error);
            this.showError('Failed to load user details');
        } finally {
            // Clear the loading flag after a short delay to allow for legitimate re-fetches
            setTimeout(() => {
                if (this.isLoadingUser === userId) {
                    this.isLoadingUser = null;
                }
            }, 1000);
        }
    }

    showUserDetails(user) {
        // Try to find existing modal or create one
        let modal = document.getElementById('user-details-modal');
        let content = document.getElementById('user-details-content');
        
        // If modal doesn't exist, create it
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'user-details-modal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 1200px; max-height: 90vh; overflow-y: auto;">
                    <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 1px solid #333;">
                        <h3 style="margin: 0; color: #fff;">User Account Details</h3>
                        <span class="close" onclick="userManagement.hideUserDetailsModal()" style="font-size: 28px; font-weight: bold; color: #fff; cursor: pointer; line-height: 1;">&times;</span>
                    </div>
                    <div id="user-details-content" class="modal-body" style="padding: 20px;"></div>
                    <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center; padding: 20px; border-top: 1px solid #333; gap: 10px;">
                        <div style="display: flex; gap: 10px;">
                            <button class="btn btn-danger" id="modal-delete-user-btn" style="background: #DC3545; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">Delete User</button>
                            <button class="btn btn-warning" id="modal-suspend-user-btn" style="background: #FFC107; color: #000; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">Suspend User</button>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button class="btn btn-primary" id="modal-edit-user-btn" style="background: #007BFF; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">Edit User</button>
                            <button class="btn btn-secondary" onclick="userManagement.hideUserDetailsModal()" style="background: #6C757D; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">Close</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            content = document.getElementById('user-details-content');
            
            // Setup action button handlers
            document.getElementById('modal-delete-user-btn')?.addEventListener('click', () => {
                const userId = modal.dataset.userId;
                if (userId) this.deleteUser(parseInt(userId));
            });
            
            document.getElementById('modal-suspend-user-btn')?.addEventListener('click', () => {
                const userId = modal.dataset.userId;
                if (userId) this.toggleUserStatus(parseInt(userId));
            });
            
            document.getElementById('modal-edit-user-btn')?.addEventListener('click', () => {
                const userId = modal.dataset.userId;
                if (userId) this.editUser(parseInt(userId));
            });
        }
        
        // Store current user ID in modal for action buttons
        modal.dataset.userId = user.id;
        
        if (!content) {
            console.error('User details content element not found');
            this.showError('Failed to display user details');
            return;
        }
        
        // Update suspend button text based on current status
        const suspendBtn = document.getElementById('modal-suspend-user-btn');
        if (suspendBtn) {
            suspendBtn.textContent = user.is_active ? 'Suspend User' : 'Activate User';
            suspendBtn.style.background = user.is_active ? '#FFC107' : '#28A745';
            suspendBtn.style.color = user.is_active ? '#000' : '#fff';
        }
        
        // Log user object to debug field names
        console.log('showUserDetails - Full user object:', user);
        console.log('showUserDetails - Available fields:', Object.keys(user));
        console.log('showUserDetails - Raw values:', {
            'user.full_name': user.full_name,
            'user.company_name': user.company_name,
            'user.phone': user.phone,
            'user.phone_number': user.phone_number,
            'user.address': user.address,
            'user.street_address': user.street_address,
            'user.full_address': user.full_address
        });
        
        // Extract full name - prioritize API response
        const fullName = user.full_name || user.name || user.fullName || 'N/A';
        const email = user.email || 'N/A';
        const username = user.username || 'N/A';
        
        // Check multiple possible field names for company (prioritize non-N/A values)
        let company = user.company_name || user.company || user.companyName || 
                     user.organization || user.organization_name;
        // Only set to 'N/A' if we truly don't have a value
        // Check if it's a valid non-empty string
        if (!company || company === 'N/A' || company === 'null' || company === null || company === '') {
            company = 'N/A';
        } else {
            // Keep the actual value, don't override it
            company = company;
        }
        
        console.log('Company extraction:', {
            'user.company_name': user.company_name,
            'user.company': user.company,
            'final company': company
        });
        
        // Check multiple possible field names for phone - prioritize API response
        const phone = user.phone || user.phone_number || user.phoneNumber || 
                     user.mobile || user.mobile_number || user.mobileNumber ||
                     user.contact_phone || user.contact_number || 'N/A';
        
        // Check multiple possible field names for address - prioritize API response
        const address = user.address || user.street_address || user.full_address || 
                       user.address_line1 || user.address_line_1 || user.street ||
                       user.fullAddress || user.streetAddress || 
                       (user.address_line1 && user.city && user.state && user.zip_code 
                        ? `${user.address_line1}, ${user.city}, ${user.state} ${user.zip_code}`
                        : null) || 'Not provided';
        
        const timezone = user.timezone || user.time_zone || user.timeZone || 'Not set';
        const role = user.user_role || user.role || 'user';
        
        console.log('Extracted values:', { fullName, email, company, phone, address, timezone, role });
        console.log('Will display:', {
            'Full Name': fullName,
            'Company': company,
            'Phone': phone,
            'Address': address
        });
        
        // Email preferences (default to true if not specified)
        const emailPrefs = user.email_preferences || user.emailPreferences || {};
        const marketingEmails = emailPrefs.marketing !== undefined ? emailPrefs.marketing : (user.marketing_emails !== undefined ? user.marketing_emails : true);
        const reportNotifications = emailPrefs.reports !== undefined ? emailPrefs.reports : (user.report_notifications !== undefined ? user.report_notifications : true);
        const securityAlerts = emailPrefs.security !== undefined ? emailPrefs.security : (user.security_alerts !== undefined ? user.security_alerts : true);
        
        // Notification preferences
        const notifPrefs = user.notification_preferences || user.notificationPreferences || {};
        const browserNotifications = notifPrefs.browser !== undefined ? notifPrefs.browser : (user.browser_notifications !== undefined ? user.browser_notifications : false);
        const marketUpdates = notifPrefs.market !== undefined ? notifPrefs.market : (user.market_updates !== undefined ? user.market_updates : false);
        const priceAlerts = notifPrefs.price !== undefined ? notifPrefs.price : (user.price_alerts !== undefined ? user.price_alerts : false);
        
        // Billing history (if available)
        const billingHistory = user.billing_history || user.billingHistory || [];
        
        content.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 24px;">
                <!-- User Profile Header -->
                <div style="display: flex; align-items: center; gap: 20px; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <div style="width: 100px; height: 100px; border-radius: 50%; overflow: hidden; flex-shrink: 0;">
                        <img src="${generateAvatarUrl(fullName, 100)}" alt="${fullName}" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <div style="flex: 1;">
                        <h2 style="margin: 0 0 8px 0; font-size: 24px; color: #fff; font-weight: 600;">${fullName}</h2>
                        <p style="margin: 4px 0; color: #B0B0B0; font-size: 16px;">${email}</p>
                        <p style="margin: 4px 0; color: #808080; font-size: 14px;">@${username}</p>
                    </div>
                    <div>
                        <span class="status-badge ${this.getUserStatusClass(user)}" style="display: inline-block; padding: 8px 16px; border-radius: 4px; font-size: 14px; font-weight: 600; background: ${this.getUserStatusClass(user) === 'active' ? '#28A745' : (this.getUserStatusClass(user) === 'pending' ? '#FFC107' : '#DC3545')}; color: #fff;">
                            ${this.getUserStatusText(user)}
                        </span>
                    </div>
                </div>
                
                <!-- Personal Information Section -->
                <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 20px;">
                    <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #fff; font-weight: 600; border-bottom: 1px solid #333; padding-bottom: 8px;">Personal Information</h3>
                    <p style="margin: 0 0 16px 0; font-size: 14px; color: #B0B0B0;">Update your personal details</p>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Full Name</label>
                            <span style="display: block; font-size: 16px; color: #fff; font-weight: 500;">${fullName}</span>
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Email Address</label>
                            <span style="display: block; font-size: 16px; color: #fff; font-weight: 500;">${email}</span>
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Company Name</label>
                            <span style="display: block; font-size: 16px; color: #fff; font-weight: 500;">${company}</span>
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Phone Number</label>
                            <span id="modal-personal-phone" style="display: block; font-size: 16px; color: #fff; font-weight: 500;">${phone}</span>
                        </div>
                        <div style="grid-column: 1 / -1;">
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Address</label>
                            <span id="modal-personal-address" style="display: block; font-size: 16px; color: #fff; font-weight: 500;">${address}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Email Preferences Section -->
                <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 20px;">
                    <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #fff; font-weight: 600; border-bottom: 1px solid #333; padding-bottom: 8px;">Email Preferences</h3>
                    <p style="margin: 0 0 16px 0; font-size: 14px; color: #B0B0B0;">Control which emails you receive</p>
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 6px;">
                            <div>
                                <label style="display: block; font-size: 14px; color: #fff; font-weight: 500; margin-bottom: 4px;">Marketing Emails</label>
                                <span style="display: block; font-size: 12px; color: #B0B0B0;">Receive updates about new features and promotions</span>
                            </div>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; background: ${marketingEmails ? '#28A745' : '#6C757D'}; color: #fff; font-weight: 500;">
                                ${marketingEmails ? 'Enabled' : 'Disabled'}
                            </span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 6px;">
                            <div>
                                <label style="display: block; font-size: 14px; color: #fff; font-weight: 500; margin-bottom: 4px;">Report Notifications</label>
                                <span style="display: block; font-size: 12px; color: #B0B0B0;">Get notified when your reports are ready</span>
                            </div>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; background: ${reportNotifications ? '#28A745' : '#6C757D'}; color: #fff; font-weight: 500;">
                                ${reportNotifications ? 'Enabled' : 'Disabled'}
                            </span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 6px;">
                            <div>
                                <label style="display: block; font-size: 14px; color: #fff; font-weight: 500; margin-bottom: 4px;">Security Alerts</label>
                                <span style="display: block; font-size: 12px; color: #B0B0B0;">Important security and account updates</span>
                            </div>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; background: ${securityAlerts ? '#28A745' : '#6C757D'}; color: #fff; font-weight: 500;">
                                ${securityAlerts ? 'Enabled' : 'Disabled'}
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Notification Preferences Section -->
                <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 20px;">
                    <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #fff; font-weight: 600; border-bottom: 1px solid #333; padding-bottom: 8px;">Notification Preferences</h3>
                    <p style="margin: 0 0 16px 0; font-size: 14px; color: #B0B0B0;">Manage your notification settings</p>
                    <div style="display: flex; flex-direction: column; gap: 12px;">
                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 6px;">
                            <div>
                                <label style="display: block; font-size: 14px; color: #fff; font-weight: 500; margin-bottom: 4px;">Browser Notifications</label>
                                <span style="display: block; font-size: 12px; color: #B0B0B0;">Receive notifications in your browser</span>
                            </div>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; background: ${browserNotifications ? '#28A745' : '#6C757D'}; color: #fff; font-weight: 500;">
                                ${browserNotifications ? 'Enabled' : 'Disabled'}
                            </span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 6px;">
                            <div>
                                <label style="display: block; font-size: 14px; color: #fff; font-weight: 500; margin-bottom: 4px;">Market Updates</label>
                                <span style="display: block; font-size: 12px; color: #B0B0B0;">Get notified about market changes</span>
                            </div>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; background: ${marketUpdates ? '#28A745' : '#6C757D'}; color: #fff; font-weight: 500;">
                                ${marketUpdates ? 'Enabled' : 'Disabled'}
                            </span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 6px;">
                            <div>
                                <label style="display: block; font-size: 14px; color: #fff; font-weight: 500; margin-bottom: 4px;">Price Alerts</label>
                                <span style="display: block; font-size: 12px; color: #B0B0B0;">Alerts when prices change significantly</span>
                            </div>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; background: ${priceAlerts ? '#28A745' : '#6C757D'}; color: #fff; font-weight: 500;">
                                ${priceAlerts ? 'Enabled' : 'Disabled'}
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Billing History Section -->
                <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 20px;">
                    <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #fff; font-weight: 600; border-bottom: 1px solid #333; padding-bottom: 8px;">Billing History</h3>
                    <p style="margin: 0 0 16px 0; font-size: 14px; color: #B0B0B0;">View and download your receipts</p>
                    ${billingHistory.length > 0 ? `
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <thead>
                                    <tr style="border-bottom: 1px solid #333;">
                                        <th style="padding: 12px; text-align: left; font-size: 12px; color: #808080; text-transform: uppercase;">Date</th>
                                        <th style="padding: 12px; text-align: left; font-size: 12px; color: #808080; text-transform: uppercase;">Description</th>
                                        <th style="padding: 12px; text-align: left; font-size: 12px; color: #808080; text-transform: uppercase;">Amount</th>
                                        <th style="padding: 12px; text-align: left; font-size: 12px; color: #808080; text-transform: uppercase;">Status</th>
                                        <th style="padding: 12px; text-align: left; font-size: 12px; color: #808080; text-transform: uppercase;">Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${billingHistory.map((bill, index) => `
                                        <tr style="border-bottom: 1px solid #222;">
                                            <td style="padding: 12px; color: #fff; font-size: 14px;">${this.formatDate(bill.date || bill.created_at)}</td>
                                            <td style="padding: 12px; color: #fff; font-size: 14px;">${bill.description || bill.plan || 'N/A'}</td>
                                            <td style="padding: 12px; color: #fff; font-size: 14px; font-weight: 500;">${bill.amount ? '$' + parseFloat(bill.amount).toFixed(2) : 'N/A'}</td>
                                            <td style="padding: 12px;">
                                                <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; background: ${bill.status === 'paid' || bill.status === 'completed' ? '#28A745' : '#FFC107'}; color: #fff;">
                                                    ${bill.status || 'Pending'}
                                                </span>
                                            </td>
                                            <td style="padding: 12px;">
                                                ${bill.receipt_url || bill.invoice_url ? `
                                                    <a href="${bill.receipt_url || bill.invoice_url}" target="_blank" style="color: #007BFF; text-decoration: none; font-size: 14px;">Download</a>
                                                ` : '<span style="color: #808080; font-size: 14px;">N/A</span>'}
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    ` : `
                        <div style="padding: 40px; text-align: center; color: #808080;">
                            <p style="margin: 0; font-size: 14px;">No billing history available</p>
                        </div>
                    `}
                </div>
                
                <!-- Account Information Section -->
                <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 20px;">
                    <h3 style="margin: 0 0 16px 0; font-size: 18px; color: #fff; font-weight: 600; border-bottom: 1px solid #333; padding-bottom: 8px;">Account Information</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">User ID</label>
                            <span style="display: block; font-size: 16px; color: #fff; font-weight: 500;">#${user.id}</span>
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Registration Date</label>
                            <span style="display: block; font-size: 16px; color: #fff; font-weight: 500;">${this.formatDate(user.created_at)}</span>
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Last Login</label>
                            <span style="display: block; font-size: 16px; color: #fff; font-weight: 500;">${user.last_login ? this.formatDate(user.last_login) : 'Never'}</span>
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Email Verified</label>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; background: ${user.is_verified ? '#28A745' : '#FFC107'}; color: #fff;">
                                ${user.is_verified ? 'Verified' : 'Pending Verification'}
                            </span>
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Account Status</label>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; background: ${user.is_active ? '#28A745' : '#DC3545'}; color: #fff;">
                                ${user.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Is Verified</label>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; background: ${user.is_verified ? '#28A745' : '#FFC107'}; color: #fff;">
                                ${user.is_verified ? 'Yes' : 'No'}
                            </span>
                        </div>
                    </div>
                </div>
                
                <!-- Role & Permissions Section -->
                <div style="background: rgba(255,255,255,0.03); border-radius: 8px; padding: 20px;">
                    <h3 style="margin: 0 0 16px 0; font-size: 18px; color: #fff; font-weight: 600; border-bottom: 1px solid #333; padding-bottom: 8px;">Role & Permissions</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Current Role</label>
                            <span style="display: inline-block; padding: 6px 16px; border-radius: 4px; font-size: 14px; background: #007BFF; color: #fff; font-weight: 500;">
                                ${this.formatRole(role)}
                            </span>
                        </div>
                        <div>
                            <label style="display: block; font-size: 12px; color: #808080; margin-bottom: 4px; text-transform: uppercase;">Access Level</label>
                            <span style="display: block; font-size: 16px; color: #fff; font-weight: 500;">${role === 'admin' ? 'Administrator' : 'Standard User'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Show modal with proper display style
        modal.style.display = 'block';
        modal.classList.add('show');
        
        // Force update displayed values from API response after modal is shown
        // Use the actual user object values (which should have phone/address from API)
        setTimeout(() => {
            console.log('setTimeout - Updating DOM with user object:', {
                full_name: user.full_name,
                company_name: user.company_name,
                phone: user.phone,
                phone_number: user.phone_number,
                address: user.address,
                street_address: user.street_address,
                full_address: user.full_address
            });
            
            // Direct updates using IDs (most reliable)
            const phoneEl = document.getElementById('modal-personal-phone');
            const addressEl = document.getElementById('modal-personal-address');
            
            if (phoneEl) {
                const phoneValue = user.phone || user.phone_number || user.phoneNumber;
                if (phoneValue && phoneValue !== 'N/A' && phoneValue !== 'null' && phoneValue !== 'undefined' && phoneValue !== null && phoneValue !== undefined) {
                    phoneEl.textContent = phoneValue;
                    console.log('Updated Phone Number (by ID) to:', phoneValue);
                } else {
                    console.log('Phone value not valid:', phoneValue, 'from user object:', user.phone, user.phone_number);
                }
            } else {
                console.error('Phone element not found!');
            }
            
            if (addressEl) {
                const addressValue = user.address || user.street_address || user.full_address;
                if (addressValue && addressValue !== 'Not provided' && addressValue !== 'null' && addressValue !== 'undefined' && addressValue !== null && addressValue !== undefined) {
                    addressEl.textContent = addressValue;
                    console.log('Updated Address (by ID) to:', addressValue);
                } else {
                    console.log('Address value not valid:', addressValue, 'from user object:', user.address, user.street_address, user.full_address);
                }
            } else {
                console.error('Address element not found!');
            }
            
            // Also update by label traversal as fallback
            const allLabels = content.querySelectorAll('label');
            allLabels.forEach(label => {
                const labelText = label.textContent.trim();
                const valueSpan = label.nextElementSibling;
                
                if (valueSpan && valueSpan.tagName === 'SPAN' && !valueSpan.id) {
                    if (labelText === 'Full Name') {
                        const fullNameValue = user.full_name || user.name || user.fullName || 'N/A';
                        if (fullNameValue && fullNameValue !== 'N/A') {
                            valueSpan.textContent = fullNameValue;
                        }
                    } else if (labelText === 'Company Name') {
                        const companyValue = user.company_name || user.company || user.companyName || 'N/A';
                        if (companyValue && companyValue !== 'N/A' && companyValue !== 'null') {
                            valueSpan.textContent = companyValue;
                        }
                    }
                }
            });
        }, 300);
        
        // Add click outside to close
        const closeHandler = (e) => {
            if (e.target === modal) {
                this.hideUserDetailsModal();
                modal.removeEventListener('click', closeHandler);
            }
        };
        modal.addEventListener('click', closeHandler);
    }

    hideUserDetailsModal() {
        const modal = document.getElementById('user-details-modal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
        }
    }

    async editUser(userId) {
        const user = this.users.find(u => u.id === userId);
        if (!user) {
            this.showError('User not found');
            return;
        }
        
        // For now, show a prompt-based edit. Can be enhanced with a proper edit modal later
        const newEmail = prompt('Enter new email address:', user.email);
        if (!newEmail || newEmail === user.email) {
            return;
        }
        
        const newName = prompt('Enter new full name:', user.full_name || user.name);
        if (!newName) {
            return;
        }
        
        const newCompany = prompt('Enter new company name:', user.company_name || user.company || '');
        
        try {
            const updateData = {
                email: newEmail,
                full_name: newName,
                company_name: newCompany || user.company_name || user.company
            };
            
            await this.api.updateUser(userId, updateData);
            this.showSuccess('User updated successfully');
            // Reload users and refresh modal if open
            await this.loadUsers();
            // If modal is open for this user, refresh it
            const modal = document.getElementById('user-details-modal');
            if (modal && modal.dataset.userId == userId) {
                this.viewUser(userId);
            }
        } catch (error) {
            console.error('Failed to update user:', error);
            this.showError('Failed to update user');
        }
    }

    async toggleUserStatus(userId) {
        const user = this.users.find(u => u.id === userId);
        const action = user?.is_active ? 'suspend' : 'activate';
        const confirmMessage = user?.is_active 
            ? `Are you sure you want to suspend user ${user.email || userId}?`
            : `Are you sure you want to activate user ${user.email || userId}?`;
            
        if (!confirm(confirmMessage)) {
            return;
        }
        
        try {
            if (user.is_active) {
                await this.api.deactivateUser(userId);
                this.showSuccess('User suspended successfully');
            } else {
                await this.api.activateUser(userId);
                this.showSuccess('User activated successfully');
            }
            // Reload users and refresh modal if open
            await this.loadUsers();
            // If modal is open for this user, refresh it
            const modal = document.getElementById('user-details-modal');
            if (modal && modal.dataset.userId == userId) {
                this.viewUser(userId);
            }
        } catch (error) {
            console.error('Failed to update user status:', error);
            this.showError('Failed to update user status');
        }
    }

    async resetUserPassword(userId) {
        const newPassword = prompt('Enter new password:');
        if (!newPassword) return;

        try {
            await this.api.resetUserPassword(userId, newPassword);
            this.showSuccess('Password reset successfully');
        } catch (error) {
            this.showError('Failed to reset password');
        }
    }

    async deleteUser(userId) {
        const user = this.users.find(u => u.id === userId);
        const userName = user?.email || user?.full_name || `User #${userId}`;
        
        if (!confirm(`Are you sure you want to delete ${userName}? This action cannot be undone.`)) {
            return;
        }

        try {
            await this.api.deleteUser(userId);
            this.showSuccess('User deleted successfully');
            // Close modal if open
            this.hideUserDetailsModal();
            // Reload users list
            await this.loadUsers();
        } catch (error) {
            console.error('Failed to delete user:', error);
            this.showError('Failed to delete user');
        }
    }

    async exportUsers() {
        try {
            const response = await this.api.exportData({
                data_type: 'users',
                format: 'csv',
                filters: this.currentFilters
            });
            
            // Download the file
            const blob = new Blob([response], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `users-export-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showSuccess('Users exported successfully');
        } catch (error) {
            this.showError('Failed to export users');
        }
    }

    goToPage(page) {
        const totalPages = this.getTotalPages();
        if (page < 1 || page > totalPages) return;
        
        this.currentPage = page;
        this.loadUsers();
    }

    getTotalPages() {
        return Math.ceil(this.totalUsers / this.pageSize);
    }

    updatePagination() {
        const totalPages = this.getTotalPages();
        const firstBtn = document.getElementById('first-page-btn');
        const prevBtn = document.getElementById('prev-page-btn');
        const nextBtn = document.getElementById('next-page-btn');
        const lastBtn = document.getElementById('last-page-btn');
        const pagesContainer = document.getElementById('pagination-pages');

        // Update button states - check if elements exist first
        if (firstBtn) firstBtn.disabled = this.currentPage === 1;
        if (prevBtn) prevBtn.disabled = this.currentPage === 1;
        if (nextBtn) nextBtn.disabled = this.currentPage === totalPages;
        if (lastBtn) lastBtn.disabled = this.currentPage === totalPages;

        // Generate page numbers - check if container exists
        if (!pagesContainer) return;
        pagesContainer.innerHTML = '';
        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `pagination-btn ${i === this.currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.addEventListener('click', () => this.goToPage(i));
            pagesContainer.appendChild(pageBtn);
        }
    }

    updateTableCount() {
        // Try multiple possible element IDs/selectors
        const countElement = document.getElementById('table-count') || 
                           document.getElementById('recordsInfo') ||
                           document.querySelector('.table-count, .user-count, .total-count, .records-info');
        
        if (countElement) {
            const start = (this.currentPage - 1) * this.pageSize + 1;
            const end = Math.min(this.currentPage * this.pageSize, this.totalUsers);
            if (countElement.id === 'recordsInfo') {
                countElement.textContent = `Showing ${start} to ${end} of ${this.totalUsers} records`;
            } else {
                countElement.textContent = `${this.totalUsers} users`;
            }
        }
    }

    showLoadingState() {
        document.body.classList.add('loading');
    }

    hideLoadingState() {
        document.body.classList.remove('loading');
    }

    showError(message) {
        // Create error toast
        const toast = document.createElement('div');
        toast.className = 'toast toast-error';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    showSuccess(message) {
        // Create success toast
        const toast = document.createElement('div');
        toast.className = 'toast toast-success';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 3000);
    }

    // Utility methods
    formatRole(role) {
        const roleMap = {
            'crane_rental_company': 'Crane Rental',
            'equipment_dealer': 'Equipment Dealer',
            'financial_institution': 'Financial Institution',
            'admin': 'Admin'
        };
        return roleMap[role] || role;
    }

    formatSubscription(tier) {
        const tierMap = {
            'basic': 'Basic',
            'pro': 'Pro',
            'enterprise': 'Enterprise'
        };
        return tierMap[tier] || tier;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    getUserStatusClass(user) {
        // Show "Pending" if user is not verified, even if is_active is True
        const isVerified = user.is_verified !== undefined ? user.is_verified : (user.isVerified !== undefined ? user.isVerified : true);
        if (!isVerified) {
            return 'pending';
        }
        const isActive = user.is_active !== undefined ? user.is_active : (user.isActive !== undefined ? user.isActive : false);
        return isActive ? 'active' : 'inactive';
    }

    getUserStatusText(user) {
        // Show "Pending" if user is not verified, even if is_active is True
        const isVerified = user.is_verified !== undefined ? user.is_verified : (user.isVerified !== undefined ? user.isVerified : true);
        if (!isVerified) {
            return 'Pending';
        }
        const isActive = user.is_active !== undefined ? user.is_active : (user.isActive !== undefined ? user.isActive : false);
        return isActive ? 'Active' : 'Inactive';
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // New methods for enhanced functionality
    handleActionIcon(action) {
        console.log('Action icon clicked:', action);
        switch (action) {
            case 'Close':
                this.closeAllModals();
                break;
            case 'Document':
                this.showDocumentModal();
                break;
            case 'Download':
                this.exportUsers();
                break;
            case 'Upload':
                this.showImportModal();
                break;
            case 'Settings':
                this.showSettingsModal();
                break;
            case 'Export':
                this.exportUsers();
                break;
            default:
                console.log('Action not implemented:', action);
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
        });
    }

    showDocumentModal() {
        this.showSuccess('Document functionality coming soon!');
    }

    showImportModal() {
        this.showSuccess('Import functionality coming soon!');
    }

    showSettingsModal() {
        this.showSuccess('Settings functionality coming soon!');
    }

    toggleBulkActions(enabled) {
        const bulkButtons = document.querySelectorAll('#delete-btn, #suspend-btn');
        bulkButtons.forEach(btn => {
            btn.disabled = !enabled;
            btn.style.opacity = enabled ? '1' : '0.5';
        });
    }

    async handleBulkAction(action) {
        if (this.selectedUsers.size === 0) {
            this.showError('Please select users first');
            return;
        }

        const userIds = Array.from(this.selectedUsers);
        
        switch (action) {
            case 'delete':
                await this.bulkDeleteUsers(userIds);
                break;
            case 'suspend':
                await this.bulkSuspendUsers(userIds);
                break;
            default:
                this.showError('Unknown bulk action');
        }
    }

    async bulkSuspendUsers(userIds) {
        if (!confirm(`Are you sure you want to suspend ${userIds.length} users?`)) {
            return;
        }

        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.showSuccess(`${userIds.length} users suspended successfully`);
            this.selectedUsers.clear();
            this.loadUsers();
        } catch (error) {
            this.showError('Failed to suspend users');
        }
    }

    // Enhanced user selection and right panel functionality
    async selectUser(user) {
        // Update the right panel with selected user details
        document.getElementById('selected-user-name').textContent = user.name || user.full_name || 'N/A';
        document.getElementById('selected-user-email').textContent = user.email;
        const avatarEl = document.getElementById('selected-user-avatar');
        if (avatarEl) {
            avatarEl.src = user.avatar || generateAvatarUrl(user.name || user.full_name || 'U', 80);
        }
        
        // Update role selection
        const roleRadios = document.querySelectorAll('input[name="user-role"]');
        roleRadios.forEach(radio => {
            radio.checked = radio.value === (user.role || user.user_role || 'user').toLowerCase();
        });
        
        // Update account enabled toggle
        const enabledToggle = document.getElementById('account-enabled');
        if (enabledToggle) {
            enabledToggle.checked = user.is_active || user.status === 'active';
        }
        
        // Highlight selected row
        document.querySelectorAll('.user-row').forEach(row => {
            row.classList.remove('selected');
        });
        document.querySelector(`[data-user-id="${user.id}"]`)?.classList.add('selected');
    }

    // Save user changes from right panel
    async saveUserChanges() {
        const selectedUser = this.getSelectedUser();
        if (!selectedUser) {
            this.showError('No user selected');
            return;
        }

        const roleRadios = document.querySelectorAll('input[name="user-role"]:checked');
        const newRole = roleRadios.length > 0 ? roleRadios[0].value : 'user';
        
        const enabledToggle = document.getElementById('account-enabled');
        const isEnabled = enabledToggle ? enabledToggle.checked : true;

        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Update local data
            const userIndex = this.users.findIndex(u => u.id === selectedUser.id);
            if (userIndex !== -1) {
                this.users[userIndex].role = newRole;
                this.users[userIndex].is_active = isEnabled;
                this.users[userIndex].status = isEnabled ? 'active' : 'inactive';
            }
            
            this.showSuccess('User updated successfully');
            this.renderUsers();
        } catch (error) {
            this.showError('Failed to update user');
        }
    }

    getSelectedUser() {
        const selectedRow = document.querySelector('.user-row.selected');
        if (!selectedRow) return null;
        
        const userId = parseInt(selectedRow.dataset.userId);
        return this.users.find(u => u.id === userId);
    }

    // Enhanced search with real-time results
    handleSearch(query) {
        console.log('Search query:', query);
        this.currentFilters.search = query;
        this.currentPage = 1;
        this.loadUsers();
    }

    // Enhanced filtering
    handleFilterChange(field, value) {
        if (value) {
            this.currentFilters[field] = value;
        } else {
            delete this.currentFilters[field];
        }
        this.currentPage = 1;
        this.loadUsers();
    }

    applyFilters() {
        // Apply status filter logic
        const statusFilter = document.getElementById('status-filter')?.value;
        if (statusFilter) {
            this.currentFilters.status = statusFilter;
        } else {
            delete this.currentFilters.status;
        }
        this.currentPage = 1;
        this.loadUsers();
    }

    applyFilters() {
        this.currentPage = 1;
        this.loadUsers();
    }

    clearFilters() {
        // Clear all filter inputs
        document.getElementById('user-search').value = '';
        document.getElementById('role-filter').value = '';
        document.getElementById('status-filter').value = '';
        document.getElementById('date-filter').value = '';

        // Clear current filters
        this.currentFilters = {};
        this.currentPage = 1;
        this.loadUsers();
    }
}

// Initialize user management when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing User Management...');
    
    // Wait for AdminAPI to be available
    const initUserManagement = () => {
        if (typeof window.adminAPI === 'undefined' && typeof AdminAPI === 'undefined') {
            console.warn('AdminAPI not yet available, retrying...');
            setTimeout(initUserManagement, 100);
            return;
        }
        
        try {
            window.userManagement = new UserManagement();
            console.log('User Management initialized successfully');
        } catch (error) {
            console.error('Error initializing User Management:', error);
        }
    };
    
    // Start initialization
    initUserManagement();
});

// Also try to initialize if DOM is already loaded
const initIfReady = () => {
    if (typeof window.adminAPI === 'undefined' && typeof AdminAPI === 'undefined') {
        setTimeout(initIfReady, 100);
        return;
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('DOM loaded, initializing User Management...');
            if (!window.userManagement) {
                window.userManagement = new UserManagement();
            }
        });
    } else {
        console.log('DOM already loaded, initializing User Management immediately...');
        if (!window.userManagement) {
            window.userManagement = new UserManagement();
        }
    }
};

initIfReady();
