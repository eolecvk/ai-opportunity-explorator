import google.genai as genai
import json
import os
from typing import Dict, List, Any
from .catalog_manager import CatalogManager

class GeminiAIClient:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None
        self.model = 'gemini-1.5-flash'
        self.catalog_manager = CatalogManager()
    
    async def generate_response(self, user_message: str, context: Dict = None) -> str:
        if not self.client:
            return "I apologize, but AI chat functionality requires a valid API key configuration."
            
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
            if not self.client:
                raise Exception("API client not configured")
                
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

    async def validate_company_name(self, company_name: str) -> Dict[str, Any]:
        """Validate if the input is a real company and handle ambiguous cases"""
        
        prompt = f"""You are a business analyst tasked with validating company names. Analyze the input "{company_name}" and determine:

1. Is this a real, existing company?
2. If ambiguous (multiple companies with similar names), provide clarification options
3. If invalid (not a company, generic terms, test data), reject it

Validation Rules:
- Accept: Real company names (Apple, Microsoft, Goldman Sachs, etc.)
- Clarify: Ambiguous names that could refer to multiple companies
- Reject: Generic terms, test inputs, non-companies, fictional names

Response format (JSON):
{{
  "status": "valid|ambiguous|invalid",
  "message": "explanation for the user",
  "suggestions": ["list of specific company options if ambiguous"],
  "company_name": "corrected/standardized company name if valid"
}}

Examples:
- "Apple" → valid (Apple Inc.)
- "Goldman" → ambiguous (Goldman Sachs, Goldman Properties, etc.)
- "test" → invalid (not a real company)
- "XYZ Corp" → invalid (generic placeholder)
- "Tesla" → valid (Tesla Inc.)"""

        try:
            if not self.client:
                return self._get_demo_company_validation(company_name)
                
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            print(f"Company validation error: {e}")
            return self._get_demo_company_validation(company_name)
    
    def _get_demo_company_validation(self, company_name: str) -> Dict[str, Any]:
        """Generate demo company validation when API is not available"""
        
        company_lower = company_name.lower().strip()
        
        # List of known real companies for demo
        valid_companies = {
            'apple': 'Apple Inc.',
            'microsoft': 'Microsoft Corporation',
            'google': 'Google (Alphabet Inc.)',
            'amazon': 'Amazon.com Inc.',
            'tesla': 'Tesla Inc.',
            'netflix': 'Netflix Inc.',
            'goldman sachs': 'Goldman Sachs Group Inc.',
            'jpmorgan': 'JPMorgan Chase & Co.',
            'wells fargo': 'Wells Fargo & Company',
            'bank of america': 'Bank of America Corporation',
            'aetna': 'Aetna Inc.',
            'allstate': 'The Allstate Corporation',
            'progressive': 'Progressive Corporation',
            'geico': 'GEICO (Berkshire Hathaway)',
            'walmart': 'Walmart Inc.',
            'coca cola': 'The Coca-Cola Company',
            'pepsi': 'PepsiCo Inc.',
            'ford': 'Ford Motor Company',
            'general motors': 'General Motors Company',
            'ibm': 'International Business Machines Corporation',
            'intel': 'Intel Corporation',
            'cisco': 'Cisco Systems Inc.'
        }
        
        # Ambiguous cases that need clarification
        ambiguous_cases = {
            'goldman': ['Goldman Sachs Group Inc.', 'Goldman Properties', 'Goldman Capital Management'],
            'morgan': ['JPMorgan Chase & Co.', 'Morgan Stanley', 'Morgan & Morgan Law Firm'],
            'wells': ['Wells Fargo & Company', 'Wells Enterprises', 'Wells Real Estate'],
            'progressive': ['Progressive Corporation (Insurance)', 'Progressive Field (Stadium)', 'Progressive Media'],
            'ford': ['Ford Motor Company', 'Ford Foundation', 'Ford Modeling Agency'],
            'capital': ['Capital One Financial', 'Capital Group', 'Capital Airlines'],
            'first': ['First American Corporation', 'First Data Corporation', 'First National Bank'],
            'american': ['American Express', 'American Airlines', 'American International Group']
        }
        
        # Invalid inputs (test data, generic terms, etc.)
        invalid_patterns = ['test', 'example', 'sample', 'demo', 'xyz', 'abc corp', 'company', 'business', 'inc', 'corp', '123', 'foo', 'bar']
        
        # Check for invalid patterns
        if any(pattern in company_lower for pattern in invalid_patterns) or len(company_name.strip()) < 2:
            return {
                "status": "invalid",
                "message": f"'{company_name}' does not appear to be a real company name. Please enter the name of an actual company (e.g., Apple, Microsoft, Goldman Sachs).",
                "suggestions": [],
                "company_name": None
            }
        
        # Check for ambiguous cases
        for key, suggestions in ambiguous_cases.items():
            if key in company_lower:
                return {
                    "status": "ambiguous",
                    "message": f"Multiple companies match '{company_name}'. Please select the specific company you're referring to:",
                    "suggestions": suggestions,
                    "company_name": None
                }
        
        # Check for valid companies
        for key, full_name in valid_companies.items():
            if key in company_lower or company_lower in key:
                return {
                    "status": "valid",
                    "message": f"Company validated: {full_name}",
                    "suggestions": [],
                    "company_name": full_name
                }
        
        # If not found in known lists, assume it might be valid but with low confidence
        if len(company_name.strip()) > 3 and not any(char.isdigit() for char in company_name):
            return {
                "status": "valid",
                "message": f"Company name accepted: {company_name}",
                "suggestions": [],
                "company_name": company_name
            }
        
        # Default to invalid
        return {
            "status": "invalid",
            "message": f"'{company_name}' does not appear to be a valid company name. Please enter the name of a real company.",
            "suggestions": [],
            "company_name": None
        }

    async def infer_company_details(self, company_name: str) -> Dict[str, Any]:
        """Infer industry and company size from company name using LLM"""
        
        prompt = f"""You are a business analyst. Given the company name "{company_name}", please analyze and provide the following information:

1. Industry - What industry does this company operate in? Choose from: banking, insurance, healthcare, manufacturing, retail, technology, logistics, finance, energy, telecommunications, automotive, aerospace, pharma, media, consulting, real-estate, or other
2. Company Size - Estimate the company size based on your knowledge. Choose from: startup, small, medium, large, enterprise
3. Brief Description - A 1-2 sentence description of what the company does

Please respond in JSON format:
{{
  "industry": "industry_name",
  "company_size": "size_category", 
  "description": "brief description of the company",
  "confidence": "high/medium/low"
}}

If you're not familiar with the company, make reasonable inferences based on the company name and respond with "confidence": "low"."""

        try:
            if not self.client:
                return self._get_demo_company_details(company_name)
                
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            print(f"Company details inference error: {e}")
            return self._get_demo_company_details(company_name)
    
    def _get_demo_company_details(self, company_name: str) -> Dict[str, Any]:
        """Generate demo company details when API is not available"""
        
        # Simple pattern matching for demo purposes
        company_lower = company_name.lower()
        
        if any(keyword in company_lower for keyword in ['bank', 'financial', 'credit', 'goldman', 'jpmorgan', 'wells fargo', 'citi']):
            return {
                "industry": "banking",
                "company_size": "large",
                "description": f"{company_name} is a financial services company providing banking and related services.",
                "confidence": "medium"
            }
        elif any(keyword in company_lower for keyword in ['insurance', 'aetna', 'allstate', 'progressive', 'geico']):
            return {
                "industry": "insurance", 
                "company_size": "large",
                "description": f"{company_name} is an insurance company providing various insurance products and services.",
                "confidence": "medium"
            }
        elif any(keyword in company_lower for keyword in ['tech', 'software', 'apple', 'google', 'microsoft', 'amazon', 'meta', 'tesla']):
            return {
                "industry": "technology",
                "company_size": "enterprise",
                "description": f"{company_name} is a technology company focused on innovative products and services.",
                "confidence": "medium"
            }
        elif any(keyword in company_lower for keyword in ['hospital', 'health', 'medical', 'pharma', 'bio']):
            return {
                "industry": "healthcare",
                "company_size": "large", 
                "description": f"{company_name} operates in the healthcare industry providing medical services or products.",
                "confidence": "medium"
            }
        else:
            return {
                "industry": "technology",
                "company_size": "medium",
                "description": f"{company_name} is a company operating in various business sectors.",
                "confidence": "low"
            }

    async def generate_pre_engagement_analysis(self, company_info: Dict) -> Dict[str, Any]:
        """Generate pre-engagement research and hypotheses for a company"""
        
        company_name = company_info.get('companyName', 'the target company')
        industry = company_info.get('industry', '')
        company_size = company_info.get('companySize', 'medium')
        
        prompt = f"""You are an analyst at a consulting firm. You are tasked with performing pre-engagement research about {company_name}. Write a few bullet points addressing the following:

Initial Research: Before the first meeting, the consulting firm's team will conduct extensive research on the client's company, industry, and competitors. This includes analyzing public reports, financial statements, and news articles to understand the client's market position, strategic initiatives, and potential challenges.

Formulating Hypotheses: Based on the initial research, the team develops preliminary hypotheses about the client's likely pain points and needs. These aren't conclusions, but rather informed guesses to guide the conversation. For example, if a company's stock is underperforming, the hypothesis might be that they have operational inefficiencies.

Company Details:
- Company Name: {company_name}
- Industry: {industry}
- Company Size: {company_size}

Please provide:
1. Initial Research findings (3-4 bullet points)
2. Strategic Hypotheses (4-5 hypotheses about potential AI opportunities and pain points)

Format the response as JSON with the following structure:
{{
  "research_findings": ["finding1", "finding2", "finding3", "finding4"],
  "strategic_hypotheses": [
    {{
      "hypothesis": "Hypothesis statement",
      "rationale": "Why this might be true",
      "ai_opportunity": "How AI could address this"
    }},
    ...
  ]
}}"""

        try:
            if not self.client:
                return self._get_demo_pre_engagement_analysis(company_info)
                
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            print(f"Pre-engagement analysis error: {e}")
            return self._get_demo_pre_engagement_analysis(company_info)

    async def generate_ai_project_recommendations(self, company_info: Dict, selected_hypotheses: List[str] = None) -> Dict[str, Any]:
        """Generate specific AI project recommendations based on selected hypotheses"""
        
        industry = company_info.get('industry', '').lower()
        company_size = company_info.get('companySize', 'medium')
        
        # If hypotheses are provided, use them to filter/prioritize projects
        if selected_hypotheses:
            return await self._generate_hypothesis_based_recommendations(company_info, selected_hypotheses)
        
        # Fallback to original behavior if no hypotheses provided
        # Check if industry is supported in catalog
        available_industries = self.catalog_manager.get_available_industries()
        if industry not in available_industries:
            # Fallback to demo recommendations for unsupported industries
            return self._get_demo_recommendations(company_info)
        
        try:
            # Get filtered projects from catalog - remove role parameter
            filtered_projects = self.catalog_manager.filter_projects_by_criteria(
                industry=industry,
                company_size=company_size,
                limit=3
            )
            
            # Format projects for response
            formatted_projects = []
            for project in filtered_projects:
                formatted_project = self.catalog_manager.format_project_for_response(project, company_size)
                formatted_projects.append(formatted_project)
            
            # Generate strategic insights without role
            strategic_insights = self._generate_strategic_insights(industry, company_size)
            
            return {
                "projects": formatted_projects,
                "strategic_insights": strategic_insights
            }
            
        except Exception as e:
            print(f"Catalog-based recommendation error: {e}")
            # Fallback to demo recommendations
            return self._get_demo_recommendations(company_info)
    
    def _generate_strategic_insights(self, industry: str, company_size: str) -> str:
        """Generate strategic insights based on industry and company size"""
        industry_insights = {
            "banking": f"AI transformation in banking should focus on risk management, fraud detection, and customer experience enhancement. These initiatives offer clear competitive advantages and regulatory compliance benefits.",
            "insurance": f"Insurance companies can leverage AI for claims processing automation, risk assessment, and predictive analytics to improve operational efficiency and customer satisfaction.",
            "healthcare": f"Healthcare AI implementations should prioritize patient care optimization, diagnostic assistance, and operational efficiency while ensuring regulatory compliance and data privacy.",
            "technology": f"Technology companies are well-positioned for advanced AI implementations that can drive product innovation, improve development processes, and enhance customer experiences.",
            "manufacturing": f"Manufacturing AI initiatives should focus on predictive maintenance, quality control, and supply chain optimization to reduce costs and improve operational efficiency.",
            "retail": f"Retail AI transformation can significantly impact customer personalization, inventory management, and demand forecasting to drive revenue growth and operational excellence."
        }
        
        size_context = {
            'startup': 'For startups, focus on quick wins that provide immediate competitive advantage with minimal infrastructure investment.',
            'small': 'Small companies should prioritize cost-effective AI solutions that scale with growth and provide clear operational benefits.',
            'medium': 'Medium-sized companies have the resources to implement comprehensive AI solutions that can transform core business processes.',
            'large': 'Large enterprises should focus on AI initiatives that can be scaled across multiple business units and geographies.',
            'enterprise': 'Enterprise-level AI implementations should drive industry leadership and create new business models through advanced AI capabilities.'
        }
        
        base_insight = industry_insights.get(industry, f"AI transformation in {industry} requires strategic focus on high-impact, measurable initiatives.")
        size_insight = size_context.get(company_size, "Scale AI implementations according to organizational readiness and resource availability.")
        
        return f"{base_insight} {size_insight}"
    
    async def _generate_hypothesis_based_recommendations(self, company_info: Dict, selected_hypotheses: List[str]) -> Dict[str, Any]:
        """Generate AI project recommendations based on selected hypotheses"""
        
        company_name = company_info.get('companyName', 'the target company')
        industry = company_info.get('industry', '')
        company_size = company_info.get('companySize', 'medium')
        
        hypotheses_text = "\n".join([f"- {h}" for h in selected_hypotheses])
        
        # Create detailed hypothesis context
        hypothesis_details = []
        for i, hypothesis in enumerate(selected_hypotheses):
            hypothesis_details.append(f"Hypothesis {i+1}: {hypothesis}")
        
        detailed_hypotheses = "\n".join(hypothesis_details)

        prompt = f"""You are an AI consultant creating specific project recommendations for {company_name} ({industry} industry, {company_size} company).

CRITICAL REQUIREMENT: Each recommended project must DIRECTLY solve specific pain points identified in the validated hypotheses below. Do NOT provide generic AI projects.

VALIDATED HYPOTHESES TO ADDRESS:
{detailed_hypotheses}

TASK: Recommend exactly 3 AI projects that specifically solve these validated problems. Each project must:

1. **Target Specific Pain Points**: Address concrete issues mentioned in the hypotheses
2. **Industry-Specific Solutions**: Tailored to {industry} industry challenges  
3. **Company-Specific Context**: Consider {company_name}'s {company_size} scale and context
4. **Measurable Alignment**: Explain exactly how each project solves the identified problems

For each project, provide:

**Format as JSON:**
{{
  "projects": [
    {{
      "title": "Specific, actionable project title",
      "description": "2-3 sentences describing the solution and its direct impact on the identified problems",
      "priority": "High/Medium/Low based on hypothesis urgency",
      "expected_roi": "Specific ROI with timeline",
      "timeline": "Implementation timeframe", 
      "investment_range": "Budget range",
      "business_value": "Quantifiable business outcomes that directly counter the hypotheses",
      "implementation_notes": "Key technical/operational requirements",
      "hypothesis_alignment": "Precisely explain which hypothesis this solves and how, referencing specific pain points mentioned in the hypothesis"
    }}
  ],
  "strategic_insights": "Strategic analysis of how these projects collectively address {company_name}'s validated challenges in {industry}"
}}

EXAMPLES OF GOOD HYPOTHESIS ALIGNMENT:
- "Solves {company_name}'s manual loan processing bottlenecks (Hypothesis 1) by automating credit assessment workflows, delivering the 70% approval time reduction opportunity identified"
- "Addresses the high false positive fraud detection issue (Hypothesis 2) by implementing ML models that reduce false alarms while improving accuracy as specified"

AVOID GENERIC ALIGNMENTS LIKE:
- "Addresses operational inefficiencies" 
- "Improves business processes"
- "Enhances customer experience"

BE SPECIFIC TO THE ACTUAL HYPOTHESES PROVIDED."""

        try:
            if not self.client:
                # Fallback to demo recommendations with hypothesis context
                return self._get_hypothesis_demo_recommendations(company_info, selected_hypotheses)
                
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            result = json.loads(response.text)
            return result
            
        except Exception as e:
            print(f"Hypothesis-based recommendation error: {e}")
            return self._get_hypothesis_demo_recommendations(company_info, selected_hypotheses)
    
    def _get_demo_pre_engagement_analysis(self, company_info: Dict) -> Dict[str, Any]:
        """Generate demo pre-engagement analysis when API is not available"""
        
        company_name = company_info.get('companyName', 'Target Company')
        industry = company_info.get('industry', 'Technology')
        company_size = company_info.get('companySize', 'medium')
        
        # Industry-specific research findings and hypotheses
        industry_data = {
            "banking": {
                "research_findings": [
                    f"{company_name} operates in a highly regulated financial services environment with increasing pressure for digital transformation",
                    f"The {industry} sector faces challenges with legacy system modernization and compliance automation",
                    f"Customer expectations for personalized, real-time financial services are driving technology investments",
                    f"Competitive pressure from fintech companies is forcing traditional banks to innovate rapidly"
                ],
                "hypotheses": [
                    {
                        "hypothesis": "Manual loan processing and credit assessment creates operational bottlenecks",
                        "rationale": "Banks typically have lengthy approval processes that could be streamlined",
                        "ai_opportunity": "AI-powered credit scoring and automated loan processing could reduce approval time by 70%"
                    },
                    {
                        "hypothesis": "Fraud detection systems may have high false positive rates",
                        "rationale": "Traditional rule-based systems often generate too many false alarms",
                        "ai_opportunity": "Machine learning fraud detection could reduce false positives by 60% while improving detection accuracy"
                    },
                    {
                        "hypothesis": "Customer service operations face scalability challenges",
                        "rationale": "High volume of routine inquiries requires significant human resources",
                        "ai_opportunity": "Intelligent chatbots could handle 80% of routine customer inquiries automatically"
                    },
                    {
                        "hypothesis": "Risk management relies heavily on historical data analysis",
                        "rationale": "Traditional risk models may not capture emerging market patterns",
                        "ai_opportunity": "Predictive analytics could improve risk assessment accuracy and enable proactive risk management"
                    }
                ]
            },
            "insurance": {
                "research_findings": [
                    f"{company_name} operates in an insurance market with evolving risk profiles and customer expectations",
                    f"Claims processing and underwriting remain largely manual, creating operational inefficiencies",
                    f"The industry faces pressure to improve customer experience while managing risk effectively",
                    f"Regulatory requirements demand accurate documentation and compliance monitoring"
                ],
                "hypotheses": [
                    {
                        "hypothesis": "Claims processing involves significant manual review and documentation",
                        "rationale": "Insurance claims typically require extensive paperwork and validation processes",
                        "ai_opportunity": "Automated claims processing using AI could reduce processing time by 65% and improve accuracy"
                    },
                    {
                        "hypothesis": "Underwriting decisions may lack comprehensive risk assessment",
                        "rationale": "Traditional underwriting may not leverage all available data sources effectively",
                        "ai_opportunity": "AI-powered underwriting could incorporate diverse data sources for more accurate risk pricing"
                    },
                    {
                        "hypothesis": "Customer interactions are reactive rather than proactive",
                        "rationale": "Most insurance companies respond to claims rather than preventing them",
                        "ai_opportunity": "Predictive analytics could identify high-risk situations and enable proactive customer engagement"
                    },
                    {
                        "hypothesis": "Fraud detection capabilities may be limited by rule-based systems",
                        "rationale": "Insurance fraud is sophisticated and evolving, requiring advanced detection methods",
                        "ai_opportunity": "Machine learning fraud detection could identify complex fraud patterns and reduce losses by 40%"
                    }
                ]
            }
        }
        
        # Use industry-specific data or fallback to generic
        data = industry_data.get(industry.lower(), {
            "research_findings": [
                f"{company_name} operates in the {industry} industry with typical sector challenges around digital transformation",
                f"Market pressures are driving the need for operational efficiency and customer experience improvements",
                f"Technology adoption varies across the organization, creating opportunities for AI-driven optimization",
                f"Competitive landscape requires innovative approaches to maintain market position"
            ],
            "hypotheses": [
                {
                    "hypothesis": "Manual processes create operational inefficiencies",
                    "rationale": f"Most {industry} companies have processes that could benefit from automation",
                    "ai_opportunity": "Process automation could reduce manual work by 50-70%"
                },
                {
                    "hypothesis": "Data insights are underutilized for strategic decisions",
                    "rationale": "Companies often have data but lack advanced analytics capabilities",
                    "ai_opportunity": "AI-powered analytics could improve decision-making speed and accuracy"
                },
                {
                    "hypothesis": "Customer experience could be more personalized",
                    "rationale": "Generic customer experiences are becoming less competitive",
                    "ai_opportunity": "AI personalization could increase customer satisfaction and retention"
                },
                {
                    "hypothesis": "Predictive capabilities are limited",
                    "rationale": "Most companies are reactive rather than proactive in their operations",
                    "ai_opportunity": "Predictive AI could enable proactive business strategies"
                }
            ]
        })
        
        return {
            "research_findings": data["research_findings"],
            "strategic_hypotheses": data["hypotheses"]
        }
    
    def _get_hypothesis_demo_recommendations(self, company_info: Dict, selected_hypotheses: List[str]) -> Dict[str, Any]:
        """Generate demo recommendations based on selected hypotheses using semantic analysis"""
        
        company_name = company_info.get('companyName', 'Your Company')
        industry = company_info.get('industry', 'technology')
        
        # Enhanced semantic project templates with industry-specific variations
        project_templates = {
            "process_automation": {
                "banking": {
                    "title": "AI-Powered Loan Processing Automation",
                    "description": "Automate credit assessment, loan approval workflows, and compliance checks using machine learning to eliminate manual bottlenecks and reduce approval times.",
                    "keywords": ["manual", "loan", "processing", "credit", "approval", "assessment", "bottleneck"],
                    "roi": "350% ROI within 12 months",
                    "timeline": "6-9 months",
                    "investment": "$300K-$600K"
                },
                "insurance": {
                    "title": "Automated Claims Processing System",
                    "description": "Deploy AI to automatically process claims, validate documentation, and make approval decisions, reducing manual review time and improving accuracy.",
                    "keywords": ["manual", "claims", "processing", "review", "documentation", "approval"],
                    "roi": "280% ROI within 10 months", 
                    "timeline": "4-7 months",
                    "investment": "$250K-$500K"
                },
                "default": {
                    "title": "Intelligent Process Automation Platform",
                    "description": "Implement AI-powered automation to streamline manual processes, reduce human error, and improve operational efficiency across key business functions.",
                    "keywords": ["manual", "process", "bottleneck", "inefficien", "workflow"],
                    "roi": "300% ROI within 15 months",
                    "timeline": "6-8 months",
                    "investment": "$250K-$450K"
                }
            },
            "fraud_detection": {
                "banking": {
                    "title": "Advanced ML Fraud Detection System",
                    "description": "Replace rule-based fraud systems with machine learning models that reduce false positives while improving detection accuracy across all banking channels.",
                    "keywords": ["fraud", "detection", "false positive", "rule-based", "alarm"],
                    "roi": "400% ROI within 18 months",
                    "timeline": "5-8 months",
                    "investment": "$400K-$800K"
                },
                "insurance": {
                    "title": "AI Insurance Fraud Prevention Platform",
                    "description": "Deploy sophisticated ML algorithms to identify fraudulent claims patterns and reduce false alarms, improving both detection accuracy and claim processing speed.",
                    "keywords": ["fraud", "detection", "claims", "false", "pattern"],
                    "roi": "320% ROI within 16 months",
                    "timeline": "4-7 months",
                    "investment": "$300K-$600K"
                },
                "default": {
                    "title": "Machine Learning Fraud Detection",
                    "description": "Advanced fraud detection system using ML to identify suspicious patterns while minimizing false positives and improving operational efficiency.",
                    "keywords": ["fraud", "detection", "false positive", "suspicious"],
                    "roi": "350% ROI within 12 months",
                    "timeline": "4-6 months",
                    "investment": "$200K-$400K"
                }
            },
            "customer_service": {
                "banking": {
                    "title": "Intelligent Banking Chatbot & Virtual Assistant",
                    "description": "Deploy AI-powered conversational agents to handle routine banking inquiries, account services, and transaction support, reducing call center volume.",
                    "keywords": ["customer", "service", "inquir", "scalability", "call", "support"],
                    "roi": "250% ROI within 10 months",
                    "timeline": "3-5 months", 
                    "investment": "$150K-$300K"
                },
                "insurance": {
                    "title": "AI Customer Support Automation",
                    "description": "Implement intelligent chatbots and automated support systems to handle policy inquiries, claims status, and customer service requests 24/7.",
                    "keywords": ["customer", "service", "inquir", "support", "scalability"],
                    "roi": "220% ROI within 8 months",
                    "timeline": "3-6 months",
                    "investment": "$120K-$250K"
                },
                "default": {
                    "title": "AI-Powered Customer Service Platform",
                    "description": "Intelligent customer service automation to handle routine inquiries, improve response times, and scale support operations efficiently.",
                    "keywords": ["customer", "service", "inquir", "support", "scalability"],
                    "roi": "200% ROI within 12 months",
                    "timeline": "4-6 months",
                    "investment": "$100K-$200K"
                }
            },
            "risk_management": {
                "banking": {
                    "title": "Predictive Risk Analytics Platform",
                    "description": "Advanced ML models for real-time risk assessment, market pattern analysis, and proactive risk management beyond traditional historical data approaches.",
                    "keywords": ["risk", "management", "historical", "pattern", "predictive", "analyt"],
                    "roi": "300% ROI within 16 months",
                    "timeline": "7-12 months",
                    "investment": "$500K-$1M"
                },
                "insurance": {
                    "title": "Dynamic Risk Assessment Engine",
                    "description": "AI-powered risk evaluation system that incorporates real-time data sources and predictive modeling to improve underwriting accuracy and pricing.",
                    "keywords": ["risk", "assessment", "underwriting", "pricing", "predictive"],
                    "roi": "280% ROI within 14 months",
                    "timeline": "6-10 months",
                    "investment": "$400K-$700K"
                },
                "default": {
                    "title": "AI Risk Management System",
                    "description": "Predictive risk analytics platform using machine learning to identify patterns and enable proactive risk management strategies.",
                    "keywords": ["risk", "management", "predictive", "proactive", "pattern"],
                    "roi": "250% ROI within 12 months",
                    "timeline": "5-8 months",
                    "investment": "$300K-$500K"
                }
            }
        }
        
        # Enhanced semantic analysis to match hypotheses to appropriate projects
        selected_projects = []
        matched_categories = set()
        hypothesis_project_map = {}  # Track which hypothesis led to each project
        
        for hypothesis in selected_hypotheses:
            hypothesis_lower = hypothesis.lower()
            best_match = None
            best_score = 0
            
            # Enhanced scoring with fuzzy matching and related concepts
            for category, variations in project_templates.items():
                project_variant = variations.get(industry, variations["default"])
                
                # Calculate semantic score with multiple factors
                score = 0
                
                # Direct keyword matches (highest weight)
                for keyword in project_variant["keywords"]:
                    if keyword in hypothesis_lower:
                        score += 2
                
                # Fuzzy/related concept matching (medium weight)
                fuzzy_matches = {
                    "data": ["insights", "analytics", "intelligence", "information", "decisions"],
                    "predictive": ["forecasting", "prediction", "anticipate", "proactive", "future"],
                    "customer": ["client", "user", "experience", "satisfaction", "service"],
                    "reactive": ["responsive", "after", "post", "following"],
                    "scalability": ["scale", "growth", "volume", "capacity", "expansion"],
                    "inefficien": ["slow", "bottleneck", "delay", "waste", "suboptimal"]
                }
                
                for base_concept, related_terms in fuzzy_matches.items():
                    if base_concept in " ".join(project_variant["keywords"]):
                        for term in related_terms:
                            if term in hypothesis_lower:
                                score += 1
                
                # Category-specific semantic boosts
                category_boosts = {
                    "process_automation": ["manual", "bottleneck", "workflow", "approval", "processing"],
                    "fraud_detection": ["fraud", "detection", "security", "false", "alarm"],
                    "customer_service": ["customer", "service", "support", "inquiry", "satisfaction"],
                    "risk_management": ["risk", "management", "assessment", "prediction", "analytics"]
                }
                
                if category in category_boosts:
                    for boost_term in category_boosts[category]:
                        if boost_term in hypothesis_lower:
                            score += 1
                
                # Prioritize unused categories and higher scores
                if score > best_score and category not in matched_categories:
                    best_score = score
                    best_match = (category, project_variant)
            
            # Accept matches with score >= 1 (was previously requiring > 0, but let's be more lenient)
            if best_match and best_score >= 1:
                category, project_data = best_match
                matched_categories.add(category)
                hypothesis_project_map[category] = hypothesis
                
                # Generate dynamic alignment text
                alignment_text = self._generate_alignment_text(hypothesis, project_data, company_name)
                
                project = {
                    "title": project_data["title"],
                    "description": project_data["description"], 
                    "priority": "High" if best_score >= 3 else "Medium",
                    "expected_roi": project_data["roi"],
                    "timeline": project_data["timeline"],
                    "investment_range": project_data["investment"],
                    "business_value": f"Directly addresses the specific challenges identified: {hypothesis[:100]}...",
                    "implementation_notes": f"Tailored for {industry} industry requirements and {company_name}'s operational context",
                    "hypothesis_alignment": alignment_text
                }
                selected_projects.append(project)
        
        # If we need more projects, add hypothesis-driven filler projects
        if len(selected_projects) < 3:
            # Select filler projects based on secondary hypothesis connections
            remaining_categories = set(project_templates.keys()) - matched_categories
            filler_projects_with_scores = []
            
            # Score remaining projects against ALL hypotheses for secondary connections
            for category in remaining_categories:
                project_data = project_templates[category].get(industry, project_templates[category]["default"])
                best_hypothesis_connection = None
                best_connection_score = 0
                
                # Find the best hypothesis connection for this filler project
                for hypothesis in selected_hypotheses:
                    hypothesis_lower = hypothesis.lower()
                    connection_score = 0
                    
                    # Look for secondary/supporting connections
                    secondary_connections = {
                        "process_automation": ["efficiency", "optimization", "streamline", "improve"],
                        "fraud_detection": ["security", "protection", "monitoring", "compliance"],
                        "customer_service": ["experience", "satisfaction", "engagement", "retention"],
                        "risk_management": ["analysis", "monitoring", "assessment", "evaluation"]
                    }
                    
                    if category in secondary_connections:
                        for connection_term in secondary_connections[category]:
                            if connection_term in hypothesis_lower:
                                connection_score += 1
                    
                    # Also check for general business improvement connections
                    improvement_terms = ["competitive", "advantage", "growth", "transformation", "moderniz"]
                    for term in improvement_terms:
                        if term in hypothesis_lower:
                            connection_score += 0.5
                    
                    if connection_score > best_connection_score:
                        best_connection_score = connection_score
                        best_hypothesis_connection = hypothesis
                
                filler_projects_with_scores.append((category, project_data, best_hypothesis_connection, best_connection_score))
            
            # Sort filler projects by their connection scores (best connections first)
            filler_projects_with_scores.sort(key=lambda x: x[3], reverse=True)
            
            # Add the best-connected filler projects
            for category, project_data, connected_hypothesis, score in filler_projects_with_scores[:3-len(selected_projects)]:
                # Generate hypothesis-connected alignment text for filler projects
                if connected_hypothesis and score > 0:
                    alignment_text = self._generate_filler_alignment_text(connected_hypothesis, project_data, company_name)
                else:
                    # Use a composite alignment referencing all hypotheses
                    alignment_text = self._generate_composite_alignment_text(selected_hypotheses, company_name, category)
                
                project = {
                    "title": project_data["title"],
                    "description": project_data["description"],
                    "priority": "Medium",
                    "expected_roi": project_data["roi"],
                    "timeline": project_data["timeline"], 
                    "investment_range": project_data["investment"],
                    "business_value": f"Supports {company_name}'s broader transformation objectives while complementing primary AI initiatives",
                    "implementation_notes": f"Tailored for {industry} industry with integration considerations for {company_name}'s validated strategic needs",
                    "hypothesis_alignment": alignment_text
                }
                selected_projects.append(project)
        
        
        # Separate truly aligned projects from filler projects
        aligned_projects = []
        filler_projects = []
        
        for project in selected_projects:
            # Check if this project was matched with score >= 1 (truly aligned)
            project_category = None
            for category, project_data in project_templates.items():
                variant = project_data.get(industry, project_data["default"])
                if variant["title"] == project["title"]:
                    project_category = category
                    break
            
            if project_category in hypothesis_project_map:
                # This is a truly aligned project - keep hypothesis alignment
                aligned_projects.append(project)
            else:
                # This is a filler project - remove hypothesis alignment
                filler_project = {k: v for k, v in project.items() if k != "hypothesis_alignment"}
                filler_projects.append(filler_project)
        
        return {
            "aligned_projects": aligned_projects,
            "filler_projects": filler_projects
        }
    
    def _generate_alignment_text(self, hypothesis: str, project_data: dict, company_name: str) -> str:
        """Generate dynamic alignment text based on hypothesis content"""
        
        # Extract key problem indicators from hypothesis
        hypothesis_lower = hypothesis.lower()
        
        # Comprehensive template patterns for different problem types
        
        # Process Automation Patterns
        if "manual" in hypothesis_lower and ("processing" in hypothesis_lower or "assessment" in hypothesis_lower or "approval" in hypothesis_lower):
            return f"Directly solves {company_name}'s manual processing bottlenecks identified in the hypothesis by automating key workflows, eliminating the operational inefficiencies highlighted."
        
        elif any(term in hypothesis_lower for term in ["bottleneck", "inefficien", "workflow"]) and ("manual" in hypothesis_lower or "process" in hypothesis_lower):
            return f"Addresses the process inefficiencies described in the hypothesis by implementing automation that streamlines {company_name}'s operations and eliminates the identified bottlenecks."
        
        # Fraud Detection Patterns
        elif "fraud" in hypothesis_lower and ("false positive" in hypothesis_lower or "false alarm" in hypothesis_lower):
            return f"Specifically addresses the false positive fraud detection issue raised in the hypothesis by implementing ML models that improve accuracy while reducing false alarms."
        
        elif "fraud" in hypothesis_lower and "detection" in hypothesis_lower:
            return f"Tackles the fraud detection challenges outlined in the hypothesis by deploying advanced AI systems that improve {company_name}'s security and risk management capabilities."
            
        # Customer Service Patterns
        elif "customer service" in hypothesis_lower and ("scalability" in hypothesis_lower or "volume" in hypothesis_lower or "capacity" in hypothesis_lower):
            return f"Tackles the customer service scalability challenges identified in the hypothesis by automating routine inquiries and improving response capacity."
        
        elif any(term in hypothesis_lower for term in ["customer", "service", "support"]) and ("reactive" in hypothesis_lower or "proactive" in hypothesis_lower):
            return f"Transforms {company_name}'s reactive customer approach mentioned in the hypothesis into a proactive, AI-powered service model that anticipates and addresses customer needs."
        
        elif "customer" in hypothesis_lower and ("experience" in hypothesis_lower or "satisfaction" in hypothesis_lower):
            return f"Directly improves the customer experience issues highlighted in the hypothesis by implementing AI-driven personalization and service optimization for {company_name}."
            
        # Risk Management Patterns
        elif "risk" in hypothesis_lower and ("historical" in hypothesis_lower or "pattern" in hypothesis_lower):
            return f"Addresses the risk management limitations noted in the hypothesis by providing predictive analytics that go beyond traditional historical data analysis."
        
        elif "risk" in hypothesis_lower and ("assessment" in hypothesis_lower or "management" in hypothesis_lower):
            return f"Enhances {company_name}'s risk assessment capabilities identified as limited in the hypothesis through advanced AI-powered risk modeling and real-time analysis."
        
        # Data & Analytics Patterns
        elif any(term in hypothesis_lower for term in ["data", "insights", "analytics"]) and any(term in hypothesis_lower for term in ["underutilized", "decisions", "strategic"]):
            return f"Directly addresses the data utilization gaps described in the hypothesis by transforming {company_name}'s data into actionable insights for strategic decision-making."
        
        elif "predictive" in hypothesis_lower and ("capabilities" in hypothesis_lower or "limited" in hypothesis_lower or "forecasting" in hypothesis_lower):
            return f"Solves the predictive analytics limitations outlined in the hypothesis by implementing advanced forecasting capabilities that enable {company_name} to anticipate future trends and opportunities."
        
        # Claims Processing (Insurance-specific)
        elif "claims" in hypothesis_lower and ("processing" in hypothesis_lower or "review" in hypothesis_lower or "manual" in hypothesis_lower):
            return f"Streamlines the manual claims processing bottlenecks identified in the hypothesis by automating {company_name}'s claim validation, review, and approval workflows."
        
        elif "underwriting" in hypothesis_lower and ("assessment" in hypothesis_lower or "decisions" in hypothesis_lower):
            return f"Improves the underwriting assessment challenges noted in the hypothesis by providing {company_name} with AI-powered risk evaluation and decision-support systems."
        
        # Operational Efficiency Patterns
        elif any(term in hypothesis_lower for term in ["operational", "efficiency", "productivity"]) and "challenge" in hypothesis_lower:
            return f"Tackles the operational efficiency challenges described in the hypothesis by optimizing {company_name}'s key business processes through intelligent automation."
        
        # Technology & Innovation Patterns
        elif any(term in hypothesis_lower for term in ["technology", "digital", "innovation"]) and any(term in hypothesis_lower for term in ["adoption", "transformation", "modernization"]):
            return f"Supports the digital transformation needs highlighted in the hypothesis by providing {company_name} with cutting-edge AI capabilities that modernize operations."
        
        # Fallback with specific hypothesis reference
        else:
            # Extract key nouns from hypothesis for more specific alignment
            key_terms = []
            problem_indicators = ["challenge", "issue", "problem", "bottleneck", "limitation", "inefficiency", "gap"]
            
            for indicator in problem_indicators:
                if indicator in hypothesis_lower:
                    # Find words around the problem indicator
                    words = hypothesis_lower.split()
                    try:
                        idx = words.index(indicator)
                        # Get context words before the problem indicator
                        context_start = max(0, idx - 3)
                        context_words = words[context_start:idx]
                        key_terms.extend([w for w in context_words if len(w) > 3 and w not in ['the', 'and', 'with', 'that', 'this', 'have', 'been']])
                    except ValueError:
                        pass
            
            if key_terms:
                primary_concern = key_terms[-1] if key_terms else "operational aspect"
                return f"Addresses the {primary_concern} challenges highlighted in the selected hypothesis, providing {company_name} with targeted AI solutions to resolve the identified pain points."
            else:
                # Last resort - but still hypothesis-specific
                return f"Supports {company_name}'s strategic objectives by addressing the specific business challenges outlined in the validated hypothesis through AI-powered improvements."
    
    def _generate_filler_alignment_text(self, hypothesis: str, project_data: dict, company_name: str) -> str:
        """Generate alignment text for filler projects that have secondary connections to hypotheses"""
        
        hypothesis_lower = hypothesis.lower()
        
        # Create supporting/complementary alignment text
        if any(term in hypothesis_lower for term in ["efficiency", "optimization", "streamline"]):
            return f"While not directly addressing the primary hypothesis, supports {company_name}'s efficiency optimization goals identified in the research by providing complementary AI capabilities that enhance overall operational performance."
        
        elif any(term in hypothesis_lower for term in ["experience", "satisfaction", "customer"]):
            return f"Complements {company_name}'s customer-focused initiatives highlighted in the hypothesis by providing supporting AI infrastructure that enhances overall service delivery and customer engagement."
        
        elif any(term in hypothesis_lower for term in ["security", "protection", "risk"]):
            return f"Strengthens {company_name}'s security and risk management framework referenced in the hypothesis by adding protective AI capabilities that support the broader risk mitigation strategy."
        
        elif any(term in hypothesis_lower for term in ["analysis", "data", "insights"]):
            return f"Enhances {company_name}'s analytical capabilities mentioned in the hypothesis by providing additional data processing and intelligence tools that support evidence-based decision making."
        
        else:
            return f"Supports the broader digital transformation objectives implied by {company_name}'s validated hypotheses, providing foundational AI capabilities that complement the primary strategic initiatives."
    
    def _generate_composite_alignment_text(self, hypotheses: list, company_name: str, category: str) -> str:
        """Generate alignment text that references multiple hypotheses for projects with weak individual connections"""
        
        # Extract key themes from all hypotheses
        all_hypotheses_text = " ".join(hypotheses).lower()
        
        # Identify dominant themes
        themes = []
        if any(term in all_hypotheses_text for term in ["manual", "process", "bottleneck", "automation"]):
            themes.append("operational efficiency")
        if any(term in all_hypotheses_text for term in ["customer", "service", "experience"]):
            themes.append("customer experience")
        if any(term in all_hypotheses_text for term in ["data", "analytics", "insights", "predictive"]):
            themes.append("data-driven decision making")
        if any(term in all_hypotheses_text for term in ["risk", "fraud", "security"]):
            themes.append("risk management")
        
        # Create composite alignment based on category and themes
        category_descriptions = {
            "process_automation": "automation capabilities",
            "fraud_detection": "security and monitoring systems", 
            "customer_service": "customer engagement tools",
            "risk_management": "analytical and assessment capabilities"
        }
        
        capability_description = category_descriptions.get(category, "AI capabilities")
        
        if themes:
            theme_list = ", ".join(themes[:-1]) + (" and " + themes[-1] if len(themes) > 1 else themes[0])
            return f"Provides essential {capability_description} that support {company_name}'s validated strategic focus areas of {theme_list}, creating a comprehensive AI ecosystem to address the identified business challenges."
        else:
            return f"Delivers foundational {capability_description} that support {company_name}'s strategic transformation agenda, complementing the specific solutions addressing the validated hypotheses."
    
    def _get_demo_recommendations(self, company_info: Dict) -> Dict[str, Any]:
        """Generate demo recommendations when API is not available"""
        industry = company_info.get('industry', 'technology')
        company_name = company_info.get('companyName', 'Your Company')
        
        # Industry-specific demo projects
        demo_projects = {
            "banking": [
                {
                    "title": "AI-Powered Fraud Detection System",
                    "description": "Advanced machine learning system for real-time fraud detection and prevention across all banking channels. Reduces false positives while improving detection accuracy.",
                    "priority": "High",
                    "expected_roi": "350% ROI within 15 months",
                    "timeline": "6-8 months",
                    "investment_range": "$300K-$600K",
                    "business_value": "Reduced fraud losses, improved customer experience, regulatory compliance",
                    "implementation_notes": "Integration with core banking systems, real-time processing infrastructure"
                },
                {
                    "title": "Automated Credit Risk Assessment",
                    "description": "AI-driven credit scoring and loan approval system that analyzes multiple data sources to make faster, more accurate lending decisions.",
                    "priority": "High",
                    "expected_roi": "280% ROI within 12 months",
                    "timeline": "4-6 months",
                    "investment_range": "$200K-$400K",
                    "business_value": "Faster loan processing, reduced default rates, improved customer satisfaction",
                    "implementation_notes": "Data integration, regulatory compliance, model validation"
                },
                {
                    "title": "Intelligent Customer Service Chatbot",
                    "description": "Advanced conversational AI for banking customer service that handles complex inquiries and transactions while maintaining security standards.",
                    "priority": "Medium",
                    "expected_roi": "200% ROI within 10 months",
                    "timeline": "3-5 months",
                    "investment_range": "$150K-$300K",
                    "business_value": "24/7 customer service, reduced operational costs, improved customer experience",
                    "implementation_notes": "NLP integration, security protocols, banking system connectivity"
                }
            ],
            "insurance": [
                {
                    "title": "Automated Claims Processing System",
                    "description": "AI-powered claims assessment and processing that analyzes documents, images, and data to automate claim decisions and reduce processing time.",
                    "priority": "High",
                    "expected_roi": "320% ROI within 14 months",
                    "timeline": "5-8 months",
                    "investment_range": "$250K-$500K",
                    "business_value": "Faster claims processing, improved accuracy, enhanced customer satisfaction",
                    "implementation_notes": "Document processing, image analysis, workflow automation"
                },
                {
                    "title": "Risk Assessment and Pricing Engine",
                    "description": "Machine learning models for more accurate risk assessment and dynamic pricing based on comprehensive data analysis.",
                    "priority": "High",
                    "expected_roi": "300% ROI within 12 months",
                    "timeline": "4-7 months",
                    "investment_range": "$200K-$400K",
                    "business_value": "Better risk pricing, increased profitability, competitive advantage",
                    "implementation_notes": "Data integration, actuarial model enhancement, regulatory compliance"
                },
                {
                    "title": "Predictive Customer Analytics",
                    "description": "AI system to predict customer lifetime value, churn probability, and cross-selling opportunities for targeted marketing.",
                    "priority": "Medium",
                    "expected_roi": "220% ROI within 10 months",
                    "timeline": "3-6 months",
                    "investment_range": "$150K-$300K",
                    "business_value": "Improved customer retention, increased revenue per customer, targeted marketing",
                    "implementation_notes": "Customer data platform, predictive modeling, marketing automation"
                }
            ],
            "technology": [
                {
                    "title": "Intelligent Code Analysis Platform",
                    "description": "AI-powered code review and security analysis system that automatically detects vulnerabilities, performance issues, and suggests optimizations.",
                    "priority": "High",
                    "expected_roi": "250% ROI within 10 months",
                    "timeline": "3-5 months",
                    "investment_range": "$150K-$300K",
                    "business_value": "Improved code quality, reduced security risks, faster development cycles",
                    "implementation_notes": "DevOps integration, static analysis tools, automated reporting"
                },
                {
                    "title": "Predictive Infrastructure Management",
                    "description": "Machine learning system for infrastructure monitoring, capacity planning, and automated resource optimization.",
                    "priority": "High",
                    "expected_roi": "300% ROI within 12 months",
                    "timeline": "4-7 months",
                    "investment_range": "$200K-$450K",
                    "business_value": "Reduced infrastructure costs, improved performance, automated scaling",
                    "implementation_notes": "Cloud platform integration, monitoring systems, automated deployment"
                },
                {
                    "title": "AI-Powered User Experience Optimization",
                    "description": "Intelligent system for A/B testing, user behavior analysis, and automated UX improvements across digital products.",
                    "priority": "Medium",
                    "expected_roi": "180% ROI within 8 months",
                    "timeline": "3-5 months",
                    "investment_range": "$100K-$250K",
                    "business_value": "Improved user engagement, higher conversion rates, data-driven UX decisions",
                    "implementation_notes": "Analytics integration, A/B testing framework, user tracking"
                }
            ]
        }
        
        projects = demo_projects.get(industry, demo_projects["technology"])
        
        strategic_insights = f"For companies in the {industry} industry, focus on AI projects that demonstrate clear ROI and align with your strategic priorities. Start with high-impact, lower-risk implementations to build internal AI capabilities and stakeholder confidence before tackling more complex transformational projects."
        
        return {
            "projects": projects,
            "strategic_insights": strategic_insights
        }
