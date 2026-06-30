# MultiAgentAssistant

Multi-agent Customer Support (SAC) assistant — answers questions about
**Products, Deliveries, and Payments** using specialized agents + RAG.

> Architecture, decisions, and roadmap: see [docs/PLANEJAMENTO.md](./docs/PLANEJAMENTO.md) and [docs/ROADMAP_ESTUDOS.md](./docs/ROADMAP_ESTUDOS.md).

## Tech stack

- **Python 3.12** · **uv** (dependency management)
- **CrewAI** (multi-agent orchestration)
- **Cerebras** (chat/reasoning LLM, via LiteLLM — swappable; started on Gemini, see note below)
- **Gemini** (embeddings only, for RAG — unrelated to the chat LLM)
- **Chroma** (local vector store for RAG)
- **FastAPI** + **Uvicorn** (backend API)
- **React** + **Vite** (web chat UI)

## Prerequisites

- Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey)) — the free tier is enough
- **Node.js** (LTS) — needed for the React/Vite frontend. Confirm with `node --version`

### 1. Install `uv` (dependency manager)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Close and reopen the terminal, then confirm: `uv --version`

### 2. Install Python (via uv)

```powershell
uv python install 3.12
```

### 3. Install the CrewAI CLI

```powershell
uv tool install crewai
uv tool update-shell
```
Confirm: `crewai version`

## Setup

### Backend (`sac_assistant/`)

1. Clone the repository
2. Enter the crew folder: `cd sac_assistant`
3. Create the `.env` file with:
   ```
   MODEL=gemini/gemini-2.5-flash
   GEMINI_API_KEY=your_key_here
   ```
4. Install dependencies: `crewai install` (includes `fastapi` and `uvicorn`)

### Frontend (`web/`)

1. Enter the web folder: `cd web` (from the repo root)
2. Install dependencies: `npm install`

## How to run

The CLI flow (single hardcoded question, no UI) still works as before:

```powershell
cd sac_assistant
crewai run
```

For the full web chat, you need **two terminals running at the same time**:

**Terminal 1 — backend API:**
```powershell
cd sac_assistant
uv run uvicorn sac_assistant.api.main:app --reload --port 8000
```

**Terminal 2 — frontend:**
```powershell
cd web
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). The chat sends
each question through the same `SacFlow` used by the CLI: a Triage agent
classifies it into Products, Delivery, Payments, or Other, then routes to the
matching specialist crew, grounded in that domain's knowledge base. Each
response shows the cited source (knowledge file or lookup tool) as a small
chip above the message. Out-of-scope questions are declined; questions the
specialists can't ground an answer for are escalated to a mock human handoff
instead of being guessed.

## Project structure

```
MultiAgentAssistant/
├── docs/                       # PLANEJAMENTO.md, ROADMAP_ESTUDOS.md
├── README.md
├── web/                        # React + Vite chat UI
│   └── src/
│       ├── App.jsx             # chat state, fetch to the backend
│       └── App.css
└── sac_assistant/              # CrewAI project
    ├── .env                    # secrets (not committed to git)
    ├── pyproject.toml          # dependencies + commands
    ├── knowledge/              # RAG knowledge base
    │   ├── products/           # catalog, warranty, usage & care
    │   ├── delivery/           # shipping, tracking, timeframes
    │   └── payments/           # payment methods, refunds
    └── src/sac_assistant/
        ├── main.py             # CLI entry point (run/train/test)
        ├── flow.py             # SacFlow: guardrail -> Triage -> router -> specialist crew -> escalation
        ├── api/
        │   └── main.py         # FastAPI app, POST /chat wraps SacFlow
        ├── crews/              # one isolated crew per domain
        │   ├── products_crew/
        │   │   ├── config/agents.yaml, tasks.yaml
        │   │   └── products_crew.py
        │   ├── delivery_crew/  (same layout)
        │   └── payments_crew/  (same layout)
        ├── guardrails/
        │   └── input_guardrail.py   # regex checks for PII / prompt injection
        ├── schemas/
        │   └── specialist_answer.py # structured Task output: answer, found_answer, source
        ├── rag/
        │   ├── ingest.py       # chunking + embeddings -> Chroma (per-domain collection)
        │   └── retriever.py    # similarity search against Chroma (per-domain collection)
        └── tools/
            ├── knowledge_search_tool.py  # one CrewAI Tool per domain, wraps the retriever
            ├── order_tool.py            # mock OrderLookupTool (Delivery)
            ├── payment_tool.py          # mock InvoiceLookupTool (Payments)
            └── ticket_tool.py           # mock open_ticket() for escalation
