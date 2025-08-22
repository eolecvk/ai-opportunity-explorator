import uuid
from typing import Dict, List
from datetime import datetime
from src.models import ChatMessage, LeadQualification
from src.ai_client import GeminiAIClient

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, List[ChatMessage]] = {}
        self.ai_client = GeminiAIClient()
    
    def create_conversation(self) -> str:
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = []
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        self.conversations[conversation_id].append(message)
    
    async def process_user_message(self, conversation_id: str, user_message: str) -> Dict:
        if conversation_id not in self.conversations:
            conversation_id = self.create_conversation()
        
        # Add user message to conversation
        self.add_message(conversation_id, "user", user_message)
        
        # Get conversation context
        context = self._build_context(conversation_id)
        
        # Generate AI response
        ai_response = await self.ai_client.generate_response(user_message, context)
        
        # Add AI response to conversation
        self.add_message(conversation_id, "assistant", ai_response)
        
        # Qualify lead if conversation has enough context
        lead_qualification = None
        if len(self.conversations[conversation_id]) >= 4:  # At least 2 exchanges
            lead_qualification = await self.ai_client.qualify_lead(
                [msg.dict() for msg in self.conversations[conversation_id]]
            )
        
        return {
            "response": ai_response,
            "conversation_id": conversation_id,
            "lead_score": lead_qualification.get("score") if lead_qualification else None,
            "next_steps": lead_qualification.get("nextSteps") if lead_qualification else None,
            "ai_opportunities": lead_qualification.get("aiOpportunities") if lead_qualification else None,
            "business_impact": lead_qualification.get("businessImpact") if lead_qualification else None,
            "feasibility_risk": lead_qualification.get("feasibilityRisk") if lead_qualification else None
        }
    
    def _build_context(self, conversation_id: str) -> Dict:
        conversation = self.conversations.get(conversation_id, [])
        
        # Extract key information from conversation for AI context
        context = {
            "conversation_length": len(conversation),
            "previous_messages": [msg.dict() for msg in conversation[-4:]]  # Last 4 messages
        }
        
        # Extract company information for AI project analysis
        company_info = self._extract_company_info(conversation)
        if company_info:
            context["company_profile"] = company_info
        
        return context
    
    def _extract_company_info(self, conversation: List) -> Dict:
        """Extract company information mentioned in conversation for AI project recommendations"""
        company_info = {}
        
        # Simple keyword extraction (in production, this would use NLP)
        conversation_text = " ".join([msg.content.lower() for msg in conversation if msg.role == "user"])
        
        # Industry detection
        industries = {
            "manufacturing": ["manufacturing", "factory", "production", "assembly"],
            "retail": ["retail", "store", "ecommerce", "shopping", "merchandise"],
            "finance": ["bank", "financial", "insurance", "investment", "fintech"],
            "healthcare": ["healthcare", "hospital", "medical", "pharmaceutical", "clinic"],
            "logistics": ["shipping", "logistics", "supply chain", "warehouse", "delivery"],
            "technology": ["software", "tech", "saas", "platform", "development"]
        }
        
        for industry, keywords in industries.items():
            if any(keyword in conversation_text for keyword in keywords):
                company_info["industry"] = industry
                break
        
        # Company size indicators
        size_indicators = {
            "large": ["enterprise", "corporation", "multinational", "fortune", "1000+", "5000+"],
            "medium": ["medium", "500", "growing", "expanding", "regional"],
            "small": ["startup", "small", "team", "local", "boutique"]
        }
        
        for size, keywords in size_indicators.items():
            if any(keyword in conversation_text for keyword in keywords):
                company_info["size"] = size
                break
        
        return company_info
    
    def get_conversation(self, conversation_id: str) -> List[ChatMessage]:
        return self.conversations.get(conversation_id, [])