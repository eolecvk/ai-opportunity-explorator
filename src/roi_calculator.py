from typing import Dict, Any
from src.models import ROICalculatorInput, ROICalculatorResult, ROIMetrics, ProjectROIInput


class ROICalculator:
    """ROI Calculator for AI implementation projects"""
    
    # Industry-specific cost multipliers and assumptions
    INDUSTRY_MULTIPLIERS = {
        "healthcare": {"cost_multiplier": 1.3, "accuracy_premium": 1.2},
        "financial": {"cost_multiplier": 1.5, "accuracy_premium": 1.4},
        "manufacturing": {"cost_multiplier": 1.1, "accuracy_premium": 1.1},
        "retail": {"cost_multiplier": 1.0, "accuracy_premium": 1.0},
        "insurance": {"cost_multiplier": 1.2, "accuracy_premium": 1.3},
        "telecom": {"cost_multiplier": 1.1, "accuracy_premium": 1.1},
        "default": {"cost_multiplier": 1.0, "accuracy_premium": 1.0}
    }
    
    # Consulting engagement pricing tiers
    CONSULTING_PRICING = {
        "pilot": {"duration_months": 3, "cost_range": "50K-150K", "description": "Proof of concept and initial implementation"},
        "enterprise": {"duration_months": 12, "cost_range": "500K-2M", "description": "Full-scale enterprise deployment"},
        "transformation": {"duration_months": 24, "cost_range": "2M-10M", "description": "Organization-wide AI transformation"}
    }
    
    def calculate_roi(self, input_data: ROICalculatorInput) -> ROICalculatorResult:
        """Calculate comprehensive ROI metrics for AI implementation"""
        
        # Get industry-specific multipliers
        industry_key = input_data.industry.lower().replace(" ", "").replace("-", "")
        multipliers = self.INDUSTRY_MULTIPLIERS.get(industry_key, self.INDUSTRY_MULTIPLIERS["default"])
        
        # Calculate current scenario metrics
        current_scenario = self._calculate_current_scenario(input_data, multipliers)
        
        # Calculate AI scenario metrics
        ai_scenario = self._calculate_ai_scenario(input_data, multipliers)
        
        # Calculate ROI metrics
        roi_metrics = self._calculate_roi_metrics(current_scenario, ai_scenario, input_data)
        
        # Get consulting pricing
        consulting_pricing = self.CONSULTING_PRICING[input_data.consulting_engagement_scale]
        
        # Generate business case summary
        business_case_summary = self._generate_business_case_summary(
            input_data, current_scenario, ai_scenario, roi_metrics, consulting_pricing
        )
        
        return ROICalculatorResult(
            current_scenario=current_scenario,
            ai_scenario=ai_scenario,
            roi_metrics=roi_metrics,
            consulting_pricing=consulting_pricing,
            business_case_summary=business_case_summary
        )
    
    def _calculate_current_scenario(self, input_data: ROICalculatorInput, multipliers: Dict) -> Dict[str, Any]:
        """Calculate metrics for current state without AI"""
        annual_cost = input_data.current_process_cost * 12 * multipliers["cost_multiplier"]
        
        # Calculate error costs (assuming errors cost 5x the process cost)
        error_rate = (100 - input_data.current_accuracy) / 100
        annual_error_cost = annual_cost * error_rate * 5
        
        # Calculate time costs (productivity impact)
        time_cost_factor = input_data.current_processing_time / 60  # hours
        annual_time_cost = annual_cost * time_cost_factor * 0.3  # 30% productivity impact
        
        total_annual_cost = annual_cost + annual_error_cost + annual_time_cost
        
        return {
            "annual_process_cost": annual_cost,
            "annual_error_cost": annual_error_cost,
            "annual_time_cost": annual_time_cost,
            "total_annual_cost": total_annual_cost,
            "accuracy_percentage": input_data.current_accuracy,
            "processing_time_minutes": input_data.current_processing_time
        }
    
    def _calculate_ai_scenario(self, input_data: ROICalculatorInput, multipliers: Dict) -> Dict[str, Any]:
        """Calculate metrics for AI-enabled state"""
        # AI operational costs
        annual_ai_cost = input_data.ai_annual_cost
        
        # Reduced process costs due to automation
        process_cost_reduction = 0.7  # 70% reduction typical for AI automation
        annual_process_cost = (input_data.current_process_cost * 12 * multipliers["cost_multiplier"]) * (1 - process_cost_reduction)
        
        # Reduced error costs due to higher accuracy
        error_rate = (100 - input_data.expected_ai_accuracy) / 100
        annual_error_cost = annual_process_cost * error_rate * 5
        
        # Reduced time costs due to faster processing
        time_cost_factor = input_data.expected_ai_processing_time / 60  # hours
        annual_time_cost = annual_process_cost * time_cost_factor * 0.1  # Reduced impact
        
        total_annual_cost = annual_process_cost + annual_ai_cost + annual_error_cost + annual_time_cost
        
        return {
            "annual_process_cost": annual_process_cost,
            "annual_ai_cost": annual_ai_cost,
            "annual_error_cost": annual_error_cost,
            "annual_time_cost": annual_time_cost,
            "total_annual_cost": total_annual_cost,
            "accuracy_percentage": input_data.expected_ai_accuracy,
            "processing_time_minutes": input_data.expected_ai_processing_time
        }
    
    def _calculate_roi_metrics(self, current: Dict, ai: Dict, input_data: ROICalculatorInput) -> ROIMetrics:
        """Calculate comprehensive ROI metrics"""
        # Annual savings
        annual_savings = current["total_annual_cost"] - ai["total_annual_cost"]
        
        # Revenue uplift (assuming 10% revenue increase from better processes)
        revenue_uplift = annual_savings * 0.1
        
        # Total benefits
        total_annual_benefit = annual_savings + revenue_uplift
        
        # ROI calculation
        total_investment = input_data.ai_implementation_cost
        total_roi_percentage = ((total_annual_benefit - input_data.ai_annual_cost) / total_investment) * 100
        
        # Payback period
        payback_period_months = total_investment / (total_annual_benefit / 12)
        
        # NPV (3-year horizon, 10% discount rate)
        discount_rate = 0.10
        years = 3
        npv = -total_investment
        for year in range(1, years + 1):
            npv += (total_annual_benefit - input_data.ai_annual_cost) / ((1 + discount_rate) ** year)
        
        # Cost-benefit ratio
        total_benefits_3yr = (total_annual_benefit - input_data.ai_annual_cost) * years
        cost_benefit_ratio = total_benefits_3yr / total_investment
        
        return ROIMetrics(
            annual_savings=annual_savings,
            revenue_uplift=revenue_uplift,
            total_roi_percentage=total_roi_percentage,
            payback_period_months=payback_period_months,
            net_present_value=npv,
            cost_benefit_ratio=cost_benefit_ratio
        )
    
    def _generate_business_case_summary(
        self, input_data: ROICalculatorInput, current: Dict, ai: Dict, 
        roi_metrics: ROIMetrics, consulting: Dict
    ) -> str:
        """Generate executive summary for the business case"""
        
        savings_formatted = f"${roi_metrics.annual_savings:,.0f}"
        roi_formatted = f"{roi_metrics.total_roi_percentage:.1f}%"
        payback_formatted = f"{roi_metrics.payback_period_months:.1f} months"
        
        summary = f"""
**Executive Summary: AI Implementation Business Case for {input_data.company_name}**

**Investment Overview:**
• Use Case: {input_data.use_case}
• Implementation Investment: ${input_data.ai_implementation_cost:,.0f}
• Annual Operating Cost: ${input_data.ai_annual_cost:,.0f}
• Consulting Engagement: {consulting['description']} ({consulting['cost_range']})

**Financial Returns:**
• Annual Cost Savings: {savings_formatted}
• Revenue Uplift: ${roi_metrics.revenue_uplift:,.0f}
• Total ROI: {roi_formatted}
• Payback Period: {payback_formatted}
• 3-Year NPV: ${roi_metrics.net_present_value:,.0f}

**Operational Improvements:**
• Accuracy: {input_data.current_accuracy:.1f}% → {input_data.expected_ai_accuracy:.1f}%
• Processing Time: {input_data.current_processing_time:.0f} min → {input_data.expected_ai_processing_time:.0f} min
• Cost Reduction: {((current['total_annual_cost'] - ai['total_annual_cost']) / current['total_annual_cost'] * 100):.1f}%

**Recommendation:**
Based on the analysis, this AI implementation shows strong financial returns with a {payback_formatted} payback period and {roi_formatted} ROI. The project aligns with industry best practices and delivers measurable business value.
"""
        
        return summary.strip()
    
    def calculate_project_roi(self, project_input: ProjectROIInput, industry: str = "default", company_size: str = "medium") -> Dict[str, Any]:
        """Calculate ROI for a specific AI project"""
        
        # Get industry-specific multipliers
        industry_key = industry.lower().replace(" ", "").replace("-", "")
        multipliers = self.INDUSTRY_MULTIPLIERS.get(industry_key, self.INDUSTRY_MULTIPLIERS["default"])
        
        # Current scenario (simplified for project-specific calculation)
        current_monthly_cost = project_input.current_process_cost * multipliers["cost_multiplier"]
        current_annual_cost = current_monthly_cost * 12
        
        # Error/inefficiency costs based on accuracy
        accuracy_factor = project_input.current_accuracy / 100
        inefficiency_cost = current_annual_cost * (1 - accuracy_factor) * 2  # 2x cost for inefficiencies
        
        # Time-based opportunity costs
        time_factor = min(project_input.current_processing_time / 30, 2)  # Cap at 2x for very slow processes
        time_cost = current_annual_cost * time_factor * 0.2  # 20% opportunity cost
        
        total_current_cost = current_annual_cost + inefficiency_cost + time_cost
        
        # AI scenario
        improvement_factor = project_input.expected_improvement
        ai_efficiency = min(project_input.current_accuracy + (100 - project_input.current_accuracy) * 0.6, 99) / 100
        ai_speed_factor = min(project_input.current_processing_time / improvement_factor / 30, 1)
        
        ai_operational_cost = current_annual_cost * 0.4  # 60% reduction typical
        ai_inefficiency_cost = ai_operational_cost * (1 - ai_efficiency) * 0.5  # Much lower error impact
        ai_time_cost = ai_operational_cost * ai_speed_factor * 0.05  # Minimal time costs
        ai_system_cost = project_input.annual_operating_cost
        
        total_ai_cost = ai_operational_cost + ai_inefficiency_cost + ai_time_cost + ai_system_cost
        
        # ROI calculations
        annual_savings = total_current_cost - total_ai_cost
        roi_percentage = ((annual_savings - ai_system_cost) / project_input.implementation_cost) * 100
        payback_months = project_input.implementation_cost / (annual_savings / 12)
        
        # 3-year NPV (10% discount rate)
        net_annual_benefit = annual_savings - ai_system_cost
        npv = -project_input.implementation_cost
        for year in range(1, 4):
            npv += net_annual_benefit / ((1 + 0.10) ** year)
        
        return {
            "project_title": project_input.project_title,
            "current_annual_cost": total_current_cost,
            "ai_annual_cost": total_ai_cost,
            "annual_savings": annual_savings,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
            "three_year_npv": npv,
            "net_annual_benefit": net_annual_benefit,
            "accuracy_improvement": f"{project_input.current_accuracy:.1f}% → {ai_efficiency * 100:.1f}%",
            "speed_improvement": f"{improvement_factor}x faster"
        }