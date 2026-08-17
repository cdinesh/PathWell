# PathWell

> **One life. Many goals. One clear path.**

PathWell is an AI-powered personal decision assistant that helps people connect decisions across career, money, investing, travel, news, and long-term goals. Instead of treating each area in isolation, PathWell surfaces assumptions, trade-offs, and practical next steps in one place.

This repository contains the PathWell MVP: a Next.js web application, a FastAPI API, and a local SQLite database with an optional PostgreSQL and Redis development stack.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/cdinesh/PathWell)

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

## Application build guide

This section explains how to reproduce the application architecture and behavior. Build the modules in the following order because later screens depend on the shared shell, API client, seeded profile, and database contracts created earlier.

### Phase 1: Create the workspace and shared foundations

1. Create a monorepo with `apps/web` for Next.js and `apps/api` for FastAPI.
2. In the web app, create the root layout and global design tokens for the paper, forest, sage, gold, red, blue, and violet color system.
3. Build `AppShell` with:
   - a persistent desktop sidebar;
   - a mobile menu button and dismissible sidebar;
   - a global-search input;
   - an **Ask PathWell** shortcut;
   - notification and profile controls;
   - an active state based on the current route.
4. Add the shared `PageHeader`, `MetricCard`, `GoalCard`, and `AdvisorStrip` components.
5. Create the browser API helper. It reads `NEXT_PUBLIC_API_URL`, defaults to `http://localhost:8000`, sends JSON, and turns a non-successful response into a visible error.
6. Create the FastAPI application, enable CORS for `WEB_ORIGIN`, and expose `GET /health`.
7. Define SQLAlchemy models and an Alembic migration for users, profiles, financial snapshots, portfolio holdings, goals, documents, agent runs, and audit logs.
8. Create a seed command that inserts the Alex Morgan demo profile once. Re-running the command must not duplicate the profile.

Expected result: `/health` returns a success response, `/docs` displays the OpenAPI interface, and every authenticated application screen can render inside the shared shell.

### Phase 2: Add identity and onboarding

1. Build `/signup` with personal details, password controls, terms acceptance, inline validation, submit feedback, and a demo-account shortcut.
2. Implement `POST /auth/register`. Normalize email addresses to lowercase, reject duplicate accounts, hash passwords, create a profile, and return the new user ID.
3. Store the returned ID in browser local storage as `pathwell_user_id`.
4. Build the four-step `/onboarding` experience.
5. Implement `PATCH /me/profile` to update the profile and mark onboarding complete.
6. Route successful onboarding to `/dashboard`.

Expected result: a new user can register, save optional profile context, and reach the main application. Selecting the demo shortcut bypasses registration and uses the seeded Alex Morgan workspace.

### Phase 3: Add personal data modules

1. Build the dashboard from shared metric, goal, recommendation, portfolio, career, and travel cards.
2. Add API read contracts for `/dashboard`, `/finance/summary`, `/investments/portfolio`, `/career/profile`, `/travel/trips`, and `/goals`.
3. Add goal creation through `POST /goals` and document metadata through `/documents` endpoints.
4. Keep provenance visible: seeded data is labeled as demo data and live-provider data is labeled with retrieval time.

Expected result: the same profile, goals, and financial assumptions are available to every backend module even when an MVP screen uses deterministic presentation data.

### Phase 4: Add the AI Advisor

1. Build an intent router for career, investment, finance, travel, and general requests.
2. Select only the agents relevant to the detected intent.
3. Return a structured result containing summary, evidence, recommendation, alternatives, trade-offs, next steps, assumptions, confidence, and disclaimer.
4. Record each completed run and its task graph in the database.
5. Render agent activity and results on `/advisor`.
6. Enforce Level 0 behavior: the advisor can analyze and recommend but cannot trade, book, transfer money, or message another person.

Expected result: career questions receive career guidance, portfolio questions receive investment research guidance, and trip-affordability questions coordinate finance and travel context.

### Phase 5: Add adaptive travel planning

