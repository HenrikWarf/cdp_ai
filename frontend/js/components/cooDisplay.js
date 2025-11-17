/**
 * Campaign Objective Object (COO) Display Component
 * Shows the structured interpretation of the campaign objective
 */

import { formatPercentage } from '../utils/helpers.js';

export class CooDisplayComponent {
    constructor(containerId = 'coo-display') {
        this.container = document.getElementById(containerId);
    }

    render(coo) {
        if (!this.container || !coo) {
            console.warn('No COO data to display');
            return;
        }

        this.container.innerHTML = '';

        // Campaign Goal
        this.container.appendChild(this.createCooItem(
            'Campaign Goal',
            `<span class="coo-badge badge-primary">${this.formatValue(coo.campaign_goal)}</span>`
        ));

        // Target Behavior
        this.container.appendChild(this.createCooItem(
            'Target Behavior',
            `<span class="coo-badge badge-info">${this.formatValue(coo.target_behavior)}</span>`
        ));

        // Target Subgroup
        if (coo.target_subgroup) {
            this.container.appendChild(this.createCooItem(
                'Target Subgroup',
                `<span class="coo-badge badge-secondary">${this.formatValue(coo.target_subgroup)}</span>`
            ));
        }

        // Metric Target
        if (coo.metric_target) {
            const metricValue = coo.metric_target.value < 1 
                ? formatPercentage(coo.metric_target.value, 0)
                : coo.metric_target.value;
            
            this.container.appendChild(this.createCooItem(
                'Success Metric',
                `<span class="coo-badge badge-warning">${this.formatValue(coo.metric_target.type)}: ${metricValue}</span>`
            ));
        }

        // Time Constraint
        if (coo.time_constraint) {
            this.container.appendChild(this.createCooItem(
                'Time Constraint',
                `<span class="coo-badge badge-purple">${this.formatValue(coo.time_constraint)}</span>`
            ));
        }

        // Proposed Intervention (can be array or string)
        let interventionHtml = '';
        if (Array.isArray(coo.proposed_intervention)) {
            interventionHtml = coo.proposed_intervention.map(intervention => 
                `<span class="coo-badge badge-success">${this.formatValue(intervention)}</span>`
            ).join(' ');
        } else {
            interventionHtml = `<span class="coo-badge badge-success">${this.formatValue(coo.proposed_intervention)}</span>`;
        }
        
        this.container.appendChild(this.createCooItem(
            'Proposed Interventions',
            interventionHtml
        ));

        // Underlying Assumptions
        if (coo.underlying_assumptions && coo.underlying_assumptions.length > 0) {
            const tags = coo.underlying_assumptions.map(assumption => 
                `<span class="coo-tag">${this.formatValue(assumption)}</span>`
            ).join('');

            this.container.appendChild(this.createCooItem(
                'Underlying Assumptions',
                `<div class="coo-tags">${tags}</div>`
            ));
        }

        // Demographic Filters (NEW)
        if (coo.demographic_filters && Object.keys(coo.demographic_filters).length > 0) {
            const demo = coo.demographic_filters;
            let demoBadges = [];
            
            // Age range
            if (demo.age_min || demo.age_max) {
                const ageRange = demo.age_min && demo.age_max 
                    ? `${demo.age_min}-${demo.age_max}` 
                    : demo.age_min 
                        ? `${demo.age_min}+` 
                        : `up to ${demo.age_max}`;
                demoBadges.push(`<span class="coo-badge badge-info">Age: ${ageRange}</span>`);
            }
            
            // Gender
            if (demo.gender) {
                demoBadges.push(`<span class="coo-badge badge-info">Gender: ${demo.gender}</span>`);
            }
            
            // Income level
            if (demo.income_level) {
                demoBadges.push(`<span class="coo-badge badge-info">Income: ${this.formatValue(demo.income_level)}</span>`);
            }
            
            // Location
            if (demo.location_country) {
                demoBadges.push(`<span class="coo-badge badge-info">Country: ${demo.location_country}</span>`);
            }
            
            if (demo.location_city) {
                demoBadges.push(`<span class="coo-badge badge-info">City: ${demo.location_city}</span>`);
            }
            
            if (demoBadges.length > 0) {
                this.container.appendChild(this.createCooItem(
                    '🎯 Demographic Targeting',
                    demoBadges.join(' ')
                ));
            }
        }
    }

    createCooItem(label, value) {
        const item = document.createElement('div');
        item.className = 'coo-item';

        item.innerHTML = `
            <div class="coo-label">${label}:</div>
            <div class="coo-value">${value}</div>
        `;

        return item;
    }

    formatValue(value) {
        if (!value) return '-';
        
        // Convert snake_case to Title Case
        return value
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

