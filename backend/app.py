from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.post("/upload-paper")
async def upload_paper(file: UploadFile = File(...)):
    """Extract text from PDF"""
    content = await file.read()
    
    # Save temporarily
    with open("temp.pdf", "wb") as f:
        f.write(content)
    
    # Extract text
    text = ""
    with pdfplumber.open("temp.pdf") as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    
    return {"text": text, "filename": file.filename}

@app.post("/analyze-topics")
async def analyze_topics(data: dict):
    """Use OpenRouter to extract and analyze topics"""
    paper_text = data.get("text")
    
    prompt = f"""
    Analyze this exam paper and extract:
    1. Main topics covered (list them)
    2. Frequency of each topic (how many questions per topic)
    3. Difficulty level of questions (easy/medium/hard)
    
    Paper text:
    {paper_text}
    
    Return as JSON:
    {{
        "topics": {{"topic_name": frequency_count}},
        "difficulty_distribution": {{"easy": count, "medium": count, "hard": count}},
        "summary": "brief summary"
    }}
    """
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Past Paper Analyzer"
        },
        json={
            "model": "google/gemini-2.0-flash-lite",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )
    
    result = response.json()
    content = result['choices'][0]['message']['content']
    
    # Parse JSON from response
    try:
        analysis = json.loads(content)
    except:
        analysis = {"error": "Could not parse response"}
    
    return analysis

@app.post("/generate-study-plan")
async def generate_study_plan(data: dict):
    """Generate prioritized study plan"""
    topics = data.get("topics", {})
    
    prompt = f"""
    Based on these topics and their frequencies, create a prioritized study plan:
    {json.dumps(topics)}
    
    Return as JSON:
    {{
        "study_plan": [
            {{"day": 1, "topic": "...", "hours": 2, "priority": "high"}},
            {{"day": 2, "topic": "...", "hours": 2, "priority": "high"}},
            {{"day": 3, "topic": "...", "hours": 1, "priority": "medium"}},
            {{"day": 4, "topic": "...", "hours": 1, "priority": "medium"}},
            {{"day": 5, "topic": "...", "hours": 1, "priority": "low"}},
            {{"day": 6, "topic": "...", "hours": 0.5, "priority": "low"}},
            {{"day": 7, "topic": "Revision", "hours": 1, "priority": "high"}}
        ],
        "total_days": 7
    }}
    """
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        json={
            "model": "google/gemini-2.0-flash-lite",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    
    result = response.json()
    content = result['choices'][0]['message']['content']
    
    try:
        plan = json.loads(content)
    except:
        plan = {"error": "Could not generate plan"}
    
    return plan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)