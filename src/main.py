from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from src.models import ConversationRequest, ConversationResponse, AIProjectRecommendation, ROICalculatorInput, ROICalculatorResult, ProjectROIInput
from src.conversation_manager import ConversationManager
from src.roi_calculator import ROICalculator

load_dotenv()

app = FastAPI(title="AI Sales Assistant POC", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the frontend
app.mount("/static", StaticFiles(directory="public"), name="static")

# Initialize conversation manager and ROI calculator
conversation_manager = ConversationManager()
roi_calculator = ROICalculator()

@app.get("/")
async def root():
    return {"message": "AI Sales Assistant POC is running"}

@app.post("/chat", response_model=ConversationResponse)
async def chat(request: ConversationRequest):
    try:
        # Validate API key is configured
        if not os.getenv('GEMINI_API_KEY'):
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Validate message content
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        result = await conversation_manager.process_user_message(
            request.conversation_id or conversation_manager.create_conversation(),
            request.message
        )
        
        return ConversationResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    conversation = conversation_manager.get_conversation(conversation_id)
    return {"conversation_id": conversation_id, "messages": conversation}

@app.post("/ai-recommendations")
async def get_ai_recommendations(company_info: dict):
    """Generate AI project recommendations based on company profile"""
    try:
        recommendations = await conversation_manager.ai_client.generate_ai_project_recommendations(company_info)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/roi-calculator", response_model=ROICalculatorResult)
async def calculate_roi(input_data: ROICalculatorInput):
    """Calculate ROI and business case for AI implementation"""
    try:
        result = roi_calculator.calculate_roi(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ROI calculation failed: {str(e)}")

@app.post("/project-roi")
async def calculate_project_roi(input_data: ProjectROIInput, industry: str = "default", company_size: str = "medium"):
    """Calculate ROI for a specific AI project"""
    try:
        result = roi_calculator.calculate_project_roi(input_data, industry, company_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project ROI calculation failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def main():
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()