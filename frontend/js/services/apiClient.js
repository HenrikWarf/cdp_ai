/**
 * API Client for communicating with the AetherSegment AI backend
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api/v1';

class ApiClient {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    /**
     * Make a fetch request with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            
            // Parse JSON response
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    /**
     * Analyze a campaign objective
     * POST /campaigns/analyze
     */
    async analyzeCampaign(objective) {
        return this.request('/campaigns/analyze', {
            method: 'POST',
            body: JSON.stringify({ objective })
        });
    }

    /**
     * Create a customer segment
     * POST /segments/create
     */
    async createSegment(campaignObjective, overrideTrigger = null, additionalFilters = null) {
        const body = { campaign_objective: campaignObjective };
        if (overrideTrigger) {
            body.override_trigger = overrideTrigger;
        }
        if (additionalFilters && Object.keys(additionalFilters).length > 0) {
            body.additional_filters = additionalFilters;
        }

        return this.request('/segments/create', {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }

    /**
     * Get customers for a segment
     * GET /segments/{segment_id}/customers
     */
    async getSegmentCustomers(segmentId, limit = null) {
        const params = limit ? `?limit=${limit}` : '';
        return this.request(`/segments/${segmentId}/customers${params}`);
    }

    /**
     * Get metadata for a segment
     * GET /segments/{segment_id}/metadata
     */
    async getSegmentMetadata(segmentId) {
        return this.request(`/segments/${segmentId}/metadata`);
    }

    /**
     * Get trigger suggestions
     * POST /triggers/suggestions
     */
    async getTriggerSuggestions(objective) {
        return this.request('/triggers/suggestions', {
            method: 'POST',
            body: JSON.stringify({ objective })
        });
    }

    /**
     * Preview filter impact on segment
     * POST /segments/preview-filters
     */
    async previewFilters(campaignObjectiveObject, newFilters) {
        return this.request('/segments/preview-filters', {
            method: 'POST',
            body: JSON.stringify({
                campaign_objective_object: campaignObjectiveObject,
                new_filters: newFilters
            })
        });
    }

    /**
     * Health check
     * GET /health
     */
    async healthCheck() {
        return this.request('/health');
    }
}

// Export a singleton instance
export const apiClient = new ApiClient();
export default ApiClient;

