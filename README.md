# 📊 Past Paper Analyzer

A FastAPI-based backend that analyzes exam papers (PDFs) and extracts **chapter-level topics**, question frequency, and difficulty distribution using AI.

---

## 🚀 Features

* 📄 Upload PDF exam papers (supports scanned + text PDFs)
* 🔍 OCR fallback using Tesseract for scanned documents
* 🧠 AI-powered topic extraction (chapter-level, not broad domains)
* 📊 Topic frequency analysis (questions per chapter)
* ⚖️ Difficulty distribution (easy / medium / hard)
* 📅 Auto-generated 7-day study plan

---

## 🧠 Key Capability

This system:

* ❌ Avoids vague categories like broad subject domains
* ✅ Extracts **specific chapters/topics** such as:

  * Electrochemistry
  * Thermodynamics
  * Data Structures
  * Probability
  * Operating Systems

---

## 🛠️ Tech Stack

* **Backend:** FastAPI
* **AI API:** OpenRouter
* **PDF Parsing:** pdfplumber
* **OCR:** pytesseract + pdf2image + PIL
* **Language:** Python

---

## 📦 Installation

### 1. Clone repo

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install system dependencies

#### Ubuntu:

```bash
sudo apt install tesseract-ocr poppler-utils
```

#### Windows:

* Install Tesseract: https://github.com/tesseract-ocr/tesseract
* Add it to PATH
* Install Poppler (required for pdf2image)

---

## 🔑 API Key Setup (IMPORTANT)

This project requires your own OpenRouter API key.

### Steps:

1. Go to: https://openrouter.ai
2. Create an account
3. Generate an API key

### Then create a `.env` file in your project root:

```env
OPENROUTER_API_KEY=your_api_key_here
```

⚠️ Without this key, the analyzer will not work.

---

## ▶️ Run the Server

```bash
uvicorn app:app --reload
```

Server runs at:

```
http://localhost:8000
```

---

## 📡 API Endpoints

### 1. Upload PDF

**POST** `/upload-paper`

**Input:** form-data (file)

**Output:**

```json
{
  "text": "extracted text..."
}
```

---

### 2. Analyze Topics

**POST** `/analyze-topics`

**Input:**

```json
{
  "text": "extracted paper text"
}
```

**Output:**

```json
{
  "topics": {
    "Electrochemistry": 3,
    "Thermodynamics": 4
  },
  "difficulty_distribution": {
    "easy": 5,
    "medium": 6,
    "hard": 2
  },
  "summary": "Paper focuses more on specific core chapters."
}
```

---

### 3. Generate Study Plan

**POST** `/generate-study-plan`

**Input:**

```json
{
  "topics": {
    "Electrochemistry": 3,
    "Thermodynamics": 4
  }
}
```

**Output:**

```json
{
  "study_plan": [
    {"day": 1, "topic": "Thermodynamics", "hours": 2, "priority": "high"}
  ],
  "total_days": 7
}
```

---

### 4. Health Check

**GET** `/health`

---

## ⚠️ Notes

* OCR is triggered automatically if text extraction is weak
* Large PDFs are truncated (~6000 chars) for AI processing
* AI output is cleaned to remove overly broad categories
* Requires stable internet connection

---

## 🧪 Future Improvements

* Multi-paper trend analysis
* More subject support
* Frontend dashboard (charts + insights)
* Topic prediction for upcoming exams

---

## 👨‍💻 Author

Built for analyzing past exam papers efficiently using AI.

---

## 📄 License

Open-source (customize as needed)

# video link :
https://drive.google.com/file/d/1bRG_PDZ3PoueyEviCyiyESg_J-lqxhiu/view?usp=drivesdk,
https://drive.google.com/file/d/1uNXUheXWzRDP785x84MbJiv5wSwOc0k8/view?usp=drivesdk




