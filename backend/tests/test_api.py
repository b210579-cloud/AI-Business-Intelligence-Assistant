
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_total_revenue():
    response = client.post(
        "/ask",
        json={"question": "What is the total revenue?"}
    )
    assert response.status_code == 200
    assert response.json()["supporting_data"]["total_revenue"] == 1439200


def test_highest_revenue_product():
    response = client.post(
        "/ask",
        json={"question": "Which product generated the highest revenue?"}
    )
    assert response.status_code == 200
    assert response.json()["supporting_data"]["product"] == "Monitor"


def test_highest_sales_region():
    response = client.post(
        "/ask",
        json={"question": "Which region has the highest sales?"}
    )
    assert response.status_code == 200
    assert response.json()["supporting_data"]["region"] == "South"


def test_monthly_revenue():
    response = client.post(
        "/ask",
        json={"question": "Show me the monthly revenue trend."}
    )
    assert response.status_code == 200
    data = response.json()["supporting_data"]
    assert len(data) == 6
    assert data[0]["revenue"] == 210250


def test_month_comparison():
    response = client.post(
        "/ask",
        json={"question": "What is the revenue change between January and February?"}
    )
    assert response.status_code == 200
    data = response.json()["supporting_data"]
    assert data["revenue_change"] == 24350


def test_empty_question():
    response = client.post(
        "/ask",
        json={"question": ""}
    )
    assert response.status_code == 400


def test_unsupported_question():
    response = client.post(
        "/ask",
        json={"question": "What is the weather today?"}
    )
    assert response.status_code == 200
    assert response.json()["supporting_data"] is None
