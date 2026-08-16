from dataclasses import dataclass
from uuid import uuid4

from .models import FinancialSnapshot, Goal, Profile
from .providers import MockTravelProvider
from .schemas import AdvisorResult, AgentTask


@dataclass(frozen=True)
class FinanceAnalysis:
    monthly_capacity: int
    emergency_gap: int
    months_without_trip: float
    months_with_trip: float
    delay_months: float


class FinanceAgent:
    name = "personal_finance"

    def analyze_trip(
        self, snapshot: FinancialSnapshot, goal: Goal, trip_cost: int
    ) -> FinanceAnalysis:
        gap = max((goal.target_value or 0) - (goal.current_value or 0), 0)
        capacity = max(snapshot.monthly_savings_capacity, 1)
        return FinanceAnalysis(
            monthly_capacity=capacity,
            emergency_gap=gap,
            months_without_trip=round(gap / capacity, 1),
            months_with_trip=round((gap + trip_cost) / capacity, 1),
            delay_months=round(trip_cost / capacity, 1),
        )


class TravelAgent:
    name = "travel_planning"

    def __init__(self, provider: MockTravelProvider | None = None):
        self.provider = provider or MockTravelProvider()

    def plan(self, destination: str, budget: int) -> dict:
        return self.provider.estimate_trip(destination, budget)


