/**
 * Trigger Suggestions Component
 * Displays recommended triggers with rankings
 */

import { formatPercentage } from '../utils/helpers.js';

export class TriggerSuggestionsComponent {
    constructor(containerId = 'trigger-suggestions') {
        this.container = document.getElementById(containerId);
        this.selectedTrigger = null;
        this.onSelectCallback = null;
    }

    render(triggers) {
        if (!this.container || !triggers || triggers.length === 0) {
            console.warn('No triggers to display');
            return;
        }

        this.container.innerHTML = '';

        triggers.forEach((trigger, index) => {
            const card = this.createTriggerCard(trigger, index);
            this.container.appendChild(card);
        });

        // Auto-select the first (best) trigger
        if (triggers.length > 0) {
            this.selectTrigger(triggers[0].trigger_name);
        }
    }

    createTriggerCard(trigger, index) {
        const card = document.createElement('div');
        card.className = 'trigger-card';
        card.dataset.triggerName = trigger.trigger_name;

        // Rank badge (1st, 2nd, 3rd)
        const rankBadge = index === 0 ? '🥇 ' : index === 1 ? '🥈 ' : index === 2 ? '🥉 ' : '';

        card.innerHTML = `
            <div class="trigger-header">
                <div class="trigger-name">${rankBadge}${trigger.trigger_name}</div>
                <div class="trigger-category">${trigger.trigger_type}</div>
            </div>
            
            <div class="trigger-metrics">
                <div class="trigger-metric">
                    <div class="metric-label">Uplift</div>
                    <div class="metric-value">${formatPercentage(trigger.predicted_uplift, 1)}</div>
                </div>
                <div class="trigger-metric">
                    <div class="metric-label">Confidence</div>
                    <div class="metric-value">${formatPercentage(trigger.confidence_score, 0)}</div>
                </div>
            </div>
            
            <div class="trigger-description">${trigger.description}</div>
            
            <div class="trigger-rationale">${trigger.rationale}</div>
        `;

        // Click to select
        card.addEventListener('click', () => {
            this.selectTrigger(trigger.trigger_name);
            if (this.onSelectCallback) {
                this.onSelectCallback(trigger);
            }
        });

        return card;
    }

    selectTrigger(triggerName) {
        // Remove selected class from all cards
        this.container.querySelectorAll('.trigger-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Add selected class to the clicked card
        const selectedCard = this.container.querySelector(`[data-trigger-name="${triggerName}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
            this.selectedTrigger = triggerName;
        }
    }

    getSelectedTrigger() {
        return this.selectedTrigger;
    }

    onSelect(callback) {
        this.onSelectCallback = callback;
    }

    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.selectedTrigger = null;
    }
}

