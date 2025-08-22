import google.genai as genai
import json
import os
from typing import Dict, List, Any

class GeminiAIClient:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = 'gemini-1.5-flash'
    
    async def generate_response(self, user_message: str, context: Dict = None) -> str:
        try:
            system_prompt = self._build_system_prompt(context or {})
            
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            
            if not response or not response.text:
                raise Exception("Empty response from AI model")
            
            return response.text.strip()
        except Exception as e:
            print(f"AI API Error: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
    
    def _build_system_prompt(self, context: Dict) -> str:
        return f"""You are an expert AI project sales consultant working for Capgemini, specializing in identifying and selling high-value AI transformation projects to enterprise clients.

Your expertise includes:
1. **AI Project Discovery**: Identify high-ROI AI opportunities in client operations
2. **Feasibility Assessment**: Evaluate technical complexity, data readiness, and implementation risk
3. **Competitive Intelligence**: Reference proven AI implementations at competitor companies
4. **Business Case Development**: Calculate ROI, timeline, and resource requirements
5. **Risk Mitigation**: Address concerns about AI adoption and change management

**Target AI Project Categories** (focus on proven, high-ROI implementations):
- **Customer Experience**: Chatbots, recommendation engines, personalized marketing
- **Operations**: Predictive maintenance, supply chain optimization, demand forecasting
- **Finance**: Fraud detection, automated reconciliation, risk assessment
- **HR**: Resume screening, performance prediction, employee sentiment analysis
- **Sales & Marketing**: Lead scoring, price optimization, customer churn prediction
- **Manufacturing**: Quality control, process optimization, anomaly detection

**Qualification Framework**:
- Industry and company size (focus on 500+ employees)
- Current data infrastructure and digital maturity
- Existing pain points that AI can solve
- Budget range ($50K - $2M+ for AI projects)
- Decision-making process and timeline
- Previous experience with AI/ML initiatives

**Sales Approach**:
- Start with business problems, not AI technology
- Reference specific competitor successes in their industry
- Emphasize proven, low-risk AI applications first
- Build roadmap from quick wins to transformational projects
- Address data privacy, governance, and ethical AI concerns proactively

Current conversation context: {json.dumps(context)}

Always lead with business impact and proven results. Ask strategic questions to uncover AI opportunities the client may not have considered."""

    async def qualify_lead(self, conversation: List[Dict]) -> Dict[str, Any]:
        qualification_prompt = f"""Analyze this conversation for AI project sales qualification. Score the lead from 1-10 based on:

**Scoring Criteria:**
- Company size and industry (2 points): 500+ employees in AI-suitable industries
- Data maturity (2 points): Existing data infrastructure, analytics capabilities
- Business pain points (2 points): Clear problems that AI can solve with high ROI
- Budget and authority (2 points): $50K+ budget, access to decision makers
- Timeline and urgency (1 point): Defined timeline, competitive pressure
- AI readiness (1 point): Previous tech adoption, change management capability

**AI Project Opportunity Assessment:**
Identify specific AI projects with high potential based on:
- High ROI potential (>3x return within 18 months)
- High feasibility (proven technology, available data)
- Low risk (incremental implementation, clear success metrics)
- Competitive advantage (competitors already implementing similar solutions)

Conversation: {json.dumps(conversation)}

Respond in JSON format:
{{
  "score": <number 1-10>,
  "reasoning": "<assessment of AI project readiness>",
  "aiOpportunities": ["<specific AI project 1>", "<specific AI project 2>"],
  "businessImpact": "<estimated ROI and business benefits>",
  "feasibilityRisk": "<technical complexity and risk assessment>",
  "nextSteps": "<recommended next steps for AI project development>"
}}"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=qualification_prompt
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Lead qualification error: {e}")
            return {
                "score": 5,
                "reasoning": "Unable to qualify due to technical error",
                "aiOpportunities": [],
                "businessImpact": "Assessment pending",
                "feasibilityRisk": "Assessment pending",
                "nextSteps": "Continue conversation to gather more information about AI readiness"
            }

    async def generate_ai_project_recommendations(self, company_info: Dict) -> Dict[str, Any]:
        """Generate specific AI project recommendations based on company profile and role"""
        
        role_focus = self._get_role_specific_focus(company_info.get('interlocutorRole', ''))
        industry_specifics = self._get_industry_specifics(company_info.get('industry', ''))
        
        recommendation_prompt = f"""You are an AI project consultant analyzing a company for AI transformation opportunities.

Company Profile:
- Company: {company_info.get('companyName', 'N/A')}
- Industry: {company_info.get('industry', 'N/A')}
- Size: {company_info.get('companySize', 'N/A')}
- Decision Maker Role: {company_info.get('interlocutorRole', 'N/A')}

{role_focus}

{industry_specifics}

Generate 3-4 specific AI project recommendations that are:
1. Highly relevant to the decision maker's priorities
2. Proven in the industry with strong ROI
3. Appropriate for the company size
4. Prioritized by implementation ease and business impact

For each project, provide:
- **Title**: Specific, actionable project name
- **Description**: Clear business problem and AI solution (2-3 sentences)
- **Priority**: High/Medium/Low based on role relevance and ROI
- **Expected ROI**: Specific percentage or multiple (e.g., "300% ROI" or "2.5x investment")
- **Timeline**: Implementation duration (e.g., "3-6 months", "6-12 months")
- **Investment Range**: Estimated cost (e.g., "$50K-$150K", "$200K-$500K")
- **Business Value**: Key benefits for this specific role
- **Implementation Notes**: Brief technical approach and requirements

Also provide strategic insights specifically tailored to the decision maker's role and concerns.

Respond in JSON format:
{{
  "projects": [
    {{
      "title": "<specific project name>",
      "description": "<2-3 sentence description of problem and solution>",
      "priority": "<High/Medium/Low>",
      "expected_roi": "<specific ROI estimate>",
      "timeline": "<implementation duration>",
      "investment_range": "<cost estimate>",
      "business_value": "<key benefits for this role>",
      "implementation_notes": "<technical approach and requirements>"
    }}
  ],
  "strategic_insights": "<2-3 sentences of strategic advice specifically for this role and industry>"
}}"""

        try:
            # Check if we have a valid API key
            if not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your_gemini_api_key_here':
                # Return demo recommendations when no API key is configured
                return self._get_demo_recommendations(company_info)
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=recommendation_prompt
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"AI project recommendation error: {e}")
            # Fallback to demo recommendations
            return self._get_demo_recommendations(company_info)
    
    def _get_demo_recommendations(self, company_info: Dict) -> Dict[str, Any]:
        """Generate demo recommendations when API is not available"""
        role = company_info.get('interlocutorRole', 'CEO')
        industry = company_info.get('industry', 'Technology')
        company_name = company_info.get('companyName', 'Your Company')
        
        # Role-specific demo projects
        demo_projects = {
            "CEO": [
                {
                    "title": "AI-Powered Revenue Optimization Platform",
                    "description": "Implement machine learning algorithms to optimize pricing strategies and identify new revenue opportunities across product lines. This platform analyzes market trends, competitor pricing, and customer behavior to maximize profitability.",
                    "priority": "High",
                    "expected_roi": "400% ROI within 18 months",
                    "timeline": "6-9 months",
                    "investment_range": "$300K-$500K",
                    "business_value": "Increased revenue growth, competitive advantage, data-driven strategic decisions",
                    "implementation_notes": "Requires integration with existing CRM and ERP systems, advanced analytics platform deployment"
                },
                {
                    "title": "Intelligent Customer Churn Prevention",
                    "description": "Deploy predictive analytics to identify at-risk customers and automatically trigger personalized retention campaigns. Uses behavioral data and engagement patterns to predict churn probability.",
                    "priority": "High",
                    "expected_roi": "250% ROI within 12 months",
                    "timeline": "4-6 months",
                    "investment_range": "$150K-$300K",
                    "business_value": "Reduced customer acquisition costs, improved customer lifetime value, higher retention rates",
                    "implementation_notes": "Leverages existing customer data, requires marketing automation integration"
                },
                {
                    "title": "Strategic Market Intelligence Dashboard",
                    "description": "Automated competitive analysis and market trend monitoring using AI to scan news, social media, and industry reports. Provides real-time insights for strategic decision making.",
                    "priority": "Medium",
                    "expected_roi": "150% ROI within 12 months",
                    "timeline": "3-5 months",
                    "investment_range": "$100K-$200K",
                    "business_value": "Faster strategic decisions, competitive advantage, market opportunity identification",
                    "implementation_notes": "Web scraping, NLP processing, business intelligence dashboard integration"
                }
            ],
            "CFO": [
                {
                    "title": "Automated Financial Risk Assessment",
                    "description": "Machine learning system to automatically assess credit risk, detect fraudulent transactions, and monitor financial anomalies in real-time. Reduces manual review time by 80%.",
                    "priority": "High",
                    "expected_roi": "350% ROI within 15 months",
                    "timeline": "5-8 months",
                    "investment_range": "$200K-$400K",
                    "business_value": "Reduced financial losses, improved compliance, operational cost savings",
                    "implementation_notes": "Integration with accounting systems, real-time monitoring infrastructure"
                },
                {
                    "title": "Intelligent Expense Management",
                    "description": "AI-powered expense categorization, duplicate detection, and policy compliance checking. Automates expense report processing and identifies cost optimization opportunities.",
                    "priority": "Medium",
                    "expected_roi": "200% ROI within 10 months",
                    "timeline": "3-5 months",
                    "investment_range": "$80K-$150K",
                    "business_value": "Process efficiency, cost control, improved financial accuracy",
                    "implementation_notes": "OCR processing, ERP integration, mobile app development"
                },
                {
                    "title": "Predictive Cash Flow Forecasting",
                    "description": "Advanced analytics to predict cash flow patterns, optimize working capital, and identify potential liquidity issues before they occur.",
                    "priority": "Medium",
                    "expected_roi": "180% ROI within 12 months",
                    "timeline": "4-6 months",
                    "investment_range": "$120K-$250K",
                    "business_value": "Better financial planning, reduced borrowing costs, optimized investments",
                    "implementation_notes": "Financial data integration, time series analysis, dashboard development"
                }
            ],
            "CTO": [
                {
                    "title": "AI-Driven Infrastructure Optimization",
                    "description": "Intelligent resource allocation and performance optimization for cloud infrastructure using machine learning to predict demand and automatically scale resources.",
                    "priority": "High",
                    "expected_roi": "300% ROI within 12 months",
                    "timeline": "4-7 months",
                    "investment_range": "$250K-$450K",
                    "business_value": "Reduced infrastructure costs, improved system performance, automated scaling",
                    "implementation_notes": "Cloud platform integration, monitoring systems, automated deployment pipelines"
                },
                {
                    "title": "Intelligent Code Quality & Security Scanner",
                    "description": "AI-powered code analysis for security vulnerabilities, performance issues, and technical debt detection. Integrates with CI/CD pipelines for continuous quality assurance.",
                    "priority": "High",
                    "expected_roi": "200% ROI within 10 months",
                    "timeline": "3-5 months",
                    "investment_range": "$100K-$200K",
                    "business_value": "Improved code quality, reduced security risks, faster development cycles",
                    "implementation_notes": "DevOps integration, static analysis tools, automated reporting"
                },
                {
                    "title": "Predictive System Maintenance",
                    "description": "Machine learning models to predict system failures and automatically schedule maintenance before issues occur, reducing downtime by 70%.",
                    "priority": "Medium",
                    "expected_roi": "250% ROI within 14 months",
                    "timeline": "5-8 months",
                    "investment_range": "$180K-$350K",
                    "business_value": "Reduced downtime, lower maintenance costs, improved reliability",
                    "implementation_notes": "System monitoring integration, anomaly detection algorithms, alerting systems"
                }
            ],
            "COO": [
                {
                    "title": "Supply Chain Optimization Platform",
                    "description": "AI-powered demand forecasting and inventory optimization to reduce waste, minimize stockouts, and optimize supplier relationships across the entire supply chain.",
                    "priority": "High",
                    "expected_roi": "320% ROI within 15 months",
                    "timeline": "6-10 months",
                    "investment_range": "$400K-$700K",
                    "business_value": "Reduced inventory costs, improved delivery times, optimized supplier relationships",
                    "implementation_notes": "ERP integration, supplier API connections, real-time tracking systems"
                },
                {
                    "title": "Automated Quality Control System",
                    "description": "Computer vision and machine learning for automated quality inspection, defect detection, and process optimization in manufacturing or service delivery.",
                    "priority": "High",
                    "expected_roi": "280% ROI within 12 months",
                    "timeline": "4-7 months",
                    "investment_range": "$200K-$400K",
                    "business_value": "Consistent quality standards, reduced manual inspection, faster processing",
                    "implementation_notes": "Camera systems, computer vision models, production line integration"
                },
                {
                    "title": "Workforce Productivity Analytics",
                    "description": "AI-driven analysis of operational efficiency, resource utilization, and process bottlenecks to optimize workforce allocation and identify improvement opportunities.",
                    "priority": "Medium",
                    "expected_roi": "190% ROI within 10 months",
                    "timeline": "3-6 months",
                    "investment_range": "$150K-$300K",
                    "business_value": "Improved operational efficiency, optimized staffing, process automation",
                    "implementation_notes": "HR system integration, performance tracking, dashboard development"
                }
            ],
            "CMO": [
                {
                    "title": "AI-Powered Customer Journey Optimization",
                    "description": "Personalized marketing campaigns using machine learning to analyze customer behavior, predict preferences, and optimize touchpoints across all marketing channels.",
                    "priority": "High",
                    "expected_roi": "400% ROI within 14 months",
                    "timeline": "5-8 months",
                    "investment_range": "$250K-$500K",
                    "business_value": "Higher conversion rates, improved customer engagement, personalized experiences",
                    "implementation_notes": "Marketing automation platform, customer data platform, A/B testing infrastructure"
                },
                {
                    "title": "Intelligent Content Generation",
                    "description": "AI-assisted content creation for marketing materials, social media posts, and product descriptions. Maintains brand voice while scaling content production.",
                    "priority": "High",
                    "expected_roi": "250% ROI within 8 months",
                    "timeline": "3-5 months",
                    "investment_range": "$100K-$200K",
                    "business_value": "Faster content creation, consistent messaging, reduced production costs",
                    "implementation_notes": "Natural language processing, brand voice training, content management integration"
                },
                {
                    "title": "Predictive Lead Scoring Platform",
                    "description": "Machine learning algorithms to score and prioritize leads based on likelihood to convert, enabling sales team to focus on highest-value prospects.",
                    "priority": "Medium",
                    "expected_roi": "180% ROI within 10 months",
                    "timeline": "4-6 months",
                    "investment_range": "$120K-$250K",
                    "business_value": "Higher conversion rates, efficient sales resource allocation, shorter sales cycles",
                    "implementation_notes": "CRM integration, lead tracking systems, sales process optimization"
                }
            ],
            "CXO": [
                {
                    "title": "Real-time Customer Experience Analytics",
                    "description": "AI-powered sentiment analysis and experience monitoring across all customer touchpoints to identify issues and opportunities for experience improvement in real-time.",
                    "priority": "High",
                    "expected_roi": "350% ROI within 12 months",
                    "timeline": "4-7 months",
                    "investment_range": "$200K-$400K",
                    "business_value": "Improved customer satisfaction, reduced churn, proactive issue resolution",
                    "implementation_notes": "Multi-channel data integration, sentiment analysis, real-time dashboards"
                },
                {
                    "title": "Intelligent Customer Support Automation",
                    "description": "AI chatbots and automated support systems that can handle complex customer inquiries, route issues appropriately, and provide personalized assistance.",
                    "priority": "High",
                    "expected_roi": "280% ROI within 10 months",
                    "timeline": "3-6 months",
                    "investment_range": "$150K-$300K",
                    "business_value": "24/7 customer support, reduced response times, lower support costs",
                    "implementation_notes": "Natural language processing, knowledge base integration, escalation workflows"
                },
                {
                    "title": "Personalization Engine",
                    "description": "Machine learning platform to deliver personalized experiences across digital touchpoints based on customer behavior, preferences, and contextual data.",
                    "priority": "Medium",
                    "expected_roi": "220% ROI within 12 months",
                    "timeline": "5-8 months",
                    "investment_range": "$180K-$350K",
                    "business_value": "Enhanced user experience, increased engagement, higher customer loyalty",
                    "implementation_notes": "Customer data platform, recommendation algorithms, A/B testing framework"
                }
            ]
        }
        
        projects = demo_projects.get(role, demo_projects["CEO"])
        
        strategic_insights = f"As a {role} in the {industry} industry, focus on AI projects that demonstrate clear ROI and align with your strategic priorities. Start with high-impact, lower-risk implementations to build internal AI capabilities and stakeholder confidence before tackling more complex transformational projects."
        
        return {
            "projects": projects,
            "strategic_insights": strategic_insights
        }
    
    def _get_role_specific_focus(self, role: str) -> str:
        """Get role-specific AI priorities and concerns"""
        role_mapping = {
            "CEO": """
**CEO Focus Areas:**
- Revenue growth and market expansion
- Operational efficiency and cost reduction
- Competitive advantage and innovation
- Risk management and strategic planning
- Customer satisfaction and retention
Prioritize projects with clear P&L impact, competitive differentiation, and scalable business value.""",
            
            "CFO": """
**CFO Focus Areas:**
- Cost optimization and margin improvement
- Financial risk reduction and compliance
- Process automation and efficiency
- Data-driven financial insights
- ROI measurement and reporting
Prioritize projects with quantifiable financial benefits, cost savings, and improved financial controls.""",
            
            "CTO": """
**CTO Focus Areas:**
- Technical innovation and modernization
- System performance and scalability
- Data infrastructure and analytics
- Security and technical risk
- Development efficiency and automation
Prioritize projects that enhance technical capabilities, improve system performance, and drive innovation.""",
            
            "COO": """
**COO Focus Areas:**
- Operational efficiency and process optimization
- Supply chain and logistics improvement
- Quality control and consistency
- Resource utilization and productivity
- Customer service operations
Prioritize projects that streamline operations, reduce manual work, and improve service delivery.""",
            
            "CMO": """
**CMO Focus Areas:**
- Customer acquisition and retention
- Marketing effectiveness and ROI
- Brand awareness and engagement
- Customer insights and personalization
- Campaign optimization and attribution
Prioritize projects that improve marketing performance, enhance customer experience, and drive growth.""",
            
            "CXO": """
**Chief Experience Officer Focus Areas:**
- Customer experience optimization
- User journey improvement
- Personalization and engagement
- Feedback analysis and insights
- Digital experience enhancement
Prioritize projects that directly improve customer satisfaction, reduce friction, and enhance user experience."""
        }
        
        return role_mapping.get(role, "Focus on general business value and operational improvements.")
    
    def _get_industry_specifics(self, industry: str) -> str:
        """Get industry-specific AI applications and considerations"""
        # Simplified industry mapping - in production, this could be more sophisticated
        if any(term in industry.lower() for term in ['healthcare', 'medical', 'hospital']):
            return """
**Healthcare Industry AI Opportunities:**
- Predictive analytics for patient outcomes
- Medical imaging and diagnostic assistance
- Drug discovery and clinical trial optimization
- Patient flow and resource optimization
- Compliance and documentation automation"""
        
        elif any(term in industry.lower() for term in ['manufacturing', 'industrial', 'factory']):
            return """
**Manufacturing Industry AI Opportunities:**
- Predictive maintenance and equipment optimization
- Quality control and defect detection
- Supply chain optimization and demand forecasting
- Production planning and scheduling
- Safety monitoring and risk prediction"""
        
        elif any(term in industry.lower() for term in ['financial', 'banking', 'fintech']):
            return """
**Financial Services AI Opportunities:**
- Fraud detection and risk assessment
- Algorithmic trading and portfolio optimization
- Customer credit scoring and underwriting
- Regulatory compliance and reporting
- Personalized financial recommendations"""
        
        elif any(term in industry.lower() for term in ['retail', 'ecommerce', 'commerce']):
            return """
**Retail Industry AI Opportunities:**
- Demand forecasting and inventory optimization
- Personalized recommendations and marketing
- Dynamic pricing and promotion optimization
- Customer service automation
- Supply chain and logistics optimization"""
        
        else:
            return """
**General Industry AI Opportunities:**
- Process automation and efficiency improvements
- Customer service enhancement
- Data analytics and business intelligence
- Risk management and compliance
- Marketing and sales optimization"""