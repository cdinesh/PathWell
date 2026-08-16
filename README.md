# PathWell

> **One life. Many goals. One clear path.**

PathWell is an AI-powered personal decision assistant that helps people connect decisions across career, money, investing, travel, news, and long-term goals. Instead of treating each area in isolation, PathWell surfaces assumptions, trade-offs, and practical next steps in one place.

This repository contains the PathWell MVP: a Next.js web application, a FastAPI API, and a local SQLite database with an optional PostgreSQL and Redis development stack.

## What you can do

- Create an account, complete onboarding, or enter with the seeded demo profile.
- Review a personal dashboard covering finances, investments, career, travel, and goals.
- Ask the AI Advisor questions spanning more than one life category.
- Build and dynamically revise day-by-day travel itineraries using real attractions and must-do activities.
- Replan a trip when dates, budget, priorities, weather, or flight conditions change.
- Explore current Breaking, AI, Technology, Health, Business, Finance, and Politics news.
- Review assumptions and trade-offs before taking action.

PathWell is currently a decision-support MVP. It does not book travel, execute trades, move money, or send messages on a user's behalf.

## Technology

| Layer | Technology |
| --- | --- |
| Web | Next.js 16, React 19, TypeScript |
| API | FastAPI, Python 3.12, Pydantic |
| Data | SQLAlchemy, Alembic, SQLite by default |
| Optional services | PostgreSQL with pgvector, Redis |
| Live news | NewsAPI |

## Repository structure

```text
PathWell/
├── apps/
│   ├── api/                 # FastAPI application and API tests
│   └── web/                 # Next.js application and UI tests
├── docs/                    # Product and architecture documentation
├── migrations/              # Alembic database migrations
├── .env.example             # Safe environment-variable template
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # Optional PostgreSQL and Redis services
└── README.md
```

## Prerequisites

Install the following before starting:

