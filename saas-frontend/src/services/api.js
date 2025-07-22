/**
 * API Service for Social Media Agent SaaS Platform
 * 
 * Handles all API communications between frontend and backend
 */

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.socialmediaagent.com' 
  : 'http://localhost:5000'

class APIService {
  constructor() {
    this.baseURL = API_BASE_URL
    this.token = localStorage.getItem('access_token')
  }

  // Helper method to make authenticated requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    // Add authorization header if token exists
    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.message || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API Request failed:', error)
      throw error
    }
  }

  // Authentication methods
  async login(email, password) {
    const response = await this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    })
    
    if (response.tokens) {
      this.token = response.tokens.access_token
      localStorage.setItem('access_token', this.token)
      localStorage.setItem('refresh_token', response.tokens.refresh_token)
    }
    
    return response
  }

  async register(userData) {
    const response = await this.request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
    
    if (response.tokens) {
      this.token = response.tokens.access_token
      localStorage.setItem('access_token', this.token)
      localStorage.setItem('refresh_token', response.tokens.refresh_token)
    }
    
    return response
  }

  async logout() {
    await this.request('/api/v1/auth/logout', { method: 'POST' })
    this.token = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) throw new Error('No refresh token available')

    const response = await fetch(`${this.baseURL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      this.token = data.access_token
      localStorage.setItem('access_token', this.token)
      return data
    } else {
      throw new Error('Token refresh failed')
    }
  }

  async getProfile() {
    return await this.request('/api/v1/auth/profile')
  }

  // Business Profile methods
  async createBusinessProfile(profileData) {
    return await this.request('/api/v1/generator/business-profiles', {
      method: 'POST',
      body: JSON.stringify(profileData)
    })
  }

  async getBusinessProfiles() {
    return await this.request('/api/v1/generator/business-profiles')
  }

  async getBusinessProfile(profileId) {
    return await this.request(`/api/v1/generator/business-profiles/${profileId}`)
  }

  async updateBusinessProfile(profileId, profileData) {
    return await this.request(`/api/v1/generator/business-profiles/${profileId}`, {
      method: 'PUT',
      body: JSON.stringify(profileData)
    })
  }

  // Content Strategy methods
  async createContentStrategy(strategyData) {
    return await this.request('/api/v1/generator/content-strategies', {
      method: 'POST',
      body: JSON.stringify(strategyData)
    })
  }

  async getContentStrategies() {
    return await this.request('/api/v1/generator/content-strategies')
  }

  // Content Generation methods
  async generateContent(generationData) {
    return await this.request('/api/v1/generator/generate-content', {
      method: 'POST',
      body: JSON.stringify(generationData)
    })
  }

  async getCampaigns() {
    return await this.request('/api/v1/generator/campaigns')
  }

  async getCampaign(campaignId) {
    return await this.request(`/api/v1/generator/campaigns/${campaignId}`)
  }

  // Content Approval methods
  async approveContent(contentId, action, feedback = null) {
    return await this.request('/api/v1/evaluation/approve-content', {
      method: 'POST',
      body: JSON.stringify({
        content_id: contentId,
        action: action, // 'approve', 'reject', 'thumbs_up', 'thumbs_down'
        feedback: feedback
      })
    })
  }

  async getContentFeedback(filters = {}) {
    const queryParams = new URLSearchParams(filters).toString()
    return await this.request(`/api/v1/evaluation/content-feedback?${queryParams}`)
  }

  async getRecommendations(businessProfileId) {
    return await this.request(`/api/v1/evaluation/recommendations/${businessProfileId}`)
  }

  // Analytics methods
  async getAnalytics(dateRange = '30d') {
    return await this.request(`/api/v1/analytics/dashboard?range=${dateRange}`)
  }

  async getPlatformAnalytics(platform, dateRange = '30d') {
    return await this.request(`/api/v1/analytics/platform/${platform}?range=${dateRange}`)
  }

  async getContentPerformance(contentId) {
    return await this.request(`/api/v1/analytics/content/${contentId}`)
  }

  // Payment methods
  async getSubscriptionPlans() {
    return await this.request('/api/v1/payments/plans')
  }

  async createSubscription(planId, paymentMethodId) {
    return await this.request('/api/v1/payments/subscribe', {
      method: 'POST',
      body: JSON.stringify({
        plan_id: planId,
        payment_method_id: paymentMethodId
      })
    })
  }

  async getSubscriptionStatus() {
    return await this.request('/api/v1/payments/subscription')
  }

  async cancelSubscription() {
    return await this.request('/api/v1/payments/cancel', {
      method: 'POST'
    })
  }

  async updatePaymentMethod(paymentMethodId) {
    return await this.request('/api/v1/payments/payment-method', {
      method: 'PUT',
      body: JSON.stringify({ payment_method_id: paymentMethodId })
    })
  }

  // Social Media OAuth methods
  async getSocialMediaConnections() {
    return await this.request('/api/v1/social/connections')
  }

  async initiateSocialAuth(platform) {
    return await this.request(`/api/v1/social/auth/${platform}/initiate`, {
      method: 'POST'
    })
  }

  async completeSocialAuth(platform, code, state) {
    return await this.request(`/api/v1/social/auth/${platform}/callback`, {
      method: 'POST',
      body: JSON.stringify({ code, state })
    })
  }

  async disconnectSocialAccount(platform) {
    return await this.request(`/api/v1/social/connections/${platform}`, {
      method: 'DELETE'
    })
  }

  async getSocialAccountInfo(platform) {
    return await this.request(`/api/v1/social/connections/${platform}`)
  }

  // Team Leader methods
  async getTeamOverview() {
    return await this.request('/api/v1/team-leader/overview')
  }

  async getCampaignStatus(campaignId) {
    return await this.request(`/api/v1/team-leader/campaigns/${campaignId}/status`)
  }

  async generateWeeklyReport(dateRange) {
    return await this.request('/api/v1/team-leader/reports/weekly', {
      method: 'POST',
      body: JSON.stringify({ date_range: dateRange })
    })
  }

  // Platform Agent methods
  async getPlatformAgentStatus(platform) {
    return await this.request(`/api/v1/platforms/${platform}/status`)
  }

  async configurePlatformAgent(platform, config) {
    return await this.request(`/api/v1/platforms/${platform}/configure`, {
      method: 'POST',
      body: JSON.stringify(config)
    })
  }

  async schedulePost(platform, postData) {
    return await this.request(`/api/v1/platforms/${platform}/schedule`, {
      method: 'POST',
      body: JSON.stringify(postData)
    })
  }

  async getScheduledPosts(platform) {
    return await this.request(`/api/v1/platforms/${platform}/scheduled`)
  }

  // External API methods
  async createWebhook(webhookData) {
    return await this.request('/api/v1/external/webhooks', {
      method: 'POST',
      body: JSON.stringify(webhookData)
    })
  }

  async getWebhooks() {
    return await this.request('/api/v1/external/webhooks')
  }

  async sendNotification(notificationData) {
    return await this.request('/api/v1/external/notifications', {
      method: 'POST',
      body: JSON.stringify(notificationData)
    })
  }

  async exportData(exportType, filters = {}) {
    return await this.request('/api/v1/external/export', {
      method: 'POST',
      body: JSON.stringify({
        type: exportType,
        filters: filters
      })
    })
  }

  // Admin methods
  async getTenantUsage() {
    return await this.request('/api/v1/admin/usage')
  }

  async updateTenantSettings(settings) {
    return await this.request('/api/v1/admin/settings', {
      method: 'PUT',
      body: JSON.stringify(settings)
    })
  }

  async getAPIKeys() {
    return await this.request('/api/v1/auth/api-keys')
  }

  async createAPIKey(keyData) {
    return await this.request('/api/v1/auth/api-keys', {
      method: 'POST',
      body: JSON.stringify(keyData)
    })
  }

  async revokeAPIKey(keyId) {
    return await this.request(`/api/v1/auth/api-keys/${keyId}`, {
      method: 'DELETE'
    })
  }

  // Utility methods
  setToken(token) {
    this.token = token
    localStorage.setItem('access_token', token)
  }

  clearToken() {
    this.token = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  isAuthenticated() {
    return !!this.token
  }
}

// Create and export a singleton instance
const apiService = new APIService()

export default apiService

// Export individual methods for convenience
export const {
  login,
  register,
  logout,
  getProfile,
  createBusinessProfile,
  getBusinessProfiles,
  generateContent,
  getCampaigns,
  approveContent,
  getAnalytics,
  getSubscriptionPlans,
  createSubscription,
  getSocialMediaConnections,
  initiateSocialAuth
} = apiService

