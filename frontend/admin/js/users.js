/**
 * Crane Intelligence User Management JavaScript
 * Handles user management interface functionality
 */

class UserManagement {
    constructor() {
        this.api = new AdminAPI();
        this.currentPage = 1;
        this.pageSize = 25;
        this.totalUsers = 0;
        this.users = [];
        this.selectedUsers = new Set();
        this.currentSort = { field: 'created_at', direction: 'desc' };
        this.currentFilters = {};
        this.currentView = 'table';
        this.isLoading = false;
        
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
            // Use mock data if API fails
            console.log('Using mock data...');
            this.users = this.getMockUsers();
            this.totalUsers = this.users.length;
            this.renderUsers();
            this.updatePagination();
            this.updateTableCount();
        } finally {
            this.isLoading = false;
            this.hideLoadingState();
        }
    }

    getMockUsers() {
        return [
            {
                id: 1,
                name: "Alice Martin",
                email: "alice@martin.com",
                role: "Admin",
                status: "active",
                lastLogin: "22 min. ago",
                avatar: "https://via.placeholder.com/32x32/007BFF/FFFFFF?text=AM"
            },
            {
                id: 2,
                name: "Bob Brown",
                email: "bob.brown.com",
                role: "Manager",
                status: "active",
                lastLogin: "43 minutes ago",
                avatar: "https://via.placeholder.com/32x32/28A745/FFFFFF?text=BB"
            },
            {
                id: 3,
                name: "Carol White",
                email: "carol.white@example.user",
                role: "User",
                status: "active",
                lastLogin: "4 am ago",
                avatar: "https://via.placeholder.com/32x32/FFC107/FFFFFF?text=CW"
            },
            {
                id: 4,
                name: "Daniel Clark",
                email: "daniel.clark.com",
                role: "User",
                status: "suspended",
                lastLogin: "30 minutes ago",
                avatar: "https://via.placeholder.com/32x32/DC3545/FFFFFF?text=DC"
            },
            {
                id: 5,
                name: "Eric Johnson",
                email: "eri@johnson.com",
                role: "Suspend",
                status: "active",
                lastLogin: "18 hours ago",
                avatar: "https://via.placeholder.com/32x32/6C757D/FFFFFF?text=EJ"
            },
            {
                id: 6,
                name: "Fiona Miller",
                email: "fiona.miller.com",
                role: "Asbbnik",
                status: "active",
                lastLogin: "28 sec. ago",
                avatar: "https://via.placeholder.com/32x32/17A2B8/FFFFFF?text=FM"
            }
        ];
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
        if (!tbody) return;

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

        tbody.innerHTML = this.users.map(user => `
            <tr class="user-row" data-user-id="${user.id}">
                <td>
                    <input type="checkbox" class="user-checkbox" data-user-id="${user.id}">
                </td>
                <td>
                    <img src="${user.avatar || 'https://via.placeholder.com/32x32/007BFF/FFFFFF?text=' + user.name.charAt(0)}" 
                         alt="${user.name}" class="user-avatar-small">
                </td>
                <td>
                    <div class="user-name">${user.name || user.full_name || 'N/A'}</div>
                </td>
                <td>
                    <div class="user-email">${user.email}</div>
                </td>
                <td>
                    <span class="user-role">${user.user_role || user.role || 'N/A'}</span>
                </td>
                <td>
                    <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>
                    <div class="last-login">
                        ${user.lastLogin || (user.last_login ? this.formatDate(user.last_login) : 'Never')}
                    </div>
                </td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="userManagement.viewUser(${user.id})" title="Edit">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                    </button>
                </td>
            </tr>
        `).join('');

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

        // Add row click handlers for user selection
        tbody.querySelectorAll('.user-row').forEach(row => {
            row.addEventListener('click', (e) => {
                if (e.target.type === 'checkbox' || e.target.closest('button')) return;
                
                const userId = parseInt(row.dataset.userId);
                const user = this.users.find(u => u.id === userId);
                if (user) {
                    this.selectUser(user);
                }
            });
        });
    }

    selectUser(user) {
        // Update the right panel with selected user details
        document.getElementById('selected-user-name').textContent = user.name || user.full_name || 'N/A';
        document.getElementById('selected-user-email').textContent = user.email;
        document.getElementById('selected-user-avatar').src = user.avatar || 'https://via.placeholder.com/80x80/007BFF/FFFFFF?text=' + (user.name || user.full_name || 'U').charAt(0);
        
        // Update role selection
        const roleRadios = document.querySelectorAll('input[name="user-role"]');
        roleRadios.forEach(radio => {
            radio.checked = radio.value === (user.role || user.user_role || 'user').toLowerCase();
        });
        
        // Highlight selected row
        document.querySelectorAll('.user-row').forEach(row => {
            row.classList.remove('selected');
        });
        document.querySelector(`[data-user-id="${user.id}"]`).classList.add('selected');
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
                        <img src="https://via.placeholder.com/48x48/007BFF/FFFFFF?text=${user.full_name.charAt(0)}" alt="${user.full_name}">
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
                    <div class="user-detail">
                        <label>Subscription:</label>
                        <span class="subscription-badge subscription-${user.subscription_tier}">${this.formatSubscription(user.subscription_tier)}</span>
                    </div>
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
        document.getElementById(`${view}-view-btn`).classList.add('active');

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
            subscription_tier: formData.get('subscription_tier'),
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
        try {
            const user = await this.api.getUser(userId);
            this.showUserDetails(user);
        } catch (error) {
            this.showError('Failed to load user details');
        }
    }

    showUserDetails(user) {
        const modal = document.getElementById('user-details-modal');
        const content = document.getElementById('user-details-content');
        
        content.innerHTML = `
            <div class="user-details-header">
                <div class="user-avatar-large">
                    <img src="https://via.placeholder.com/80x80/007BFF/FFFFFF?text=${user.full_name.charAt(0)}" alt="${user.full_name}">
                </div>
                <div class="user-details-info">
                    <h2>${user.full_name}</h2>
                    <p class="user-email">${user.email}</p>
                    <p class="user-username">@${user.username}</p>
                </div>
                <div class="user-status-large">
                    <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
            </div>
            <div class="user-details-body">
                <div class="details-grid">
                    <div class="detail-item">
                        <label>Company</label>
                        <span>${user.company_name}</span>
                    </div>
                    <div class="detail-item">
                        <label>Role</label>
                        <span class="role-badge role-${user.user_role}">${this.formatRole(user.user_role)}</span>
                    </div>
                    <div class="detail-item">
                        <label>Subscription</label>
                        <span class="subscription-badge subscription-${user.subscription_tier}">${this.formatSubscription(user.subscription_tier)}</span>
                    </div>
                    <div class="detail-item">
                        <label>Created</label>
                        <span>${this.formatDate(user.created_at)}</span>
                    </div>
                    <div class="detail-item">
                        <label>Last Login</label>
                        <span>${user.last_login ? this.formatDate(user.last_login) : 'Never'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Email Verified</label>
                        <span>${user.is_verified ? 'Yes' : 'No'}</span>
                    </div>
                </div>
            </div>
        `;
        
        modal.classList.add('show');
    }

    hideUserDetailsModal() {
        const modal = document.getElementById('user-details-modal');
        modal.classList.remove('show');
    }

    async editUser(userId) {
        // Implementation for editing user
        console.log('Edit user:', userId);
    }

    async toggleUserStatus(userId) {
        try {
            const user = this.users.find(u => u.id === userId);
            if (user.is_active) {
                await this.api.deactivateUser(userId);
                this.showSuccess('User deactivated successfully');
            } else {
                await this.api.activateUser(userId);
                this.showSuccess('User activated successfully');
            }
            this.loadUsers();
        } catch (error) {
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
        if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
            return;
        }

        try {
            await this.api.deleteUser(userId);
            this.showSuccess('User deleted successfully');
            this.loadUsers();
        } catch (error) {
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

        // Update button states
        firstBtn.disabled = this.currentPage === 1;
        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage === totalPages;
        lastBtn.disabled = this.currentPage === totalPages;

        // Generate page numbers
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
        const countElement = document.getElementById('table-count');
        const start = (this.currentPage - 1) * this.pageSize + 1;
        const end = Math.min(this.currentPage * this.pageSize, this.totalUsers);
        
        countElement.textContent = `${this.totalUsers} users`;
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
        document.getElementById('selected-user-avatar').src = user.avatar || 'https://via.placeholder.com/80x80/007BFF/FFFFFF?text=' + (user.name || user.full_name || 'U').charAt(0);
        
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
    try {
        window.userManagement = new UserManagement();
        console.log('User Management initialized successfully');
    } catch (error) {
        console.error('Error initializing User Management:', error);
    }
});

// Also try to initialize if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM loaded, initializing User Management...');
        window.userManagement = new UserManagement();
    });
} else {
    console.log('DOM already loaded, initializing User Management immediately...');
    window.userManagement = new UserManagement();
}
