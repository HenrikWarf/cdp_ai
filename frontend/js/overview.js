/**
 * Overview Dashboard - Main Application Logic
 */

import { apiClient } from './services/apiClient.js';
import { formatNumber, formatPercentage, formatCurrency } from './utils/helpers.js';

class OverviewDashboard {
    constructor() {
        this.stats = null;
        this.init();
    }

    async init() {
        console.log('Initializing Overview Dashboard...');
        
        // Setup refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.handleRefresh());
        }
        
        await this.loadStats();
        this.render();
    }

    async loadStats(forceRefresh = false) {
        try {
            console.log(forceRefresh ? 'Refreshing overview stats...' : 'Loading overview stats...');
            this.stats = await apiClient.getOverviewStats(forceRefresh);
            console.log('Stats loaded:', this.stats);
            
            // Update last updated display
            this.updateLastUpdated();
            
            // Show refresh button now that we have data
            const refreshBtn = document.getElementById('refresh-btn');
            if (refreshBtn) {
                refreshBtn.style.display = 'inline-flex';
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    async handleRefresh() {
        const refreshBtn = document.getElementById('refresh-btn');
        const originalText = refreshBtn.innerHTML;
        
        try {
            // Show loading state
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<span class="spinner"></span> Refreshing...';
            
            // Force refresh from backend
            await this.loadStats(true);
            this.render();
            
            // Show success feedback
            refreshBtn.innerHTML = '✓ Refreshed';
            setTimeout(() => {
                refreshBtn.innerHTML = originalText;
            }, 2000);
        } catch (error) {
            console.error('Refresh failed:', error);
            refreshBtn.innerHTML = '✗ Failed';
            setTimeout(() => {
                refreshBtn.innerHTML = originalText;
            }, 2000);
        } finally {
            refreshBtn.disabled = false;
        }
    }
    
    updateLastUpdated() {
        const lastUpdatedEl = document.getElementById('last-updated');
        if (!lastUpdatedEl || !this.stats) return;
        
        const lastUpdated = this.stats.last_updated;
        const cached = this.stats.cached;
        
        if (lastUpdated) {
            const date = new Date(lastUpdated);
            const timeAgo = this.formatTimeAgo(date);
            const cacheIndicator = cached ? ' (cached)' : ' (fresh)';
            
            lastUpdatedEl.innerHTML = `
                <span style="opacity: 0.7;">Last updated:</span> 
                <strong>${timeAgo}</strong>
                <span style="opacity: 0.6; font-size: var(--text-xs);">${cacheIndicator}</span>
            `;
        }
    }
    
    formatTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        
        if (diffSecs < 60) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return date.toLocaleDateString();
    }

    render() {
        if (!this.stats) {
            return;
        }

        this.renderMetrics();
        this.renderGeoChart();
        this.renderValueChart();
        this.renderOpportunities();
        this.renderBehavioralInsights();
        this.renderDataHealth();
    }

    renderMetrics() {
        const metrics = this.stats.metrics;

        // Total Customers
        const totalCustomersEl = document.getElementById('total-customers');
        if (totalCustomersEl) {
            totalCustomersEl.textContent = formatNumber(metrics.total_customers);
        }

        // Abandoned Carts
        const abandonedCartsEl = document.getElementById('abandoned-carts');
        if (abandonedCartsEl) {
            abandonedCartsEl.textContent = formatNumber(metrics.abandoned_carts_7d);
        }

        // Average CLV
        const avgClvEl = document.getElementById('avg-clv');
        if (avgClvEl) {
            avgClvEl.textContent = formatPercentage(metrics.avg_clv_score, 0);
        }

        // At-Risk Customers
        const atRiskEl = document.getElementById('at-risk-customers');
        if (atRiskEl) {
            atRiskEl.textContent = formatNumber(metrics.at_risk_customers);
        }
    }

    renderGeoChart() {
        const container = document.getElementById('geo-chart');
        if (!container || !this.stats.geographic_distribution) {
            return;
        }

        const geoData = this.stats.geographic_distribution;
        console.log('🌍 Geographic Distribution Data:', geoData);
        console.log('🌍 Keys:', Object.keys(geoData));
        const total = Object.values(geoData).reduce((sum, val) => sum + val, 0);

        // Sort by count descending and take top 5
        const sortedGeo = Object.entries(geoData)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5);
        
        console.log('🌍 Sorted Geo (top 5):', sortedGeo);

        // Create scrollable container with top 5
        const chartHTML = sortedGeo.map(([location, count]) => {
            const percentage = (count / total) * 100;
            console.log(`🌍 Rendering: ${location} - ${count} (${percentage.toFixed(1)}%)`);
            return `
                <div class="chart-bar">
                    <div class="chart-label">${location}</div>
                    <div class="chart-bar-bg">
                        <div class="chart-bar-fill" style="width: ${percentage}%">
                            <span class="chart-bar-value">${formatNumber(count)}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        // Show "Top 5" indicator if there are more countries
        const totalCountries = Object.keys(geoData).length;
        const topIndicator = totalCountries > 5 
            ? `<div class="chart-footer">Showing top 5 of ${totalCountries} countries</div>` 
            : '';

        console.log('🌍 Setting container.innerHTML with', totalCountries, 'countries');
        console.log('🌍 Chart HTML length:', chartHTML.length);
        
        container.innerHTML = `
            <div class="chart-scroll-container">
                ${chartHTML}
            </div>
            ${topIndicator}
        `;
        
        console.log('🌍 Render complete! Container innerHTML set.');
    }

    renderValueChart() {
        const container = document.getElementById('value-chart');
        if (!container || !this.stats.value_segments) {
            return;
        }

        const segments = this.stats.value_segments;
        const total = Object.values(segments).reduce((sum, val) => sum + val, 0);

        // Define order and labels
        const segmentOrder = [
            { key: 'high', label: 'High Value (≥75%)', color: '#00A86B' },
            { key: 'medium', label: 'Medium Value (50-75%)', color: '#0066CC' },
            { key: 'low', label: 'Low Value (<50%)', color: '#94A3B8' }
        ];

        container.innerHTML = segmentOrder.map(({ key, label, color }) => {
            const count = segments[key] || 0;
            const percentage = (count / total) * 100;
            return `
                <div class="chart-bar">
                    <div class="chart-label">${label}</div>
                    <div class="chart-bar-bg">
                        <div class="chart-bar-fill" style="width: ${percentage}%; background: ${color}">
                            <span class="chart-bar-value">${formatNumber(count)}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderOpportunities() {
        const container = document.getElementById('opportunities-list');
        if (!container || !this.stats.opportunities) {
            return;
        }

        const opportunities = this.stats.opportunities;

        container.innerHTML = opportunities.map(opp => `
            <div class="opportunity-item">
                <div class="opportunity-icon">${opp.icon}</div>
                <div class="opportunity-content">
                    <div class="opportunity-title">${opp.title}</div>
                    <div class="opportunity-description">${opp.description}</div>
                    <div class="opportunity-stats">
                        <div class="opportunity-stat">
                            <span>👥</span>
                            <span>${formatNumber(opp.segment_size)} customers</span>
                        </div>
                        <div class="opportunity-stat">
                            <span>📈</span>
                            <span>${formatPercentage(opp.potential_uplift, 0)} potential uplift</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderBehavioralInsights() {
        const container = document.getElementById('behavioral-insights');
        if (!container || !this.stats.behavioral_insights) {
            return;
        }

        const insights = this.stats.behavioral_insights;

        container.innerHTML = insights.map(insight => `
            <div class="insight-item">
                <div class="insight-icon">${insight.icon}</div>
                <div class="insight-content">
                    <div class="insight-title">${insight.label}</div>
                    <div class="insight-value">${insight.value}</div>
                    <div class="insight-description">${insight.description}</div>
                </div>
            </div>
        `).join('');
    }

    renderDataHealth() {
        const container = document.getElementById('data-health');
        if (!container || !this.stats.data_health) {
            return;
        }

        const health = this.stats.data_health;

        container.innerHTML = `
            <div class="data-health-item">
                <div class="data-health-label">Total Events</div>
                <div class="data-health-value">${formatNumber(health.total_events)}</div>
                <span class="data-health-status healthy">✓ Active</span>
            </div>
            <div class="data-health-item">
                <div class="data-health-label">Latest Event</div>
                <div class="data-health-value">${this.formatDate(health.latest_event)}</div>
                <span class="data-health-status healthy">✓ Real-time</span>
            </div>
            <div class="data-health-item">
                <div class="data-health-label">Data Freshness</div>
                <div class="data-health-value">${health.data_freshness}</div>
                <span class="data-health-status healthy">✓ Fresh</span>
            </div>
            <div class="data-health-item">
                <div class="data-health-label">Customer Coverage</div>
                <div class="data-health-value">${formatPercentage(health.customer_coverage, 0)}</div>
                <span class="data-health-status healthy">✓ Complete</span>
            </div>
        `;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else if (diffDays < 7) {
            return `${diffDays}d ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    showError(message) {
        console.error(message);
        // You could show a toast notification here
    }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new OverviewDashboard();
    });
} else {
    new OverviewDashboard();
}

