# AI Project Sales Assistant POC

A specialized AI sales consultant for identifying and selling high-value AI transformation projects to enterprise clients (like Capgemini's approach).

## Features

- **AI Project Discovery**: Identifies high-ROI AI opportunities in client operations
- **Intelligent Lead Qualification**: Scores leads based on AI project readiness (company size, data maturity, budget, etc.)
- **Competitive Intelligence**: References proven AI implementations at competitor companies
- **ROI & Feasibility Analysis**: Evaluates technical complexity, business impact, and implementation risk
- **Industry-Specific Recommendations**: Tailored AI project suggestions based on company profile
- **Real-time Assessment**: Live conversation analysis and opportunity detection

## Setup

1. **Install dependencies using UV:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

3. **Get a Gemini API key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy it to your `.env` file

## Running the Application

**Development mode:**
```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uv run ai-sales-assistant
```

## Usage

1. Open your browser to `http://localhost:8000/static/index.html`
2. Start chatting with the AI sales assistant
3. The system will automatically qualify leads and provide scores after a few exchanges

## API Endpoints

- `POST /chat` - Send a message to the AI assistant
- `GET /conversation/{id}` - Retrieve conversation history
- `GET /health` - Health check endpoint

## Project Structure

```
src/
├── main.py              # FastAPI application
├── ai_client.py         # Gemini AI integration
├── conversation_manager.py # Conversation logic
├── models.py            # Pydantic data models
└── __init__.py

public/
├── index.html           # Frontend interface
├── style.css            # Styling
└── app.js              # Frontend JavaScript

pyproject.toml          # Project configuration and dependencies
uv.lock                 # Dependency lock file
.env.example            # Environment template
```

## Notes

- This is a POC designed for testing and demonstration
- The Gemini API has a generous free tier perfect for development
- Conversations are stored in memory (will reset on restart)
- For production use, consider adding persistent storage
