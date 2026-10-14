# Retail Banking Frontend (Streamlit)

Minimal Streamlit UI for the Retail Banking FastAPI backend.

## Setup

```bash
cd retail_banking_frontend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
# backend must be running at $BACKEND_URL (default http://localhost:8000)
export BACKEND_URL=http://localhost:8000   # optional
streamlit run app.py --server.port 8501
```

Open http://localhost:8501.

## Equivalent curl commands

```bash
# Tab 1 — Search Knowledge Base
curl -s "http://localhost:8000/knowledge/search?query=overdraft&top_k=3"

# Tab 2 — LLM Generating Complaint Summary
curl -s -X POST "http://localhost:8000/complaints/1/summary"

# Tab 3 — Ask Agent
curl -s -X POST "http://localhost:8000/agent/ask" \
     -H "Content-Type: application/json" \
     -d '{"question":"How many complaints are open?"}'
```

## Screenshot checklist

### Search Knowledge Base
- Success: input `overdraft`, top_k `3` → table with columns `id`, `title`, `score`, `snippet` (snippet ≤ 200 chars).
- Failure: empty query → yellow warning "Please enter a query."; backend down → red connection-error banner.

### LLM Generating Complaint Summary
- Success: valid `complaint_id` → rendered markdown summary + `input_tokens` / `output_tokens` metrics + expandable raw JSON.
- Failure: non-existent id → red "HTTP 404" with error JSON body shown.

### Ask Agent
- Success: question posted → rendered `answer`, metrics for `tool_calls_made`, `complete`, `stop_reason`, token counts, raw JSON expander.
- Failure: empty question → yellow warning; timeout (>60s) → red timeout message.