1. Create typed trip constraints for destination, dates, travelers, budget, pace, interests, dietary preferences, accessibility requirements, and fixed obligations.
2. Validate those constraints in both HTML controls and the FastAPI request schema.
3. Generate one itinerary day for every inclusive trip date.
4. Use the Italy catalog for the seeded trip and generic templates for other destinations.
5. Return priority, time, duration, cost, rationale, location, and optional official URL for every stop.
6. Add rain, flight-delay, and lower-cost replanning scenarios.
7. Display budget allocation, freshness, and warnings that prices and availability are illustrative.

Expected result: changing constraints or selecting a disruption regenerates the affected itinerary immediately without performing a booking.

### Phase 6: Add live news and document validation

1. Integrate NewsAPI on the server so the browser never receives the provider key.
2. Support Breaking, AI, Technology, Health, Business, Finance, and Politics categories.
3. Return publisher, timestamp, description, image, and source URL for each valid article.
4. Do not fabricate fallback news when the provider is unavailable.
5. Validate document type, size, and batch count before simulating an upload.
6. Keep real object-storage upload behind a future provider boundary.

Expected result: news clearly distinguishes loading, success, empty, and configuration-error states; documents clearly distinguish uploading, ready, and failed states.

### Phase 7: Verify and deploy

1. Run backend tests and linting.
2. Run frontend tests, TypeScript checking, and a production build.
3. Deploy PostgreSQL, FastAPI, and Next.js from `render.yaml`.
4. Configure the public frontend URL as `WEB_ORIGIN` and the public API URL as `NEXT_PUBLIC_API_URL`.
5. Verify `/health`, `/docs`, signup, advisor, travel, and news from the public domain.

## Route and navigation map

| Entry or control | Destination | Expected behavior |
| --- | --- | --- |
| `/` | `/signup` | Redirects immediately to account creation. |
| PathWell logo/sidebar | Current screen | Identifies the workspace; the logo is not currently a home link. |
| **Home** | `/dashboard` | Opens the cross-domain overview. |
| **Finance** | `/finance` | Opens seeded finance metrics and an advisor prompt. |
| **Investments** | `/investments` | Opens seeded allocation and risk metrics. |
| **Career** | `/career` | Opens career progress and skill-gap metrics. |
| **Travel** | `/travel` | Loads and displays the adaptive itinerary. |
| **Real-time News** | `/news` | Loads Breaking headlines by default. |
| **Goals** | `/goals` | Displays goals and the add-goal modal. |
| **AI Advisor** | `/advisor` | Opens the cross-domain question workspace. |
| **Documents** | `/documents` | Opens the simulated secure-upload workspace. |
| **Notifications** | `/notifications` | Opens the deterministic notification overview. |
| **Settings** | `/settings` | Opens the deterministic control-center overview. |
| Top-bar **Ask PathWell** | `/advisor` | Opens the advisor from any shell screen. |
| Mobile `☰` | Sidebar | Opens navigation; selecting a link or `×` closes it. |

The top-bar search and notification icon are visual MVP controls and do not yet execute a search or open a notification drawer. The footer avatar represents the seeded demo workspace.

## Complete user flows and module behavior

### 1. Signup and demo access

**Route:** `/signup`

**Entry:** Visiting `/` redirects here.

Inputs:

| Input | Validation |
| --- | --- |
| Full name | Required; at least 2 characters. |
| Email | Required; valid email format; duplicate email returns a server error. |
| Phone number | Required; 7–20 digits/phone characters; optional leading `+`. |
| Date of birth | Required date. |
| Password | At least 10 characters with uppercase, lowercase, and a number. |
| Confirm password | Must exactly match Password. |
| Terms | Must be selected. |

Flow:

1. Enter all fields.
2. Optionally select **Show passwords** to toggle both password fields between masked and visible text.
3. Select the terms checkbox.
4. Click **Create account →**.
5. Invalid fields display inline messages and no API request is sent.
6. During submission, the button reads **Creating your workspace…** and is disabled.
7. A successful response saves `pathwell_user_id` and navigates to `/onboarding`.
8. A duplicate email, unavailable API, or server validation issue appears in the error panel.

