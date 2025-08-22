class AIDiscoveryApp {
    constructor() {
        this.discoveryForm = document.getElementById('discoveryForm');
        this.discoverButton = document.getElementById('discoverButton');
        this.companyForm = document.getElementById('companyForm');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.resultsContent = document.getElementById('resultsContent');
        this.recommendations = document.getElementById('recommendations');
        this.newAnalysisButton = document.getElementById('newAnalysisButton');
        
        this.initEventListeners();
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
        this.newAnalysisButton.addEventListener('click', () => this.resetForm());
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.discoveryForm);
        const companyInfo = {
            companyName: formData.get('companyName'),
            industry: formData.get('industry'),
            companySize: formData.get('companySize'),
            interlocutorRole: formData.get('interlocutorRole')
        };
        
        this.showResults();
        this.setLoading(true);
        
        try {
            const response = await fetch('/ai-recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(companyInfo)
            });
            
            if (!response.ok) {
                throw new Error('Failed to get AI recommendations');
            }
            
            const data = await response.json();
            console.log('Received data:', data);
            this.displayRecommendations(data, companyInfo);
            
        } catch (error) {
            console.error('Error:', error);
            this.showError('Failed to generate AI project recommendations. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }
    
    displayRecommendations(data, companyInfo) {
        console.log('displayRecommendations called with:', data, companyInfo);
        this.recommendations.innerHTML = '';
        this.companyInfo = companyInfo; // Store for ROI calculations
        this.currentProjects = data.projects; // Store projects for ROI calculations
        
        const header = document.createElement('div');
        header.className = 'company-header';
        header.innerHTML = `
            <h3>AI Opportunities for ${companyInfo.companyName}</h3>
            <p><strong>Industry:</strong> ${companyInfo.industry} | <strong>Role:</strong> ${companyInfo.interlocutorRole} | <strong>Size:</strong> ${companyInfo.companySize}</p>
        `;
        this.recommendations.appendChild(header);
        
        if (data.projects && data.projects.length > 0) {
            data.projects.forEach((project, index) => {
                const card = this.createRecommendationCard(project, index);
                this.recommendations.appendChild(card);
            });
        }
        
        if (data.strategic_insights) {
            const insights = document.createElement('div');
            insights.className = 'strategic-insights';
            insights.innerHTML = `
                <h3>Strategic Insights for ${companyInfo.interlocutorRole}</h3>
                <p>${data.strategic_insights}</p>
            `;
            this.recommendations.appendChild(insights);
        }
    }
    
    createRecommendationCard(project, index) {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        
        const priorityClass = this.getPriorityClass(project.priority);
        
        card.innerHTML = `
            <h3>${project.title}</h3>
            <p>${project.description}</p>
            <div class="recommendation-meta">
                <div class="meta-item">
                    <span>Priority:</span>
                    <span class="${priorityClass}">${project.priority}</span>
                </div>
                <div class="meta-item">
                    <span>ROI:</span>
                    <span class="roi-value">${project.expected_roi}</span>
                </div>
                <div class="meta-item">
                    <span>Timeline:</span>
                    <span class="timeline">${project.timeline}</span>
                </div>
                <div class="meta-item">
                    <span>Investment:</span>
                    <span class="investment">${project.investment_range}</span>
                </div>
            </div>
            ${project.business_value ? `<div class="business-value-section"><strong>🎯 Business Value:</strong> <span>${project.business_value}</span></div>` : ''}
            ${project.implementation_notes ? `<div class="implementation-section"><strong>⚙️ Implementation:</strong> <span>${project.implementation_notes}</span></div>` : ''}
            
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
    
    showResults() {
        this.companyForm.style.display = 'none';
        this.resultsContainer.style.display = 'block';
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
    
    resetForm() {
        this.companyForm.style.display = 'block';
        this.resultsContainer.style.display = 'none';
        this.discoveryForm.reset();
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