- [Python 3.12 or newer](https://www.python.org/downloads/)
- [Node.js 20 or newer](https://nodejs.org/)
- npm, included with Node.js
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) only if you want PostgreSQL and Redis
- Git

Verify the main tools:

```bash
python3 --version
node --version
npm --version
git --version
```

## Quick start with SQLite

SQLite is the simplest option and does not require Docker. Run all backend commands from the repository root.

### 1. Clone and enter the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd PathWell
```

If you already have the project locally, open a terminal in the `PathWell` folder and continue with step 2.

### 2. Create the environment file

```bash
cp .env.example .env
```

The default values are ready for local SQLite development. Never commit `.env`; it may contain private API keys.

### 3. Create the Python environment and install the API

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e 'apps/api[dev]'
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

`pip install -e 'apps/api[dev]'` installs the API in editable mode plus its testing and linting tools. Code changes are then available without reinstalling the package.

### 4. Create and seed the database

```bash
alembic -c alembic.ini upgrade head
python -m thrive.seed
```

Alembic creates or upgrades `thrive.db` to the latest schema. The seed command adds the Alex Morgan demo profile and sample data. Both commands must be run from the `PathWell` root while `.venv` is active.

### 5. Start the API

```bash
uvicorn thrive.main:app --app-dir apps/api --reload --port 8000
```

Confirm that the API is running:

- API documentation: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

Keep this terminal running.

### 6. Start the web application

Open a second terminal:

```bash
cd PathWell/apps/web
npm install
npm run dev
```

If the second terminal already starts in the repository root, use only `cd apps/web`.

Open http://localhost:3000 and select **Use demo account** to explore the seeded experience.

## Environment variables

The root `.env` file controls local API and web integration.

| Variable | Required | Default or purpose |
| --- | --- | --- |
| `ENVIRONMENT` | No | Runtime name; defaults to `development`. |
| `DATABASE_URL` | No | Defaults to `sqlite:///./thrive.db`. |
| `REDIS_URL` | No | Redis connection for planned background capabilities. |
| `WEB_ORIGIN` | Yes in production | Allowed web origin for API CORS, such as `http://localhost:3000`. |
| `NEXT_PUBLIC_API_URL` | Yes | Browser-visible API base URL, such as `http://localhost:8000`. |
| `NEWS_API_KEY` | For live news | Developer key from NewsAPI. |
| `OPENAI_API_KEY` | No for current demo | Reserved for model-backed advisor capabilities. |
| `OBJECT_STORAGE_BUCKET` | No | Reserved for document storage. |
| `OBJECT_STORAGE_ENDPOINT` | No | Reserved for document storage. |

After changing `.env`, restart the API. Restart the Next.js development server after changing any `NEXT_PUBLIC_` variable.

## Enable real-time news

1. Create a developer key at [NewsAPI](https://newsapi.org/).
2. Add it to the root `.env` file:

   ```dotenv
   NEWS_API_KEY=your_key_here
   ```

3. Restart the API.

The News area then retrieves current headlines and links to their publishers. Without a key, PathWell displays a configuration message and does not invent headlines.

## Optional PostgreSQL and Redis setup

Start the included containers:

```bash
docker compose up -d
```

Change `DATABASE_URL` in `.env`:

```dotenv
DATABASE_URL=postgresql+psycopg://thrive:thrive@localhost:5432/thrive
```

Then create and seed the PostgreSQL database:

```bash
source .venv/bin/activate
alembic -c alembic.ini upgrade head
python -m thrive.seed
```

Check or stop the containers with:

```bash
docker compose ps
docker compose down
```

The named Docker volume preserves PostgreSQL data when the containers stop.

## Demo scenario

Open **AI Advisor** and try:

> Can I afford a $3,000 trip to Italy this year without delaying my emergency-fund goal?

The MVP combines seeded financial and travel context, then displays its assumptions, alternatives, and recommendation. You can also ask career-focused questions or open Travel to update constraints and regenerate an itinerary.

## View the SQLite database in VS Code

1. Install a trusted SQLite extension such as **SQLite Viewer** from the VS Code Extensions panel.
2. Open `PathWell/thrive.db` from the Explorer.
3. Use the extension's table explorer to view table schemas and rows.

You can also inspect it from the terminal if the SQLite CLI is installed:

```bash
sqlite3 thrive.db
```

Then run:

```sql
.tables
.schema
SELECT * FROM users LIMIT 10;
.quit
```

## Development commands

Run backend commands from the repository root with `.venv` active:

```bash
pytest apps/api/tests
ruff check apps/api
```

Run frontend commands from `apps/web`:

```bash
npm test
npm run typecheck
npm run build
```

## Common problems

### `alembic: command not found`

Activate the Python environment and install the API dependencies:

```bash
source .venv/bin/activate
pip install -e 'apps/api[dev]'
```

### Alembic cannot find its configuration or migrations

Run the command from the `PathWell` root and use the root configuration:

```bash
alembic -c alembic.ini upgrade head
```

### The web app says the API is unavailable

- Confirm the API terminal is still running on port `8000`.
- Confirm `.env` contains `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- Open http://localhost:8000/docs to verify the API directly.
- Restart both servers after changing environment variables.

### Port 3000 or 8000 is already in use

Stop the existing process, or use another port. If the API port changes, update `NEXT_PUBLIC_API_URL` to match it.

### News does not load

Confirm `NEWS_API_KEY` is present in the root `.env`, restart the API, and check whether the NewsAPI developer plan permits the request being made.

## Production deployment

PathWell has two deployable services:

1. Deploy `apps/api` to a Python-capable host and run database migrations during release.
2. Deploy `apps/web` to a Next.js-capable host.
3. Set the web service's `NEXT_PUBLIC_API_URL` to the public API URL.
4. Set the API's `WEB_ORIGIN` to the public web URL.
5. Use managed PostgreSQL in production; do not rely on a server's temporary SQLite filesystem.
6. Store `NEWS_API_KEY` and other secrets in the hosting provider's environment settings, never in GitHub.

Before publishing, verify:

```bash
pytest apps/api/tests
ruff check apps/api
cd apps/web
npm test
npm run typecheck
npm run build
```

## Security and product boundaries

- Financial and investment output is educational scenario analysis, not investment, tax, or legal advice.
- The MVP supports read-only and internal preparation actions only.
- Approval Levels 2 and 3 are represented in the architecture but cannot execute external actions.
- Local `.env`, database files, virtual environments, and build artifacts are excluded from Git.

## Documentation

- [Product definition](docs/PRODUCT.md)
- [Architecture](docs/ARCHITECTURE.md)

## Status

PathWell is an early-stage MVP intended for product validation and development. Feedback, issues, and contributions are welcome after the GitHub repository is published.
