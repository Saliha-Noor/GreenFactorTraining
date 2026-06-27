# Exam Forge Study Agent — Multi-Agent AI Study Companion

> Turn your lectures and past papers into structured notes, a study plan, a practice paper, and a scored quiz — fully automated using AI.

Built as a course project during an internship at **UAV Lab**, after completing the **Agentic AI course by Andrew Ng on DeepLearning.AI**.

---

## What it does

You connect your Google Classroom, pick a subject folder from GitHub, or upload files directly. Study Agent processes only the files you select and runs them through a 6-agent pipeline:

| Agent | Job |
|---|---|
|  Fetcher | Downloads lectures from Classroom and past papers from GitHub |
|  Notes | Generates structured bullet-point study notes in parallel |
|  Planner | Ranks every topic by exam importance and estimates study time |
|  Paper Analyzer | Finds which topics and question types appear most in past papers |
|  Practice Paper | Generates exam-style open-ended questions matching past paper format |
|  Quiz + Evaluator | Creates a targeted MCQ quiz and scores every answer with AI feedback |

---

## Demo

> Architecture diagram and demo video 

---

## Tech Stack

| Tool | Purpose | Cost |
|---|---|---|
| [Groq API](https://console.groq.com) | LLM inference (llama-3.3-70b + llama-3.1-8b) | Free |
| Google Classroom API | Fetch lectures from enrolled courses | Free |
| Google Drive API | Download attached files | Free |
| GitHub REST API | Fetch past papers by repo and folder | Free |
| Streamlit | Frontend UI | Free |
| python-pptx | Parse PowerPoint slides | Free |
| python-docx | Parse Word documents | Free |
| pdfplumber | Extract text from PDFs | Free |

**100% free to run.**

---

## Project Structure

```
study_agent/
├── app.py                        ← Streamlit UI (run this)
├── .env                          ← API keys (never pushed)
├── credentials.json              ← Google OAuth (never pushed)
├── requirements.txt
│
├── agents/
│   ├── fetcher_agent.py          ← Day 1: downloads + chunks files
│   ├── notes_agent.py            ← Day 2: generates study notes
│   ├── planner_agent.py          ← Day 3: builds study plan
│   ├── paper_analyzer_agent.py   ← Day 4: analyses past papers
│   ├── quiz_agent.py             ← Day 5: generates MCQ quiz
│   ├── practice_paper_agent.py   ← Day 5: generates practice paper
│   └── scoring_agent.py          ← Day 6: scores quiz + feedback
│
├── tools/
│   ├── classroom_tool.py         ← Google Classroom OAuth + download
│   ├── github_tool.py            ← GitHub API: folders + files
│   ├── pdf_tool.py               ← PDF reading + chunking
│   └── file_converter.py         ← PPTX + DOCX → text
│
└── data/
    ├── raw/                      ← downloaded files (not pushed)
    ├── chunks/                   ← JSON text chunks (not pushed)
    └── output/
        ├── notes/                ← generated study notes
        ├── plan.json             ← study plan
        ├── paper_analysis.json   ← past paper patterns
        ├── quiz/                 ← MCQ quiz + practice paper
        ├── scores/               ← score report
        └── feedback/             ← per-question feedback
```

---

## Setup

### 1 — Clone the repo

```bash
git clone https://github.com/Saliha-Noor/GreenFactor.git
cd GreenFactor
git checkout Saliha_Noor
```

### 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### 3 — Create `.env` file

```
GROQ_API_KEY=your_groq_key_here
GITHUB_TOKEN=your_github_token        # optional for public repos
GITHUB_REPOS=username/repo1,username/repo2
```

Get a free Groq key at [console.groq.com](https://console.groq.com).

### 4 — Set up Google Classroom (one-time)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → enable **Google Classroom API** and **Google Drive API**
3. Go to **Credentials → Create OAuth client ID** → choose **Desktop app**
4. Download the JSON → rename it to `credentials.json`
5. Place it in your project root folder

Every user then logs in with their own Gmail account. The app never shares credentials between users.

### 5 — Run

```bash
streamlit run app.py
```

Browser opens at `http://localhost:8501`.

---

## How to use

| Step | What to do |
|---|---|
| 1 | Go to **Add Materials** → connect Classroom or select GitHub folder → pick your files → click Process |
| 2 | Go to **Study & Plan** → generate notes → build study plan → analyse past papers → generate practice paper |
| 3 | Go to **Take Quiz** → generate quiz → answer questions → submit |
| 4 | Go to **My Results** → see your score, grade, and per-question feedback |

To start fresh with different files, click **Clear all** on the Add Materials page.

---

## Key design decisions

**Only selected files are processed.** When you click Process, only the lectures and papers you chose are chunked. Nothing from a previous session carries over.

**Two LLM models.** High-volume tasks (notes, paper analysis) use `llama-3.1-8b-instant` for speed. Quality tasks (planning, quiz, feedback) use `llama-3.3-70b-versatile` for accuracy.

**Parallel processing.** The Notes and Paper Analyzer agents run 5 Groq API calls simultaneously using `ThreadPoolExecutor` — making bulk processing 5x faster than sequential.

**Practice paper ≠ MCQ quiz.** The practice paper generates open-ended, short-answer questions in the style of actual past papers. The quiz generates MCQs. They serve different purposes.

---

## Agentic AI patterns used

- **Tool Use** — each agent calls specific tools in sequence
- **Parallelism** — `ThreadPoolExecutor` for batch LLM calls
- **Planning before acting** — Planner runs before Quiz so questions are weighted correctly
- **Human in the loop** — user attempts the quiz before the Evaluator scores it
- **Retry with backoff** — agents retry failed Groq calls before giving up

All patterns from the **Agentic AI course by Andrew Ng on DeepLearning.AI**.

---

## Requirements

```
groq
pdfplumber
requests
python-dotenv
python-pptx
python-docx
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
streamlit
pandas
```

---

## Important — files not pushed to GitHub

The following are in `.gitignore` and will never be committed:

```
.env
credentials.json
token.json
data/raw/
data/chunks/
data/output/
```

---

## Built with

- 🎓 **Andrew Ng's Agentic AI course** DeepLearning.AI
- 🔬 **UAV Lab internship**  where this was built
- 🐍 Python 3.11+

