from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ConversationRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    response: str
    conversation_id: str
    lead_score: Optional[int] = None
    next_steps: Optional[str] = None
    ai_opportunities: Optional[List[str]] = None
    business_impact: Optional[str] = None
    feasibility_risk: Optional[str] = None

class LeadQualification(BaseModel):
    score: int
    reasoning: str
    nextSteps: str
    aiOpportunities: Optional[List[str]] = None
    businessImpact: Optional[str] = None
    feasibilityRisk: Optional[str] = None

class AIProjectRecommendation(BaseModel):
    name: str
    businessProblem: str
    aiSolution: str
    roiEstimate: str
    feasibility: str
    riskLevel: str
    competitorExamples: List[str]
    timeline: str
    successMetrics: List[str]

class ProjectROIInput(BaseModel):
    project_title: str
    current_process_cost: float = Field(..., gt=0, description="Current monthly process cost for this specific project area")
    current_accuracy: float = Field(..., ge=0, le=100, description="Current accuracy/efficiency percentage")
    current_processing_time: float = Field(..., gt=0, description="Current processing time in minutes")
    expected_improvement: float = Field(..., ge=1, le=10, description="Expected improvement multiplier (1.5x, 2x, etc.)")
    implementation_cost: float = Field(..., gt=0, description="Project implementation cost")
    annual_operating_cost: float = Field(..., ge=0, description="Annual operating cost for this project")

class ROICalculatorInput(BaseModel):
    company_name: str = Field(..., min_length=1, description="Company name")
    industry: str = Field(..., min_length=1, description="Industry sector")
    company_size: str = Field(..., min_length=1, description="Company size category")
    use_case: str = Field(..., min_length=1, description="AI use case description")
    current_process_cost: float = Field(..., gt=0, description="Current monthly process cost")
    current_accuracy: float = Field(..., ge=0, le=100, description="Current accuracy percentage")
    current_processing_time: float = Field(..., gt=0, description="Current processing time in minutes")
    expected_ai_accuracy: float = Field(..., ge=0, le=100, description="Expected AI accuracy percentage")
    expected_ai_processing_time: float = Field(..., gt=0, description="Expected AI processing time in minutes")
    ai_implementation_cost: float = Field(..., gt=0, description="AI implementation cost")
    ai_annual_cost: float = Field(..., ge=0, description="Annual AI operating cost")
    consulting_engagement_scale: str = Field(..., min_length=1, description="Consulting engagement scale")

class ROIMetrics(BaseModel):
    annual_savings: float
    revenue_uplift: float
    total_roi_percentage: float
    payback_period_months: float
    net_present_value: float
    cost_benefit_ratio: float

class ROICalculatorResult(BaseModel):
    current_scenario: Dict[str, Any]
    ai_scenario: Dict[str, Any]
    roi_metrics: ROIMetrics
    consulting_pricing: Dict[str, Any]
    business_case_summary: str