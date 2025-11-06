/**
 * Campaign Templates Component
 * Displays pre-defined campaign templates in accordion groups
 */

import { CAMPAIGN_TEMPLATES } from '../data/campaignTemplates.js';

export class CampaignTemplatesComponent {
    constructor(containerId = 'campaign-templates-container') {
        this.container = document.getElementById(containerId);
        this.onTemplateSelect = null; // Callback for when template is selected
        this.expandedAccordion = null; // Track which accordion is open
    }

    render() {
        if (!this.container) {
            console.warn('Campaign templates container not found');
            return;
        }

        this.container.innerHTML = '';

        // Create header
        const header = document.createElement('div');
        header.className = 'templates-header';
        header.innerHTML = `
            <h3>Choose a Campaign Template</h3>
            <p class="subtitle">Select a pre-built campaign to get started quickly</p>
        `;
        this.container.appendChild(header);

        // Create accordions container
        const accordionsContainer = document.createElement('div');
        accordionsContainer.className = 'campaign-accordions';

        // Render each campaign group as an accordion
        Object.entries(CAMPAIGN_TEMPLATES).forEach(([groupKey, group]) => {
            const accordion = this.createAccordion(groupKey, group);
            accordionsContainer.appendChild(accordion);
        });

        this.container.appendChild(accordionsContainer);
    }

    createAccordion(groupKey, group) {
        const accordion = document.createElement('div');
        accordion.className = 'campaign-accordion';
        accordion.dataset.group = groupKey;

        // Accordion header
        const header = document.createElement('div');
        header.className = 'accordion-header';
        header.innerHTML = `
            <div class="accordion-title">
                <span class="accordion-icon">▶</span>
                <span class="accordion-label">${group.title}</span>
                <span class="accordion-count">${group.campaigns.length} templates</span>
            </div>
        `;

        // Accordion content
        const content = document.createElement('div');
        content.className = 'accordion-content';
        content.style.display = 'none';

        // Create campaign cards
        group.campaigns.forEach(campaign => {
            const card = this.createCampaignCard(campaign);
            content.appendChild(card);
        });

        // Toggle accordion on header click
        header.addEventListener('click', () => {
            this.toggleAccordion(accordion, header, content);
        });

        accordion.appendChild(header);
        accordion.appendChild(content);

        return accordion;
    }

    createCampaignCard(campaign) {
        const card = document.createElement('div');
        card.className = 'campaign-card';
        card.innerHTML = `
            <div class="card-header">
                <h4 class="card-title">${campaign.title}</h4>
            </div>
            <p class="card-description">${campaign.description}</p>
            <div class="card-objective">
                <span class="objective-label">Campaign:</span>
                <span class="objective-text">${campaign.fullObjective}</span>
            </div>
            <button class="btn-use-template btn btn-primary btn-sm" data-campaign-id="${campaign.id}">
                Use This Template
            </button>
        `;

        // Add click handler for "Use Template" button
        const button = card.querySelector('.btn-use-template');
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectTemplate(campaign);
        });

        return card;
    }

    toggleAccordion(accordion, header, content) {
        const isOpen = content.style.display === 'block';
        const icon = header.querySelector('.accordion-icon');

        if (isOpen) {
            // Close this accordion
            content.style.display = 'none';
            icon.style.transform = 'rotate(0deg)';
            accordion.classList.remove('active');
            this.expandedAccordion = null;
        } else {
            // Close any other open accordion
            if (this.expandedAccordion) {
                const openContent = this.expandedAccordion.querySelector('.accordion-content');
                const openIcon = this.expandedAccordion.querySelector('.accordion-icon');
                openContent.style.display = 'none';
                openIcon.style.transform = 'rotate(0deg)';
                this.expandedAccordion.classList.remove('active');
            }

            // Open this accordion
            content.style.display = 'block';
            icon.style.transform = 'rotate(90deg)';
            accordion.classList.add('active');
            this.expandedAccordion = accordion;
        }
    }

    selectTemplate(campaign) {
        console.log('Template selected:', campaign.title);
        
        // Call the callback if provided
        if (this.onTemplateSelect && typeof this.onTemplateSelect === 'function') {
            this.onTemplateSelect(campaign.fullObjective, campaign.title);
        }
    }

    setOnTemplateSelect(callback) {
        this.onTemplateSelect = callback;
    }

    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.expandedAccordion = null;
    }
}




