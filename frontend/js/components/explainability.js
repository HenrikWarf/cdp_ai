/**
 * Explainability Component
 * Shows why a segment was selected and feature importance
 */

import { formatPercentage } from '../utils/helpers.js';

export class ExplainabilityComponent {
    constructor(containerId = 'explainability-section') {
        this.container = document.getElementById(containerId);
    }

    render(explainability) {
        if (!this.container || !explainability) {
            console.warn('No explainability data to display');
            return;
        }

        this.container.innerHTML = '';

        // Main explanation text
        if (explainability.why_this_segment) {
            const explanationText = document.createElement('div');
            explanationText.className = 'explanation-text';
            explanationText.textContent = explainability.why_this_segment;
            this.container.appendChild(explanationText);
        }

        // Key factors section
        if (explainability.key_factors && explainability.key_factors.length > 0) {
            const factorsSection = this.createKeyFactorsSection(explainability.key_factors);
            this.container.appendChild(factorsSection);
        }

        // Confidence and sample size info
        const infoSection = this.createInfoSection(explainability);
        this.container.appendChild(infoSection);
    }

    createKeyFactorsSection(factors) {
        const section = document.createElement('div');
        section.className = 'key-factors';

        section.innerHTML = '<h4>Key Decision Factors</h4>';

        const factorList = document.createElement('div');
        factorList.className = 'factor-list';

        factors.forEach(factor => {
            factorList.appendChild(this.createFactorItem(factor));
        });

        section.appendChild(factorList);
        return section;
    }

    createFactorItem(factor) {
        const item = document.createElement('div');
        item.className = 'factor-item';

        const importancePercent = Math.round(factor.importance * 100);

        item.innerHTML = `
            <div class="factor-header">
                <span class="factor-name">${factor.feature}</span>
                <span class="factor-importance">${importancePercent}%</span>
            </div>
            <div class="factor-description">${factor.description}</div>
            <div class="factor-bar">
                <div class="factor-bar-fill" style="width: ${importancePercent}%"></div>
            </div>
        `;

        return item;
    }

    createInfoSection(explainability) {
        const section = document.createElement('div');
        section.className = 'info-section mt-lg';

        const confidenceBadge = explainability.confidence_level === 'high' 
            ? '<span class="coo-badge" style="background: var(--success-color)">High Confidence</span>'
            : '<span class="coo-badge" style="background: var(--warning-color)">Moderate Confidence</span>';

        section.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius-md);">
                <div>
                    <strong>Analysis Confidence:</strong> ${confidenceBadge}
                </div>
                <div style="text-align: right; color: var(--text-secondary);">
                    <small>Based on ${explainability.sample_size || 0} customer profiles</small>
                </div>
            </div>
        `;

        return section;
    }

    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

