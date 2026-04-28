from fastapi.testclient import TestClient


def test_list_books_returns_empty_list(client: TestClient) -> None:
    response = client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert "books" in data
    assert isinstance(data["books"], list)