```

## Environment variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Gemini API key — **only used for RAG embeddings** (`rag/ingest.py`/`retriever.py`), independent of the chat LLM. **Never commit** (stays only in `.env`) |
| `MODEL` | Chat/reasoning LLM used by Triage and the specialists (e.g., `cerebras/gpt-oss-120b`). Swappable thanks to LiteLLM — see note below |
| `CEREBRAS_API_KEY` | Required if `MODEL` points to a `cerebras/...` model |

> **Why Cerebras instead of Gemini for chat**: the project started on `gemini/gemini-2.5-flash`
> for everything, but its free tier is capped at 20 requests/day, which kept getting exhausted
> during manual testing. Cerebras's free tier is far more generous, and — important detail — it's
> one of the few providers crewai treats as "native" (the others tried, like `groq/...`, hit a real
> crewai bug where an internal prompt-caching marker leaks into the request and gets rejected by
> providers without native support). Embeddings stayed on Gemini since switching them would have
> required rewriting `rag/ingest.py`/`retriever.py`, and Anthropic/Groq/Cerebras don't offer an
> embeddings API of their own anyway.

---

## Progress

- [x] **Step 1** — Tooling installed (uv 0.11.21, Python 3.12.13)
- [x] **Step 2** — Gemini API key generated
- [x] **Step 3** — Create the project (CrewAI scaffold in `sac_assistant/`)
- [x] **Step 4** — `.env` configured; `.gitignore` already protects the `.env`
- [x] **Step 5** — hello-crew validated with Gemini (`crewai run` generated `report.md`)

**✅ Phase 0 complete** — CrewAI + Gemini working.

- [x] **Step 1** — Products knowledge base written (`catalog.md`, `guarantee_and_devolution.md`, `usage_and_care.md`)
- [x] **Step 2** — `ingest.py`: chunking by Markdown section + Gemini embeddings + Chroma storage
- [x] **Step 3** — `retriever.py`: similarity search validated (correct chunk retrieved for a paraphrased question)
- [x] **Step 4** — `ProductKnowledgeSearchTool` wrapping the retriever as a CrewAI Tool
- [x] **Step 5** — `products_specialist` agent + `answer_product_question` task replacing the generic template
- [x] **Step 6** — End-to-end validated via `crewai run`: tool calling works, answers cite sources, and the agent honestly declines out-of-scope questions instead of hallucinating

**✅ Phase 1 complete** — single-agent RAG working end-to-end.

- [x] **Step 1** — Delivery and Payments knowledge bases written (`shipping_and_tracking.md`, `payment_and_refunds.md`); Products catalog expanded to 9 items across multiple brands
- [x] **Step 2** — `ingest.py`/`retriever.py` generalized to take a `collection_name`, one Chroma collection per domain (Products, Delivery, Payments)
- [x] **Step 3** — `DeliveryKnowledgeSearchTool` and `PaymentKnowledgeSearchTool` added alongside the existing Product tool
- [x] **Step 4** — Crew split into 3 isolated single-agent crews (`ProductsCrew`, `DeliveryCrew`, `PaymentsCrew`), each with its own `agents.yaml`/`tasks.yaml`
- [x] **Step 5** — Triage agent added (direct `Agent.kickoff()` with structured `TriageResult` output, no Crew overhead)
- [x] **Step 6** — `SacFlow` assembled: `@start` triage → `@router` → `@listen` per domain; validated end-to-end for Products, Delivery, Payments, and out-of-scope ("Other") questions — only the matching crew runs, no wasted LLM calls

**✅ Phase 2 complete** — Triage + multi-agent Flow working end-to-end.

- [x] **Step 1** — Input guardrail (`guardrails/input_guardrail.py`): regex-based detection of PII (CPF, credit card) and prompt-injection patterns, validated for both cases plus a normal question passing through untouched
- [x] **Step 2** — `SacFlow` reorganized: `@start guardrail_check` → `@router` → `"blocked"` (refusal, no LLM call) or `"allowed"` (continues into the existing triage → router → specialist chain)
- [x] **Step 3** — Mock tools added: `OrderLookupTool` (Delivery) and `InvoiceLookupTool` (Payments); validated that the agent correctly picks the lookup tool for a specific order/invoice number vs. the knowledge-search tool for general policy questions, and honestly reports "not found" instead of guessing a status
- [x] **Step 4** — Escalation: `SpecialistAnswer` (Pydantic `output_pydantic`) added to all 3 specialist tasks with an internal `found_answer` flag; `check_escalation` listens to all 3 specialists (`or_`) and overrides the answer with a handoff message + opens a mock ticket (`open_ticket()`) whenever Triage `confidence < 0.6` OR `found_answer` is `false`. Validated end-to-end: a question with no grounded answer in any knowledge base correctly triggered the ticket and the handoff message, with `confidence`/`found_answer` never exposed to the customer.

**✅ Phase 3 complete** — guardrail, mock tools, and escalation all working end-to-end.

- [x] **Step 1** — FastAPI backend (`api/main.py`): `POST /chat` wraps `SacFlow`, returns `{answer, intent, source}` (`confidence` stays internal); validated standalone via `curl`
- [x] **Step 2** — React + Vite chat UI (`web/`): input box, message list, calling the backend over `fetch`; validated end-to-end in the browser — including an unplanned bonus, the agent replying in Portuguese when asked in Portuguese, confirming the bilingual behavior planned since `Plan.md` section 2, though not yet deliberately tested for consistency
- [x] **Step 3** — Polish: `SpecialistAnswer` extended with a `source` field (kept separate from the answer text, instead of the agent citing it inline); UI redesigned with avatar bubbles, fade-in animation, and a "📄 Leu `<file>`" / "🔧 Consultei `<tool>`" chip rendered above the bubble (aligned to it, not the page); the `intent` badge was removed from the bubble since it added no value for the end customer

**✅ Phase 4 complete** — FastAPI backend + React chat UI working end-to-end, citations shown as a separate chip instead of inline text.

- [x] **Knowledge base expansion** — Products knowledge restructured from a single `catalog.md`
  into 12 per-category files (`keyboards.md`, `mice.md`, `headsets.md`, `webcams.md`,
  `backpacks.md`, `mousepads.md`, `monitors.md`, `chairs.md`, `controllers.md`,
  `usb_hubs.md`, `chargers.md`, `ssds.md`), 23 products total, each with deeper specs,
  a per-category Compatibility section, and a per-category FAQ; plus two new cross-cutting
  documents, `model_comparisons.md` and `compatibility_faq.md`. Delivery and Payments each
  got a `specific_*_cases.md` (edge cases: failed delivery attempts, duplicate charges,
  chargebacks, etc.) and a dedicated `*_faq.md`. No code changes were needed — `ingest.py`
  already globs any `.md` file in the domain folder. Re-ingested: Products 81 chunks,
  Delivery 15 chunks, Payments 14 chunks (up from ~9, ~5, ~5 before).