Alternative flow: click **Use demo account** to navigate directly to `/dashboard`. Requests without a stored user ID use the seeded demo user on the MVP backend.

### 2. Onboarding

**Route:** `/onboarding`

**Screens:** Financial → Investing → Career → Lifestyle.

1. **Financial:** annual income, monthly take-home, current savings, and primary financial goal.
2. **Investing:** experience, risk tolerance, and investment horizon.
3. **Career:** current role, desired role, and comma-separated skills.
4. **Lifestyle:** travel style and comma-separated travel interests.

All inputs are optional. **Continue →** advances one step and **← Back** returns to the prior step. On the first step, **Skip onboarding** routes to `/dashboard`. On the final step, **Finish →** converts numeric values, converts comma-separated values to arrays, updates the profile when a user ID is available, and routes to `/dashboard`. The button displays **Saving…** while the request runs.

### 3. Dashboard

**Route:** `/dashboard`

The dashboard presents the seeded Alex Morgan scenario:

- net worth, monthly income, monthly spending, and savings-rate metrics;
- the first three active goals with calculated progress;
- two recommended next moves;
- portfolio value, allocations, daily change, and concentration warning;
- AI Product Manager goal progress and next skill;
- upcoming Italy trip dates, budget, and saved amount.

Navigation actions:

- **Ask your advisor** and **Review plan** open `/advisor`.
- **View all** opens `/goals`.
- **See career plan** and **Continue your plan** open `/career`.
- **Details** opens `/investments`.
- **Open trip** opens `/travel`.
- The bottom **Ask advisor →** link opens `/advisor` with the displayed question prefilled through the `prompt` query parameter.

Current MVP behavior: dashboard cards use deterministic seeded presentation data from `apps/web/lib/data.ts`. The API also exposes a user-scoped `/dashboard` contract for the next integration step.

### 4. Finance

**Route:** `/finance`

**API contract:** `GET /finance/summary`

The screen displays available cash, total debt, and monthly savings capacity. It also shows that personalized profile context, shared goals, and explainable mock insights are available while live financial-provider connectivity remains a later phase.

Click **Ask advisor →** on “Where did I overspend this month?” to open `/advisor` with that question prefilled. The advisor classifies finance-related language, reviews cash-flow and goal context, and returns an educational analysis. No bank account is connected and no money can be moved.

### 5. Investments

**Route:** `/investments`

**API contract:** `GET /investments/portfolio`

The screen displays portfolio value, equity allocation, and technology concentration. The seeded holdings are VOO, QQQ, MSFT, NVDA, BND, and AAPL.

Click **Ask advisor →** on “Explain my biggest portfolio risk.” The advisor detects investment terms, reviews allocation, evaluates concentration, and returns research guidance with assumptions and a disclaimer. Output is educational and must not be treated as personalized investment advice; trading is not available.

### 6. Career

**Route:** `/career`

**API contract:** `GET /career/profile`

The screen displays progress toward AI Product Manager, the next recommended skill, and two mock role matches. Click **Ask advisor →** on “What should I learn next?” to open the advisor with the career prompt prefilled.

Expected advisor output for the seeded profile focuses on AI product discovery and evaluation, explains the skill gap, recommends a four-week case study, compares alternatives, and provides concrete next steps. Career intent must remain career-focused rather than defaulting to financial advice.

### 7. Adaptive Travel Planner

**Route:** `/travel`

**API contract:** `POST /travel/plan`

Initial load automatically submits the seeded Italy trip: May 8–16, 2027, one traveler, a `$3,000` budget, balanced pace, and food/culture/architecture interests. While loading, the screen displays the replanning status. On success it shows trip dates, travelers, pace, interests, total budget, freshness, day tabs, itinerary, and budget allocation.

#### Edit trip flow

