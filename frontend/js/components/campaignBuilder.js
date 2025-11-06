/**
 * Campaign Builder Component
 * Progressive disclosure builder: Goal → Trigger → Product
 */

import { BUILDER_CONFIG } from '../data/campaignTemplates.js';

export class CampaignBuilderComponent {
    constructor(containerId = 'campaign-builder-container') {
        this.container = document.getElementById(containerId);
        this.onCampaignGenerate = null; // Callback for when campaign is generated
        
        // Builder state
        this.selectedGoal = null;
        this.selectedTrigger = null;
        this.selectedProduct = null;
    }

    render() {
        if (!this.container) {
            console.warn('Campaign builder container not found');
            return;
        }

        this.container.innerHTML = '';

        // Create header
        const header = document.createElement('div');
        header.className = 'builder-header';
        header.innerHTML = `
            <h3>Build Your Custom Campaign</h3>
            <p class="subtitle">Follow the steps to create a tailored campaign objective</p>
        `;
        this.container.appendChild(header);

        // Create steps container
        const stepsContainer = document.createElement('div');
        stepsContainer.className = 'builder-steps';

        // Step 1: Goal (always visible)
        const step1 = this.createStep(1, 'Select Your Goal', true);
        const goalSelect = this.createDropdown('goal', BUILDER_CONFIG.goals, 'Choose campaign goal...', true);
        step1.appendChild(goalSelect);
        stepsContainer.appendChild(step1);

        // Step 2: Trigger (hidden initially)
        const step2 = this.createStep(2, 'Choose Your Trigger', false);
        const triggerSelect = this.createDropdown('trigger', BUILDER_CONFIG.triggers, 'Choose trigger type...', false);
        step2.appendChild(triggerSelect);
        stepsContainer.appendChild(step2);

        // Step 3: Product Category (hidden initially)
        const step3 = this.createStep(3, 'Select Product Category', false);
        const productSelect = this.createDropdown('product', BUILDER_CONFIG.productCategories, 'Choose product category...', false);
        step3.appendChild(productSelect);
        stepsContainer.appendChild(step3);

        this.container.appendChild(stepsContainer);

        // Action buttons container
        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'builder-actions';

        // Clear button
        const clearBtn = document.createElement('button');
        clearBtn.id = 'clear-builder-btn';
        clearBtn.className = 'btn btn-outline';
        clearBtn.innerHTML = 'Clear Selection';
        clearBtn.addEventListener('click', () => this.reset());
        actionsContainer.appendChild(clearBtn);

        // Generate button (disabled initially)
        const generateBtn = document.createElement('button');
        generateBtn.id = 'generate-campaign-btn';
        generateBtn.className = 'btn btn-primary';
        generateBtn.disabled = true;
        generateBtn.innerHTML = 'Generate Campaign Objective';
        generateBtn.addEventListener('click', () => this.generateCampaign());
        actionsContainer.appendChild(generateBtn);

        this.container.appendChild(actionsContainer);

        // Add event listeners
        this.attachEventListeners();
    }

    createStep(stepNumber, title, isVisible) {
        const step = document.createElement('div');
        step.className = `builder-step ${isVisible ? 'visible' : 'hidden'}`;
        step.dataset.step = stepNumber;
        step.innerHTML = `
            <div class="step-header">
                <span class="step-number">${stepNumber}</span>
                <span class="step-title">${title}</span>
            </div>
        `;
        return step;
    }

    createDropdown(type, options, placeholder, isEnabled) {
        const wrapper = document.createElement('div');
        wrapper.className = 'dropdown-wrapper';

        const select = document.createElement('select');
        select.id = `builder-${type}`;
        select.className = 'builder-select';
        select.disabled = !isEnabled;

        // Add placeholder option
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder;
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        select.appendChild(placeholderOption);

        // Add options
        options.forEach(option => {
            const optionEl = document.createElement('option');
            optionEl.value = option.value;
            optionEl.textContent = option.label;
            optionEl.dataset.description = option.description || option.examples || '';
            select.appendChild(optionEl);
        });

        wrapper.appendChild(select);

        // Add description display
        const description = document.createElement('div');
        description.className = 'dropdown-description';
        description.style.display = 'none';
        wrapper.appendChild(description);

        return wrapper;
    }

    attachEventListeners() {
        // Goal selection
        const goalSelect = document.getElementById('builder-goal');
        if (goalSelect) {
            goalSelect.addEventListener('change', (e) => {
                this.selectedGoal = e.target.value;
                this.showDescription('goal', e.target.selectedOptions[0].dataset.description);
                this.revealNextStep(2);
                this.updateGenerateButton();
            });
        }

        // Trigger selection
        const triggerSelect = document.getElementById('builder-trigger');
        if (triggerSelect) {
            triggerSelect.addEventListener('change', (e) => {
                this.selectedTrigger = e.target.value;
                this.showDescription('trigger', e.target.selectedOptions[0].dataset.description);
                this.revealNextStep(3);
                this.updateGenerateButton();
            });
        }

        // Product selection
        const productSelect = document.getElementById('builder-product');
        if (productSelect) {
            productSelect.addEventListener('change', (e) => {
                this.selectedProduct = e.target.value;
                this.showDescription('product', e.target.selectedOptions[0].dataset.description);
                this.updateGenerateButton();
            });
        }
    }

    showDescription(type, description) {
        const select = document.getElementById(`builder-${type}`);
        if (select) {
            const wrapper = select.parentElement;
            const descEl = wrapper.querySelector('.dropdown-description');
            if (descEl && description) {
                descEl.textContent = description;
                descEl.style.display = 'block';
            }
        }
    }

    revealNextStep(stepNumber) {
        const step = this.container.querySelector(`[data-step="${stepNumber}"]`);
        if (step) {
            step.classList.remove('hidden');
            step.classList.add('visible');
            
            // Enable the dropdown in this step
            const select = step.querySelector('select');
            if (select) {
                select.disabled = false;
            }
        }
    }

    updateGenerateButton() {
        const generateBtn = document.getElementById('generate-campaign-btn');
        if (generateBtn) {
            const allSelected = this.selectedGoal && this.selectedTrigger && this.selectedProduct;
            generateBtn.disabled = !allSelected;
        }
    }

    generateCampaign() {
        if (!this.selectedGoal || !this.selectedTrigger || !this.selectedProduct) {
            console.warn('Cannot generate campaign: missing selections');
            return;
        }

        // Get labels for better readability
        const goalLabel = this.getSelectedLabel('goal');
        const triggerLabel = this.getSelectedLabel('trigger');
        const productLabel = this.getSelectedLabel('product');

        // Generate campaign objective using template
        const objective = BUILDER_CONFIG.generateObjective(
            this.selectedGoal,
            triggerLabel,
            productLabel
        );

        console.log('Campaign generated:', objective);

        // Call the callback if provided
        if (this.onCampaignGenerate && typeof this.onCampaignGenerate === 'function') {
            this.onCampaignGenerate(objective, `Custom: ${goalLabel} - ${productLabel}`);
        }
    }

    getSelectedLabel(type) {
        const select = document.getElementById(`builder-${type}`);
        if (select && select.selectedOptions.length > 0) {
            return select.selectedOptions[0].textContent;
        }
        return '';
    }

    setOnCampaignGenerate(callback) {
        this.onCampaignGenerate = callback;
    }

    reset() {
        this.selectedGoal = null;
        this.selectedTrigger = null;
        this.selectedProduct = null;
        this.render();
    }

    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.selectedGoal = null;
        this.selectedTrigger = null;
        this.selectedProduct = null;
    }
}

