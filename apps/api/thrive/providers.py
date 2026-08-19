import json
import ssl
from datetime import UTC, datetime
from typing import Literal, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

from .config import settings
from .travel_catalog import ITALY_DAYS

NewsCategory = Literal["breaking", "ai", "technology", "health", "business", "finance", "politics"]


class TravelProvider(Protocol):
    def estimate_trip(self, destination: str, budget: int) -> dict: ...


class MarketDataProvider(Protocol):
    def portfolio_change(self, tickers: list[str]) -> dict: ...


class JobsProvider(Protocol):
    def recommended_roles(self, target: str) -> list[dict]: ...


class NewsProvider(Protocol):
    def headlines(self, category: NewsCategory) -> dict: ...


class NewsProviderError(RuntimeError):
    pass


class NewsApiProvider:
    headlines_endpoint = "https://newsapi.org/v2/top-headlines"
    everything_endpoint = "https://newsapi.org/v2/everything"

    def headlines(self, category: NewsCategory) -> dict:
        api_key = settings().news_api_key
        if not api_key:
            raise NewsProviderError("Real-time news is not configured. Add NEWS_API_KEY to .env.")
        endpoint = self.headlines_endpoint
        parameters: dict[str, str | int] = {"country": "us", "pageSize": 30}
        if category == "technology":
            parameters["category"] = "technology"
        elif category in {"health", "business"}:
            parameters["category"] = category
        elif category == "ai":
            endpoint = self.everything_endpoint
            parameters = {
                "q": '("artificial intelligence" OR OpenAI OR ChatGPT OR "machine learning")',
                "searchIn": "title,description",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 30,
            }
        elif category == "finance":
            endpoint = self.everything_endpoint
            parameters = {
                "q": '(finance OR markets OR economy OR investing)',
                "searchIn": "title,description",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 30,
            }
        elif category == "politics":
            endpoint = self.everything_endpoint
            parameters = {
                "q": '(politics OR government OR congress OR election)',
                "searchIn": "title,description",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 30,
            }
        request = Request(
            f"{endpoint}?{urlencode(parameters)}",
            headers={"X-Api-Key": api_key, "User-Agent": "PathWell/0.1"},
        )
        try:
            tls_context = ssl.create_default_context(cafile=certifi.where())
            with urlopen(request, timeout=8, context=tls_context) as response:
                payload = json.load(response)
        except (HTTPError, URLError, TimeoutError) as error:
            raise NewsProviderError(f"News provider request failed: {error}") from error
        retrieved_at = datetime.now(UTC).isoformat()
        articles = [
            {
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "image_url": article.get("urlToImage"),
                "source": (article.get("source") or {}).get("name") or "Unknown source",
                "published_at": article.get("publishedAt"),
            }
            for article in payload.get("articles", [])
            if article.get("title") and article.get("url")
        ]
        return {"category": category, "retrieved_at": retrieved_at, "articles": articles}