1. Click **Edit trip details**.
2. Update any of these fields:
   - Destination: required, 2–120 characters.
   - Travelers: 1–12.
   - Start and end dates: end cannot precede start; maximum inclusive trip length is 15 days.
   - Total budget: `$100`–`$250,000` at the API boundary.
   - Pace: Relaxed, Balanced, or Active.
   - Interests: comma-separated, maximum 10 after conversion.
   - Dietary preferences: optional, up to 300 characters.
   - Accessibility requirements: optional, up to 500 characters.
   - Fixed obligations: optional, up to 1,000 characters.
3. Click **Update itinerary →** to regenerate or **Cancel**/`×`/the backdrop to dismiss.
4. A successful update closes the editor, selects the first day, and replaces the plan.
5. A validation or connectivity failure leaves an error message and does not create a booking.

#### Daily itinerary flow

- Select a day tab to change the visible date.
- Filter stops by **all**, **must**, **recommended**, or **flexible**.
- Each stop shows time, priority, duration, estimated cost, category, location, and why it matches the trip.
- **Done** marks the stop completed in browser state.
- **Remove** hides the stop in browser state.
- **Maps ↗** opens a Google Maps search in a new tab.
- **Official site ↗** appears when the catalog includes an official URL.
- If filtering/removing leaves no stops, **Show all stops** resets the priority filter.

Done and Remove states are session-local UI changes in the current MVP and are not persisted to the database.

#### Real-time adjustment controls

- **Rain expected:** replaces outdoor templates with indoor food, museum/gallery, and workshop options.
- **Flight delayed 2h:** removes the first two arrival-day stops and displays a change notice.
- **Lower activity costs:** reduces stop estimates to approximately 70%, with a minimum estimate of `$8`.

The right-side budget panel allocates 30% transport, 32% lodging, 18% food, 12% activities, and 8% buffer. These are illustrative calculations; live weather, prices, hours, traffic, and availability are not checked.

### 8. Goals

**Route:** `/goals`

**API contracts:** `GET /goals`, `POST /goals`

The page starts with the four seeded goals. Progress is calculated as `current ÷ target × 100` and capped at 100%.

1. Click **+ Add goal**.
2. Enter a required title.
3. Select Career, Finance, Travel, Investment, or Personal.
4. Enter a required target greater than or equal to 1.
5. Click **Save goal** to add a zero-progress card, or **Cancel**/the backdrop to dismiss.

Current MVP behavior: the visible page adds the goal to browser component state and resets after refresh. The backend persistence endpoint exists and validates lowercase categories, title length, non-negative values, optional target date, and priority; wiring the current modal to that endpoint is a defined next integration step.

### 9. AI Advisor

**Route:** `/advisor`

**API contract:** `POST /ai/chat`

1. Enter a question in the composer or arrive from an advisor link with a prefilled prompt.
2. The **Send →** button remains disabled for messages shorter than 3 characters.
3. Click **Send →**. The button changes to **Agents working…** and the agent panel advances through five activity states.
4. The orchestrator classifies the request and uses relevant seeded context.
5. The completed output displays:
   - Summary
   - What I found
   - Recommendation
   - Options
   - Trade-offs
   - Next steps
   - Expandable assumptions and confidence
   - Safety disclaimer
6. An API failure appears in the conversation as an error.

Intent examples:

| Question | Expected coordination |
| --- | --- |
| “What should I learn next?” | Career profile and career coach. |
| “Explain my portfolio concentration.” | Investment profile and research workflow. |
| “Can I afford a $3,000 Italy trip?” | Finance agent, travel agent, then orchestrator synthesis. |
| “Where did I overspend?” | Finance context and goal trade-offs. |

All advisor requests are Level 0/read-only. A completed response is saved as an agent run and an audit event, but no external action occurs.

### 10. Real-time News

**Route:** `/news`

**API contract:** `GET /news/headlines?category=<category>`

