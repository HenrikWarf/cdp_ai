/**
 * Campaign Input Component
 * Handles the campaign objective input interface
 */

import { showToast } from '../utils/helpers.js';

export class CampaignInputComponent {
    constructor() {
        this.inputElement = document.getElementById('campaign-objective');
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.exampleChips = document.querySelectorAll('.chip[data-example]');
        
        this.onAnalyzeCallback = null;
        
        this.init();
    }

    init() {
        // Analyze button click
        this.analyzeBtn.addEventListener('click', () => this.handleAnalyze());
        
        // Clear button click
        this.clearBtn.addEventListener('click', () => this.clear());
        
        // Example chips
        this.exampleChips.forEach(chip => {
            chip.addEventListener('click', () => {
                const example = chip.getAttribute('data-example');
                this.setExample(example);
            });
        });
        
        // Enter key to analyze (Ctrl+Enter)
        this.inputElement.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.handleAnalyze();
            }
        });
    }

    setExample(exampleType) {
        const examples = {
            cart: "Increase conversion for abandoned carts by 20% within 48 hours with a personalized discount offer for high-value shoppers",
            retention: "Re-engage lapsed customers who haven't purchased in 60 days with exclusive early access to new products",
            upsell: "Drive premium tier upgrades for active users with 30%+ engagement using limited-time exclusive features",
            winback: "Win back churned customers from the past 90 days with a compelling 25% discount and free shipping offer"
        };

        const text = examples[exampleType];
        if (text) {
            this.inputElement.value = text;
            this.inputElement.focus();
            showToast('Example loaded! Click "Analyze Campaign" to continue.', 'info');
        }
    }

    getValue() {
        return this.inputElement.value.trim();
    }

    setValue(value) {
        this.inputElement.value = value;
    }

    clear() {
        this.inputElement.value = '';
        this.inputElement.focus();
    }

    handleAnalyze() {
        const value = this.getValue();
        
        if (!value) {
            showToast('Please enter a campaign objective', 'warning');
            this.inputElement.focus();
            return;
        }

        if (value.length < 20) {
            showToast('Please provide a more detailed campaign objective (at least 20 characters)', 'warning');
            return;
        }

        // Call the callback if set
        if (this.onAnalyzeCallback) {
            this.onAnalyzeCallback(value);
        }
    }

    setLoading(isLoading) {
        if (isLoading) {
            this.analyzeBtn.disabled = true;
            this.inputElement.disabled = true;
            this.analyzeBtn.querySelector('.btn-text').style.display = 'none';
            this.analyzeBtn.querySelector('.btn-loader').style.display = 'flex';
        } else {
            this.analyzeBtn.disabled = false;
            this.inputElement.disabled = false;
            this.analyzeBtn.querySelector('.btn-text').style.display = 'inline';
            this.analyzeBtn.querySelector('.btn-loader').style.display = 'none';
        }
    }

    onAnalyze(callback) {
        this.onAnalyzeCallback = callback;
    }
}

