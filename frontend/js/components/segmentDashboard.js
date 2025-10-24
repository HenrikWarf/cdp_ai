/**
 * Segment Dashboard Component
 * Displays segment metrics and overview
 */

import { formatNumber, formatCurrency, formatPercentage } from '../utils/helpers.js';

export class SegmentDashboardComponent {
    constructor(containerId = 'segment-dashboard') {
        this.defaultContainer = document.getElementById(containerId);
    }

    render(metadata, coo = null, container = null) {
        // Use provided container or fall back to default
        const targetContainer = container || this.defaultContainer;
        
        if (!targetContainer || !metadata) {
            console.warn('No metadata or container to display');
            return;
        }

        targetContainer.innerHTML = '';

        // Create stats grid
        const statsGrid = this.createStatsGrid(metadata);
        targetContainer.appendChild(statsGrid);

        // Create demographic breakdown if available
        if (metadata.demographic_breakdown && Object.keys(metadata.demographic_breakdown).length > 0) {
            const demoSection = this.createDemographicSection(metadata.demographic_breakdown);
            targetContainer.appendChild(demoSection);
        }

        // Create product categories section if available
        if (metadata.common_product_categories && metadata.common_product_categories.length > 0) {
            const categoriesSection = this.createCategoriesSection(metadata.common_product_categories);
            targetContainer.appendChild(categoriesSection);
        }
    }

    createStatsGrid(metadata) {
        const grid = document.createElement('div');
        grid.className = 'segment-stats-grid';

        // Segment size
        grid.appendChild(this.createStatCard(
            'Segment Size',
            formatNumber(metadata.estimated_size),
            'customers',
            'primary'
        ));

        // Average CLV
        grid.appendChild(this.createStatCard(
            'Avg CLV Score',
            formatPercentage(metadata.avg_clv_score, 0),
            `${Math.round(metadata.avg_clv_score * 100)}th percentile`,
            'secondary'
        ));

        // Predicted Uplift
        grid.appendChild(this.createStatCard(
            'Predicted Uplift',
            formatPercentage(metadata.predicted_uplift, 1),
            'conversion increase',
            'success'
        ));

        // Predicted ROI
        grid.appendChild(this.createStatCard(
            'Predicted ROI',
            metadata.predicted_roi,
            'return on investment',
            'warning'
        ));

        // Average cart value if available
        if (metadata.avg_cart_value) {
            grid.appendChild(this.createStatCard(
                'Avg Cart Value',
                formatCurrency(metadata.avg_cart_value),
                'per customer',
                'success'
            ));
        }

        return grid;
    }

    createStatCard(label, value, subtitle, colorClass = 'primary') {
        const card = document.createElement('div');
        card.className = `stat-card ${colorClass}`;
        
        card.innerHTML = `
            <div class="stat-label">${label}</div>
            <div class="stat-value">${value}</div>
            <div class="stat-subtitle">${subtitle}</div>
        `;

        return card;
    }

    createDemographicSection(demographics) {
        const section = document.createElement('div');
        section.className = 'demographic-section';

        section.innerHTML = '<h4>Geographic Distribution</h4>';

        const list = document.createElement('div');
        list.className = 'demographic-list';

        // Handle all cities (sorted by count, descending)
        if (demographics.top_cities) {
            const cities = Array.isArray(demographics.top_cities) 
                ? demographics.top_cities 
                : Object.entries(demographics.top_cities)
                    .sort((a, b) => b[1] - a[1]); // Sort by count descending

            let totalCount = 0;
            cities.forEach(([city, count]) => {
                list.appendChild(this.createDemographicItem(city, count));
                totalCount += parseInt(count);
            });

            // Add total row
            if (cities.length > 1) {
                const totalItem = this.createDemographicItem('Total', totalCount);
                totalItem.classList.add('demographic-total');
                list.appendChild(totalItem);
            }
        }

        section.appendChild(list);
        return section;
    }

    createDemographicItem(label, value) {
        const item = document.createElement('div');
        item.className = 'demographic-item';

        item.innerHTML = `
            <span class="demographic-label">${label}</span>
            <span class="demographic-value">${formatNumber(value)}</span>
        `;

        return item;
    }

    createCategoriesSection(categories) {
        const section = document.createElement('div');
        section.className = 'categories-section';

        section.innerHTML = '<h4>Common Product Categories</h4>';

        const tags = document.createElement('div');
        tags.className = 'category-tags';

        categories.forEach(category => {
            const tag = document.createElement('div');
            tag.className = 'category-tag';
            tag.textContent = category;
            tags.appendChild(tag);
        });

        section.appendChild(tags);
        return section;
    }

    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

