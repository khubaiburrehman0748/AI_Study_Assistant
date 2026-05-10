# 🎓 AI Study Assistant
### Smart Q&A + Adaptive Study Planner + Task Tracker

A full-stack web application that helps students study smarter:
answers academic questions via LLM, generates structured study plans,
tracks task completion, and adapts suggestions based on progress.

---

## 📁 File Structure

```
ai_study_assistant/
├── backend/
│   ├── app.py                   # Flask entry point (serves API + frontend)
│   ├── requirements.txt
│   ├── .env.example             # Copy to .env and add your API key
│   ├── data/                    # Auto-created — stores tasks.json, plans.json
│   ├── modules/
│   │   ├── llm_handler.py       # OpenRouter / Groq API calls
│   │   ├── intent_detector.py   # Keyword-based intent classification
│   │   ├── planner.py           # Study plan generation logic
│   │   └── tracker.py           # Task CRUD + progress stats + suggestions
│   └── routes/
│       ├── chat.py              # POST /api/chat  — main chat endpoint
│       ├── planner.py           # POST /api/plan  — direct plan creation
│       └── tracker.py           # GET/PATCH /api/tasks, /api/progress, etc.
└── frontend/
    ├── templates/
    │   └── index.html           # Single-page app shell
    └── static/
        ├── css/style.css        # Dark editorial UI
        └── js/app.js            # All frontend logic
```

---

## ⚡ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A free API key from [OpenRouter](https://openrouter.ai) or [Groq](https://console.groq.com)

### 2. Install dependencies
```bash
cd ai_study_assistant/backend
pip install -r requirements.txt
```

### 3. Configure API key
```bash
cp .env.example .env
# Edit .env and paste your API key
```

**For OpenRouter** (recommended — free tier available):
```
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
```

**For Groq** (very fast, free):
```
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
```

### 4. Run the server
```bash
cd backend
python app.py
```

### 5. Open the app
Visit: **http://localhost:5000**

---

## 🔌 API Reference

### POST /api/chat
Main chat endpoint — handles all user input.

**Request:**
```json
{
  "message": "What is database normalization?",
  "context": "studying DBMS"
}
```

**Response:**
```json
{
  "reply": "Database normalization is the process of organizing...",
  "intent": "question",
  "confidence": "high",
  "data": { "type": "answer" }
}
```

---

### POST /api/plan
Create a study plan directly.

**Request:**
```json
{
  "subject": "Python",
  "days": 5,
  "hours_per_day": 3,
  "goal": "Final exam"
}
```

**Response:**
```json
{
  "success": true,
  "plan_id": "a3f2bc1d",
  "tasks_created": 14,
  "plan": {
    "subject": "Python",
    "days": 5,
    "total_topics": 10,
    "schedule": [...]
  }
}
```

---

### GET /api/tasks
List all tasks. Optional query params: `status=pending|done`, `subject=Python`

### PATCH /api/tasks/{task_id}/status
```json
{ "status": "done" }
```

### GET /api/progress
Returns completion stats.

### GET /api/suggest
Returns adaptive next-step suggestion.

---

## 💬 Sample Chat Inputs & Outputs

| User Input | Detected Intent | Bot Behaviour |
|---|---|---|
| "What is recursion?" | question | Calls LLM, returns explanation |
| "Explain Big O notation" | question | Calls LLM with academic prompt |
| "Study plan for Database, 5 days, 2h/day" | planning | Generates 5-day plan, saves tasks |
| "Show my progress" | progress | Returns stats + progress bar |
| "What should I study next?" | suggestion | Returns adaptive next-task advice |
| "Mark task done" (with task_id) | progress | Updates task status in JSON |
| "Hi!" | general | Greeting response |

---

## 🧠 Intent Detection Logic

No ML — pure keyword matching:

| Intent | Trigger keywords |
|---|---|
| `question` | what, why, how, explain, define + ends with ? |
| `planning` | study plan, schedule, exam in, N days |
| `progress` | done, completed, show progress, tasks |
| `suggestion` | what next, suggest, what should I |
| `general` | anything else (falls back to LLM Q&A) |

---

## 🔒 LLM Usage Policy

The LLM is called **only** for:
- Answering academic questions
- Generating topic explanations

It is **NOT** used for:
- Study plan structure (pure Python logic)
- Task tracking (JSON file operations)
- Intent detection (keyword rules)
- Progress calculation (arithmetic)

This keeps the system **predictable, fast, and cost-efficient**.

---

## 📊 Data Storage

Data is saved in `backend/data/` as JSON:

**tasks.json** — array of task objects:
```json
{
  "id": "a1b2c3d4",
  "subject": "Python",
  "day": 1,
  "topic": "Variables & Data Types",
  "duration_hours": 1.5,
  "type": "study",
  "status": "pending",
  "created_at": "2025-01-01T10:00:00"
}
```

**plans.json** — map of plan metadata by plan_id.

---


