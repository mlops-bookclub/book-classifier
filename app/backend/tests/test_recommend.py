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
