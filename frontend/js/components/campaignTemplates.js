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
        
        // Get group icon
        const groupIcons = {
            'abandoned_cart': '🛒',
            'winback': '🔄',
            'cross_sell': '🔀',
            'new_customer': '👋',
            'vip_highvalue': '⭐',
            'product_specific': '🏠'
        };
        const groupIcon = groupIcons[groupKey] || '📋';

        // Accordion header
        const header = document.createElement('div');
        header.className = 'accordion-header';
        header.innerHTML = `
            <div class="accordion-title">
                <span class="accordion-icon">▶</span>
                <span class="accordion-group-icon">${groupIcon}</span>
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
        
        // Get campaign metadata (icon, badges, etc.)
        const metadata = this.getCampaignMetadata(campaign);
        
        card.innerHTML = `
            <div class="card-left">
                <div class="card-metrics-compact">
                    <div class="metric-compact">
                        <span class="metric-icon">📈</span>
                        <span class="metric-value">${metadata.uplift}</span>
                    </div>
                    <div class="metric-compact">
                        <span class="metric-icon">⚡</span>
                        <span class="metric-value">${metadata.difficulty}</span>
                    </div>
                    <div class="metric-compact">
                        <span class="metric-icon">🎯</span>
                        <span class="metric-value">${metadata.targetSize}</span>
                    </div>
                </div>
            </div>
            
            <div class="card-content">
                <div class="card-header-compact">
                    <h4 class="card-title">${campaign.title}</h4>
                    <div class="card-badges">${metadata.badges}</div>
                </div>
                <p class="card-description">${campaign.description}</p>
                <div class="card-objective-compact">
                    <strong>Goal:</strong> ${campaign.fullObjective}
                </div>
            </div>
            
            <div class="card-action">
                <button class="btn-use-template btn btn-primary btn-sm" data-campaign-id="${campaign.id}">
                    Use Template
                </button>
            </div>
        `;

        // Add click handler for "Use Template" button
        const button = card.querySelector('.btn-use-template');
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectTemplate(campaign);
        });

        return card;
    }
    
    getCampaignMetadata(campaign) {
        // Define metadata for different campaign types
        const metadata = {
            // Abandoned Cart campaigns
            'cart_discount': { icon: '🛒', uplift: '20-25%', difficulty: 'Easy', targetSize: 'Medium', badges: '<span class="card-badge badge-conversion">Conversion</span>' },
            'cart_shipping': { icon: '🛒', uplift: '25-30%', difficulty: 'Easy', targetSize: 'Small', badges: '<span class="card-badge badge-conversion">Conversion</span><span class="card-badge badge-highvalue">High-Value</span>' },
            'cart_urgency': { icon: '🛒', uplift: '15-20%', difficulty: 'Medium', targetSize: 'Medium', badges: '<span class="card-badge badge-conversion">Conversion</span><span class="card-badge badge-urgency">Urgency</span>' },
            
            // Win-back campaigns
            'winback_exclusive': { icon: '🔄', uplift: '12-15%', difficulty: 'Medium', targetSize: 'Large', badges: '<span class="card-badge badge-retention">Retention</span>' },
            'winback_new_products': { icon: '🔄', uplift: '10-12%', difficulty: 'Medium', targetSize: 'Large', badges: '<span class="card-badge badge-retention">Retention</span><span class="card-badge badge-content">Content</span>' },
            'winback_vip': { icon: '🔄', uplift: '20-25%', difficulty: 'Hard', targetSize: 'Small', badges: '<span class="card-badge badge-retention">Retention</span><span class="card-badge badge-highvalue">VIP</span>' },
            
            // Cross-sell campaigns
            'crosssell_complementary': { icon: '🔀', uplift: '18-20%', difficulty: 'Easy', targetSize: 'Medium', badges: '<span class="card-badge badge-revenue">Revenue</span><span class="card-badge badge-product">Product</span>' },
            'crosssell_category': { icon: '🔀', uplift: '20-25%', difficulty: 'Medium', targetSize: 'Medium', badges: '<span class="card-badge badge-revenue">Revenue</span><span class="card-badge badge-product">Product</span>' },
            'crosssell_bundle': { icon: '🔀', uplift: '25-30%', difficulty: 'Medium', targetSize: 'Large', badges: '<span class="card-badge badge-revenue">Revenue</span><span class="card-badge badge-bundle">Bundle</span>' },
            
            // New customer campaigns
            'welcome_discount': { icon: '👋', uplift: '25-30%', difficulty: 'Easy', targetSize: 'Medium', badges: '<span class="card-badge badge-acquisition">Acquisition</span>' },
            'onboarding_content': { icon: '👋', uplift: '30-40%', difficulty: 'Hard', targetSize: 'Medium', badges: '<span class="card-badge badge-acquisition">Acquisition</span><span class="card-badge badge-content">Content</span>' },
            'early_loyalty': { icon: '👋', uplift: '20-25%', difficulty: 'Easy', targetSize: 'Small', badges: '<span class="card-badge badge-acquisition">Acquisition</span><span class="card-badge badge-loyalty">Loyalty</span>' },
            
            // VIP/High-value campaigns
            'vip_launch': { icon: '⭐', uplift: '15-20%', difficulty: 'Medium', targetSize: 'Small', badges: '<span class="card-badge badge-highvalue">VIP</span><span class="card-badge badge-product">Product Launch</span>' },
            'vip_retention': { icon: '⭐', uplift: '25-30%', difficulty: 'Hard', targetSize: 'Small', badges: '<span class="card-badge badge-highvalue">VIP</span><span class="card-badge badge-loyalty">Loyalty</span>' },
            'vip_sale_access': { icon: '⭐', uplift: '30-35%', difficulty: 'Medium', targetSize: 'Small', badges: '<span class="card-badge badge-highvalue">VIP</span><span class="card-badge badge-urgency">Exclusive</span>' },
            
            // Product-specific campaigns
            'living_room_cross_sell': { icon: '🛋️', uplift: '25-30%', difficulty: 'Medium', targetSize: 'Medium', badges: '<span class="card-badge badge-product">Living Room</span><span class="card-badge badge-revenue">Cross-Sell</span>' },
            'bedroom_collection': { icon: '🛏️', uplift: '20-25%', difficulty: 'Medium', targetSize: 'Medium', badges: '<span class="card-badge badge-product">Bedroom</span><span class="card-badge badge-bundle">Bundle</span>' },
            'office_wfh': { icon: '💼', uplift: '15-20%', difficulty: 'Hard', targetSize: 'Large', badges: '<span class="card-badge badge-product">Office</span><span class="card-badge badge-content">WFH</span>' },
            'seasonal_outdoor': { icon: '🌳', uplift: '20-25%', difficulty: 'Medium', targetSize: 'Medium', badges: '<span class="card-badge badge-product">Outdoor</span><span class="card-badge badge-seasonal">Seasonal</span>' },
            'lighting_refresh': { icon: '💡', uplift: '25-30%', difficulty: 'Easy', targetSize: 'Large', badges: '<span class="card-badge badge-product">Lighting</span><span class="card-badge badge-revenue">Cross-Sell</span>' }
        };
        
        // Return metadata or defaults
        return metadata[campaign.id] || { 
            icon: '📋', 
            uplift: '15-20%', 
            difficulty: 'Medium', 
            targetSize: 'Medium',
            badges: '<span class="card-badge badge-general">General</span>'
        };
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