class Orchestrator:
    def __init__(self) -> None:
        self.finance = FinanceAgent()
        self.travel = TravelAgent()

    def classify(self, request: str) -> str:
        text = request.lower()
        career = {
            "career",
            "learn",
            "skill",
            "resume",
            "job",
            "interview",
            "promotion",
            "salary",
            "product manager",
        }
        investment = {"portfolio", "stock", "invest", "etf", "allocation", "nvda", "risk"}
        travel = {"trip", "travel", "italy", "flight", "hotel", "itinerary", "vacation"}
        finance = {
            "finance",
            "budget",
            "spending",
            "saving",
            "debt",
            "cash",
            "emergency fund",
            "afford",
        }
        matches = {
            "career": sum(word in text for word in career),
            "investment": sum(word in text for word in investment),
            "travel": sum(word in text for word in travel),
            "finance": sum(word in text for word in finance),
        }
        if matches["travel"] and matches["finance"]:
            return "finance_travel"
        return max(matches, key=matches.get) if max(matches.values()) else "general"

    def run(
        self,
        request: str,
        snapshot: FinancialSnapshot | None,
        emergency_goal: Goal | None,
        profile: Profile,
    ) -> tuple[list[AgentTask], AdvisorResult, list[str], str]:
        intent = self.classify(request)
        if intent == "career":
            tasks, result = self._career(request, profile)
            return (
                tasks,
                result,
                [
                    "Reviewing your career goal",
                    "Mapping your existing strengths",
                    "Identifying the highest-value skill gap",
                    "Building a focused learning sequence",
                    "Preparing your next actions",
                ],
                intent,
            )
        if intent in {"investment", "finance", "travel", "general"}:
            if snapshot is None:
                return self._profile_required(intent)
            tasks, result = self._single_domain(intent, request, snapshot, profile)
            activities = {
                "investment": [
                    "Reviewing your portfolio",
                    "Checking allocation",
                    "Evaluating concentration",
                    "Comparing risk factors",
                    "Preparing research guidance",
                ],
                "finance": [
                    "Reviewing your cash flow",
                    "Checking current goals",
                    "Comparing options",
                    "Evaluating trade-offs",
                    "Preparing your recommendation",
                ],
                "travel": [
                    "Reviewing your travel preferences",
                    "Estimating a sample budget",
                    "Checking goal constraints",
                    "Building options",
                    "Preparing your trip guidance",
                ],
                "general": [
                    "Understanding your request",
                    "Reviewing your profile",
                    "Selecting relevant context",
                    "Building a plan",
                    "Preparing next steps",
                ],
            }[intent]
            return tasks, result, activities, intent

        if snapshot is None or emergency_goal is None:
            return self._profile_required(intent)
        tasks, result = self._trip_affordability(snapshot, emergency_goal)
        return (
            tasks,
            result,
            [
                "Reviewing your financial goals",
                "Estimating an Italy trip budget",
                "Comparing scenarios",
                "Evaluating goal impact",
                "Preparing your recommendation",
            ],
            intent,
        )

    def _profile_required(
        self, intent: str
    ) -> tuple[list[AgentTask], AdvisorResult, list[str], str]:
        task = AgentTask(
            task_id=str(uuid4()),
            agent="orchestrator",
            objective="Request missing profile context",
            status="completed",
        )
        result = AdvisorResult(
            summary="Complete the relevant profile section so I can give you a personalized answer.",
            what_i_found=["The request was understood, but the required saved context is missing."],
            recommendation="Add the missing profile details, then run this request again.",
            trade_offs=["Continuing without verified context would produce generic guidance."],
            next_steps=["Complete onboarding", "Retry the request"],
            assumptions=[],
            alternatives=[{"label": "Continue", "funding": "Complete profile"}],
            confidence=0.98,
            disclaimer="No recommendation or external action was performed.",
        )
        return (
            [task],
            result,
            [
                "Understanding your request",
                "Checking available profile context",
                "Identifying missing information",
            ],
            intent,
        )

    def _trip_affordability(
        self, snapshot: FinancialSnapshot, emergency_goal: Goal
    ) -> tuple[list[AgentTask], AdvisorResult]:
        finance_id, travel_id, synth_id = (str(uuid4()) for _ in range(3))
        tasks = [
            AgentTask(
                task_id=finance_id,
                agent="personal_finance",
                objective="Measure trip impact on emergency fund",
                status="completed",
            ),
            AgentTask(
                task_id=travel_id,
                agent="travel_planning",
                objective="Build an illustrative Italy trip budget",
                status="completed",
            ),
            AgentTask(
                task_id=synth_id,
                agent="orchestrator",
                objective="Compare affordability scenarios",
                dependencies=[finance_id, travel_id],
                status="completed",
            ),
        ]
        trip = self.travel.plan("Italy", 3000)
        finance = self.finance.analyze_trip(snapshot, emergency_goal, trip["total"])
        affordable_cash = snapshot.checking + snapshot.savings - (emergency_goal.current_value or 0)
        does_not_delay = finance.delay_months <= 0
        summary = (
            "The $3,000 Italy trip is cash-feasible, but it would delay your emergency-fund goal by approximately "
            f"{finance.delay_months} months unless you fund it separately or reduce the budget."
        )
        if does_not_delay:
            summary = "The trip appears affordable without delaying the emergency-fund goal under the stated assumptions."
        result = AdvisorResult(
            summary=summary,
            what_i_found=[
                f"Emergency-fund gap: ${finance.emergency_gap:,}.",
                f"Current monthly savings capacity: ${finance.monthly_capacity:,}.",
                f"Estimated goal timing changes from {finance.months_without_trip} to {finance.months_with_trip} months if the trip uses planned savings.",
                f"Illustrative trip budget: ${trip['total']:,}; available cash above recorded emergency savings: ${affordable_cash:,}.",
            ],
            recommendation="Protect the emergency-fund contribution and create a separate travel sinking fund. A $2,400 version is the best balance if travel this year is important.",
            trade_offs=[
                "Paying $3,000 now preserves the trip experience but slows the emergency goal.",
                "Reducing the trip to $2,400 shortens the delay.",
                "Waiting until the travel fund is complete avoids drawing from emergency savings.",
            ],
            next_steps=[
                "Set a dedicated Italy travel goal",
                "Save $600 per month for five months",
                "Verify live flight and lodging prices before committing",
            ],
            assumptions=[
                "Monthly savings capacity remains $1,650",
                "No major income or expense changes",
                "Trip prices are illustrative mock data",
                "Emergency savings are not used for booking",
            ],
            alternatives=[
                {
                    "label": "Full trip",
                    "budget": 3000,
                    "estimated_delay_months": finance.delay_months,
                },
                {
                    "label": "Lean trip",
                    "budget": 2400,
                    "estimated_delay_months": round(2400 / finance.monthly_capacity, 1),
                },
                {"label": "No-delay plan", "budget": 3000, "funding": "$600/month for 5 months"},
            ],
            confidence=0.86,
            disclaimer="Educational financial planning scenario only; not investment, tax, or legal advice. Live travel prices were not checked.",
        )
        return tasks, result

    def _career(self, request: str, profile: Profile) -> tuple[list[AgentTask], AdvisorResult]:
        career_id, synth_id = str(uuid4()), str(uuid4())
        goal = profile.career_goal or "your target role"
        tasks = [
            AgentTask(
                task_id=career_id,
                agent="career_coach",
                objective="Identify the next highest-value skill",
                status="completed",
            ),
            AgentTask(
                task_id=synth_id,
                agent="orchestrator",
                objective="Create a personalized learning recommendation",
                dependencies=[career_id],
                status="completed",
            ),
        ]
        return tasks, AdvisorResult(
            summary=f"For your goal of becoming an {goal}, learn AI product discovery and evaluation next—not another general technical course.",
            what_i_found=[
                f"Your current role ({profile.occupation or 'financial analyst'}) already demonstrates analytical rigor and business judgment.",
                "The largest gap is evidence that you can identify an AI product problem, define success, evaluate model behavior, and make trade-offs.",
                "A portfolio case study will create stronger hiring evidence than a certificate alone.",
            ],
            recommendation="Complete one focused AI product case study over four weeks: interview users, define the problem and metrics, prototype an AI workflow, build a small evaluation set, and document product and safety trade-offs.",
            trade_offs=[
                "A certification is easier to signal, but a case study provides richer evidence of product judgment.",
                "Learning model internals is useful, but should not displace discovery, evaluation, and execution skills.",
                "A broad curriculum offers coverage; a focused project creates interview-ready stories faster.",
            ],
            next_steps=[
                "Choose one workflow from financial analysis that AI could improve",
                "Interview three potential users and write a one-page problem brief",
                "Define five evaluation cases and success metrics",
                "Publish the case study and practice a five-minute product walkthrough",
            ],
            assumptions=[
                "Your target remains AI Product Manager",
                "You can dedicate about five hours per week",
                "Recommendations use the seeded career profile; no resume or live job description was analyzed",
            ],
            alternatives=[
                {"label": "Best evidence", "funding": "4-week AI product case study"},
                {"label": "Structured path", "funding": "Product discovery + AI evaluation course"},
                {"label": "Fast practice", "funding": "Weekly teardown and mock interview"},
            ],
            confidence=0.84,
            disclaimer="Career guidance based on your saved profile and mock data. Verify course quality and role requirements before investing time or money.",
        )

    def _single_domain(
        self, intent: str, request: str, snapshot: FinancialSnapshot, profile: Profile
    ) -> tuple[list[AgentTask], AdvisorResult]:
        task_id, synth_id = str(uuid4()), str(uuid4())
        agent = {
            "investment": "investment_research",
            "finance": "personal_finance",
            "travel": "travel_planning",
            "general": "orchestrator",
        }[intent]
        summaries = {
            "investment": "Your most important portfolio issue to research is technology concentration, not the daily price movement.",
            "finance": f"Your current monthly savings capacity is approximately ${snapshot.monthly_savings_capacity:,}; protect that margin when prioritizing goals.",
            "travel": "Start with a goal-safe trip budget, then verify live flights and lodging before committing.",
            "general": "I need a little more detail to turn this into a specific, personalized plan.",
        }
        recommendations = {
            "investment": "Review look-through sector exposure across VOO, QQQ, MSFT, NVDA, and AAPL, then set a concentration range aligned with your moderate risk profile.",
            "finance": "Direct the monthly margin toward the highest-priority goal and reassess after any material income or expense change.",
            "travel": "Create a draft itinerary and separate travel sinking fund; treat all current prices as illustrative until a live provider is connected.",
            "general": "Add your desired outcome, deadline, constraints, and the decision you need to make.",
        }
        tasks = [
            AgentTask(task_id=task_id, agent=agent, objective=request, status="completed"),
            AgentTask(
                task_id=synth_id,
                agent="orchestrator",
                objective="Synthesize domain guidance",
                dependencies=[task_id],
                status="completed",
            ),
        ]
        return tasks, AdvisorResult(
            summary=summaries[intent],
            what_i_found=[
                f"The request was routed to the {agent.replace('_', ' ')} agent.",
                f"Relevant saved context: risk tolerance is {profile.risk_tolerance or 'not set'} and career goal is {profile.career_goal or 'not set'}.",
                "External providers are mocked, so no current market price, availability, or job claim is being made.",
            ],
            recommendation=recommendations[intent],
            trade_offs=[
                "More personalization requires additional verified profile data.",
                "Current information requires a live authorized provider.",
            ],
            next_steps=[
                "Review the recommendation",
                "Add any missing constraints",
                "Connect a live provider in Week 2 if current data is required",
            ],
            assumptions=["Seeded demo profile is current", "No external action is authorized"],
            alternatives=[
                {"label": "Focused plan", "funding": "Use saved profile context"},
                {"label": "Research mode", "funding": "Connect verified live data"},
            ],
            confidence=0.72,
            disclaimer="Educational planning guidance using seeded and mock data. No external action was performed.",
        )
