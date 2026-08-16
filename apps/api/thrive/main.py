from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .agents import Orchestrator
from .auth import current_user
from .config import settings
from .database import Base, engine, get_db
from .models import (
    AgentRun,
    AuditLog,
    Document,
    FinancialSnapshot,
    Goal,
    PortfolioHolding,
    Profile,
    User,
)
from .providers import (
    MockJobsProvider,
    MockMarketDataProvider,
    MockTravelProvider,
    NewsApiProvider,
    NewsCategory,
    NewsProviderError,
)
from .schemas import (
    ChatRequest,
    ChatResponse,
    DocumentCreate,
    DocumentResponse,
    GoalCreate,
    OnboardingRequest,
    RegisterRequest,
    SessionResponse,
    TripPlanRequest,
)
from .security import hash_password
from .seed import seed


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings().environment == "development":
        Base.metadata.create_all(engine)
        seed()
    yield


app = FastAPI(title="PathWell API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=[settings().web_origin], allow_methods=["*"], allow_headers=["*"]
)
orchestrator = Orchestrator()
news_provider = NewsApiProvider()
travel_provider = MockTravelProvider()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "thrive-api"}


@app.get("/news/headlines")
def news_headlines(category: NewsCategory = "breaking") -> dict:
    try:
        return news_provider.headlines(category)
    except NewsProviderError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.post("/auth/register", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> SessionResponse:
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(
        full_name=payload.full_name,
        email=payload.email.lower(),
        phone=payload.phone,
        date_of_birth=payload.date_of_birth,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    db.add(Profile(user_id=user.id, preferences={}))
    db.add(AuditLog(user_id=user.id, event="user.registered", detail={"method": "password"}))
    db.commit()
    return SessionResponse(user_id=user.id, full_name=user.full_name, onboarding_complete=False)


@app.get("/me")
def me(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    profile = db.get(Profile, user.id)
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "onboarding_complete": user.onboarding_complete,
        "profile": {
            "occupation": profile.occupation,
            "income": profile.income,
            "risk_tolerance": profile.risk_tolerance,
            "career_goal": profile.career_goal,
            "travel_style": profile.travel_style,
            "preferences": profile.preferences,
        },
    }


@app.patch("/me/profile")
def onboarding(
    payload: OnboardingRequest, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict:
    profile = db.get(Profile, user.id)
    profile.income = payload.income or profile.income
    profile.monthly_take_home = payload.monthly_take_home or profile.monthly_take_home
    profile.risk_tolerance = payload.risk_tolerance or profile.risk_tolerance
    profile.occupation = payload.current_role or profile.occupation
    profile.career_goal = payload.desired_role or profile.career_goal
    profile.travel_style = payload.travel_style or profile.travel_style
    profile.preferences = {
        **profile.preferences,
        "skills": payload.skills,
        "travel_interests": payload.travel_interests,
        "investment_experience": payload.investment_experience,
        "investment_horizon": payload.investment_horizon,
    }
    user.onboarding_complete = True
    db.add(
        AuditLog(
            user_id=user.id, event="onboarding.completed", detail={"optional_fields_skipped": True}
        )
    )
    db.commit()
    return {"status": "completed"}


@app.get("/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    profile = db.get(Profile, user.id)
    finance = db.scalar(select(FinancialSnapshot).where(FinancialSnapshot.user_id == user.id))
    goals = db.scalars(select(Goal).where(Goal.user_id == user.id)).all()
    holdings = db.scalars(select(PortfolioHolding).where(PortfolioHolding.user_id == user.id)).all()
    portfolio = MockMarketDataProvider().portfolio_change([h.ticker for h in holdings])
    jobs = MockJobsProvider().recommended_roles(profile.career_goal or "Product Manager")
    net_worth = (
        finance.checking
        + finance.savings
        + finance.investments
        - finance.student_loan
        - finance.credit_card
    )
    return {
        "user": {"name": user.full_name, "occupation": profile.occupation},
        "finance": {
            "net_worth": net_worth,
            "income": finance.monthly_income,
            "spending": finance.monthly_spending,
            "savings_rate": round(finance.monthly_savings_capacity / finance.monthly_income * 100),
            "cash": finance.checking + finance.savings,
            "debt": finance.student_loan + finance.credit_card,
        },
        "goals": [
            {
                "id": g.id,
                "category": g.category,
                "title": g.title,
                "target": g.target_value,
                "current": g.current_value,
                "priority": g.priority,
            }
            for g in goals
        ],
        "portfolio": {
            "value": finance.investments,
            "daily_change": portfolio["daily_change_percent"],
            "holdings": [
                {"ticker": h.ticker, "allocation": h.allocation, "value": h.value} for h in holdings
            ],
            "risk": "Technology concentration is 60%",
        },
        "career": {
            "goal": profile.career_goal,
            "next_skill": "AI product discovery and evaluation",
            "jobs": jobs,
        },
        "travel": {"destination": "Italy", "dates": "May 8–16, 2027", "saved": 600, "budget": 3000},
        "recommendations": [
            {
                "domain": "finance",
                "title": "Protect your emergency-fund pace",
                "summary": "Create a separate travel sinking fund.",
                "impact": "Avoids using protected savings",
                "priority": "high",
            },
            {
                "domain": "career",
                "title": "Ship an AI product case study",
                "summary": "Turn your analytics background into product evidence.",
                "impact": "Closes the strongest portfolio gap",
                "priority": "medium",
            },
        ],
    }


@app.get("/goals")
def list_goals(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[dict]:
    goals = db.scalars(select(Goal).where(Goal.user_id == user.id)).all()
    return [
        {
            "id": g.id,
            "category": g.category,
            "title": g.title,
            "target_value": g.target_value,
            "current_value": g.current_value,
            "priority": g.priority,
            "status": g.status,
        }
        for g in goals
    ]


@app.get("/finance/summary")
def finance_summary(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    snapshot = db.scalar(select(FinancialSnapshot).where(FinancialSnapshot.user_id == user.id))
    if not snapshot:
        raise HTTPException(status_code=404, detail="Financial profile not found")
    return {
        "checking": snapshot.checking,
        "savings": snapshot.savings,
        "investments": snapshot.investments,
        "debt": snapshot.student_loan + snapshot.credit_card,
        "monthly_income": snapshot.monthly_income,
        "monthly_spending": snapshot.monthly_spending,
        "monthly_savings_capacity": snapshot.monthly_savings_capacity,
        "source": "seeded_demo",
    }


@app.get("/investments/portfolio")
def investment_portfolio(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    holdings = db.scalars(select(PortfolioHolding).where(PortfolioHolding.user_id == user.id)).all()
    return {
        "holdings": [
            {"ticker": item.ticker, "allocation": item.allocation, "value": item.value}
            for item in holdings
        ],
        "risk": "Technology concentration is 60%",
        "freshness": "Seeded demo data",
        "disclaimer": "For educational and research purposes; not investment advice.",
    }


@app.get("/career/profile")
def career_profile(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    profile = db.get(Profile, user.id)
    return {
        "current_role": profile.occupation,
        "career_goal": profile.career_goal,
        "next_skill": "AI product discovery and evaluation",
        "opportunities": MockJobsProvider().recommended_roles(
            profile.career_goal or "Product Manager"
        ),
        "source": "seeded_demo",
    }


@app.get("/travel/trips")
def travel_trips(user: User = Depends(current_user)) -> list[dict]:
    return [
        {
            "id": "italy-demo",
            "destination": "Italy",
            "dates": "May 8–16, 2027",
            "budget": 3000,
            "saved": 600,
            "status": "drafted",
            "freshness": "Illustrative itinerary; live availability not checked",
        }
    ]


@app.post("/travel/plan")
def plan_trip(
    payload: TripPlanRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = travel_provider.build_itinerary(payload)
    db.add(
        AuditLog(
            user_id=user.id,
            event="trip.plan_generated",
            detail={
                "destination": payload.destination,
                "adjustment": payload.adjustment,
                "approval_level": 1,
            },
        )
    )
    db.commit()
    return result


@app.post("/goals", status_code=201)
def create_goal(
    payload: GoalCreate, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> dict:
    goal = Goal(user_id=user.id, **payload.model_dump())
    db.add(goal)
    db.add(AuditLog(user_id=user.id, event="goal.created", detail={"category": payload.category}))
    db.commit()
    return {"id": goal.id, **payload.model_dump(mode="json"), "status": "active"}


@app.get("/documents", response_model=list[DocumentResponse])
def documents(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Document]:
    return list(db.scalars(select(Document).where(Document.user_id == user.id)).all())


@app.post("/documents/upload-url", response_model=DocumentResponse, status_code=201)
def upload_url(
    payload: DocumentCreate, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> DocumentResponse:
    doc_id = str(uuid4())
    doc = Document(
        id=doc_id,
        user_id=user.id,
        filename=payload.filename,
        mime_type=payload.mime_type,
        size=payload.size,
        storage_key=f"users/{user.id}/{doc_id}/{payload.filename}",
        status="ready",
    )
    db.add(doc)
    db.commit()
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        mime_type=doc.mime_type,
        size=doc.size,
        status=doc.status,
        uploaded_at=doc.uploaded_at,
        upload_url=f"mock://signed-upload/{doc.id}",
    )


@app.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> Response:
    doc = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return Response(status_code=204)


@app.post("/ai/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> ChatResponse:
    snapshot = db.scalar(select(FinancialSnapshot).where(FinancialSnapshot.user_id == user.id))
    profile = db.get(Profile, user.id)
    emergency = db.scalar(
        select(Goal).where(Goal.user_id == user.id, Goal.title == "Emergency Fund")
    )
    tasks, result, activities, intent = orchestrator.run(
        payload.message, snapshot, emergency, profile
    )
    run = AgentRun(
        user_id=user.id,
        request=payload.message,
        status="completed",
        tasks=[t.model_dump() for t in tasks],
        result=result.model_dump(),
    )
    db.add(run)
    db.add(
        AuditLog(
            user_id=user.id,
            event="agent_run.completed",
            detail={"approval_level": 0, "intent": intent, "agents": [t.agent for t in tasks]},
        )
    )
    db.commit()
    return ChatResponse(
        run_id=run.id,
        status="completed",
        activities=activities,
        tasks=tasks,
        result=result,
    )
