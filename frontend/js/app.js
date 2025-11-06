/**
 * AetherSegment AI - Main Application
 * Orchestrates all components and manages application state
 */

import { apiClient } from './services/apiClient.js';
import { CampaignInputComponent } from './components/campaignInput.js';
import { CooDisplayComponent } from './components/cooDisplay.js';
import { TriggerSuggestionsComponent } from './components/triggerSuggestions.js';
import { SegmentDashboardComponent } from './components/segmentDashboard.js';
import { ExplainabilityComponent } from './components/explainability.js';
import { CampaignTemplatesComponent } from './components/campaignTemplates.js';
import { CampaignBuilderComponent } from './components/campaignBuilder.js';
import {
    showToast,
    scrollToElement,
    formatCurrency,
    formatNumber,
    copyToClipboard,
    downloadJSON,
    downloadCSV
} from './utils/helpers.js';

class AetherSegmentApp {
    constructor() {
        // Components
        this.campaignInput = new CampaignInputComponent();
        this.cooDisplay = new CooDisplayComponent();
        this.triggerSuggestions = new TriggerSuggestionsComponent();
        this.segmentDashboard = new SegmentDashboardComponent();
        this.explainability = new ExplainabilityComponent();
        this.campaignTemplates = new CampaignTemplatesComponent();
        this.campaignBuilder = new CampaignBuilderComponent();

        // State
        this.currentCampaignObjective = null;
        this.currentAnalysis = null;
        this.currentSegment = null;
        this.selectedTrigger = null;  // NEW: Track selected trigger
        this.currentSegmentMetadata = null;  // NEW: Track updated segment metadata after trigger selection
        this.appliedFilters = {};
        this.currentCampaignMode = 'templates'; // Track which mode is active

        // Section elements
        this.campaignInputSection = document.getElementById('campaign-input-section');
        this.analysisResultsSection = document.getElementById('analysis-results-section');
        this.refineSegmentSection = document.getElementById('refine-segment-section');
        this.activateSegmentSection = document.getElementById('activate-segment-section');
        this.segmentDetailsSection = document.getElementById('segment-details-section');

        this.init();
    }

    init() {
        console.log('Initializing AetherSegment AI...');

        // Initialize campaign templates and builder
        this.initializeCampaignSelector();

        // Setup campaign input handler
        this.campaignInput.onAnalyze((objective) => {
            this.analyzeCampaign(objective);
        });

        // Setup trigger selection handler
        this.triggerSuggestions.onSelect((trigger) => {
            console.log('Trigger selected:', trigger);
            this.handleTriggerSelection(trigger);
        });

        // Setup action buttons
        this.setupActionButtons();

        // Check backend health
        this.checkBackendHealth();

        console.log('AetherSegment AI initialized successfully');
    }

    initializeCampaignSelector() {
        // Setup template selection callback
        this.campaignTemplates.setOnTemplateSelect((objective, title) => {
            this.handleTemplateSelection(objective, title);
        });

        // Setup builder generation callback
        this.campaignBuilder.setOnCampaignGenerate((objective, title) => {
            this.handleBuilderGeneration(objective, title);
        });

        // Setup mode toggle
        this.setupModeToggle();
    }

    setupModeToggle() {
        const templatesBtn = document.getElementById('mode-templates');
        const builderBtn = document.getElementById('mode-builder');
        const templatesContainer = document.getElementById('campaign-templates-container');
        const builderContainer = document.getElementById('campaign-builder-container');

        if (templatesBtn && builderBtn && templatesContainer && builderContainer) {
            templatesBtn.addEventListener('click', () => {
                this.switchMode('templates', templatesBtn, builderBtn, templatesContainer, builderContainer);
            });

            builderBtn.addEventListener('click', () => {
                this.switchMode('builder', builderBtn, templatesBtn, builderContainer, templatesContainer);
            });
        }
    }

    switchMode(mode, activeBtn, inactiveBtn, showContainer, hideContainer) {
        // Check if clicking the already active button
        if (activeBtn.classList.contains('active')) {
            // Deactivate - hide everything
            activeBtn.classList.remove('active');
            showContainer.style.display = 'none';
            this.currentCampaignMode = null;
            console.log(`Deactivated ${mode} mode`);
            return;
        }

        this.currentCampaignMode = mode;

        // Render content when first showing (lazy render)
        if (mode === 'templates' && !showContainer.hasChildNodes()) {
            this.campaignTemplates.render();
        } else if (mode === 'builder' && !showContainer.hasChildNodes()) {
            this.campaignBuilder.render();
        }

        // Update button states
        activeBtn.classList.add('active');
        inactiveBtn.classList.remove('active');

        // Toggle containers
        showContainer.style.display = 'block';
        hideContainer.style.display = 'none';

        console.log(`Switched to ${mode} mode`);
    }

    handleTemplateSelection(objective, title) {
        console.log('Template selected:', title);
        
        // Populate the textarea
        const textarea = document.getElementById('campaign-objective');
        if (textarea) {
            textarea.value = objective;
        }

        // Show toast confirmation
        showToast(`Template "${title}" loaded! Click "Analyze Campaign" to continue.`, 'success');

        // Scroll to textarea
        setTimeout(() => {
            const inputCard = document.querySelector('.campaign-input-card');
            if (inputCard) {
                scrollToElement(inputCard);
            }
        }, 100);
    }

    handleBuilderGeneration(objective, title) {
        console.log('Campaign generated:', title);
        
        // Populate the textarea
        const textarea = document.getElementById('campaign-objective');
        if (textarea) {
            textarea.value = objective;
        }

        // Show toast confirmation
        showToast(`Campaign "${title}" generated! Click "Analyze Campaign" to continue.`, 'success');

        // Scroll to textarea
        setTimeout(() => {
            const inputCard = document.querySelector('.campaign-input-card');
            if (inputCard) {
                scrollToElement(inputCard);
            }
        }, 100);
    }

