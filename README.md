# 📊 Past Paper Analyzer (Chemistry)

A FastAPI-based backend that analyzes exam papers (PDFs) and extracts **chapter-level topics**, question frequency, and difficulty distribution using AI.

---

# video link :
https://drive.google.com/file/d/1bRG_PDZ3PoueyEviCyiyESg_J-lqxhiu/view?usp=drivesdk,
https://drive.google.com/file/d/1uNXUheXWzRDP785x84MbJiv5wSwOc0k8/view?usp=drivesdk



## 🚀 Features

* 📄 Upload PDF exam papers (supports scanned + text PDFs)
* 🔍 OCR fallback using Tesseract for scanned documents
* 🧠 AI-powered topic extraction (chapter-level, not broad domains)
* 📊 Topic frequency analysis (questions per chapter)
* ⚖️ Difficulty distribution (easy / medium / hard)
* 📅 Auto-generated 7-day study plan

---

## 🧠 Key Improvement

Unlike basic analyzers, this system:

* ❌ Avoids vague categories like *Organic / Inorganic / Physical*
* ✅ Extracts **actual chapters** like:

  * Electrochemistry
  * Thermodynamics
  * Chemical Kinetics
  * Coordination Compounds

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
* Add to PATH
* Install Poppler (for pdf2image)

---

## 🔑 Environment Setup

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
```

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
  "summary": "Paper focuses more on physical chemistry chapters."
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
* AI output is cleaned to remove unwanted broad categories
* Requires stable internet (OpenRouter API)

---

## 🧪 Future Improvements

* Multi-paper trend analysis
* Subject support beyond Chemistry
* Frontend dashboard (charts + insights)
* Topic-wise prediction for upcoming exams

---

## 👨‍💻 Author

Built for analyzing past exam papers efficiently using AI.

---

## 📄 License

Open-source (customize as needed)
