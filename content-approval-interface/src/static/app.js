/**
 * Content Approval Interface JavaScript Application
 */

class ContentApprovalApp {
    constructor() {
        this.suggestions = [];
        this.selectedSuggestions = new Set();
        this.currentFilters = {
            status: 'pending_review',
            platform: '',
            content_type: ''
        };
        this.currentOffset = 0;
        this.limit = 12;
        this.totalCount = 0;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadAnalytics();
        this.loadSuggestions();
        this.updateLastUpdated();
    }
    
    bindEvents() {
        // Filter events
        document.getElementById('applyFiltersBtn').addEventListener('click', () => {
            this.applyFilters();
        });
        
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refresh();
        });
        
        // Batch action events
        document.getElementById('batchApproveBtn').addEventListener('click', () => {
            this.batchAction('approve');
        });
        
        document.getElementById('batchRejectBtn').addEventListener('click', () => {
            this.batchAction('reject');
        });
        
        document.getElementById('clearSelectionBtn').addEventListener('click', () => {
            this.clearSelection();
        });
        
        document.getElementById('selectAllBtn').addEventListener('click', () => {
            this.selectAll();
        });
        
        // Modal events
        document.getElementById('closeModalBtn').addEventListener('click', () => {
            this.closeModal();
        });
        
        document.getElementById('contentModal').addEventListener('click', (e) => {
            if (e.target.id === 'contentModal') {
                this.closeModal();
            }
        });
        
        // Load more button
        document.getElementById('loadMoreBtn').addEventListener('click', () => {
            this.loadMoreSuggestions();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }
    
    async loadAnalytics() {
        try {
            const response = await fetch('/api/content/analytics/summary');
            const data = await response.json();
            
            if (data.success) {
                this.renderAnalytics(data.summary);
            }
        } catch (error) {
            console.error('Failed to load analytics:', error);
        }
    }
    
    renderAnalytics(summary) {
        const analyticsGrid = document.getElementById('analyticsGrid');
        
        const cards = [
            {
                title: 'Total Suggestions',
                value: summary.total_suggestions,
                icon: 'fas fa-lightbulb',
                color: 'blue'
            },
            {
                title: 'Pending Review',
                value: summary.pending_suggestions,
                icon: 'fas fa-clock',
                color: 'yellow'
            },
            {
                title: 'Approved',
                value: summary.approved_suggestions,
                icon: 'fas fa-check-circle',
                color: 'green'
            },
            {
                title: 'Approval Rate',
                value: `${summary.approval_rate}%`,
                icon: 'fas fa-chart-line',
                color: 'purple'
            }
        ];
        
        analyticsGrid.innerHTML = cards.map(card => `
            <div class="bg-white rounded-lg shadow-sm p-6">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 bg-${card.color}-100 rounded-lg flex items-center justify-center">
                            <i class="${card.icon} text-${card.color}-600"></i>
                        </div>
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">${card.title}</p>
                        <p class="text-2xl font-semibold text-gray-900">${card.value}</p>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    async loadSuggestions(reset = true) {
        if (reset) {
            this.currentOffset = 0;
            this.suggestions = [];
        }
        
        this.showLoading();
        
        try {
            const params = new URLSearchParams({
                limit: this.limit,
                offset: this.currentOffset,
                ...this.currentFilters
            });
            
            // Remove empty filters
            for (const [key, value] of params.entries()) {
                if (!value) {
                    params.delete(key);
                }
            }
            
            const response = await fetch(`/api/content/suggestions?${params}`);
            const data = await response.json();
            
            if (data.success) {
                if (reset) {
                    this.suggestions = data.suggestions;
                } else {
                    this.suggestions.push(...data.suggestions);
                }
                this.totalCount = data.total_count;
                this.renderSuggestions();
                this.updateLoadMoreButton();
            } else {
                this.showToast('Failed to load suggestions', 'error');
            }
        } catch (error) {
            console.error('Failed to load suggestions:', error);
            this.showToast('Failed to load suggestions', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async loadMoreSuggestions() {
        this.currentOffset += this.limit;
        await this.loadSuggestions(false);
    }
    
    renderSuggestions() {
        const contentGrid = document.getElementById('contentGrid');
        const emptyState = document.getElementById('emptyState');
        const totalCountEl = document.getElementById('totalCount');
        
        totalCountEl.textContent = `${this.totalCount} suggestions`;
        
        if (this.suggestions.length === 0) {
            contentGrid.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }
        
        emptyState.style.display = 'none';
        contentGrid.style.display = 'grid';
        
        contentGrid.innerHTML = this.suggestions.map(suggestion => this.createContentCard(suggestion)).join('');
        
        // Bind card events
        this.bindCardEvents();
    }
    
    createContentCard(suggestion) {
        const statusClass = suggestion.status === 'approved' ? 'approved' : 
                           suggestion.status === 'rejected' ? 'rejected' : 'pending';
        
        const platformIcon = this.getPlatformIcon(suggestion.platform);
        const contentTypeColor = this.getContentTypeColor(suggestion.content_type);
        
        const isSelected = this.selectedSuggestions.has(suggestion.id);
        
        return `
            <div class="content-card ${statusClass} bg-white rounded-lg shadow-sm p-6 relative" data-id="${suggestion.id}">
                <!-- Selection Checkbox -->
                <div class="absolute top-4 left-4">
                    <input type="checkbox" class="suggestion-checkbox w-4 h-4 text-blue-600 rounded" 
                           ${isSelected ? 'checked' : ''} data-id="${suggestion.id}">
                </div>
                
                <!-- Platform and Content Type -->
                <div class="flex justify-between items-start mb-4 ml-8">
                    <div class="flex items-center space-x-2">
                        <span class="platform-badge text-sm font-medium text-gray-600">
                            <i class="${platformIcon}"></i>
                            ${suggestion.platform.charAt(0).toUpperCase() + suggestion.platform.slice(1)}
                        </span>
                        <span class="px-2 py-1 text-xs font-medium rounded-full bg-${contentTypeColor}-100 text-${contentTypeColor}-800">
                            ${suggestion.content_type}
                        </span>
                    </div>
                    <div class="flex items-center space-x-1">
                        ${suggestion.engagement_score ? `
                            <span class="text-xs text-gray-500">
                                <i class="fas fa-chart-bar"></i> ${suggestion.engagement_score}
                            </span>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Content Preview -->
                <div class="mb-4">
                    <h3 class="font-semibold text-gray-900 mb-2 line-clamp-2">${suggestion.title}</h3>
                    <p class="text-gray-600 text-sm line-clamp-3">${suggestion.body}</p>
                </div>
                
                <!-- Hashtags -->
                ${suggestion.hashtags && suggestion.hashtags.length > 0 ? `
                    <div class="mb-4">
                        <div class="flex flex-wrap gap-1">
                            ${suggestion.hashtags.slice(0, 3).map(tag => `
                                <span class="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">${tag}</span>
                            `).join('')}
                            ${suggestion.hashtags.length > 3 ? `
                                <span class="text-xs text-gray-500">+${suggestion.hashtags.length - 3} more</span>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                <!-- Status Badge -->
                <div class="mb-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                 ${suggestion.status === 'approved' ? 'bg-green-100 text-green-800' :
                                   suggestion.status === 'rejected' ? 'bg-red-100 text-red-800' :
                                   'bg-yellow-100 text-yellow-800'}">
                        <i class="fas ${suggestion.status === 'approved' ? 'fa-check' :
                                       suggestion.status === 'rejected' ? 'fa-times' :
                                       'fa-clock'} mr-1"></i>
                        ${suggestion.status.replace('_', ' ').toUpperCase()}
                    </span>
                </div>
                
                <!-- Action Buttons -->
                <div class="flex justify-between items-center">
                    <button class="view-details-btn text-blue-600 hover:text-blue-800 text-sm font-medium" 
                            data-id="${suggestion.id}">
                        <i class="fas fa-eye mr-1"></i>View Details
                    </button>
                    
                    ${suggestion.status === 'pending_review' ? `
                        <div class="flex space-x-2">
                            <button class="feedback-button approve-btn bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700" 
                                    data-id="${suggestion.id}" data-action="approve">
                                <i class="fas fa-check"></i>
                            </button>
                            <button class="feedback-button reject-btn bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700" 
                                    data-id="${suggestion.id}" data-action="reject">
                                <i class="fas fa-times"></i>
                            </button>
                            <button class="feedback-button thumbs-up-btn bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700" 
                                    data-id="${suggestion.id}" data-action="thumbs_up">
                                <i class="fas fa-thumbs-up"></i>
                            </button>
                            <button class="feedback-button thumbs-down-btn bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700" 
                                    data-id="${suggestion.id}" data-action="thumbs_down">
                                <i class="fas fa-thumbs-down"></i>
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    bindCardEvents() {
        // Checkbox events
        document.querySelectorAll('.suggestion-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const suggestionId = e.target.dataset.id;
                if (e.target.checked) {
                    this.selectedSuggestions.add(suggestionId);
                } else {
                    this.selectedSuggestions.delete(suggestionId);
                }
                this.updateBatchActionsPanel();
            });
        });
        
        // View details events
        document.querySelectorAll('.view-details-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const suggestionId = e.target.dataset.id;
                this.showContentDetails(suggestionId);
            });
        });
        
        // Feedback button events
        document.querySelectorAll('.feedback-button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const suggestionId = e.target.dataset.id;
                const action = e.target.dataset.action;
                this.submitFeedback(suggestionId, action);
            });
        });
    }
    
    getPlatformIcon(platform) {
        const icons = {
            facebook: 'fab fa-facebook',
            twitter: 'fab fa-twitter',
            instagram: 'fab fa-instagram',
            linkedin: 'fab fa-linkedin',
            tiktok: 'fab fa-tiktok'
        };
        return icons[platform] || 'fas fa-globe';
    }
    
    getContentTypeColor(contentType) {
        const colors = {
            educational: 'blue',
            promotional: 'green',
            entertaining: 'purple',
            inspirational: 'yellow'
        };
        return colors[contentType] || 'gray';
    }
    
    async submitFeedback(suggestionId, action) {
        try {
            const response = await fetch(`/api/content/suggestions/${suggestionId}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    feedback_type: action,
                    feedback_score: action === 'thumbs_up' ? 5 : action === 'thumbs_down' ? 1 : null
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(`Feedback submitted: ${action}`, 'success');
                
                // Update the suggestion in our local data
                const suggestionIndex = this.suggestions.findIndex(s => s.id === suggestionId);
                if (suggestionIndex !== -1) {
                    this.suggestions[suggestionIndex] = data.suggestion;
                }
                
                // Re-render the suggestions
                this.renderSuggestions();
                
                // Reload analytics
                this.loadAnalytics();
            } else {
                this.showToast('Failed to submit feedback', 'error');
            }
        } catch (error) {
            console.error('Failed to submit feedback:', error);
            this.showToast('Failed to submit feedback', 'error');
        }
    }
    
    async batchAction(action) {
        if (this.selectedSuggestions.size === 0) {
            this.showToast('No suggestions selected', 'info');
            return;
        }
        
        try {
            const response = await fetch('/api/content/suggestions/batch-action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    suggestion_ids: Array.from(this.selectedSuggestions),
                    action: action
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(`${action} applied to ${data.count} suggestions`, 'success');
                this.clearSelection();
                this.refresh();
            } else {
                this.showToast('Failed to perform batch action', 'error');
            }
        } catch (error) {
            console.error('Failed to perform batch action:', error);
            this.showToast('Failed to perform batch action', 'error');
        }
    }
    
    showContentDetails(suggestionId) {
        const suggestion = this.suggestions.find(s => s.id === suggestionId);
        if (!suggestion) return;
        
        const modalContent = document.getElementById('modalContent');
        
        modalContent.innerHTML = `
            <div class="space-y-6">
                <!-- Header Info -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <h4 class="font-medium text-gray-900 mb-2">Platform</h4>
                        <div class="flex items-center space-x-2">
                            <i class="${this.getPlatformIcon(suggestion.platform)}"></i>
                            <span>${suggestion.platform.charAt(0).toUpperCase() + suggestion.platform.slice(1)}</span>
                        </div>
                    </div>
                    <div>
                        <h4 class="font-medium text-gray-900 mb-2">Content Type</h4>
                        <span class="px-2 py-1 text-sm font-medium rounded-full bg-${this.getContentTypeColor(suggestion.content_type)}-100 text-${this.getContentTypeColor(suggestion.content_type)}-800">
                            ${suggestion.content_type}
                        </span>
                    </div>
                </div>
                
                <!-- Content -->
                <div>
                    <h4 class="font-medium text-gray-900 mb-2">Title</h4>
                    <p class="text-gray-700">${suggestion.title}</p>
                </div>
                
                <div>
                    <h4 class="font-medium text-gray-900 mb-2">Content</h4>
                    <div class="bg-gray-50 rounded-lg p-4">
                        <p class="text-gray-700 whitespace-pre-wrap">${suggestion.body}</p>
                    </div>
                </div>
                
                <!-- Full Text Preview -->
                <div>
                    <h4 class="font-medium text-gray-900 mb-2">Full Post Preview</h4>
                    <div class="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500">
                        <p class="text-gray-700 whitespace-pre-wrap">${suggestion.full_text}</p>
                    </div>
                </div>
                
                <!-- Hashtags -->
                ${suggestion.hashtags && suggestion.hashtags.length > 0 ? `
                    <div>
                        <h4 class="font-medium text-gray-900 mb-2">Hashtags</h4>
                        <div class="flex flex-wrap gap-2">
                            ${suggestion.hashtags.map(tag => `
                                <span class="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">${tag}</span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <!-- Call to Action -->
                ${suggestion.call_to_action ? `
                    <div>
                        <h4 class="font-medium text-gray-900 mb-2">Call to Action</h4>
                        <p class="text-gray-700">${suggestion.call_to_action}</p>
                    </div>
                ` : ''}
                
                <!-- Metadata -->
                <div class="grid grid-cols-2 gap-4 pt-4 border-t">
                    <div>
                        <h4 class="font-medium text-gray-900 mb-2">Engagement Score</h4>
                        <p class="text-gray-700">${suggestion.engagement_score || 'N/A'}</p>
                    </div>
                    <div>
                        <h4 class="font-medium text-gray-900 mb-2">Character Count</h4>
                        <p class="text-gray-700">${suggestion.character_count || 'N/A'}</p>
                    </div>
                    <div>
                        <h4 class="font-medium text-gray-900 mb-2">Generated At</h4>
                        <p class="text-gray-700">${new Date(suggestion.generated_at).toLocaleString()}</p>
                    </div>
                    <div>
                        <h4 class="font-medium text-gray-900 mb-2">Status</h4>
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                     ${suggestion.status === 'approved' ? 'bg-green-100 text-green-800' :
                                       suggestion.status === 'rejected' ? 'bg-red-100 text-red-800' :
                                       'bg-yellow-100 text-yellow-800'}">
                            ${suggestion.status.replace('_', ' ').toUpperCase()}
                        </span>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                ${suggestion.status === 'pending_review' ? `
                    <div class="flex justify-center space-x-4 pt-4 border-t">
                        <button class="modal-feedback-btn bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700" 
                                data-id="${suggestion.id}" data-action="approve">
                            <i class="fas fa-check mr-2"></i>Approve
                        </button>
                        <button class="modal-feedback-btn bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700" 
                                data-id="${suggestion.id}" data-action="reject">
                            <i class="fas fa-times mr-2"></i>Reject
                        </button>
                        <button class="modal-feedback-btn bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700" 
                                data-id="${suggestion.id}" data-action="thumbs_up">
                            <i class="fas fa-thumbs-up mr-2"></i>Thumbs Up
                        </button>
                        <button class="modal-feedback-btn bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700" 
                                data-id="${suggestion.id}" data-action="thumbs_down">
                            <i class="fas fa-thumbs-down mr-2"></i>Thumbs Down
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Bind modal feedback events
        document.querySelectorAll('.modal-feedback-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const suggestionId = e.target.dataset.id;
                const action = e.target.dataset.action;
                this.submitFeedback(suggestionId, action);
                this.closeModal();
            });
        });
        
        document.getElementById('contentModal').classList.add('show');
    }
    
    closeModal() {
        document.getElementById('contentModal').classList.remove('show');
    }
    
    applyFilters() {
        this.currentFilters = {
            status: document.getElementById('statusFilter').value,
            platform: document.getElementById('platformFilter').value,
            content_type: document.getElementById('contentTypeFilter').value
        };
        
        this.loadSuggestions();
    }
    
    clearSelection() {
        this.selectedSuggestions.clear();
        document.querySelectorAll('.suggestion-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateBatchActionsPanel();
    }
    
    selectAll() {
        this.suggestions.forEach(suggestion => {
            this.selectedSuggestions.add(suggestion.id);
        });
        document.querySelectorAll('.suggestion-checkbox').forEach(checkbox => {
            checkbox.checked = true;
        });
        this.updateBatchActionsPanel();
    }
    
    updateBatchActionsPanel() {
        const panel = document.getElementById('batchActionsPanel');
        const selectedCount = document.getElementById('selectedCount');
        
        selectedCount.textContent = `${this.selectedSuggestions.size} items selected`;
        
        if (this.selectedSuggestions.size > 0) {
            panel.style.display = 'block';
        } else {
            panel.style.display = 'none';
        }
    }
    
    updateLoadMoreButton() {
        const container = document.getElementById('loadMoreContainer');
        const hasMore = this.suggestions.length < this.totalCount;
        
        if (hasMore && this.suggestions.length > 0) {
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    }
    
    showLoading() {
        document.getElementById('loadingState').style.display = 'flex';
        document.getElementById('contentGrid').style.display = 'none';
        document.getElementById('emptyState').style.display = 'none';
    }
    
    hideLoading() {
        document.getElementById('loadingState').style.display = 'none';
    }
    
    refresh() {
        this.clearSelection();
        this.loadAnalytics();
        this.loadSuggestions();
        this.updateLastUpdated();
        this.showToast('Content refreshed', 'success');
    }
    
    updateLastUpdated() {
        const now = new Date();
        document.getElementById('lastUpdated').textContent = `Last updated: ${now.toLocaleTimeString()}`;
    }
    
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ContentApprovalApp();
});

