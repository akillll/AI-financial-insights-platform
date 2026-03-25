# AI-Powered Financial Household Management

---

## Table of Contents
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [How It Works](#how-it-works)
- [Why It Works This Way](#why-it-works-this-way)
- [Assumptions](#assumptions)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy |
| Database | Dev: MySQL · Prod: PostgreSQL |
| Transcription | OpenAI Whisper (`gpt-4o-transcribe`) |
| Audio Extraction | GPT-4o |
| Column Mapping | GPT-4o-mini |
| Frontend | ReactJS + TailwindCSS + Recharts |
| Hosting | Render (backend) + Netlify (frontend) |

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Backend

```bash
git clone https://github.com/akillll/AI-financial-insights-platform.git
cd backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Fill in: DATABASE_URL, OPENAI_API_KEY
```

Run migrations:
```bash
alembic upgrade head
```

Start server:
```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## How It Works

### Excel Upload

Wealth management spreadsheets are messy in practice. Every advisor, CRM, and custodian has their own column naming conventions — "AUM", "Account Value", "Total Assets" all mean the same thing. Rather than hardcoding a rigid mapping that breaks the moment a new format shows up, the pipeline has three stages:

**Stage 1 — AI Column Mapping**

Every set of column headers gets passed to GPT-4o-mini, which figures out what each column actually means and maps it to a standard field name (e.g. `"Client DOB"` → `date_of_birth`, `"AUM"` → `account_value`). The mapping is cached in memory, so uploading the same sheet structure again costs zero extra API calls. For this demo, the cache is in-memory and resets every session — in production this would be replaced with something like Redis.

**Stage 2 — Sanitization**

Before any data touches the database, a single `sanitize_dataframe()` call converts every pandas NaN, NaT, and NA into Python `None`. This happens at one place — the edge of the DataFrame — rather than being scattered across dozens of field-specific checks. Any new column or unexpected format gets caught here automatically.

**Stage 3 — Upsert Pipeline**

Data is grouped by household name and written through a chain of upsert functions: Household → Members → Investment Experience → Accounts → Investment Profiles → Bank Accounts → Beneficiaries. Every function is idempotent — uploading the same file twice updates existing records rather than creating duplicates. Account deduplication uses account number as the primary key, and falls back to account type + custodian when no number is present.

---

### Audio Upload

Advisors often record voice notes after client meetings. The audio pipeline is designed to turn those recordings into structured data that enriches an existing client record — not create a shadow duplicate.

**Step 1 — Transcription**

The audio file is transcribed using OpenAI's `gpt-4o-transcribe` model.

**Step 2 — Extraction**

The transcript is passed to GPT-4o with a detailed prompt that covers every field in the data model — household financials, member details, investment experience, accounts, beneficiaries, and bank details. The prompt also handles things like compound risk tolerances ("conservative to moderate").

**Step 3 — Validation**

A Pydantic model (`AudioExtract`) validates everything before it touches the database — clamping percentages to valid ranges, normalising dates regardless of how they were spoken, and rejecting negative financial values.

**Step 4 — Save + Confirm**

Extracted data is immediately saved to the database and returned to the advisor with primary keys attached. The advisor reviews the pre-filled form, makes any corrections, and submits. The confirm step updates records by ID only — no fuzzy field matching at this stage.

---

## Why It Works This Way

### The Column Mapping Problem

Hardcoding a column map is a maintenance trap — it breaks the moment a new advisor joins or a custodian changes their export format. Using GPT-4o-mini as the mapping layer means novel column names just work with no engineering needed. `"Client Net Worth"`, `"Total NW"`, and `"NW ($)"` all correctly resolve to `total_net_worth`.

This approach also fits fintech compliance requirements well: only the column headers are ever sent to the LLM, never the actual customer data. The sensitive data stays local and only the sheet structure is exposed. This makes the solution cheaper (fewer tokens), faster, and safer for an industry where customer data privacy is non-negotiable.

### Human-in-the-Loop on Audio

Audio uploads are always tied to a household the advisor selects before uploading. The alternative — letting the AI guess which household to update — creates a silent data corruption risk that's hard to detect and damaging to fix. Requiring the advisor to pick the household first keeps a human in the loop at the one point where a mistake matters most. In practice it's a one-click confirmation, not a burden.

### Two-Step Extract + Confirm

The audio pipeline saves extracted data immediately after transcription and returns it to the advisor as a pre-filled form. The advisor reviews, corrects anything the model got wrong, and confirms. This means the AI does the heavy lifting of structuring the data, but a human has eyes on it before it's treated as final.

### Idempotent Writes

Every write is an upsert. Uploading the same Excel file twice is safe — existing records get updated, not duplicated. This matters because advisors frequently re-export and re-upload corrected sheets.

### Incomplete Data Is Fine

The pipeline never errors on missing fields. `set_if_present()` ensures only non-null values are written, so a household with just a name and income is as valid as one with full account details.

### Known Limitation — Unstructured Notes

The audio extraction prompt captures fields that don't map to any database column — things like financial priorities, asset notes, and career change context. Currently these are returned in the API response but not persisted. Storing them as freeform advisor notes is an obvious next step.

### AI Reliability & Confidence Scoring (Planned)

One thing I started exploring but couldn't fully complete within the time available is a confidence layer on top of audio extraction. The idea is to assign a score to each extracted value by combining two signals — self-consistency (running extraction multiple times and checking how often the model agrees with itself) and grounding (verifying that the extracted value actually appears in the transcript using fuzzy matching). In a financial context, blindly trusting AI output is a real risk. Surfacing confidence scores in the review UI would help advisors know exactly where to focus their attention before confirming data.

---

> **A note on product thinking**
>
> The real moat for a system like this isn't the technology — it's domain understanding. Financial workflows vary a lot across advisors, firms, and tools, and the edge cases that matter most (partial ownership, conflicting updates, informal notes, non-standard terminology) only show up through real-world use. The closer you work with actual financial professionals, the more of these you catch early. That feedback loop — real users, real scenarios, continuous iteration — is what turns a working technical solution into something that actually fits how people work day to day.

---

## Assumptions

- **Audio always maps to an existing household.** The UI enforces this by requiring household selection before upload. Audio is for enriching existing records, not creating new ones.

- **Household name is the unique identifier for Excel imports.** Two rows sharing a household name are treated as the same household. This matches how wealth management works in practice — a household represents a family unit.

- **Account deduplication uses account number first, then type + custodian.** Account numbers are the most stable identifier. When absent, type + custodian is used as a composite key.

- **Column mapping cache is keyed by header set.** The same columns always produce the same mapping. Cache is in-memory for this demo and resets on server restart — production would use Redis or similar.

- **GPT-4o-mini handles column mapping; GPT-4o handles audio extraction.** Column mapping is a straightforward classification task that doesn't need the full model. Audio extraction involves ambiguity and inference across many field types, so it gets the stronger model.