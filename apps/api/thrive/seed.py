from datetime import date

from sqlalchemy import select

from .auth import DEMO_EMAIL
from .database import Base, SessionLocal, engine
from .models import FinancialSnapshot, Goal, PortfolioHolding, Profile, User
from .security import hash_password


def seed() -> str:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if existing:
            return existing.id
        user = User(
            full_name="Alex Morgan",
            email=DEMO_EMAIL,
            phone="+1 303 555 0147",
            date_of_birth=date(1995, 4, 18),
            password_hash=hash_password("DemoPass123"),
            onboarding_complete=True,
        )
        db.add(user)
        db.flush()
        db.add(
            Profile(
                user_id=user.id,
                occupation="Senior Financial Analyst",
                income=112000,
                monthly_take_home=6700,
                risk_tolerance="moderate",
                career_goal="Become an AI Product Manager",
                travel_style="International · food · culture",
                preferences={"notifications": "important_only", "quiet_hours": "21:00–07:00"},
            )
        )
        db.add(
            FinancialSnapshot(
                user_id=user.id,
                checking=8400,
                savings=17500,
                investments=68000,
                student_loan=14800,
                credit_card=1200,
                monthly_income=6700,
                monthly_spending=5050,
                monthly_savings_capacity=1650,
            )
        )
        goals = [
            Goal(
                user_id=user.id,
                category="financial",
                title="Emergency Fund",
                target_value=25000,
                current_value=17500,
                target_date=date(2027, 2, 1),
                priority="high",
            ),
            Goal(
                user_id=user.id,
                category="financial",
                title="House Down Payment",
                target_value=80000,
                current_value=28500,
                target_date=date(2029, 6, 1),
                priority="high",
            ),
            Goal(
                user_id=user.id,
                category="travel",
                title="Italy Trip",
                target_value=3000,
                current_value=600,
                target_date=date(2027, 5, 1),
                priority="medium",
            ),
            Goal(
                user_id=user.id,
                category="career",
                title="AI Product Manager",
                target_value=100,
                current_value=35,
                target_date=date(2027, 8, 1),
                priority="high",
            ),
        ]
        db.add_all(goals)
        allocations = {"VOO": 28, "QQQ": 19, "MSFT": 16, "NVDA": 14, "AAPL": 11, "BND": 12}
        db.add_all(
            [
                PortfolioHolding(
                    user_id=user.id, ticker=ticker, allocation=value, value=680 * value
                )
                for ticker, value in allocations.items()
            ]
        )
        db.commit()
        return user.id


if __name__ == "__main__":
    print(f"Seeded demo user: {seed()}")
