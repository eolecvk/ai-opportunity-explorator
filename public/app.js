class AIDiscoveryApp {
    constructor() {
        this.discoveryForm = document.getElementById('discoveryForm');
        this.discoverButton = document.getElementById('discoverButton');
        this.companyForm = document.getElementById('companyForm');
        
        // Validation phase elements
        this.validationContainer = document.getElementById('validationContainer');
        this.validationLoadingIndicator = document.getElementById('validationLoadingIndicator');
        this.validationContent = document.getElementById('validationContent');
        this.validationMessage = document.getElementById('validationMessage');
        this.suggestionsSection = document.getElementById('suggestionsSection');
        this.suggestionsList = document.getElementById('suggestionsList');
        this.proceedButton = document.getElementById('proceedButton');
        this.backToInputButton = document.getElementById('backToInputButton');
        
        // Research phase elements
        this.researchContainer = document.getElementById('researchContainer');
        this.researchLoadingIndicator = document.getElementById('researchLoadingIndicator');
        this.researchContent = document.getElementById('researchContent');
        this.researchFindingsList = document.getElementById('researchFindingsList');
        this.hypothesesList = document.getElementById('hypothesesList');
        this.validateHypothesesButton = document.getElementById('validateHypothesesButton');
        this.backToFormButton = document.getElementById('backToFormButton');
        
        // Results phase elements
        this.resultsContainer = document.getElementById('resultsContainer');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.resultsContent = document.getElementById('resultsContent');
        this.recommendations = document.getElementById('recommendations');
        this.selectedHypothesesDisplay = document.getElementById('selectedHypothesesDisplay');
        this.selectedHypothesesList = document.getElementById('selectedHypothesesList');
        this.newAnalysisButton = document.getElementById('newAnalysisButton');
        this.backToHypothesesButton = document.getElementById('backToHypothesesButton');
        
        // Application state
        this.companyInfo = null;
        this.validationResult = null;
        this.researchData = null;
        this.selectedHypotheses = [];
        
        this.initEventListeners();
    }
    
    displayResearchFindings(data) {
        // Display research findings
        this.researchFindingsList.innerHTML = '';
        data.research_findings.forEach(finding => {
            const li = document.createElement('li');
            li.textContent = finding;
            this.researchFindingsList.appendChild(li);
        });
        
        // Display hypotheses as selectable options
        this.hypothesesList.innerHTML = '';
        data.strategic_hypotheses.forEach((hypothesis, index) => {
            const hypothesisCard = document.createElement('div');
            hypothesisCard.className = 'hypothesis-card';
            
            hypothesisCard.innerHTML = `
                <label class="hypothesis-checkbox">
                    <input type="checkbox" value="${hypothesis.hypothesis}" data-index="${index}">
                    <div class="hypothesis-content">
                        <h4>${hypothesis.hypothesis}</h4>
                        <p class="rationale"><strong>Rationale:</strong> ${hypothesis.rationale}</p>
                        <p class="ai-opportunity"><strong>AI Opportunity:</strong> ${hypothesis.ai_opportunity}</p>
                    </div>
                </label>
            `;
            
            this.hypothesesList.appendChild(hypothesisCard);
        });
        
        // Add event listeners for checkboxes
        const checkboxes = this.hypothesesList.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateSelectedHypotheses());
        });
    }
    
    updateSelectedHypotheses() {
        const checkboxes = this.hypothesesList.querySelectorAll('input[type="checkbox"]:checked');
        this.selectedHypotheses = Array.from(checkboxes).map(cb => cb.value);
        
        // Enable/disable the validate button based on selection
        this.validateHypothesesButton.disabled = this.selectedHypotheses.length === 0;
    }
    
    async handleHypothesesValidation() {
        if (this.selectedHypotheses.length === 0) {
            alert('Please select at least one hypothesis to continue.');
            return;
        }
        
        this.showResults();
        this.setLoading(true);
        this.updateRecommendationLoadingMessage('Generating AI project recommendations based on validated hypotheses...');
        
        try {
            const response = await fetch('/ai-recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    company_info: this.companyInfo,
                    selected_hypotheses: this.selectedHypotheses
                })
            });
            
            if (!response.ok) {
                if (response.status === 429) {
                    this.updateRecommendationLoadingMessage('API quota exceeded. Implementing exponential backoff retry. This may take up to 10 minutes...');
                }
                throw new Error(`Failed to get AI recommendations (${response.status})`);
            }
            
            const data = await response.json();
            console.log('Recommendations data:', data);
            this.displayRecommendations(data, this.companyInfo);
            
        } catch (error) {
            console.error('Error:', error);
            const errorMessage = error.message.includes('429')
                ? 'API quota exceeded. The system has attempted multiple retries with exponential backoff. Please try again in a few hours when the quota resets.'
                : 'Failed to generate AI project recommendations. Please try again.';
            this.showError(errorMessage);
        } finally {
            this.setLoading(false);
        }
    }
    
    showResearchError(message) {
        this.researchContent.innerHTML = `
            <div class="error-message" style="color: #dc3545; text-align: center; padding: 20px;">
                <h3>Error</h3>
                <p>${message}</p>
                <button onclick="location.reload()" class="secondary-button">Try Again</button>
            </div>
        `;
    }
    
    formatCurrency(value) {
        if (value >= 1000000) {
            return `$${(value / 1000000).toFixed(1)}M USD`;
        } else if (value >= 1000) {
            return `$${(value / 1000).toFixed(0)}K USD`;
        } else {
            return `$${value.toLocaleString()}`;
        }
    }
    
    generateROIForm(project, index) {
        // Check if project has custom ROI calculator
        if (project.roi_calculator && project.roi_calculator.variables) {
            return this.generateCatalogROIForm(project, index);
        } else {
            return this.generateDefaultROIForm(project, index);
        }
    }
    
    generateCatalogROIForm(project, index) {
        const roiConfig = project.roi_calculator;
        const variables = roiConfig.variables;
        
        let formHTML = `<form class="roi-form catalog-roi-form" data-project-index="${index}" data-project-title="${project.title}">`;
        
        // Generate input fields for each variable
        const variableKeys = Object.keys(variables);
        for (let i = 0; i < variableKeys.length; i += 2) {
            formHTML += '<div class="roi-input-row">';
            
            // First variable in the row
            const var1 = variableKeys[i];
            const config1 = variables[var1];
            formHTML += this.generateVariableInput(var1, config1);
            
            // Second variable in the row (if exists)
            if (i + 1 < variableKeys.length) {
                const var2 = variableKeys[i + 1];
                const config2 = variables[var2];
                formHTML += this.generateVariableInput(var2, config2);
            }
            
            formHTML += '</div>';
        }
        
        formHTML += `
            <button type="submit" class="calculate-roi-btn">Calculate Project-Specific ROI</button>
        </form>`;
        
        return formHTML;
    }
    
    generateVariableInput(varName, config) {
        const inputType = config.type === 'currency' ? 'number' : config.type;
        const step = config.step || (config.type === 'currency' ? 100 : 1);
        const prefix = config.type === 'currency' ? '$' : '';
        const suffix = config.type === 'currency' ? 'K' : '';
        
        return `
            <div class="roi-input-group">
                <label title="${config.tooltip || ''}">${config.label}</label>
                <div class="input-with-prefix">
                    ${prefix ? `<span class="input-prefix">${prefix}</span>` : ''}
                    <input 
                        type="${inputType}" 
                        name="${varName}" 
                        placeholder="${config.default}" 
                        value="${config.default}"
                        min="${config.min || 0}" 
                        max="${config.max || ''}" 
                        step="${step}" 
                        required>
                    ${suffix ? `<span class="input-suffix">${suffix}</span>` : ''}
                </div>
                ${config.tooltip ? `<small class="tooltip-text">${config.tooltip}</small>` : ''}
            </div>
        `;
    }
    
    generateDefaultROIForm(project, index) {
        return `
            <form class="roi-form" data-project-index="${index}" data-project-title="${project.title}">
                <div class="roi-input-row">
                    <div class="roi-input-group">
                        <label>Current Monthly Process Cost ($)</label>
                        <input type="number" name="current_process_cost" placeholder="25000" required step="1000">
                    </div>
                    <div class="roi-input-group">
                        <label>Current Accuracy/Efficiency (%)</label>
                        <input type="number" name="current_accuracy" placeholder="80" required min="0" max="100" step="0.1">
                    </div>
                </div>
                <div class="roi-input-row">
                    <div class="roi-input-group">
                        <label>Current Processing Time (minutes)</label>
                        <input type="number" name="current_processing_time" placeholder="30" required min="1" step="0.1">
                    </div>
                    <div class="roi-input-group">
                        <label>Expected Improvement Factor</label>
                        <select name="expected_improvement" required>
                            <option value="">Select improvement</option>
                            <option value="1.5">1.5x improvement</option>
                            <option value="2">2x improvement</option>
                            <option value="2.5">2.5x improvement</option>
                            <option value="3">3x improvement</option>
                            <option value="4">4x improvement</option>
                            <option value="5">5x improvement</option>
                        </select>
                    </div>
                </div>
                <div class="roi-input-row">
                    <div class="roi-input-group">
                        <label>Implementation Cost ($)</label>
                        <input type="number" name="implementation_cost" placeholder="200000" required step="10000">
                    </div>
                    <div class="roi-input-group">
                        <label>Annual Operating Cost ($)</label>
                        <input type="number" name="annual_operating_cost" placeholder="50000" required step="1000">
                    </div>
                </div>
                <button type="submit" class="calculate-roi-btn">Calculate ROI</button>
            </form>
        `;
    }
    
    initEventListeners() {
        this.discoveryForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        this.proceedButton.addEventListener('click', () => this.proceedToAnalysis());
        this.backToInputButton.addEventListener('click', () => this.showCompanyForm());
        this.validateHypothesesButton.addEventListener('click', () => this.handleHypothesesValidation());
        this.backToFormButton.addEventListener('click', () => this.showCompanyForm());
        this.newAnalysisButton.addEventListener('click', () => this.resetForm());
        this.backToHypothesesButton.addEventListener('click', () => this.showResearchStep());
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.discoveryForm);
        const companyName = formData.get('companyName');
        
        if (!companyName || !companyName.trim()) {
            alert('Please enter a company name.');
            return;
        }
        
        this.showValidationStep();
        this.setValidationLoading(true);
        this.updateValidationLoadingMessage('Validating company name...');
        
        try {
            // First, validate the company name
            const validationResponse = await fetch('/validate-company', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ company_name: companyName })
            });
            
            if (!validationResponse.ok) {
                if (validationResponse.status === 429) {
                    this.updateValidationLoadingMessage('API rate limit reached. Retrying with backoff strategy...');
                    // Let it retry automatically via backend
                }
                throw new Error(`Failed to validate company name (${validationResponse.status})`);
            }
            
            this.validationResult = await validationResponse.json();
            console.log('Validation result:', this.validationResult);
            this.displayValidationResult(this.validationResult);
            
        } catch (error) {
            console.error('Error:', error);
            const errorMessage = error.message.includes('429') 
                ? 'API quota exceeded. The system is automatically retrying. This may take a few minutes...'
                : 'Failed to validate company name. Please try again.';
            this.showValidationError(errorMessage);
        } finally {
            this.setValidationLoading(false);
        }
    }

    async proceedToAnalysis() {
        const companyName = this.validationResult.company_name || this.validationResult.original_name;
        
        this.showResearchStep();
        this.setResearchLoading(true);
        this.updateResearchLoadingMessage('Analyzing company details...');
        
        try {
            // Infer company details from the validated name
            const detailsResponse = await fetch('/infer-company-details', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ company_name: companyName })
            });
            
            if (!detailsResponse.ok) {
                if (detailsResponse.status === 429) {
                    this.updateResearchLoadingMessage('API rate limit reached. Applying exponential backoff retry strategy...');
                }
                throw new Error(`Failed to analyze company details (${detailsResponse.status})`);
            }
            
            const companyDetails = await detailsResponse.json();
            
            // Build complete company info with inferred details
            this.companyInfo = {
                companyName: companyName,
                industry: companyDetails.industry,
                companySize: companyDetails.company_size,
                description: companyDetails.description,
                confidence: companyDetails.confidence
            };
            
            // Now do the pre-engagement analysis
            this.updateResearchLoadingMessage('Conducting pre-engagement research and hypothesis generation...');
            
            const analysisResponse = await fetch('/pre-engagement-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.companyInfo)
            });
            
            if (!analysisResponse.ok) {
                if (analysisResponse.status === 429) {
                    this.updateResearchLoadingMessage('API quota reached. Retrying with intelligent backoff. Please wait as this may take several minutes...');
                }
                throw new Error(`Failed to get pre-engagement analysis (${analysisResponse.status})`);
            }
            
            this.researchData = await analysisResponse.json();
            console.log('Research data:', this.researchData);
            this.displayResearchFindings(this.researchData);
            
        } catch (error) {
            console.error('Error:', error);
            const errorMessage = error.message.includes('429')
                ? 'API quota exceeded. The system is automatically retrying with exponential backoff. This process may take several minutes due to rate limits.'
                : 'Failed to analyze company. Please check the company name and try again.';
            this.showResearchError(errorMessage);
        } finally {
            this.setResearchLoading(false);
        }
    }
    
    displayRecommendations(data, companyInfo) {
        console.log('displayRecommendations called with:', data, companyInfo);
        this.recommendations.innerHTML = '';
        this.companyInfo = companyInfo; // Store for ROI calculations
        
        // Combine aligned and filler projects for ROI calculations
        this.currentProjects = [...(data.aligned_projects || []), ...(data.filler_projects || [])];
        
        const header = document.createElement('div');
        header.className = 'company-header';
        header.innerHTML = `
            <h2>${companyInfo.companyName}</h2>
            <p><strong>Industry:</strong> ${companyInfo.industry}</p>
            ${companyInfo.description ? `<p class="company-description">${companyInfo.description}</p>` : ''}
        `;
        this.recommendations.appendChild(header);
        
        // Display selected hypotheses if any
        if (this.selectedHypotheses.length > 0) {
            this.selectedHypothesesDisplay.style.display = 'block';
            this.selectedHypothesesList.innerHTML = '';
            this.selectedHypotheses.forEach(hypothesis => {
                const li = document.createElement('li');
                li.textContent = hypothesis;
                this.selectedHypothesesList.appendChild(li);
            });
        } else {
            this.selectedHypothesesDisplay.style.display = 'none';
        }
        
        // Display aligned projects first (with hypothesis alignment)
        if (data.aligned_projects && data.aligned_projects.length > 0) {
            const alignedHeader = document.createElement('div');
            alignedHeader.className = 'section-header';
            alignedHeader.innerHTML = `<h3>🎯 Recommended Projects</h3>`;
            this.recommendations.appendChild(alignedHeader);
            
            data.aligned_projects.forEach((project, index) => {
                const card = this.createRecommendationCard(project, index, true);
                this.recommendations.appendChild(card);
            });
        }
        
        // Display filler projects behind "Explore additional opportunities" button
        if (data.filler_projects && data.filler_projects.length > 0) {
            const fillerSection = document.createElement('div');
            fillerSection.className = 'filler-projects-section';
            fillerSection.innerHTML = `
                <div class="explore-more-button-container">
                    <button class="explore-more-button" onclick="this.parentElement.nextElementSibling.classList.toggle('hidden'); this.textContent = this.textContent.includes('Show') ? '🔼 Hide Additional Projects' : '🔽 Show Additional Projects';">
                        🔽 Show Additional Projects (${data.filler_projects.length})
                    </button>
                </div>
                <div class="additional-opportunities hidden">
                    <h4>Additional Projects</h4>
                    <p style="color: #666; font-size: 0.9em; margin-bottom: 20px;">These projects may provide additional value to your organization.</p>
                </div>
            `;
            this.recommendations.appendChild(fillerSection);
            
            const additionalContainer = fillerSection.querySelector('.additional-opportunities');
            data.filler_projects.forEach((project, index) => {
                const adjustedIndex = (data.aligned_projects?.length || 0) + index;
                const card = this.createRecommendationCard(project, adjustedIndex, false);
                additionalContainer.appendChild(card);
            });
        }
        
    }
    
    createRecommendationCard(project, index, isAligned = true) {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        
        const priorityClass = this.getPriorityClass(project.priority);
        
        card.innerHTML = `
            <h3>${project.title}</h3>
            <p>${project.description}</p>
            <div class="recommendation-meta">
                <div class="meta-item">
                    <span>Timeline:</span>
                    <span class="timeline">${project.timeline}</span>
                </div>
                <div class="meta-item">
                    <span>Investment:</span>
                    <span class="investment">${project.investment_range}</span>
                </div>
            </div>
            ${isAligned && project.hypothesis_alignment ? `<div class="hypothesis-alignment-section"><strong>🔬 Hypothesis Alignment:</strong> <span>${project.hypothesis_alignment}</span></div>` : ''}
            
            <div class="roi-calculator-section">
                <button class="roi-toggle-btn" onclick="this.parentElement.parentElement.querySelector('.roi-calculator').classList.toggle('hidden')">
                    📊 Calculate Detailed ROI & Business Case
                </button>
                <div class="roi-calculator hidden" id="roi-calc-${index}">
                    <h4>ROI Calculator for "${project.title}"</h4>
                    ${this.generateROIForm(project, index)}
                    <div class="roi-results hidden" id="roi-results-${index}"></div>
                </div>
            </div>
        `;
        
        // Add event listener for the form
        const form = card.querySelector('.roi-form');
        form.addEventListener('submit', (e) => this.handleROICalculation(e));
        
        return card;
    }
    
    getPriorityClass(priority) {
        switch(priority?.toLowerCase()) {
            case 'critical': return 'priority-critical';
            case 'high': return 'priority-high';
            case 'medium': return 'priority-medium';
            case 'low': return 'priority-low';
            default: return '';
        }
    }
    
    showValidationStep() {
        this.companyForm.style.display = 'none';
        this.validationContainer.style.display = 'block';
        this.researchContainer.style.display = 'none';
        this.resultsContainer.style.display = 'none';
    }
    
    showResearchStep() {
        this.companyForm.style.display = 'none';
        this.validationContainer.style.display = 'none';
        this.resultsContainer.style.display = 'none';
        this.researchContainer.style.display = 'block';
    }
    
    showResults() {
        this.companyForm.style.display = 'none';
        this.validationContainer.style.display = 'none';
        this.researchContainer.style.display = 'none';
        this.resultsContainer.style.display = 'block';
    }
    
    showCompanyForm() {
        this.companyForm.style.display = 'block';
        this.validationContainer.style.display = 'none';
        this.researchContainer.style.display = 'none';
        this.resultsContainer.style.display = 'none';
    }
    
    setLoading(loading) {
        if (loading) {
            this.loadingIndicator.style.display = 'block';
            this.resultsContent.style.display = 'none';
        } else {
            this.loadingIndicator.style.display = 'none';
            this.resultsContent.style.display = 'block';
        }
    }
    
    setValidationLoading(loading) {
        if (loading) {
            this.validationLoadingIndicator.style.display = 'block';
            this.validationContent.style.display = 'none';
        } else {
            this.validationLoadingIndicator.style.display = 'none';
            this.validationContent.style.display = 'block';
        }
    }
    
    setResearchLoading(loading) {
        if (loading) {
            this.researchLoadingIndicator.style.display = 'block';
            this.researchContent.style.display = 'none';
        } else {
            this.researchLoadingIndicator.style.display = 'none';
            this.researchContent.style.display = 'block';
        }
    }
    
    updateValidationLoadingMessage(message) {
        const loadingText = this.validationLoadingIndicator.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }
    
    updateResearchLoadingMessage(message) {
        const loadingText = this.researchLoadingIndicator.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }
    
    updateRecommendationLoadingMessage(message) {
        const loadingText = this.loadingIndicator.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
    }
    
    displayValidationResult(result) {
        const messageClass = result.status === 'valid' ? 'success' : 
                            result.status === 'ambiguous' ? 'warning' : 'error';
        
        // Build confidence and sources display
        let confidenceDisplay = '';
        let sourcesDisplay = '';
        
        if (result.confidence !== undefined) {
            const confidenceLevel = result.confidence >= 80 ? 'High' : 
                                  result.confidence >= 50 ? 'Medium' : 'Low';
            const confidenceColor = result.confidence >= 80 ? '#28a745' : 
                                   result.confidence >= 50 ? '#ffc107' : '#dc3545';
            
            confidenceDisplay = `
                <div class="confidence-indicator" style="margin-top: 10px;">
                    <span style="color: ${confidenceColor}; font-weight: bold;">
                        ${confidenceLevel} Confidence (${result.confidence}%)
                    </span>
                </div>
            `;
        }
        
        if (result.sources && result.sources.length > 0) {
            sourcesDisplay = `
                <div class="validation-sources" style="margin-top: 8px; font-size: 0.9em; color: #666;">
                    <strong>Verified via:</strong> ${result.sources.join(', ')}
                </div>
            `;
        }
        
        this.validationMessage.innerHTML = `
            <div class="validation-status ${messageClass}">
                <h3>${result.status === 'valid' ? '✓' : result.status === 'ambiguous' ? '⚠️' : '❌'} ${result.message}</h3>
                ${confidenceDisplay}
                ${sourcesDisplay}
            </div>
        `;
        
        if (result.status === 'ambiguous' && result.suggestions.length > 0) {
            this.suggestionsSection.style.display = 'block';
            this.suggestionsList.innerHTML = '<h4>Please select the company you meant:</h4>';
            
            result.suggestions.forEach(suggestion => {
                const suggestionButton = document.createElement('button');
                suggestionButton.className = 'suggestion-button';
                suggestionButton.textContent = suggestion;
                suggestionButton.addEventListener('click', () => {
                    this.validationResult = {
                        status: 'valid',
                        message: `Selected: ${suggestion}`,
                        company_name: suggestion
                    };
                    this.displayValidationResult(this.validationResult);
                });
                this.suggestionsList.appendChild(suggestionButton);
            });
        } else {
            this.suggestionsSection.style.display = 'none';
        }
        
        // Show/hide proceed button based on validation status
        if (result.status === 'valid') {
            this.proceedButton.style.display = 'block';
        } else {
            this.proceedButton.style.display = 'none';
        }
    }
    
    showValidationError(message) {
        this.validationContent.innerHTML = `
            <div class="error-message" style="color: #dc3545; text-align: center; padding: 20px;">
                <h3>Error</h3>
                <p>${message}</p>
                <button onclick="location.reload()" class="secondary-button">Try Again</button>
            </div>
        `;
    }
    
    resetForm() {
        this.companyForm.style.display = 'block';
        this.validationContainer.style.display = 'none';
        this.researchContainer.style.display = 'none';
        this.resultsContainer.style.display = 'none';
        this.discoveryForm.reset();
        this.companyInfo = null;
        this.validationResult = null;
        this.researchData = null;
        this.selectedHypotheses = [];
    }
    
    async handleROICalculation(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const projectIndex = form.dataset.projectIndex;
        const projectTitle = form.dataset.projectTitle;
        
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Calculating...';
        submitButton.disabled = true;
        
        try {
            let roiResult;
            
            if (form.classList.contains('catalog-roi-form')) {
                // Handle catalog-based ROI calculation
                roiResult = await this.handleCatalogROICalculation(form, formData, projectIndex);
            } else {
                // Handle default ROI calculation
                roiResult = await this.handleDefaultROICalculation(form, formData, projectTitle);
            }
            
            this.displayROIResults(roiResult, projectIndex);
            
        } catch (error) {
            console.error('ROI Calculation Error:', error);
            const resultsDiv = document.getElementById(`roi-results-${projectIndex}`);
            resultsDiv.innerHTML = `
                <div style="color: #dc3545; padding: 15px; text-align: center;">
                    <strong>Error calculating ROI</strong><br>
                    Please check your inputs and try again.
                </div>
            `;
            resultsDiv.classList.remove('hidden');
        } finally {
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    }
    
    async handleCatalogROICalculation(form, formData, projectIndex) {
        // Get the project data to access ROI calculator config
        const projectCard = form.closest('.recommendation-card');
        const projectTitle = form.dataset.projectTitle;
        
        // Find the project data from our stored recommendations
        let projectData = null;
        if (this.currentProjects) {
            projectData = this.currentProjects.find(p => p.title === projectTitle);
        }
        
        if (!projectData || !projectData.roi_calculator) {
            throw new Error('Project ROI calculator configuration not found');
        }
        
        // Collect variable values from form
        const variableValues = {};
        const roiConfig = projectData.roi_calculator;
        
        for (const varName of Object.keys(roiConfig.variables)) {
            const value = parseFloat(formData.get(varName));
            if (isNaN(value)) {
                throw new Error(`Invalid value for ${varName}`);
            }
            
            // Convert currency values from K to actual values
            if (roiConfig.variables[varName].type === 'currency') {
                variableValues[varName] = value * 1000;
            } else {
                variableValues[varName] = value;
            }
        }
        
        const response = await fetch('/catalog-roi', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                roi_config: roiConfig,
                variable_values: variableValues
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to calculate catalog ROI');
        }
        
        return await response.json();
    }
    
    async handleDefaultROICalculation(form, formData, projectTitle) {
        const roiInput = {
            project_title: projectTitle,
            current_process_cost: parseFloat(formData.get('current_process_cost')),
            current_accuracy: parseFloat(formData.get('current_accuracy')),
            current_processing_time: parseFloat(formData.get('current_processing_time')),
            expected_improvement: parseFloat(formData.get('expected_improvement')),
            implementation_cost: parseFloat(formData.get('implementation_cost')),
            annual_operating_cost: parseFloat(formData.get('annual_operating_cost'))
        };
        
        const response = await fetch(`/project-roi?industry=${encodeURIComponent(this.companyInfo.industry)}&company_size=${encodeURIComponent(this.companyInfo.companySize)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(roiInput)
        });
        
        if (!response.ok) {
            throw new Error('Failed to calculate ROI');
        }
        
        return await response.json();
    }
    
    displayROIResults(result, projectIndex) {
        const resultsDiv = document.getElementById(`roi-results-${projectIndex}`);
        
        if (result.variables_used) {
            // This is a catalog-based ROI result
            this.displayCatalogROIResults(result, resultsDiv);
        } else {
            // This is a default ROI result
            this.displayDefaultROIResults(result, resultsDiv);
        }
        
        resultsDiv.classList.remove('hidden');
    }
    
    displayCatalogROIResults(result, resultsDiv) {
        const roiColor = result.roi_percentage > 200 ? '#28a745' : result.roi_percentage > 100 ? '#ffc107' : '#dc3545';
        
        resultsDiv.innerHTML = `
            <div class="roi-results-content">
                <h5>📈 Project-Specific ROI Analysis</h5>
                <div class="roi-metrics-grid">
                    <div class="roi-metric">
                        <div class="roi-metric-value" style="color: ${roiColor};">${result.roi_percentage.toFixed(1)}%</div>
                        <div class="roi-metric-label">Total ROI</div>
                    </div>
                    <div class="roi-metric">
                        <div class="roi-metric-value">${this.formatCurrency(result.annual_benefit)}</div>
                        <div class="roi-metric-label">Annual Benefit</div>
                    </div>
                    <div class="roi-metric">
                        <div class="roi-metric-value">${result.breakeven_months ? result.breakeven_months.toFixed(1) + ' months' : 'N/A'}</div>
                        <div class="roi-metric-label">Breakeven Period</div>
                    </div>
                    <div class="roi-metric">
                        <div class="roi-metric-value">${this.formatCurrency(result.three_year_npv)}</div>
                        <div class="roi-metric-label">3-Year NPV</div>
                    </div>
                </div>
                
                <div class="variables-used">
                    <h6>📊 Variables Used in Calculation</h6>
                    <div class="variables-grid">
                        ${Object.entries(result.variables_used)
                            .filter(([key, value]) => key !== 'implementation_cost' && key !== 'ongoing_cost')
                            .map(([key, value]) => `
                                <div class="variable-item">
                                    <span class="variable-name">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                                    <span class="variable-value">${typeof value === 'number' && value >= 1000 ? this.formatCurrency(value) : value}</span>
                                </div>
                            `).join('')}
                    </div>
                </div>
                
                <div class="business-case-summary">
                    <h6>💼 Executive Summary</h6>
                    <p>This project delivers <strong>${result.roi_percentage.toFixed(0)}% ROI</strong> 
                    ${result.breakeven_months ? `with a breakeven period of <strong>${result.breakeven_months.toFixed(1)} months</strong>` : ''}. 
                    The implementation generates <strong>${this.formatCurrency(result.annual_benefit)}</strong> in annual benefits 
                    with a 3-year NPV of <strong>${this.formatCurrency(result.three_year_npv)}</strong>.</p>
                </div>
            </div>
        `;
    }
    
    displayDefaultROIResults(result, resultsDiv) {
        const roiColor = result.roi_percentage > 200 ? '#28a745' : result.roi_percentage > 100 ? '#ffc107' : '#dc3545';
        
        resultsDiv.innerHTML = `
            <div class="roi-results-content">
                <h5>📈 ROI Analysis Results</h5>
                <div class="roi-metrics-grid">
                    <div class="roi-metric">
                        <div class="roi-metric-value" style="color: ${roiColor};">${result.roi_percentage.toFixed(1)}%</div>
                        <div class="roi-metric-label">Total ROI</div>
                    </div>
                    <div class="roi-metric">
                        <div class="roi-metric-value">${this.formatCurrency(result.annual_savings)}</div>
                        <div class="roi-metric-label">Annual Savings</div>
                    </div>
                    <div class="roi-metric">
                        <div class="roi-metric-value">${result.payback_months.toFixed(1)} months</div>
                        <div class="roi-metric-label">Payback Period</div>
                    </div>
                    <div class="roi-metric">
                        <div class="roi-metric-value">${this.formatCurrency(result.three_year_npv)}</div>
                        <div class="roi-metric-label">3-Year NPV</div>
                    </div>
                </div>
                
                <div class="roi-comparison">
                    <h6>Without AI vs With AI</h6>
                    <div class="comparison-row">
                        <span>Annual Cost:</span>
                        <span class="current-cost">${this.formatCurrency(result.current_annual_cost)}</span>
                        <span>→</span>
                        <span class="ai-cost">${this.formatCurrency(result.ai_annual_cost)}</span>
                    </div>
                    <div class="comparison-row">
                        <span>Performance:</span>
                        <span class="improvement">${result.accuracy_improvement}</span>
                        <span>|</span>
                        <span class="improvement">${result.speed_improvement}</span>
                    </div>
                </div>
                
                <div class="business-case-summary">
                    <h6>💼 Executive Summary</h6>
                    <p>This ${result.project_title} project delivers <strong>${result.roi_percentage.toFixed(0)}% ROI</strong> 
                    with a payback period of <strong>${result.payback_months.toFixed(1)} months</strong>. 
                    The initiative will save <strong>${this.formatCurrency(result.annual_savings)}</strong> annually while 
                    improving ${result.accuracy_improvement.split(' → ')[0]} accuracy to ${result.accuracy_improvement.split(' → ')[1]} 
                    and achieving ${result.speed_improvement} processing speed.</p>
                </div>
            </div>
        `;
    }

    showError(message) {
        this.recommendations.innerHTML = `
            <div class="error-message" style="color: #dc3545; text-align: center; padding: 20px;">
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new AIDiscoveryApp();
});