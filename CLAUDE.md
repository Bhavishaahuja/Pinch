# Pinch

Solo entry in the Meta Global AI Developer Hackathon (Indie track). Pinch is a one-gesture approval layer for AI agents on Ray-Ban Display + Neural Band.

- Agent: Muse Wonder (Meta Model API)
- Risk scorer: Muse Spark Open (Baseten)
- Demo: contesting a $65 parking ticket

## Stack

- Backend: Python 3 + FastAPI
- Display web app: plain HTML/CSS/JS, no frameworks

## Rules

- **Never guess API details.** Meta Model API, Baseten and Ray-Ban Display names, endpoints, model ids and parameters come only from the `docs/` folder. If something's missing, stop and ask.
- **Secrets** come only from `.env` via python-dotenv. Never hardcode keys, never commit `.env`.
- **Code style:** natural variable names, casual inline comments, explicit loops instead of clever one-liners or heavy functional patterns. Keep it readable.
- **Writing** (README, comments, docs): casual and concise. Never use em dashes.
- **Hackathon window:** everything gets built between Oct 27 and Nov 4, 2026. Log notable work with dates in the README build log.
