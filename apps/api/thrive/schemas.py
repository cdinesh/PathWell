from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(pattern=r"^\+?[0-9 ()-]{7,20}$")
    date_of_birth: date
    password: str = Field(min_length=10, max_length=128)
    terms_accepted: bool

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        if not (
            any(c.isupper() for c in value)
            and any(c.islower() for c in value)
            and any(c.isdigit() for c in value)
        ):
            raise ValueError("Password must include uppercase, lowercase, and a number")
        return value

    @field_validator("terms_accepted")
    @classmethod
    def terms_required(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Terms must be accepted")
        return value


class SessionResponse(BaseModel):
    user_id: str
    full_name: str
    onboarding_complete: bool


class OnboardingRequest(BaseModel):
    income: int | None = Field(default=None, ge=0)
    monthly_take_home: int | None = Field(default=None, ge=0)
    recurring_expenses: int | None = Field(default=None, ge=0)
    savings: int | None = Field(default=None, ge=0)
    debt: int | None = Field(default=None, ge=0)
    financial_goal: str | None = None
    investment_experience: str | None = None
    risk_tolerance: str | None = None
    investment_horizon: str | None = None
    current_role: str | None = None
    desired_role: str | None = None
    skills: list[str] = Field(default_factory=list)
    travel_interests: list[str] = Field(default_factory=list)
    travel_style: str | None = None


class GoalCreate(BaseModel):
    category: Literal["financial", "career", "travel", "investment", "personal"]
    title: str = Field(min_length=2, max_length=180)
    target_value: int | None = Field(default=None, ge=0)
    current_value: int | None = Field(default=0, ge=0)
    target_date: date | None = None
    priority: Literal["low", "medium", "high"] = "medium"


class DocumentCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    mime_type: Literal[
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    size: int = Field(gt=0, le=10_485_760)


class ChatRequest(BaseModel):
    message: str = Field(min_length=3, max_length=4000)


class TripPlanRequest(BaseModel):
    destination: str = Field(min_length=2, max_length=120)
    start_date: date
    end_date: date
    travelers: int = Field(default=1, ge=1, le=12)
    budget: int = Field(ge=100, le=250_000)
    pace: Literal["relaxed", "balanced", "active"] = "balanced"
    interests: list[str] = Field(default_factory=list, max_length=10)
    dietary_preferences: str | None = Field(default=None, max_length=300)
    accessibility_requirements: str | None = Field(default=None, max_length=500)
    fixed_obligations: str | None = Field(default=None, max_length=1000)
    adjustment: Literal["none", "rain", "flight_delay", "lower_budget"] = "none"
    flight_delay_minutes: int = Field(default=0, ge=0, le=1440)

    @field_validator("end_date")
    @classmethod
    def valid_dates(cls, value: date, info) -> date:
        start = info.data.get("start_date")
        if start and value < start:
            raise ValueError("End date must be on or after start date")
        if start and (value - start).days > 14:
            raise ValueError("The MVP supports trips up to 15 days")
        return value


class AgentTask(BaseModel):
    task_id: str
    agent: str
    objective: str
    dependencies: list[str] = Field(default_factory=list)
    status: Literal["pending", "running", "waiting_approval", "completed", "failed"]


class AdvisorResult(BaseModel):
    summary: str
    what_i_found: list[str]
    recommendation: str
    trade_offs: list[str]
    next_steps: list[str]
    assumptions: list[str]
    alternatives: list[dict]
    confidence: float = Field(ge=0, le=1)
    disclaimer: str


class ChatResponse(BaseModel):
    run_id: str
    status: str
    activities: list[str]
    tasks: list[AgentTask]
    result: AdvisorResult


class DocumentResponse(BaseModel):
    id: str
    filename: str
    mime_type: str
    size: int
    status: str
    uploaded_at: datetime
    upload_url: str | None = None
