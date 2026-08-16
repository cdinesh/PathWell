from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def uid() -> str:
    return str(uuid4())


def now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30))
    date_of_birth: Mapped[date] = mapped_column(Date)
    password_hash: Mapped[str] = mapped_column(String(256))
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Profile(Base):
    __tablename__ = "profiles"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    occupation: Mapped[str | None] = mapped_column(String(160))
    income: Mapped[int | None] = mapped_column(Integer)
    monthly_take_home: Mapped[int | None] = mapped_column(Integer)
    risk_tolerance: Mapped[str | None] = mapped_column(String(30))
    career_goal: Mapped[str | None] = mapped_column(String(200))
    travel_style: Mapped[str | None] = mapped_column(String(100))
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)


class Goal(Base):
    __tablename__ = "goals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(180))
    target_value: Mapped[int | None] = mapped_column(Integer)
    current_value: Mapped[int | None] = mapped_column(Integer)
    target_date: Mapped[date | None] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="active")


class FinancialSnapshot(Base):
    __tablename__ = "financial_snapshots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    checking: Mapped[int] = mapped_column(Integer)
    savings: Mapped[int] = mapped_column(Integer)
    investments: Mapped[int] = mapped_column(Integer)
    student_loan: Mapped[int] = mapped_column(Integer)
    credit_card: Mapped[int] = mapped_column(Integer)
    monthly_income: Mapped[int] = mapped_column(Integer)
    monthly_spending: Mapped[int] = mapped_column(Integer)
    monthly_savings_capacity: Mapped[int] = mapped_column(Integer)


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    ticker: Mapped[str] = mapped_column(String(12))
    allocation: Mapped[float] = mapped_column(Float)
    value: Mapped[int] = mapped_column(Integer)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer)
    storage_key: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="ready")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AgentRun(Base):
    __tablename__ = "agent_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    request: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30))
    tasks: Mapped[list] = mapped_column(JSON, default=list)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    event: Mapped[str] = mapped_column(String(100))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
