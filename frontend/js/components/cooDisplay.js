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
            `<span class="coo-badge">${this.formatValue(coo.campaign_goal)}</span>`
        ));

        // Target Behavior
        this.container.appendChild(this.createCooItem(
            'Target Behavior',
            this.formatValue(coo.target_behavior)
        ));

        // Target Subgroup
        if (coo.target_subgroup) {
            this.container.appendChild(this.createCooItem(
                'Target Subgroup',
                `<span class="coo-badge" style="background: var(--secondary-color);">${this.formatValue(coo.target_subgroup)}</span>`
            ));
        }

        // Metric Target
        if (coo.metric_target) {
            const metricValue = coo.metric_target.value < 1 
                ? formatPercentage(coo.metric_target.value, 0)
                : coo.metric_target.value;
            
            this.container.appendChild(this.createCooItem(
                'Success Metric',
                `${this.formatValue(coo.metric_target.type)}: <strong>${metricValue}</strong>`
            ));
        }

        // Time Constraint
        if (coo.time_constraint) {
            this.container.appendChild(this.createCooItem(
                'Time Constraint',
                this.formatValue(coo.time_constraint)
            ));
        }

        // Proposed Intervention
        this.container.appendChild(this.createCooItem(
            'Proposed Intervention',
            `<span class="coo-badge" style="background: var(--success-color);">${this.formatValue(coo.proposed_intervention)}</span>`
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