class MockTravelProvider:
    def estimate_trip(self, destination: str, budget: int) -> dict:
        return {
            "destination": destination,
            "total": budget,
            "breakdown": {
                "flights": 900,
                "lodging": 900,
                "food": 540,
                "activities": 360,
                "local_transport": 180,
                "buffer": 120,
            },
            "freshness": "Illustrative Week 1 estimate — live availability not checked",
        }

    def build_itinerary(self, request) -> dict:
        day_count = (request.end_date - request.start_date).days + 1
        daily_budget = request.budget // day_count
        templates = [
            (
                "Historic center orientation",
                "Neighborhood walk",
                "must",
                "09:00",
                120,
                request.destination,
                None,
            ),
            (
                "Local market and regional lunch",
                "Food & culture",
                "recommended",
                "12:00",
                150,
                request.destination,
                None,
            ),
            (
                "Signature museum or landmark",
                "Culture",
                "must",
                "15:00",
                150,
                request.destination,
                None,
            ),
            (
                "Independent neighborhood dinner",
                "Dining",
                "flexible",
                "19:00",
                90,
                request.destination,
                None,
            ),
        ]
        if request.pace == "relaxed":
            templates = templates[:3]
        if request.adjustment == "rain":
            templates = [
                (
                    "Covered market tasting",
                    "Indoor food",
                    "must",
                    "10:00",
                    120,
                    request.destination,
                    None,
                ),
                (
                    "Museum and gallery route",
                    "Indoor culture",
                    "must",
                    "13:00",
                    180,
                    request.destination,
                    None,
                ),
                (
                    "Cooking workshop",
                    "Indoor experience",
                    "recommended",
                    "17:30",
                    150,
                    request.destination,
                    None,
                ),
            ]
        days = []
        for index in range(day_count):
            date_value = request.start_date.fromordinal(request.start_date.toordinal() + index)
            catalog_day = None
            day_templates = templates
            if (
                "italy" in request.destination.lower()
                and request.adjustment != "rain"
                and index < len(ITALY_DAYS)
            ):
                catalog_day = ITALY_DAYS[index]
                day_templates = catalog_day["items"]
                if request.pace == "relaxed":
                    day_templates = day_templates[:3]
            items = [
                {
                    "id": f"day-{index + 1}-stop-{item_index + 1}",
                    "time": time,
                    "title": title if catalog_day else f"{title} · {request.destination}",
                    "category": category,
                    "priority": priority,
                    "duration_minutes": duration,
                    "estimated_cost": max(15, daily_budget // (len(day_templates) + 1)),
                    "why": f"Matches your {request.pace} pace and {', '.join(request.interests[:2]) or 'general'} interests.",
                    "location": location,
                    "official_url": official_url,
                    "status": "planned",
                }
                for item_index, (
                    title,
                    category,
                    priority,
                    time,
                    duration,
                    location,
                    official_url,
                ) in enumerate(day_templates)
            ]
            days.append(
                {
                    "id": f"day-{index + 1}",
                    "date": date_value.isoformat(),
                    "title": catalog_day["title"]
                    if catalog_day
                    else f"Day {index + 1} · {request.destination}",
                    "items": items,
                }
            )
        notices = []
        if request.adjustment == "rain":
            notices.append(
                "Outdoor stops were replaced with indoor alternatives for the selected rain scenario."
            )
        if request.adjustment == "flight_delay":
            remove_count = 2 if request.flight_delay_minutes >= 120 else 1
            days[0]["items"] = days[0]["items"][remove_count:]
            notices.append(
                f"Arrival day was shortened for a {request.flight_delay_minutes}-minute flight delay."
            )
        if request.adjustment == "lower_budget":
            for day in days:
                for item in day["items"]:
                    item["estimated_cost"] = max(8, round(item["estimated_cost"] * 0.7))
            notices.append("Costs were reduced by prioritizing free and lower-cost options.")
        return {
            "trip": {
                "destination": request.destination,
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "travelers": request.travelers,
                "budget": request.budget,
                "pace": request.pace,
                "interests": request.interests,
            },
            "days": days,
            "budget": {
                "total": request.budget,
                "transport": round(request.budget * 0.30),
                "lodging": round(request.budget * 0.32),
                "food": round(request.budget * 0.18),
                "activities": round(request.budget * 0.12),
                "buffer": round(request.budget * 0.08),
            },
            "notices": notices,
            "freshness": "Generated now from mock planning data; live prices, weather, traffic, hours, and availability were not checked.",
        }


class MockMarketDataProvider:
    def portfolio_change(self, tickers: list[str]) -> dict:
        return {"daily_change_percent": 0.74, "as_of": "Seeded demo data", "tickers": tickers}


class MockJobsProvider:
    def recommended_roles(self, target: str) -> list[dict]:
        return [
            {"title": target, "company": "Northwind AI", "fit": 84},
            {"title": "Technical Product Manager", "company": "Lumina", "fit": 79},
        ]
