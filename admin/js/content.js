/**
 * Content Management JavaScript
 * Handles content creation, editing, and management
 */

class ContentManager {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 25;
        this.currentContent = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadContent();
        this.loadStats();
    }

    bindEvents() {
        // Content creation
        document.getElementById('createContentBtn').addEventListener('click', () => this.showContentModal());
        document.getElementById('uploadMediaBtn').addEventListener('click', () => this.uploadMedia());
        
        // Modal events
        document.getElementById('closeModal').addEventListener('click', () => this.hideContentModal());
        document.getElementById('cancelContent').addEventListener('click', () => this.hideContentModal());
        document.getElementById('saveContent').addEventListener('click', () => this.saveContent());
        
        // Filters
        document.getElementById('contentTypeFilter').addEventListener('change', () => this.loadContent());
        document.getElementById('statusFilter').addEventListener('change', () => this.loadContent());
        document.getElementById('searchInput').addEventListener('input', this.debounce(() => this.loadContent(), 300));
    }

    async loadContent() {
        try {
            const filters = {
                skip: (this.currentPage - 1) * this.itemsPerPage,
                limit: this.itemsPerPage,
                content_type: document.getElementById('contentTypeFilter').value,
                status: document.getElementById('statusFilter').value,
                search: document.getElementById('searchInput').value
            };

            const api = new AdminAPI();
            const response = await api.getContent(filters);
            this.renderContentTable(response.items || []);
            this.renderPagination(response.total || 0);
        } catch (error) {
            console.error('Error loading content:', error);
            this.showError('Failed to load content');
        }
    }

    async loadStats() {
        try {
            const api = new AdminAPI();
            const stats = await api.getContentStats();
            document.getElementById('totalContent').textContent = stats.total_content || 0;
            document.getElementById('publishedContent').textContent = stats.published_content || 0;
            document.getElementById('draftContent').textContent = stats.draft_content || 0;
            document.getElementById('totalViews').textContent = stats.total_views || 0;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    renderContentTable(content) {
        const tbody = document.getElementById('contentTableBody');
        tbody.innerHTML = '';

        if (content.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No content found</td></tr>';
            return;
        }

        content.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <div class="content-title">
                        <strong>${item.title}</strong>
                        <div class="content-meta">${item.slug}</div>
                    </div>
                </td>
                <td><span class="type-badge ${item.content_type}">${item.content_type}</span></td>
                <td><span class="status-badge ${item.status}">${item.status}</span></td>
                <td>${item.author_name || 'Unknown'}</td>
                <td>${item.view_count || 0}</td>
                <td>${this.formatDate(item.created_at)}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-secondary" onclick="contentManager.editContent(${item.id})">Edit</button>
                        <button class="btn btn-sm btn-primary" onclick="contentManager.previewContent(${item.id})">Preview</button>
                        <button class="btn btn-sm btn-danger" onclick="contentManager.deleteContent(${item.id})">Delete</button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    renderPagination(total) {
        const pagination = document.getElementById('contentPagination');
        const totalPages = Math.ceil(total / this.itemsPerPage);
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let html = '<div class="pagination-controls">';
        
        // Previous button
        if (this.currentPage > 1) {
            html += `<button class="btn btn-sm btn-secondary" onclick="contentManager.goToPage(${this.currentPage - 1})">Previous</button>`;
        }
        
        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                html += `<button class="btn btn-sm btn-primary active">${i}</button>`;
            } else {
                html += `<button class="btn btn-sm btn-secondary" onclick="contentManager.goToPage(${i})">${i}</button>`;
            }
        }
        
        // Next button
        if (this.currentPage < totalPages) {
            html += `<button class="btn btn-sm btn-secondary" onclick="contentManager.goToPage(${this.currentPage + 1})">Next</button>`;
        }
        
        html += '</div>';
        pagination.innerHTML = html;
    }

    showContentModal(content = null) {
        this.currentContent = content;
        const modal = document.getElementById('contentModal');
        const title = document.getElementById('modalTitle');
        const form = document.getElementById('contentForm');
        
        if (content) {
            title.textContent = 'Edit Content';
            form.title.value = content.title;
            form.content_type.value = content.content_type;
            form.content.value = content.content;
            form.excerpt.value = content.excerpt || '';
            form.status.value = content.status;
        } else {
            title.textContent = 'Create Content';
            form.reset();
        }
        
        modal.style.display = 'block';
    }

    hideContentModal() {
        document.getElementById('contentModal').style.display = 'none';
        this.currentContent = null;
    }

    async saveContent() {
        try {
            const form = document.getElementById('contentForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            if (this.currentContent) {
                await AdminAPI.updateContent(this.currentContent.id, data);
                this.showSuccess('Content updated successfully');
            } else {
                await AdminAPI.createContent(data);
                this.showSuccess('Content created successfully');
            }
            
            this.hideContentModal();
            this.loadContent();
        } catch (error) {
            console.error('Error saving content:', error);
            this.showError('Failed to save content');
        }
    }

    async editContent(id) {
        try {
            const content = await AdminAPI.getContentById(id);
            this.showContentModal(content);
        } catch (error) {
            console.error('Error loading content:', error);
            this.showError('Failed to load content');
        }
    }

    async previewContent(id) {
        try {
            const content = await AdminAPI.getContentById(id);
            window.open(`/content/preview/${id}`, '_blank');
        } catch (error) {
            console.error('Error previewing content:', error);
            this.showError('Failed to preview content');
        }
    }

    async deleteContent(id) {
        if (!confirm('Are you sure you want to delete this content?')) {
            return;
        }
        
        try {
            await AdminAPI.deleteContent(id);
            this.showSuccess('Content deleted successfully');
            this.loadContent();
        } catch (error) {
            console.error('Error deleting content:', error);
            this.showError('Failed to delete content');
        }
    }

    async uploadMedia() {
        // Create file input
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*,video/*,.pdf,.doc,.docx';
        input.multiple = true;
        
        input.onchange = async (e) => {
            const files = Array.from(e.target.files);
            for (const file of files) {
                try {
                    await AdminAPI.uploadMedia(file);
                    this.showSuccess(`File ${file.name} uploaded successfully`);
                } catch (error) {
                    console.error('Error uploading file:', error);
                    this.showError(`Failed to upload ${file.name}`);
                }
            }
        };
        
        input.click();
    }

    goToPage(page) {
        this.currentPage = page;
        this.loadContent();
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    showSuccess(message) {
        // Simple success notification
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    showError(message) {
        // Simple error notification
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
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
}

// Initialize content manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.contentManager = new ContentManager();
});