1. The screen loads **Breaking** by default and shows six skeleton cards while waiting.
2. Select Breaking, AI, Technology, Health, Business, Finance, or Politics to issue a new provider request.
3. Click **Refresh** to reload the active category; it is disabled while loading.
4. A successful feed shows provider status, retrieval time, headline count, publisher, publication time, image, title, and optional description.
5. Select a card to open the original publisher URL in a new tab.
6. A zero-result response displays **No current headlines found**.
7. A missing key or provider error displays configuration guidance and a **Try again** button.

`NEWS_API_KEY` remains server-side. PathWell intentionally shows an error rather than fabricated or stale fallback headlines.

### 11. Documents

**Route:** `/documents`

**API contracts:** `GET /documents`, `POST /documents/upload-url`, `DELETE /documents/{id}`

The screen starts with a seeded resume entry. Users can click **Choose files**, click the drop zone, or drag files into it.

Validation and behavior:

- Accepted: PDF, JPG/JPEG, PNG, DOCX.
- Maximum size: 10 MB per file.
- Maximum processed batch: first 5 selected files.
- Invalid type or size: status becomes **Failed** with a visible reason.
- Valid file: simulated progress advances from 15% to 100%, then status becomes **Ready**.
- `×` removes the item from the browser list.

Current MVP behavior: the page simulates signed object-storage upload and keeps the list in browser state. The backend already provides user-scoped metadata creation/deletion and a mock signed URL; binary storage is not enabled.

### 12. Notifications and Settings

**Routes:** `/notifications`, `/settings`

Notifications shows deterministic goal, portfolio, and career signals plus a prompt asking what changed this week. Settings shows structured-memory status, mock integration status, and quiet hours plus a prompt asking what PathWell remembers. Their advisor links navigate to `/advisor` with the relevant prompt.

These are presentation modules in the current MVP. Notification delivery, editable settings, production memories, and external integration controls are future work.

## Functional acceptance checklist

Use this checklist before submitting the project:

- [ ] `/` redirects to `/signup`.
- [ ] Invalid signup data produces inline validation messages.
- [ ] Valid registration creates a user and opens onboarding.
- [ ] Demo access opens the seeded dashboard.
- [ ] Onboarding moves forward/backward and finishes at the dashboard.
- [ ] Every sidebar link opens the expected route and active state.
- [ ] Career questions produce career-specific advisor output.
- [ ] Italy affordability produces cross-domain finance/travel output.
- [ ] Travel loads a day-by-day itinerary with different Italy attractions.
- [ ] Editing trip constraints regenerates the itinerary.
- [ ] Rain, delay, and lower-cost controls visibly change the plan.
- [ ] News categories load live headlines when `NEWS_API_KEY` is configured.
- [ ] News shows a truthful error when the provider is unavailable.
- [ ] Document type, size, and five-file limits behave as documented.
- [ ] Goal modal validates required title and positive target.
- [ ] API documentation loads at `/docs` and health returns success.
- [ ] No workflow executes a trade, booking, transfer, email, or other external action.

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

### One-click Render deployment

The root [`render.yaml`](render.yaml) Blueprint deploys the complete application:

- `pathwell-app-cdinesh`: public Next.js web application
- `pathwell-api-cdinesh`: public FastAPI service
- `pathwell-db-cdinesh`: managed PostgreSQL database

Click **Deploy to Render** near the top of this README, sign in to Render, and approve the Blueprint. Render will ask for `NEWS_API_KEY`; it can be left blank initially and added later from the API service's **Environment** page.

The API automatically applies Alembic migrations and seeds the demo profile every time it starts. After the deployment completes, open:

- Application: `https://pathwell-app-cdinesh.onrender.com`
- API documentation: `https://pathwell-api-cdinesh.onrender.com/docs`
- API health check: `https://pathwell-api-cdinesh.onrender.com/health`

Every push to the GitHub `main` branch automatically redeploys the affected service. Render's free web services can spin down while idle, so the first application or API request after inactivity might take longer. Choose a paid instance in Render if the application must remain continuously warm.

### Other hosting providers

PathWell has two deployable application services:

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
