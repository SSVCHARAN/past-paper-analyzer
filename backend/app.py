from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import requests
import json
from dotenv import load_dotenv
import os
import re
from typing import List

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def extract_json_from_text(text):
    """Extract JSON from text that might be wrapped in markdown"""
    try:
        return json.loads(text)
    except:
        pass
    
    patterns = [
        r'```json\n(.*?)\n```',
        r'```\n(.*?)\n```',
        r'\{.*\}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1) if '```' in pattern else match.group(0))
            except:
                continue
    
    return None

@app.post("/upload-paper")
async def upload_paper(files: List[UploadFile] = File(...)):
    """Extract text from multiple PDFs (handles both text and scanned PDFs with OCR)"""
    combined_text = ""
    
    for file in files:
        try:
            content = await file.read()
            
            temp_filename = f"temp_{file.filename}"
            with open(temp_filename, "wb") as f:
                f.write(content)
            
            text = ""
            
            # First try normal text extraction
            print(f"Trying normal text extraction for {file.filename}...")
            try:
                with pdfplumber.open(temp_filename) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            except Exception as e:
                print(f"Text extraction failed: {e}")
            
            # If minimal text found, use OCR on images with preprocessing
            if not text or len(text.strip()) < 100:
                print(f"Text too short for {file.filename}, trying OCR with preprocessing...")
                try:
                    import pytesseract
                    from pdf2image import convert_from_path
                    from PIL import Image, ImageEnhance, ImageFilter
                    
                    images = convert_from_path(temp_filename, dpi=300)
                    print(f"Converting {len(images)} pages with DPI 300...")
                    
                    for idx, image in enumerate(images):
                        print(f"OCR processing page {idx + 1}...")
                        
                        # Preprocess image for better OCR
                        # Convert to grayscale
                        image = image.convert('L')
                        
                        # Increase contrast
                        enhancer = ImageEnhance.Contrast(image)
                        image = enhancer.enhance(2)
                        
                        # Increase brightness
                        enhancer = ImageEnhance.Brightness(image)
                        image = enhancer.enhance(1.2)
                        
                        # Sharpen
                        image = image.filter(ImageFilter.SHARPEN)
                        
                        # OCR
                        ocr_text = pytesseract.image_to_string(image, lang='eng')
                        if ocr_text and len(ocr_text.strip()) > 0:
                            text += ocr_text + "\n"
                            print(f"Page {idx + 1}: Extracted {len(ocr_text)} characters")
                        
                except Exception as e:
                    print(f"OCR failed for {file.filename}: {e}")
            
            combined_text += text + "\n\n"
            
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
        except Exception as e:
            print(f"Error processing {file.filename}: {str(e)}")
            
    if not combined_text.strip():
        return {"error": "No text could be extracted from PDFs. Please try different exam papers."}
    
    if len(combined_text.strip()) < 50:
        return {"error": "Extracted text is too short. Please use clearer exam papers."}
    
    print(f"Successfully extracted {len(combined_text)} characters total")
    return {"text": combined_text, "file_count": len(files)}

@app.post("/analyze-topics")
async def analyze_topics(data: dict):
    """Use OpenRouter to extract and analyze topics"""
    paper_text = data.get("text", "")
    
    if not paper_text or len(paper_text.strip()) < 20:
        return {"error": "PDF text is too short"}
    
    paper_text_limited = paper_text[:15000]
    
    prompt = f"""You are an exam paper analyzer. Analyze this exam paper text and identify:
1. LESSON-WISE breakdown: Which lessons/chapters are covered?
2. TOPIC-WISE breakdown: What specific topics within each lesson?
3. Question count per topic
4. Difficulty distribution (easy, medium, hard)

Extract ALL topics and lessons mentioned. Be specific and detailed.

Exam paper text:
{paper_text_limited}

Respond with ONLY a JSON object in this exact format, no other text:
{{
    "topics": {{"Lesson 1: Topic Name": number_of_questions, "Lesson 2: Another Topic": number_of_questions, "Lesson 3: Topic Name": number_of_questions}},
    "difficulty_distribution": {{"easy": number, "medium": number, "hard": number}},
    "summary": "One sentence summary covering all lessons"
}}"""
    
    try:
        print(f"Sending request to OpenRouter...")
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Past Paper Analyzer",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            },
            timeout=60
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = response.text
            print(f"API Error: {error_msg}")
            return {"error": f"API Error {response.status_code}: {error_msg[:200]}"}
        
        result = response.json()
        
        if 'error' in result:
            return {"error": f"API returned error: {result['error']}"}
        
        if 'choices' not in result or len(result['choices']) == 0:
            return {"error": "Invalid API response structure"}
        
        content = result['choices'][0]['message']['content']
        print(f"API Response: {content[:100]}")
        
        parsed = extract_json_from_text(content)
        
        if parsed:
            if "topics" in parsed and "difficulty_distribution" in parsed:
                return parsed
            else:
                return {"error": "API response missing required fields"}
        else:
            return {"error": "Could not parse API response as JSON"}
    
    except requests.exceptions.Timeout:
        return {"error": "API request timed out (>60s)"}
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to API"}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {"error": f"Server error: {str(e)}"}

@app.post("/generate-study-plan")
async def generate_study_plan(data: dict):
    """Generate prioritized study plan based on topics"""
    topics = data.get("topics", {})
    
    if not topics:
        return {"error": "No topics provided"}
    
    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
    
    prompt = f"""Create a 7-day study plan for an exam with these topics (sorted by importance):
{json.dumps(sorted_topics)}

Respond with ONLY a JSON object in this exact format, no other text:
{{
    "study_plan": [
        {{"day": 1, "topic": "topic name", "hours": 2, "priority": "high"}},
        {{"day": 2, "topic": "topic name", "hours": 2, "priority": "high"}},
        {{"day": 3, "topic": "topic name", "hours": 1.5, "priority": "medium"}},
        {{"day": 4, "topic": "topic name", "hours": 1.5, "priority": "medium"}},
        {{"day": 5, "topic": "topic name", "hours": 1, "priority": "low"}},
        {{"day": 6, "topic": "topic name", "hours": 1, "priority": "low"}},
        {{"day": 7, "topic": "Revision of all topics", "hours": 2, "priority": "high"}}
    ],
    "total_days": 7
}}"""
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return {"error": f"API Error: {response.text[:200]}"}
        
        result = response.json()
        
        if 'error' in result:
            return {"error": f"API returned error: {result['error']}"}
        
        if 'choices' not in result or len(result['choices']) == 0:
            return {"error": "Invalid API response"}
        
        content = result['choices'][0]['message']['content']
        
        parsed = extract_json_from_text(content)
        
        if parsed and "study_plan" in parsed:
            return parsed
        else:
            return {"error": "Could not parse study plan response"}
    
    except requests.exceptions.Timeout:
        return {"error": "API request timed out"}
    except Exception as e:
        return {"error": f"Error generating study plan: {str(e)}"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "api_key_set": bool(OPENROUTER_API_KEY)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)