    setupActionButtons() {
        // Step 2: Analysis Results buttons (go directly to refine segment)
        const proceedToRefineBtn = document.getElementById('proceed-to-refine-btn');
        if (proceedToRefineBtn) {
            proceedToRefineBtn.addEventListener('click', () => this.showRefineSegment());
        }

        // Step 3: Refine Segment buttons
        const previewFiltersBtn = document.getElementById('preview-filters-btn');
        if (previewFiltersBtn) {
            previewFiltersBtn.addEventListener('click', () => this.previewFilterImpact());
        }

        const clearFiltersBtn = document.getElementById('clear-filters-btn');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }

        const proceedToActivateBtn = document.getElementById('proceed-to-activate-btn');
        if (proceedToActivateBtn) {
            proceedToActivateBtn.addEventListener('click', () => this.showActivateSegment());
        }

        const backToAnalysisBtnRefine = document.getElementById('back-to-analysis-btn-refine');
        if (backToAnalysisBtnRefine) {
            backToAnalysisBtnRefine.addEventListener('click', () => this.showAnalysisResults());
        }

        // Step 5: Activate Segment buttons
        const backToRefineBtn = document.getElementById('back-to-refine-btn');
        if (backToRefineBtn) {
            backToRefineBtn.addEventListener('click', () => this.showRefineSegment());
        }

        // Create Segment button
        const createSegmentBtn = document.getElementById('create-segment-btn');
        if (createSegmentBtn) {
            createSegmentBtn.addEventListener('click', () => this.createSegment());
        }

        // New Campaign button (from results)
        const newCampaignBtn = document.getElementById('new-campaign-btn');
        if (newCampaignBtn) {
            newCampaignBtn.addEventListener('click', () => this.startNewCampaign());
        }

        // Another Campaign button (from segment details)
        const anotherCampaignBtn = document.getElementById('another-campaign-btn');
        if (anotherCampaignBtn) {
            anotherCampaignBtn.addEventListener('click', () => this.startNewCampaign());
        }

        // Export buttons
        const exportJsonBtn = document.getElementById('export-json-btn');
        if (exportJsonBtn) {
            exportJsonBtn.addEventListener('click', () => this.exportJSON());
        }

        const exportCsvBtn = document.getElementById('export-csv-btn');
        if (exportCsvBtn) {
            exportCsvBtn.addEventListener('click', () => this.exportCSV());
        }

        const copyApiBtn = document.getElementById('copy-api-btn');
        if (copyApiBtn) {
            copyApiBtn.addEventListener('click', () => this.copyApiEndpoint());
        }

