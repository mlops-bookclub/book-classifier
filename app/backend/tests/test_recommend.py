from fastapi.testclient import TestClient


def test_recommend_returns_default_five(client: TestClient) -> None:
    response = client.post("/recommend", json={"book_title": "The Hunger Games"})
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) == 5


def test_recommend_respects_n_recommendations(client: TestClient) -> None:
    response = client.post(
        "/recommend",
        json={"book_title": "The Hunger Games", "n_recommendations": 2},
    )
    assert response.status_code == 200
    assert len(response.json()["recommendations"]) == 2


def test_recommend_response_shape(client: TestClient) -> None:
    response = client.post("/recommend", json={"book_title": "Divergent"})
    assert response.status_code == 200
    first = response.json()["recommendations"][0]
    assert "title" in first
    assert "author" in first
    assert "score" in first


def test_recommend_requires_book_title(client: TestClient) -> None:
    response = client.post("/recommend", json={})
    assert response.status_code == 422


# --- Security / input-validation tests ---


def test_recommend_rejects_blank_title(client: TestClient) -> None:
    response = client.post("/recommend", json={"book_title": "   "})
    assert response.status_code == 422


def test_recommend_rejects_html_injection(client: TestClient) -> None:
    response = client.post(
        "/recommend", json={"book_title": "<script>alert(1)</script>"}
    )
    assert response.status_code == 422


def test_recommend_rejects_template_injection(client: TestClient) -> None:
    response = client.post("/recommend", json={"book_title": "{{7*7}}"})
    assert response.status_code == 422


def test_recommend_rejects_title_exceeding_max_length(client: TestClient) -> None:
    response = client.post("/recommend", json={"book_title": "A" * 201})
    assert response.status_code == 422


def test_recommend_strips_surrounding_whitespace(client: TestClient) -> None:
    """Leading/trailing whitespace is silently stripped; the request succeeds."""
    response = client.post(
        "/recommend", json={"book_title": "  The Hunger Games  "}
    )
    assert response.status_code == 200


def test_recommend_rejects_oversized_body(client: TestClient) -> None:
    """Payloads whose Content-Length exceeds 10 KB are rejected with 413."""
    large_title = "A" * 10_300
    response = client.post("/recommend", json={"book_title": large_title})
    assert response.status_code == 413
