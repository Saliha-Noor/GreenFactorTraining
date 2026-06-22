# ⚖️ LegalLens — Multi-Agent Legal Contract Review System

A production-ready, AI-powered legal contract review system that uses **4 specialized agents** orchestrated via **LangGraph** to automatically extract, classify, and assess risk across **41 CUAD clause types** from uploaded PDF contracts.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [The 4-Agent Pipeline](#the-4-agent-pipeline)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [CUAD Dataset](#cuad-dataset)
- [Anti-Hallucination Measures](#anti-hallucination-measures)
- [Contributing](#contributing)

---

## Overview

LegalLens automates the tedious process of reviewing legal contracts by leveraging a multi-agent AI pipeline. Upload a PDF contract and receive a structured risk analysis report — complete with identified clauses, risk scores, negotiation tips, and an executive summary — all grounded in the **Contract Understanding Atticus Dataset (CUAD)**.

The system is designed with **anti-hallucination safeguards** at every stage, ensuring that all identified clauses are backed by exact verbatim quotes from the source document.

---

## Key Features

- **🤖 4-Agent AI Pipeline** — Parser, Classifier, Risk Analyzer, and Report Generator working in sequence
- **📊 41 CUAD Clause Types** — Full coverage of the industry-standard CUAD taxonomy
- **🔒 Anti-Hallucination Validation** — Every clause quote is verified against the source text
- **📈 Risk Scoring (1–10)** — Each clause receives a granular risk score with rationale
- **💡 Negotiation Tips** — Actionable suggestions for each risky clause
- **📝 Executive Summary** — AI-generated overview with key recommendations
- **📄 Word Report Export** — Download professionally formatted `.docx` reports
- **🖥️ Modern Web UI** — Drag-and-drop PDF upload with real-time pipeline progress tracking
- **📚 CUAD Database Browser** — Explore all 41 clause types and their training examples
- **📜 Analysis History** — View and compare past contract analyses
- **⚡ Rate Limit Resilience** — Built-in retry logic with exponential backoff for API rate limits

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/JS/CSS)                │
│              Drag & Drop Upload · Live Progress         │
│              Report Viewer · History · CUAD Browser      │
└────────────────────────┬────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────┐
│                  FastAPI Backend (main.py)               │
│            File Upload · Background Tasks · CORS        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│             LangGraph Orchestrator Pipeline              │
│                                                         │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌───────┐ │
│  │  Parser   │→│ Classifier  │→│   Risk    │→│Report │ │
│  │  Agent    │  │   Agent     │  │ Analyzer  │ │ Agent │ │
│  │(PyPDF2)  │  │(Groq LLM)  │  │(Groq LLM)│ │(Groq) │ │
│  └──────────┘  └────────────┘  └──────────┘  └───────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│            SQLite Database + CUAD Dataset                │
│     41 Clause Types · Training Examples · History        │
└─────────────────────────────────────────────────────────┘
```

---

## The 4-Agent Pipeline

| Agent | Name | Role | LLM? |
|-------|------|------|------|
| **Agent 1** | PDF Parser | Extracts and cleans text from uploaded PDF contracts page-by-page | ❌ Deterministic |
| **Agent 2** | CUAD Classifier | Identifies and categorizes clauses into the 41 CUAD types using overlapping page chunks | ✅ Groq LLM |
| **Agent 3** | Risk Analyzer | Evaluates each clause's specific language for risk and assigns scores (1–10) | ✅ Groq LLM |
| **Agent 4** | Report Generator | Assembles the final structured report with executive summary and recommendations | ✅ Groq LLM |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **AI Orchestration** | LangGraph |
| **LLM Provider** | Groq (LLaMA 3.1 8B Instant) |
| **LLM Framework** | LangChain |
| **PDF Processing** | PyPDF2 |
| **Database** | SQLite + SQLAlchemy ORM |
| **Data Validation** | Pydantic |
| **Report Generation** | python-docx |
| **Frontend** | HTML5, Vanilla CSS, Vanilla JavaScript |
| **Dataset** | CUAD v1 (Contract Understanding Atticus Dataset) |

---

## Project Structure

```
Legal-contract-Reviewer/
├── main.py                  # FastAPI app entry point & API routes
├── config.py                # Central configuration (paths, API keys)
├── setup_cuad.py            # One-time CUAD dataset download & DB seeding
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (API keys) — NOT committed
├── .gitignore               # Git ignore rules
│
├── agents/                  # The 4 AI agents
│   ├── __init__.py
│   ├── state.py             # LangGraph shared state definition (TypedDict)
│   ├── orchestrator.py      # LangGraph pipeline wiring (START → END)
│   ├── parser_agent.py      # Agent 1: PDF text extraction & cleaning
│   ├── classifier_agent.py  # Agent 2: CUAD clause classification
│   ├── risk_agent.py        # Agent 3: Risk evaluation & scoring
│   └── report_agent.py      # Agent 4: Final report assembly
│
├── database/                # Database layer
│   ├── __init__.py
│   ├── connection.py        # SQLAlchemy engine & session factory
│   ├── models.py            # ORM models (ClauseType, ClauseExample, AnalyzedContract)
│   └── seed_cuad.py         # CUAD JSON parser & database seeder
│
├── schemas/                 # Pydantic validation models
│   └── contract.py          # IdentifiedClause, RiskAssessment, ContractReport
│
├── reports/                 # Report generation
│   ├── __init__.py
│   └── docx_generator.py    # Word document report generator
│
├── frontend/                # Web UI
│   ├── index.html           # Main HTML page
│   ├── style.css            # Styling (dark theme, glassmorphism)
│   └── app.js               # Frontend logic (upload, polling, rendering)
│
├── uploads/                 # Uploaded PDF contracts (auto-created)
├── reports/                 # Generated DOCX reports (auto-created)
└── cuad_data/               # Downloaded CUAD dataset (auto-created)
```

---

## Setup & Installation

### Prerequisites

- **Python 3.11+**
- A **Groq API Key** (free at [console.groq.com](https://console.groq.com))

### 1. Clone the Repository

```bash
git clone https://github.com/<your-org>/Legal-contract-Reviewer.git
cd Legal-contract-Reviewer
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
DATABASE_URL=sqlite:///contract_review.db
```

### 5. Download CUAD Dataset & Seed Database

```bash
python setup_cuad.py
```

This will:
- Download the CUAD v1 JSON dataset (~25 MB) from GitHub
- Initialize the SQLite database
- Seed 41 clause type definitions and training examples

### 6. Start the Server

```bash
python main.py
```

The server will start at **http://localhost:8000**.

---

## Usage

1. Open **http://localhost:8000** in your browser.
2. **Drag and drop** a PDF contract onto the upload zone (or click to browse).
3. Watch the **4-agent pipeline** execute in real-time with progress indicators.
4. View the generated **risk analysis report** directly in the browser.
5. **Download** a formatted Word (.docx) report for offline sharing.
6. Browse the **CUAD Database** tab to explore all 41 clause types and their training examples.
7. Check the **History** tab to revisit past contract analyses.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload a PDF and trigger the analysis pipeline |
| `GET` | `/api/pipeline/status/{task_id}` | Poll real-time pipeline execution status |
| `GET` | `/api/reports` | List all previously analyzed contracts |
| `GET` | `/api/reports/{id}` | Get a specific analysis report (JSON) |
| `GET` | `/api/reports/{id}/download` | Download the Word (.docx) report |
| `GET` | `/api/clause-types` | List all 41 CUAD clause types |
| `GET` | `/api/clause-examples/{id}` | Get CUAD training examples for a clause type |
| `GET` | `/api/stats` | Dashboard statistics |

---

## CUAD Dataset

The system is grounded in the **Contract Understanding Atticus Dataset (CUAD)**, a large-scale dataset of 13,000+ expert-annotated clauses across 510 commercial legal contracts. The 41 clause types include:

| Category | Examples |
|----------|----------|
| **Identification** | Document Name, Parties, Agreement Date, Effective Date |
| **Duration** | Expiration Date, Renewal Term, Notice Period to Terminate |
| **Restrictions** | Non-Compete, Exclusivity, No-Solicit, Anti-Assignment |
| **IP & Licensing** | IP Ownership, License Grant, Source Code Escrow |
| **Financial** | Revenue Sharing, Price Restrictions, Minimum Commitment |
| **Liability** | Uncapped Liability, Cap on Liability, Liquidated Damages |
| **Other** | Governing Law, Audit Rights, Insurance, Warranty Duration |

---

## Anti-Hallucination Measures

LegalLens implements multiple safeguards to prevent AI hallucination:

1. **Exact Quote Requirement** — The LLM is instructed to quote verbatim text from the contract.
2. **Multi-Strategy Post-Validation** — Every quoted excerpt is verified against the source document using 5 matching strategies (first-N words, last-N words, sliding window).
3. **Whitespace Normalization** — PDF line breaks and formatting are normalized before validation to prevent false negatives.
4. **Clause Type Validation** — Only the 41 defined CUAD types are accepted; unknown types are rejected.
5. **Confidence Scoring** — Weaker matches receive reduced confidence scores for transparency.
6. **Deterministic Parsing** — Agent 1 (Parser) uses no LLM, eliminating hallucination at the extraction stage.
7. **Rule-Based Fallback** — If the LLM fails, Agent 3 falls back to predefined base-risk scores per clause type.

---

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

---

## License

This project is developed for academic and research purposes.

---

<p align="center">
  <strong>Built with ❤️ using LangGraph • Groq • CUAD</strong><br>
  <em>Prepared by Muhammad Abuzar Ejaz</em>
</p>
