# 🌱 GreenDev AI

**Evidence-based green code analysis — 5-agent AI pipeline**

Analyzes Python code for energy consumption and carbon footprint, compares against real Intel RAPL benchmark data, and generates a Green Score + Carbon Cost Projection using Gemini AI.

---

## System Architecture

```
User Uploads Python File
        ↓
Code Analysis Agent  →  ast module (functions, loops, lines, complexity)
        ↓
Planner Agent (Orchestrator)  →  Gemini API — decides execution plan dynamically
        ↓
Energy Agent ∥ Benchmark Agent  →  CodeCarbon + Energy-Languages Dataset (parallel)
        ↓
SCI Agent  →  Estimated SCI + Real SCI (with deviation check)
        ↓
Planner reflects  →  anomaly detection, reflection notes
        ↓
Recommendation Agent  →  Gemini API — Green Score + Carbon Projection (JSON)
        ↓
Report Generator  →  PDF + Markdown
        ↓
React Dashboard  →  all results + Download Report button
```

---

## Tech Stack

| Layer       | Technology                                      |
|-------------|--------------------------------------------------|
| Frontend    | React 18 + Vite + Recharts                       |
| Backend     | FastAPI + Uvicorn                                |
| Agent 1     | Python `ast` module                              |
| Agent 2     | CodeCarbon (`EmissionsTracker`)                  |
| Agent 3     | Energy-Languages Dataset (Python, C, C++, Java)  |
| Agent 4     | SCI formula (IEEE Green Software Foundation)     |
| Agent 5     | Google Gemini API (`gemini-1.5-flash`)           |
| Planner     | Google Gemini API (orchestration + reflection)   |
| Reports     | fpdf2 (PDF) + Markdown                          |

---

## Folder Structure

```
greendev-ai/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── code_analysis_agent.py   # Agent 1 — ast parsing
│   │   ├── energy_agent.py          # Agent 2 — CodeCarbon (✅ tested)
│   │   ├── benchmark_agent.py       # Agent 3 — RAPL dataset
│   │   ├── sci_agent.py             # Agent 4 — SCI formula
│   │   ├── recommendation_agent.py  # Agent 5 — Gemini Green Score
│   │   └── planner_agent.py         # Orchestrator — Gemini planning+reflection
│   ├── data/
│   │   └── dataset_subset.csv       # Python, C, C++, Java RAPL data
│   ├── reports/                     # Generated PDF/MD reports saved here
│   ├── main.py                      # FastAPI server
│   ├── report_generator.py          # PDF + Markdown export
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   ├── GreenScore.jsx
│   │   │   ├── EnergyMetrics.jsx
│   │   │   ├── BenchmarkComparison.jsx
│   │   │   ├── SCIScores.jsx
│   │   │   ├── CarbonProjection.jsx
│   │   │   ├── PlannerInfo.jsx
│   │   │   └── DownloadReport.jsx
│   │   ├── utils/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Setup Instructions

### Step 1 — Clone & enter project

```bash
cd greendev-ai
```

### Step 2 — Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set your Gemini API key
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac

# Edit .env and paste your Gemini API key:
# GEMINI_API_KEY=your_key_here
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

### Step 3 — Run backend

```bash
# Inside backend/ with venv activated
uvicorn main:app --reload --port 8000
```

Backend will be live at: http://localhost:8000

### Step 4 — Frontend setup

```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

Frontend will be live at: http://localhost:5173

---

## Usage

1. Open http://localhost:5173 in your browser
2. Upload any `.py` file using the drag-and-drop zone
3. Click **Analyze Code**
4. Watch the 5-agent pipeline run step by step
5. See results: Green Score, Energy Metrics, RAPL Benchmark, SCI Scores, Carbon Projection
6. Download your full report as **PDF** or **Markdown**

---

## Environment Variables

| Variable        | Description                  | Required |
|-----------------|------------------------------|----------|
| `GEMINI_API_KEY`| Your Google Gemini API key   | ✅ Yes   |

---

## Notes

- **No RAPL hardware needed** — Agent 3 uses pre-collected Intel RAPL data from the Energy-Languages research dataset
- **WSL2 / Windows** — CodeCarbon automatically falls back to TDP-estimation mode (no real RAPL available), which is expected
- **Planner Agent** uses Gemini to dynamically decide execution order and detects anomalies via a reflection loop
- **Dataset** covers 4 languages: Python, C, C++, Java across 8 task types (sorting, binary-trees, fibonacci, matrix-multiply, string-processing, regex, io-heavy, general)

---

## Dataset Source

Energy-Languages Dataset — real Intel RAPL measurements collected on bare-metal hardware by researchers comparing energy efficiency across programming languages.

---

*Built by Saliha Noor — GreenDev AI*
