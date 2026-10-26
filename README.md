# Pinch

One-gesture approval for AI agents, right in your Ray-Ban Display lens. Pinch to approve, done.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in your keys
uvicorn backend.main:app --reload
```

Check it's alive at http://localhost:8000/health.

## Built during the hackathon

- **Oct 26 (kickoff day):** repo setup only. README, config files, empty FastAPI app with a health check. No Pinch features yet.

## Pre-existing work

None. All code was written during the hackathon.