        // Location filter - Country change should filter cities
        const countryFilter = document.getElementById('filter-country');
        const cityFilter = document.getElementById('filter-city');
        if (countryFilter && cityFilter) {
            countryFilter.addEventListener('change', () => this.filterCitiesByCountry());
        }
    }

    async checkBackendHealth() {
        try {
            await apiClient.healthCheck();
            console.log('✓ Backend connection successful');
        } catch (error) {
            console.error('✗ Backend connection failed:', error);
            showToast(
                'Warning: Could not connect to backend. Make sure the server is running on http://localhost:5000',
                'warning'
            );
        }
    }

    async analyzeCampaign(objective) {
        console.log('Analyzing campaign:', objective);

        // Set loading state
        this.campaignInput.setLoading(true);

        try {
            // Call API
            const analysis = await apiClient.analyzeCampaign(objective);

            console.log('Analysis result:', analysis);

            // Store state
            this.currentCampaignObjective = objective;
            this.currentAnalysis = analysis;

            // Display results
            this.displayAnalysisResults(analysis);

            // Show success message
            showToast('Campaign analyzed successfully!', 'success');

        } catch (error) {
            console.error('Analysis failed:', error);
            showToast(`Failed to analyze campaign: ${error.message}`, 'error');
        } finally {
            this.campaignInput.setLoading(false);
        }
    }

    async displayAnalysisResults(analysis) {
        // Display Campaign Objective Object
        this.cooDisplay.render(analysis.campaign_objective_object);

        // Display Trigger Selection (all options with recommended one pre-selected)
        if (analysis.trigger_suggestions && analysis.recommended_trigger) {
            this.displayTriggerSelection(analysis.trigger_suggestions, analysis.recommended_trigger);
            // Auto-select the recommended trigger
            this.selectedTrigger = {
                trigger_name: analysis.recommended_trigger.trigger_name,
                predicted_uplift: analysis.recommended_trigger.predicted_uplift,
                confidence_score: analysis.recommended_trigger.confidence_score,
                filteredSize: analysis.segment_preview.estimated_size
            };
            console.log('🎯 Auto-selected recommended trigger:', this.selectedTrigger.trigger_name);
            console.log(`   📊 Predicted Uplift: ${Math.round(this.selectedTrigger.predicted_uplift * 100)}%`);
            console.log(`   🔒 Confidence: ${Math.round(this.selectedTrigger.confidence_score * 100)}%`);
        }

        // Initialize currentSegmentMetadata with the full unfiltered segment
        this.currentSegmentMetadata = {
            ...analysis.segment_preview
        };

        // Display Full Segment Dashboard in Step 2 (WITHOUT demographics/categories)
        const fullSegmentDashboard = document.getElementById('full-segment-dashboard');
        if (fullSegmentDashboard) {
            this.segmentDashboard.render(
                this.currentSegmentMetadata,
                analysis.campaign_objective_object,
                fullSegmentDashboard,
                false  // Don't show demographics in step 2
            );
        }

        // Display AI-Applied Filters
        this.displayAIFilters(analysis.segment_preview.ai_filters || []);

        // Show cart value filter if this is an abandoned cart campaign
        const cartValueGroup = document.getElementById('cart-value-filter-group');
        if (cartValueGroup && analysis.campaign_objective_object.target_behavior === 'abandoned_cart') {
            cartValueGroup.style.display = 'block';
        }

        // Show analysis results section, hide others
        this.showAnalysisResults();

        // Scroll to results
        setTimeout(() => scrollToElement(this.analysisResultsSection), 100);

        // AUTOMATICALLY APPLY THE RECOMMENDED TRIGGER
        // This updates the segment with the trigger filter
        if (this.selectedTrigger) {
            console.log('🎯 Auto-applying recommended trigger:', this.selectedTrigger.trigger_name);
            await this.updateSegmentWithTrigger();
        }
    }

    displayTriggerSelection(triggers, recommendedTrigger) {
        const triggerContainer = document.getElementById('trigger-selection-container');
        if (!triggerContainer) return;

        const html = `
            <div class="trigger-options">
                <!-- No Trigger Option -->
                <div class="trigger-option no-trigger" data-trigger="none">
                    <div class="trigger-option-content">
                        <div class="trigger-option-name">❌ No Trigger Filter</div>
                        <div class="trigger-option-stats">
                            <span>Use all eligible customers without trigger filtering</span>
                        </div>
                    </div>
                </div>

                ${triggers.map((trigger, index) => `
                    <div class="trigger-option ${trigger.trigger_name === recommendedTrigger.trigger_name ? 'selected' : ''}" 
                         data-trigger="${trigger.trigger_name}"
                         data-uplift="${trigger.predicted_uplift}"
                         data-confidence="${trigger.confidence_score}">
                        <div class="trigger-option-content">
                            <div class="trigger-option-name">
                                ${trigger.trigger_name}
                                ${trigger.trigger_name === recommendedTrigger.trigger_name ? '<span class="badge badge-success" style="margin-left: 8px;">Recommended</span>' : ''}
                            </div>
                            <div class="trigger-option-stats">
                                <div class="trigger-option-stat">
                                    <span>Uplift:</span>
                                    <strong>${Math.round(trigger.predicted_uplift * 100)}%</strong>
                                </div>
                                <div class="trigger-option-stat">
                                    <span>Confidence:</span>
                                    <strong>${Math.round(trigger.confidence_score * 100)}%</strong>
                                </div>
                            </div>
                        </div>
                        ${index === 0 ? '<span class="trigger-icon">🎯</span>' : ''}
                    </div>
                `).join('')}
            </div>
        `;

        triggerContainer.innerHTML = html;

        // Add click handlers
        const options = triggerContainer.querySelectorAll('.trigger-option');
        options.forEach(option => {
            option.addEventListener('click', () => {
                this.handleTriggerOptionClick(option);
            });
        });
    }

    async handleTriggerOptionClick(option) {
        const triggerName = option.dataset.trigger;
        
        console.log('🖱️ User clicked trigger option:', triggerName);
        
        // Update UI selection
        const allOptions = document.querySelectorAll('.trigger-option');
        allOptions.forEach(opt => opt.classList.remove('selected'));
        option.classList.add('selected');

        // Update selected trigger
        if (triggerName === 'none') {
            console.log('❌ No trigger selected - will show full segment');
            this.selectedTrigger = null;
        } else {
            this.selectedTrigger = {
                trigger_name: triggerName,
                predicted_uplift: parseFloat(option.dataset.uplift),
                confidence_score: parseFloat(option.dataset.confidence),
                filteredSize: null // Will be fetched
            };
            console.log('✅ Selected trigger:', this.selectedTrigger);
            console.log(`   📊 Uplift: ${Math.round(this.selectedTrigger.predicted_uplift * 100)}%`);
            console.log(`   🎯 Confidence: ${Math.round(this.selectedTrigger.confidence_score * 100)}%`);
        }

        // Fetch and update segment stats
        await this.updateSegmentWithTrigger();
    }

    async updateSegmentWithTrigger() {
        try {
            console.log('📊 Updating segment with trigger:', this.selectedTrigger ? this.selectedTrigger.trigger_name : 'none');
            
            showToast('Updating segment...', 'info');

            // Call backend to get segment with selected trigger
            const preview = await apiClient.previewFilters(
                this.currentAnalysis.campaign_objective_object,
                {}, // No manual filters yet
                this.selectedTrigger ? this.selectedTrigger.trigger_name : null
            );

            console.log('✅ Received preview from backend:', {
                final_size: preview.final_size,
                final_avg_clv: preview.final_avg_clv,
                final_avg_cart_value: preview.final_avg_cart_value,
                trigger: this.selectedTrigger ? this.selectedTrigger.trigger_name : 'none'
            });

            // Calculate predicted uplift and ROI based on selected trigger
            let predicted_uplift = 0;
            let predicted_roi = '3-5x'; // Default
            
            if (this.selectedTrigger) {
                predicted_uplift = this.selectedTrigger.predicted_uplift;
                // Calculate ROI based on uplift and confidence
                const uplift = this.selectedTrigger.predicted_uplift;
                const confidence = this.selectedTrigger.confidence_score;
                
                // ROI calculation: Higher uplift + higher confidence = better ROI
                const roi_score = (uplift * confidence) * 100; // 0-100 scale
                
                if (roi_score >= 70) {
                    predicted_roi = '5-8x';
                } else if (roi_score >= 60) {
                    predicted_roi = '4-6x';
                } else if (roi_score >= 50) {
                    predicted_roi = '3-5x';
                } else if (roi_score >= 40) {
                    predicted_roi = '2-4x';
                } else {
                    predicted_roi = '1-3x';
                }
            } else {
                // No trigger selected - use base prediction from analysis
                predicted_uplift = this.currentAnalysis.segment_preview.predicted_uplift || 0;
                predicted_roi = this.currentAnalysis.segment_preview.predicted_roi || '3-5x';
            }

            // Create updated metadata and STORE IT
            this.currentSegmentMetadata = {
                ...this.currentAnalysis.segment_preview,
                estimated_size: preview.final_size,
                avg_clv_score: preview.final_avg_clv,
                avg_cart_value: preview.final_avg_cart_value,
                predicted_uplift: predicted_uplift,
                predicted_roi: predicted_roi
            };

            console.log('💾 Updated metadata:', {
                size: this.currentSegmentMetadata.estimated_size,
                clv: this.currentSegmentMetadata.avg_clv_score,
                uplift: `${Math.round(predicted_uplift * 100)}%`,
                roi: predicted_roi
            });

            // Update segment dashboard
            const fullSegmentDashboard = document.getElementById('full-segment-dashboard');
            if (fullSegmentDashboard) {
                this.segmentDashboard.render(
                    this.currentSegmentMetadata,
                    this.currentAnalysis.campaign_objective_object,
                    fullSegmentDashboard,
                    false
                );
            }

            // Update subtitle with trigger and uplift info
            const subtitle = document.getElementById('segment-subtitle');
            if (subtitle) {
                if (this.selectedTrigger) {
                    const upliftPercent = Math.round(this.selectedTrigger.predicted_uplift * 100);
                    const confidencePercent = Math.round(this.selectedTrigger.confidence_score * 100);
                    subtitle.innerHTML = `
                        Filtered to customers highly responsive to <strong>${this.selectedTrigger.trigger_name}</strong>
                        <span style="color: var(--success-color); margin-left: 12px;">
                            📈 Predicted Uplift: <strong>${upliftPercent}%</strong>
                        </span>
                        <span style="color: var(--primary-color); margin-left: 12px;">
                            🎯 Confidence: <strong>${confidencePercent}%</strong>
                        </span>
                    `;
                } else {
                    subtitle.textContent = 'These customers match your campaign criteria';
                }
            }

            // Update AI filters display
            this.displayAIFilters(this.currentAnalysis.segment_preview.ai_filters || []);

            showToast(`Segment updated: ${preview.final_size.toLocaleString()} customers`, 'success');
        } catch (error) {
            console.error('❌ Failed to update segment:', error);
            showToast('Failed to update segment', 'error');
        }
    }

    displayAIFilters(aiFilters) {
        const aiFiltersDisplay = document.getElementById('ai-filters-display');
        const aiFiltersReview = document.getElementById('ai-filters-review');

        let html = '';
        
        // Show AI behavior filters
        if (aiFilters && aiFilters.length > 0) {
            html += aiFilters.map(filter => `
                <div class="filter-badge ai-filter">
                    <strong>${filter.filter_type}:</strong> ${filter.description}
                </div>
            `).join('');
        }
        
        // Show trigger filter if applied (from selectedTrigger)
        if (this.selectedTrigger) {
            html += `
                <div class="filter-badge ai-filter" style="border-left-color: var(--success-color);">
                    <strong>🎯 Trigger Filter:</strong> ${this.selectedTrigger.trigger_name.replace('_', ' ')} (${Math.round(this.selectedTrigger.predicted_uplift * 100)}% predicted uplift)
                </div>
            `;
        }
        
        if (!html) {
            html = '<p class="text-secondary">No specific filters applied</p>';
        }

        if (aiFiltersDisplay) aiFiltersDisplay.innerHTML = `<div style="margin-top: 1rem;">${html}</div>`;
        if (aiFiltersReview) aiFiltersReview.innerHTML = html;
    }

    showAnalysisResults() {
        this.campaignInputSection.style.display = 'none';
        this.analysisResultsSection.style.display = 'block';
        this.refineSegmentSection.style.display = 'none';
        this.activateSegmentSection.style.display = 'none';
        this.segmentDetailsSection.style.display = 'none';
    }

    // REMOVED: showTriggerSelection() - triggers are now in Step 2 (Analysis page)

    showRefineSegment() {
        // Render AI filters review
        if (this.currentAnalysis) {
            this.displayAIFilters(this.currentAnalysis.segment_preview.ai_filters);
            
            // Show current segment after trigger filter - USE UPDATED METADATA
            const triggerFilteredDashboard = document.getElementById('trigger-filtered-dashboard');
            if (triggerFilteredDashboard && this.currentSegmentMetadata) {
                this.segmentDashboard.render(
                    this.currentSegmentMetadata,  // Use updated metadata from trigger selection
                    this.currentAnalysis.campaign_objective_object,
                    triggerFilteredDashboard,
                    false  // Compact mode
                );
            }
        }

        this.campaignInputSection.style.display = 'none';
        this.analysisResultsSection.style.display = 'none';
        this.refineSegmentSection.style.display = 'block';
        this.activateSegmentSection.style.display = 'none';
        this.segmentDetailsSection.style.display = 'none';
        setTimeout(() => scrollToElement(this.refineSegmentSection), 100);
    }

    async showActivateSegment() {
        // Apply manual filters to get final segment data
        if (this.currentAnalysis && this.appliedFilters && Object.keys(this.appliedFilters).length > 0) {
            try {
                console.log('📋 Applying manual filters before activation:', this.appliedFilters);
                
                // Fetch final segment with manual filters + trigger
                const preview = await apiClient.previewFilters(
                    this.currentAnalysis.campaign_objective_object,
                    this.appliedFilters,
                    this.selectedTrigger ? this.selectedTrigger.trigger_name : null
                );
                
                console.log('✅ Final segment with filters:', {
                    size: preview.final_size,
                    clv: preview.final_avg_clv,
                    filters: Object.keys(this.appliedFilters)
                });

                // Calculate predicted uplift and ROI
                let predicted_uplift = 0;
                let predicted_roi = '3-5x';
                
                if (this.selectedTrigger) {
                    predicted_uplift = this.selectedTrigger.predicted_uplift;
                    const roi_score = (this.selectedTrigger.predicted_uplift * this.selectedTrigger.confidence_score) * 100;
                    
                    if (roi_score >= 70) predicted_roi = '5-8x';
                    else if (roi_score >= 60) predicted_roi = '4-6x';
                    else if (roi_score >= 50) predicted_roi = '3-5x';
                    else if (roi_score >= 40) predicted_roi = '2-4x';
                    else predicted_roi = '1-3x';
                }

                // Update current metadata with filtered results
                this.currentSegmentMetadata = {
                    ...this.currentSegmentMetadata,
                    estimated_size: preview.final_size,
                    avg_clv_score: preview.final_avg_clv,
                    avg_cart_value: preview.final_avg_cart_value,
                    predicted_uplift: predicted_uplift,
                    predicted_roi: predicted_roi
                };
            } catch (error) {
                console.error('❌ Failed to apply filters:', error);
                showToast('Failed to apply filters', 'error');
            }
        }

        // Render final overview in Step 4
        if (this.currentAnalysis) {
            // Display final segment overview with applied filters
            const finalDashboard = document.getElementById('final-segment-dashboard');
            if (finalDashboard && this.currentSegmentMetadata) {
                this.segmentDashboard.render(
                    this.currentSegmentMetadata,  // Use updated metadata with filters
                    this.currentAnalysis.campaign_objective_object,
                    finalDashboard,
                    false  // Don't show demographics/product categories
                );
            }
        }

        this.campaignInputSection.style.display = 'none';
        this.analysisResultsSection.style.display = 'none';
        this.refineSegmentSection.style.display = 'none';
        this.activateSegmentSection.style.display = 'block';
        this.segmentDetailsSection.style.display = 'none';
        setTimeout(() => scrollToElement(this.activateSegmentSection), 100);
    }

    async handleTriggerSelection(trigger) {
        // Store selected trigger
        this.selectedTrigger = trigger;
        
        // Show preview of trigger impact
        const previewCard = document.getElementById('trigger-preview-card');
        const previewContent = document.getElementById('trigger-preview-content');
        const applyBtn = document.getElementById('apply-trigger-btn');
        
        if (previewCard && previewContent) {
            const currentSize = this.currentAnalysis.segment_preview.estimated_size;
            
            // Show loading state
            previewContent.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div class="spinner" style="margin: 0 auto 1rem;"></div>
                    <p>Calculating trigger impact from BigQuery...</p>
                </div>
            `;
            previewCard.style.display = 'block';
            
            try {
                // Call backend to get REAL filtered size from BigQuery
                const preview = await apiClient.previewFilters(
                    this.currentAnalysis.campaign_objective_object,
                    {},  // No manual filters yet
                    trigger.trigger_name  // Apply trigger sensitivity filter
                );
                
                const filteredSize = preview.final_size;
                
                // Store the REAL filtered size for when user applies
                this.selectedTrigger.filteredSize = filteredSize;
                
                const upliftScore = trigger.predicted_uplift || 0.65;
                
                previewContent.innerHTML = `
                    <div class="preview-comparison">
                        <div class="preview-metric before">
                            <div class="metric-label">Before Trigger Filter</div>
                            <div class="metric-value">${currentSize.toLocaleString()}</div>
                            <div class="metric-sublabel">All eligible customers</div>
                        </div>
                        <div class="preview-arrow">→</div>
                        <div class="preview-metric after">
                            <div class="metric-label">After ${trigger.trigger_name.replace('_', ' ')}</div>
                            <div class="metric-value">${filteredSize.toLocaleString()}</div>
                            <div class="metric-change neutral">${Math.round((filteredSize/currentSize)*100)}% retained</div>
                        </div>
                    </div>
                    <div style="padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius-md); margin-top: 1rem;">
                        <p><strong>Impact:</strong> Segment will be filtered to customers with high sensitivity to <strong>${trigger.trigger_name.replace('_', ' ')}</strong>.</p>
                        <p style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">
                            Only customers with ${trigger.trigger_name.replace('_', ' ')} sensitivity score > 65% will be included.
                        </p>
                        <p style="margin-top: 0.5rem; color: var(--success-color); font-size: 0.9rem;">
                            <strong>Predicted Uplift: ${Math.round(upliftScore * 100)}%</strong>
                        </p>
                    </div>
                `;
                
                if (applyBtn) applyBtn.style.display = 'inline-block';
            } catch (error) {
                console.error('Failed to fetch trigger preview:', error);
                previewContent.innerHTML = `
                    <div style="padding: 1rem; background: var(--error-bg); border-radius: var(--radius-md); color: var(--error-color);">
                        <p><strong>Error:</strong> Failed to calculate trigger impact. ${error.message}</p>
                    </div>
                `;
            }
        }
    }

    async applyTriggerAndContinue() {
        if (!this.selectedTrigger) {
            showToast('No trigger selected', 'warning');
            return;
        }

        // Use the pre-calculated filtered size from the preview
        const filteredSize = this.selectedTrigger.filteredSize;
        
        // Store original size before trigger filter
        if (!this.currentAnalysis.segment_preview.original_size) {
            this.currentAnalysis.segment_preview.original_size = this.currentAnalysis.segment_preview.estimated_size;
        }
        
        // Update segment preview with trigger-filtered data
        this.currentAnalysis.segment_preview.estimated_size = filteredSize;
        this.currentAnalysis.segment_preview.trigger_applied = {
            name: this.selectedTrigger.trigger_name,
            uplift: this.selectedTrigger.predicted_uplift
        };
        
        showToast(`Trigger filter applied! Segment: ${filteredSize.toLocaleString()} customers`, 'success');
        this.showRefineSegment();
    }

    async previewFilterImpact() {
        if (!this.currentAnalysis) {
            showToast('No campaign analysis found', 'error');
            return;
        }

        // Collect filter values
        const filters = {};
        
        const country = document.getElementById('filter-country').value;
        if (country) filters.location_country = country;

        const city = document.getElementById('filter-city').value;
        if (city) filters.location_city = city;

        const clvMin = document.getElementById('filter-clv-min').value;
        if (clvMin) filters.clv_min = parseFloat(clvMin) / 100; // Convert % to decimal

        const cartMin = document.getElementById('filter-cart-min').value;
        if (cartMin) filters.cart_value_min = parseFloat(cartMin);

        // Check if any filters are applied
        if (Object.keys(filters).length === 0) {
            showToast('Please add at least one filter to preview', 'warning');
            return;
        }
        
        // Get the selected trigger if any
        const selectedTrigger = this.selectedTrigger ? this.selectedTrigger.trigger_name : null;

        const previewBtn = document.getElementById('preview-filters-btn');
        const originalText = previewBtn.innerHTML;
        previewBtn.innerHTML = '<span class="spinner"></span> Previewing...';
        previewBtn.disabled = true;

        try {
            const preview = await apiClient.previewFilters(
                this.currentAnalysis.campaign_objective_object,
                filters,
                selectedTrigger  // Pass the selected trigger so backend applies trigger filter
            );

            // Update the current segment dashboard with filtered data
            const triggerFilteredDashboard = document.getElementById('trigger-filtered-dashboard');
            if (triggerFilteredDashboard) {
                // Calculate predicted uplift and ROI
                let predicted_uplift = 0;
                let predicted_roi = '3-5x';
                
                if (this.selectedTrigger) {
                    predicted_uplift = this.selectedTrigger.predicted_uplift;
                    const roi_score = (this.selectedTrigger.predicted_uplift * this.selectedTrigger.confidence_score) * 100;
                    
                    if (roi_score >= 70) predicted_roi = '5-8x';
                    else if (roi_score >= 60) predicted_roi = '4-6x';
                    else if (roi_score >= 50) predicted_roi = '3-5x';
                    else if (roi_score >= 40) predicted_roi = '2-4x';
                    else predicted_roi = '1-3x';
                }

                // Update metadata with filtered values
                const filteredMetadata = {
                    ...this.currentSegmentMetadata,
                    estimated_size: preview.final_size,
                    avg_clv_score: preview.final_avg_clv,
                    avg_cart_value: preview.final_avg_cart_value,
                    predicted_uplift: predicted_uplift,
                    predicted_roi: predicted_roi
                };

                // Re-render the dashboard with updated values
                this.segmentDashboard.render(
                    filteredMetadata,
                    this.currentAnalysis.campaign_objective_object,
                    triggerFilteredDashboard,
                    false
                );
            }

            this.displayFilterPreview(preview);
            this.appliedFilters = filters;

            showToast('Filter preview updated', 'success');
        } catch (error) {
            console.error('Preview failed:', error);
            showToast(`Failed to preview filters: ${error.message}`, 'error');
        } finally {
            previewBtn.innerHTML = originalText;
            previewBtn.disabled = false;
        }
    }

    displayFilterPreview(preview) {
        const previewCard = document.getElementById('filter-preview-card');
        const previewContent = document.getElementById('filter-preview-content');

        if (!previewCard || !previewContent) return;

        const percentChange = ((preview.final_size - preview.starting_size) / preview.starting_size * 100);
        const changeClass = percentChange >= 0 ? 'positive' : 'negative';

        const html = `
            <div class="preview-comparison">
                <div class="preview-metric before">
                    <div class="metric-label">Starting Size</div>
                    <div class="metric-value">${formatNumber(preview.starting_size)}</div>
                </div>
                <div class="preview-arrow">→</div>
                <div class="preview-metric after">
                    <div class="metric-label">After Filters</div>
                    <div class="metric-value">${formatNumber(preview.final_size)}</div>
                    <div class="metric-change ${changeClass}">
                        ${percentChange > 0 ? '+' : ''}${percentChange.toFixed(1)}% (${preview.percentage_retained}% retained)
                    </div>
                </div>
            </div>

            <div class="preview-comparison">
                <div class="preview-metric before">
                    <div class="metric-label">Avg CLV</div>
                    <div class="metric-value">${(preview.final_avg_clv * 100).toFixed(0)}%</div>
                    ${preview.clv_interpretation ? `
                        <div class="metric-detail" style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            ${preview.clv_interpretation.tier_label} • ${preview.clv_interpretation.percentile}
                        </div>
                    ` : ''}
                </div>
            </div>

            ${preview.filters_applied && preview.filters_applied.length > 0 ? `
                <div class="filters-applied-list">
                    <h4>Filters Applied</h4>
                    ${preview.filters_applied.map(filter => `
                        <div class="filter-item">
                            <span class="filter-description">${filter.description}</span>
                            <span class="filter-impact">${formatNumber(filter.impact)} customers</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;

        previewContent.innerHTML = html;
        previewCard.style.display = 'block';

        // Scroll to preview
        setTimeout(() => scrollToElement(previewCard), 100);
    }

    filterCitiesByCountry() {
        const countrySelect = document.getElementById('filter-country');
        const citySelect = document.getElementById('filter-city');
        
        if (!countrySelect || !citySelect) return;
        
        const selectedCountry = countrySelect.value;
        
        // City-to-country mapping based on our data
        const cityCountryMap = {
            // United States
            'New York': 'United States',
            'Los Angeles': 'United States',
            'Chicago': 'United States',
            'Houston': 'United States',
            'Phoenix': 'United States',
            'Seattle': 'United States',
            // United Kingdom
            'London': 'United Kingdom',
            'Manchester': 'United Kingdom',
            'Birmingham': 'United Kingdom',
            'Glasgow': 'United Kingdom',
            'Edinburgh': 'United Kingdom',
            // Canada
            'Toronto': 'Canada',
            'Vancouver': 'Canada',
            'Montreal': 'Canada',
            'Calgary': 'Canada',
            'Ottawa': 'Canada',
            // Australia
            'Sydney': 'Australia',
            'Melbourne': 'Australia',
            'Brisbane': 'Australia',
            'Perth': 'Australia',
            'Adelaide': 'Australia'
        };
        
        // Get all city options
        const allOptions = Array.from(citySelect.options);
        
        // Show/hide options based on selected country
        allOptions.forEach(option => {
            if (option.value === '') {
                // Always show "All Cities" option
                option.style.display = '';
                option.disabled = false;
            } else {
                const cityCountry = cityCountryMap[option.value];
                if (!selectedCountry || cityCountry === selectedCountry) {
                    option.style.display = '';
                    option.disabled = false;
                } else {
                    option.style.display = 'none';
                    option.disabled = true;
                }
            }
        });
        
        // Reset city selection if current selection is now invalid
        if (citySelect.value && selectedCountry) {
            const currentCity = citySelect.value;
            if (cityCountryMap[currentCity] !== selectedCountry) {
                citySelect.value = '';
            }
        }
    }

    clearFilters() {
        document.getElementById('filter-country').value = '';
        document.getElementById('filter-city').value = '';
        document.getElementById('filter-clv-min').value = '';
        document.getElementById('filter-cart-min').value = '';

        // Reset city filter to show all cities
        this.filterCitiesByCountry();

        const previewCard = document.getElementById('filter-preview-card');
        if (previewCard) previewCard.style.display = 'none';

        this.appliedFilters = {};

        showToast('Filters cleared', 'info');
    }


    async createSegment() {
        if (!this.currentCampaignObjective) {
            showToast('No campaign objective found', 'error');
            return;
        }

        const createBtn = document.getElementById('create-segment-btn');
        const originalText = createBtn.innerHTML;
        createBtn.innerHTML = '<span class="spinner"></span> Creating Segment...';
        createBtn.disabled = true;

        try {
            // Use selectedTrigger from state (set during trigger selection step)
            const selectedTrigger = this.selectedTrigger ? this.selectedTrigger.trigger_name : null;

            // Create segment with trigger and applied filters
            const segment = await apiClient.createSegment(
                this.currentCampaignObjective,
                selectedTrigger,
                this.appliedFilters
            );

            console.log('Segment created:', segment);

            // Store state
            this.currentSegment = segment;

            // Display segment details
            this.displaySegmentDetails(segment);

            // Show success message
            showToast('Segment created successfully!', 'success');

        } catch (error) {
            console.error('Segment creation failed:', error);
            showToast(`Failed to create segment: ${error.message}`, 'error');
        } finally {
            createBtn.innerHTML = originalText;
            createBtn.disabled = false;
        }
    }

    displaySegmentDetails(segment) {
        // Display segment ID
        const segmentIdDisplay = document.getElementById('segment-id-display');
        if (segmentIdDisplay) {
            segmentIdDisplay.textContent = `Segment ID: ${segment.segment_id}`;
        }

        // Display segment stats
        const segmentStats = document.getElementById('segment-stats');
        if (segmentStats) {
            segmentStats.innerHTML = `
                <div class="segment-stats-grid">
                    <div class="stat-card primary">
                        <div class="stat-label">Total Customers</div>
                        <div class="stat-value">${formatNumber(segment.estimated_size)}</div>
                        <div class="stat-subtitle">in this segment</div>
                    </div>
                    <div class="stat-card success">
                        <div class="stat-label">Avg CLV Score</div>
                        <div class="stat-value">${Math.round(segment.metadata.avg_clv_score * 100)}%</div>
                        <div class="stat-subtitle">customer lifetime value</div>
                    </div>
                    <div class="stat-card secondary">
                        <div class="stat-label">Predicted Uplift</div>
                        <div class="stat-value">${Math.round(segment.metadata.predicted_uplift * 100)}%</div>
                        <div class="stat-subtitle">conversion increase</div>
                    </div>
                    <div class="stat-card warning">
                        <div class="stat-label">Predicted ROI</div>
                        <div class="stat-value">${segment.metadata.predicted_roi}</div>
                        <div class="stat-subtitle">return on investment</div>
                    </div>
                </div>
            `;
        }

        // Display comprehensive journey summary
        if (segment.comprehensive_summary) {
            this.displayJourneySummary(segment.comprehensive_summary);
        }

        // Display customer list
        this.displayCustomerList(segment.customer_profiles);

        // Display API endpoint
        const apiEndpointDisplay = document.getElementById('api-endpoint-display');
        if (apiEndpointDisplay) {
            const endpoint = `GET http://localhost:5000/api/v1/segments/${segment.segment_id}/customers`;
            apiEndpointDisplay.innerHTML = `<code>${endpoint}</code>`;
        }

        // Hide all workflow sections, show segment details
        this.campaignInputSection.style.display = 'none';
        this.analysisResultsSection.style.display = 'none';
        this.refineSegmentSection.style.display = 'none';
        this.activateSegmentSection.style.display = 'none';
        this.segmentDetailsSection.style.display = 'block';

        // Scroll to segment details
        setTimeout(() => scrollToElement(this.segmentDetailsSection), 100);
    }

    displayCustomerList(customers) {
        const customerList = document.getElementById('customer-list');
        if (!customerList || !customers || customers.length === 0) {
            return;
        }

        customerList.innerHTML = '';

        // Display up to 20 customers
        const displayCount = Math.min(customers.length, 20);

        for (let i = 0; i < displayCount; i++) {
            const customer = customers[i];
            const card = this.createCustomerCard(customer);
            customerList.appendChild(card);
        }

        if (customers.length > displayCount) {
            const moreInfo = document.createElement('div');
            moreInfo.style.textAlign = 'center';
            moreInfo.style.padding = 'var(--spacing-md)';
            moreInfo.style.color = 'var(--text-secondary)';
            moreInfo.textContent = `+ ${customers.length - displayCount} more customers`;
            customerList.appendChild(moreInfo);
        }
    }

    displayJourneySummary(summary) {
        const journeyContainer = document.getElementById('segment-journey-summary');
        const journeyContent = document.getElementById('journey-content');
        
        if (!journeyContainer || !journeyContent || !summary) {
            return;
        }
        
        // Build filtering steps HTML
        const stepsHTML = summary.filtering_steps.map((step, index) => {
            const stepNum = index + 1;
            return `
                <div class="journey-step">
                    <div class="step-number">${stepNum}</div>
                    <div class="step-content">
                        <div class="step-title">${step.step}</div>
                        <div class="step-description">${step.description.replace(/\n/g, '<br>')}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Build final summary
        const finalHTML = `
            <div class="journey-steps">
                ${stepsHTML}
            </div>
            <div class="journey-result">
                <div class="result-icon">✓</div>
                <div class="result-content">
                    <div class="result-title">Final Result</div>
                    <div class="result-description">
                        ${summary.final_characteristics.total_customers.toLocaleString()} highly-targeted customers with an average CLV score of ${Math.round(summary.final_characteristics.avg_clv_score * 100)}%${summary.final_characteristics.clv_interpretation ? ` (${summary.final_characteristics.clv_interpretation.tier_label})` : ''}, optimized for maximum campaign impact.
                    </div>
                </div>
            </div>
        `;
        
        journeyContent.innerHTML = finalHTML;
        journeyContainer.style.display = 'block';
    }

    createCustomerCard(customer) {
        const card = document.createElement('div');
        card.className = 'customer-card';

        let cartInfo = '';
        if (customer.abandoned_cart_id && customer.cart_value) {
            cartInfo = `
                <div class="customer-cart">
                    <div class="cart-info">
                        <span>Cart: ${customer.abandoned_cart_id}</span>
                        <span class="cart-value">${formatCurrency(customer.cart_value)}</span>
                    </div>
                </div>
            `;
        }

        // Build product affinity display
        let productAffinity = '';
        if (customer.favorite_category || customer.price_tier_preference) {
            productAffinity = '<div class="customer-affinity">';
            if (customer.favorite_category) {
                productAffinity += `<span class="affinity-tag">🏠 ${customer.favorite_category}</span>`;
            }
            if (customer.secondary_category) {
                productAffinity += `<span class="affinity-tag secondary">📦 ${customer.secondary_category}</span>`;
            }
            if (customer.price_tier_preference) {
                const tierEmoji = customer.price_tier_preference === 'premium' ? '💎' : 
                                 customer.price_tier_preference === 'mid' ? '⭐' : '💰';
                productAffinity += `<span class="affinity-tag tier">${tierEmoji} ${customer.price_tier_preference}</span>`;
            }
            productAffinity += '</div>';
        }
        
        card.innerHTML = `
            <div class="customer-header">
                <div class="customer-name">${customer.first_name}</div>
                <div class="customer-score">CLV: ${Math.round(customer.clv_score * 100)}%</div>
            </div>
            ${productAffinity}
            <div class="customer-details">
                <div class="customer-detail">
                    <strong>ID:</strong> ${customer.customer_id}
                </div>
                <div class="customer-detail">
                    <strong>Email:</strong> ${customer.email}
                </div>
                ${customer.location_city ? `
                    <div class="customer-detail">
                        <strong>Location:</strong> ${customer.location_city}
                    </div>
                ` : ''}
            </div>
            ${cartInfo}
        `;

        return card;
    }

    exportJSON() {
        if (!this.currentSegment) {
            showToast('No segment data to export', 'warning');
            return;
        }

        downloadJSON(this.currentSegment, `segment_${this.currentSegment.segment_id}.json`);
        showToast('Segment exported as JSON', 'success');
    }

    exportCSV() {
        if (!this.currentSegment || !this.currentSegment.customer_profiles) {
            showToast('No customer data to export', 'warning');
            return;
        }

        // Flatten customer data for CSV
        const csvData = this.currentSegment.customer_profiles.map(customer => ({
            customer_id: customer.customer_id,
            email: customer.email,
            first_name: customer.first_name,
            clv_score: customer.clv_score,
            location_city: customer.location_city || '',
            abandoned_cart_id: customer.abandoned_cart_id || '',
            cart_value: customer.cart_value || ''
        }));

        downloadCSV(csvData, `segment_${this.currentSegment.segment_id}_customers.csv`);
        showToast('Customers exported as CSV', 'success');
    }

    copyApiEndpoint() {
        if (!this.currentSegment) {
            showToast('No segment created yet', 'warning');
            return;
        }

        const endpoint = `http://localhost:5000/api/v1/segments/${this.currentSegment.segment_id}/customers`;
        copyToClipboard(endpoint);
    }

    startNewCampaign() {
        // Clear state
        this.currentCampaignObjective = null;
        this.currentAnalysis = null;
        this.currentSegment = null;
        this.selectedTrigger = null;
        this.appliedFilters = {};

        // Clear components
        this.campaignInput.clear();
        this.cooDisplay.clear();
        this.triggerSuggestions.clear();
        this.segmentDashboard.clear();
        this.explainability.clear();

        // Clear filter inputs
        this.clearFilters();

        // Show campaign input, hide all other sections
        this.campaignInputSection.style.display = 'block';
        this.analysisResultsSection.style.display = 'none';
        this.refineSegmentSection.style.display = 'none';
        this.activateSegmentSection.style.display = 'none';
        this.segmentDetailsSection.style.display = 'none';

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });

        showToast('Ready for a new campaign!', 'info');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AetherSegmentApp();
});

