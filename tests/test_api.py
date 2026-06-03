import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add project root to python path to import backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api import app, is_advisory_query

client = TestClient(app)

def test_is_advisory_query_true():
    assert is_advisory_query("Should I invest in HDFC liquid fund?") == True
    assert is_advisory_query("Which fund is the best to buy?") == True
    assert is_advisory_query("I want some portfolio advice") == True

def test_is_advisory_query_false():
    assert is_advisory_query("What is the expense ratio?") == False
    assert is_advisory_query("Who is the fund manager?") == False

def test_chat_advisory_rejection():
    # Test that advisory queries get intercepted by the guardrail
    response = client.post("/chat", json={"query": "Should I invest my money?"})
    assert response.status_code == 200
    data = response.json()
    assert "I can only provide factual information" in data["response"]
    assert "https://www.amfiindia.com/" in data["sources"]
