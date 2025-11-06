import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_generate_logo():
    # Test payload for logo generation
    payload = {
        "company_name": "Sprintium",
        "industry": "Edu-Tech",
        "style": "Modern, Innovative use of whitespace, Minimalistic logo",
        "colors": "Blue",
        "additional_details": "Sprintium is a technology company which will accelerate Generative AI Development and Adoption for other other companies. They offer workshops and courses for quickly helping other users as well",
    }

    response = client.post("/generate-logo", json=payload)

    # Assert the response status code is 200
    assert response.status_code == 200

    # Assert the response contains the expected fields
    response_data = response.json()
    assert "image_url" in response_data
    # Add more assertions as needed based on your API response structure
