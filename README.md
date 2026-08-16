# PathWell

**One life. Many goals. One clear path.**

PathWell is your personal AI advisor for making smarter decisions about money, investing, career, travel, and the goals connecting them—all in one place.

## What works

- Validated sign-up, onboarding, and demo-session flow
- Personalized dashboard and navigable Finance, Investments, Career, Travel, Real-time News, Goals, Documents, and Settings views
- User-scoped REST APIs and seeded Alex Morgan demo profile
- Document validation and metadata architecture (mock signed upload in development)
- Structured agent workflow with orchestrator, Finance Agent, and Travel Agent
- Adaptive travel planner with editable constraints, day-by-day itinerary, priority filters, budget allocation, and rain/flight-delay/cost replanning
- Required Italy trip-affordability workflow with activity status, assumptions, alternatives, and recommendation
- Level 0/read-only and Level 1/internal action policy boundaries

## Quick start

Prerequisites: Node 20+, Python 3.12+, Docker (optional for PostgreSQL/Redis).

```bash
cd PathWell
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -e 'apps/api[dev]'
alembic -c alembic.ini upgrade head
python -m thrive.seed
uvicorn thrive.main:app --app-dir apps/api --reload --port 8000
```

In another terminal:

```bash
cd PathWell/apps/web
npm install
npm run dev
```

Open http://localhost:3000. API documentation is at http://localhost:8000/docs.

### Real-time news

Create a developer key at [NewsAPI](https://newsapi.org/), then add it to `.env`:

```bash
NEWS_API_KEY=your_key_here
```

Restart the API. The News section retrieves current Breaking, AI, Technology, Health, Business, Finance, and Politics headlines with publisher links and timestamps. Without a key, the UI shows a configuration state and never substitutes fabricated headlines.

The default database is local SQLite for a no-Docker demo. To use PostgreSQL and Redis:

```bash
docker compose up -d
```

Then set `DATABASE_URL=postgresql+psycopg://thrive:thrive@localhost:5432/thrive` before running Alembic and the API.

## Demo

Select **Use demo account** on sign-up or open the dashboard directly. In AI Advisor, run:

> Can I afford a $3,000 trip to Italy this year without delaying my emergency-fund goal?

The advisory response is deterministic and based on seeded data. News is live only when NewsAPI is configured. No bookings, trades, emails, or money movement occur.

## Safety

Financial and investment output is educational scenario analysis, not investment, tax, or legal advice. External actions at approval Levels 2 and 3 are architected but not executable in this MVP.

See [Architecture](docs/ARCHITECTURE.md) and [Product Definition](docs/PRODUCT.md).
