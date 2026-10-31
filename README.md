# Arthiq: a voice-first AI agent for kirana udhar

Team SETU (Aryan Chouhan, Drishti Jain), MITS Gwalior. Paytm Build for India AI Hackathon, track: Merchant Growth AI.

One spoken sentence updates ledger + stock + due date after a spoken read-back and "yes".
Then Arthiq collects the money by itself: reminder ladder, UPI link, promises, webhook reconciliation.

## Run
    python -m venv venv && venv\Scripts\activate
    pip install sarvamai fastapi "uvicorn[standard]" sqlalchemy pydantic rapidfuzz httpx python-dotenv python-multipart apscheduler
    echo SARVAM_API_KEY=your_key> .env
    echo SARVAM_LLM_MODEL=sarvam-105b>> .env
    python demo_reset.py
    uvicorn app.api.main:app --reload

Pages: `/` voice app, `/console` collections, `/insights` stock and cash, `/dashboard` inbox, audit, outbox, briefing.

## Tests (each uses a throwaway DB)
    python try_ladder.py      python try_collect.py     python try_stockcash.py
    python try_dashboard.py   python -m eval.run_eval   (needs network; writes eval/results.md)

## Design rules
1. The LLM understands and writes; code decides amounts, totals, balances, dates, permissions.
2. Every ledger change is read back and needs a "yes".
3. Tools only: the LLM never touches the database or sends messages.
4. Idempotent everywhere (idempotency keys, unique constraints).
5. Humans stay in charge: disputes, supplier orders, late fees need approval; audit log is append-only.
6. Spoken replies come from fixed per-language templates; customer reminders pass a safety filter.

## Demo vs production
| Part | Demo | Production |
|---|---|---|
| Scheduler | APScheduler | Celery + Redis |
| Database | SQLite | PostgreSQL |
| Payments | Mock Paytm page + fake webhook | Paytm payment link + signed webhook |
| Messages | Simulated outbox | WhatsApp Business API, SMS (DLT), telephony |
| Languages | 11 for voice; collection/cash/briefing templates for hi, en, mr, gu | Native-speaker language packs |

Planned: Arthiq Proof, Arthiq Negotiator, stock-in by voice, multi-shop auth.