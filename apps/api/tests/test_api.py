def test_registration_and_profile(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Jamie Rivera",
            "email": "jamie@example.com",
            "phone": "+1 303 555 1212",
            "date_of_birth": "1993-05-14",
            "password": "StrongPass123",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 201
    user_id = response.json()["user_id"]
    me = client.get("/me", headers={"x-user-id": user_id})
    assert me.status_code == 200
    assert me.json()["email"] == "jamie@example.com"


def test_goal_creation_is_user_scoped(client):
    first = client.post(
        "/auth/register",
        json={
            "full_name": "First User",
            "email": "first@example.com",
            "phone": "3035551000",
            "date_of_birth": "1990-01-01",
            "password": "StrongPass123",
            "terms_accepted": True,
        },
    ).json()
    second = client.post(
        "/auth/register",
        json={
            "full_name": "Second User",
            "email": "second@example.com",
            "phone": "3035552000",
            "date_of_birth": "1991-01-01",
            "password": "StrongPass123",
            "terms_accepted": True,
        },
    ).json()
    client.post(
        "/goals",
        headers={"x-user-id": first["user_id"]},
        json={"category": "financial", "title": "Private goal", "target_value": 1000},
    )
    assert len(client.get("/goals", headers={"x-user-id": second["user_id"]}).json()) == 0


def test_multi_agent_trip_workflow(client):
    response = client.post(
        "/ai/chat",
        json={
            "message": "Can I afford a $3,000 trip to Italy this year without delaying my emergency-fund goal?"
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert [task["agent"] for task in body["tasks"]] == [
        "personal_finance",
        "travel_planning",
        "orchestrator",
    ]
    assert "delay" in body["result"]["summary"].lower()
    assert body["result"]["alternatives"]


def test_career_question_routes_only_to_career_agent(client):
    response = client.post("/ai/chat", json={"message": "What should I learn next?"})
    assert response.status_code == 200
    body = response.json()
    agents = [task["agent"] for task in body["tasks"]]
    assert agents == ["career_coach", "orchestrator"]
    assert "AI product discovery" in body["result"]["summary"]
    assert "Italy" not in body["result"]["summary"]
    assert body["activities"][0] == "Reviewing your career goal"


def test_document_access_is_user_scoped(client):
    first = client.post(
        "/auth/register",
        json={
            "full_name": "Doc Owner",
            "email": "owner@example.com",
            "phone": "3035553000",
            "date_of_birth": "1990-01-01",
            "password": "StrongPass123",
            "terms_accepted": True,
        },
    ).json()
    second = client.post(
        "/auth/register",
        json={
            "full_name": "Other User",
            "email": "other@example.com",
            "phone": "3035554000",
            "date_of_birth": "1991-01-01",
            "password": "StrongPass123",
            "terms_accepted": True,
        },
    ).json()
    doc = client.post(
        "/documents/upload-url",
        headers={"x-user-id": first["user_id"]},
        json={"filename": "resume.pdf", "mime_type": "application/pdf", "size": 1024},
    ).json()
    assert (
        client.delete(
            f"/documents/{doc['id']}", headers={"x-user-id": second["user_id"]}
        ).status_code
        == 404
    )


def test_seeded_domain_routes(client):
    assert client.get("/finance/summary").status_code == 200
    portfolio = client.get("/investments/portfolio").json()
    assert len(portfolio["holdings"]) == 6
    assert client.get("/career/profile").json()["career_goal"] == "Become an AI Product Manager"
    assert client.get("/travel/trips").json()[0]["status"] == "drafted"


def test_news_requires_provider_configuration(client, monkeypatch):
    from thrive.config import settings

    monkeypatch.setattr(settings(), "news_api_key", "")
    response = client.get("/news/headlines?category=ai")
    assert response.status_code == 503
    assert "NEWS_API_KEY" in response.json()["detail"]


def test_news_rejects_unknown_category(client):
    assert client.get("/news/headlines?category=sports").status_code == 422


def test_news_uses_a_verified_ca_bundle(client, monkeypatch):
    import ssl

    from thrive import providers
    from thrive.config import settings

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"articles": []}'

    captured = {}

    def fake_urlopen(request, **kwargs):
        captured["url"] = request.full_url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr(settings(), "news_api_key", "test-key")
    monkeypatch.setattr(providers, "urlopen", fake_urlopen)

    response = client.get("/news/headlines?category=ai")

    assert response.status_code == 200
    assert captured["timeout"] == 8
    assert captured["context"].verify_mode == ssl.CERT_REQUIRED
    assert captured["context"].check_hostname is True
    assert "/v2/everything?" in captured["url"]
    assert "sortBy=publishedAt" in captured["url"]


def test_business_news_uses_top_headlines(client, monkeypatch):
    from thrive import providers
    from thrive.config import settings

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return b'{"articles": []}'

    captured = {}

    def fake_urlopen(request, **kwargs):
        captured["url"] = request.full_url
        return FakeResponse()

    monkeypatch.setattr(settings(), "news_api_key", "test-key")
    monkeypatch.setattr(providers, "urlopen", fake_urlopen)

    response = client.get("/news/headlines?category=business")

    assert response.status_code == 200
    assert "/v2/top-headlines?" in captured["url"]
    assert "category=business" in captured["url"]


def test_trip_plan_reacts_to_weather_and_delay(client):
    base = {
        "destination": "Italy",
        "start_date": "2027-05-08",
        "end_date": "2027-05-10",
        "travelers": 1,
        "budget": 3000,
        "pace": "balanced",
        "interests": ["food", "culture"],
    }
    rain = client.post("/travel/plan", json={**base, "adjustment": "rain"})
    assert rain.status_code == 200
    assert "Indoor" in rain.json()["days"][0]["items"][0]["category"]
    delayed = client.post(
        "/travel/plan",
        json={**base, "adjustment": "flight_delay", "flight_delay_minutes": 120},
    )
    assert delayed.status_code == 200
    assert len(delayed.json()["days"][0]["items"]) == 2
    assert "120-minute" in delayed.json()["notices"][0]


def test_italy_itinerary_uses_unique_real_attractions_each_day(client):
    response = client.post(
        "/travel/plan",
        json={
            "destination": "Italy",
            "start_date": "2027-05-08",
            "end_date": "2027-05-16",
            "travelers": 1,
            "budget": 3000,
            "pace": "balanced",
            "interests": ["food", "culture"],
        },
    )
    assert response.status_code == 200
    days = response.json()["days"]
    assert days[0]["items"][0]["title"] == "Pantheon"
    assert days[1]["items"][0]["title"] == "Colosseum"
    assert days[3]["items"][0]["title"] == "Cathedral of Santa Maria del Fiore"
    assert days[6]["items"][0]["title"] == "St. Mark’s Basilica"
    titles = [item["title"] for day in days for item in day["items"]]
    assert len(titles) == len(set(titles))
    assert all(item["location"] for day in days for item in day["items"])


def test_trip_plan_validates_date_order(client):
    response = client.post(
        "/travel/plan",
        json={
            "destination": "Italy",
            "start_date": "2027-05-10",
            "end_date": "2027-05-08",
            "budget": 3000,
        },
    )
    assert response.status_code == 422
