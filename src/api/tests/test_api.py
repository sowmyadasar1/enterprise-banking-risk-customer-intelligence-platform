"""
Automated Test Suite for the Enterprise Banking FastAPI Platform.
Uses FastAPI TestClient (no live server needed).
"""
import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..config import API_KEY, API_PREFIX

client = TestClient(app)
HEADERS = {"X-API-Key": API_KEY}


# ═══════════════════════════════════════════════════════════════════
#  HEALTH & SYSTEM TESTS
# ═══════════════════════════════════════════════════════════════════
class TestHealth:
    def test_health_endpoint(self):
        resp = client.get(f"{API_PREFIX}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "models_loaded" in data

    def test_info_endpoint(self):
        resp = client.get(f"{API_PREFIX}/info")
        assert resp.status_code == 200
        data = resp.json()
        assert "capabilities" in data
        assert len(data["capabilities"]) == 4

    def test_models_endpoint(self):
        resp = client.get(f"{API_PREFIX}/models")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data

    def test_root_redirect(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "docs" in resp.json()


# ═══════════════════════════════════════════════════════════════════
#  SECURITY TESTS
# ═══════════════════════════════════════════════════════════════════
class TestSecurity:
    def test_missing_api_key(self):
        resp = client.post(f"{API_PREFIX}/predict/fraud", json={})
        assert resp.status_code == 401

    def test_invalid_api_key(self):
        resp = client.post(
            f"{API_PREFIX}/predict/fraud",
            json={},
            headers={"X-API-Key": "wrong-key"},
        )
        assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════
#  VALIDATION TESTS (Schema Rejection)
# ═══════════════════════════════════════════════════════════════════
class TestValidation:
    def test_fraud_missing_fields(self):
        resp = client.post(
            f"{API_PREFIX}/predict/fraud",
            json={"transaction_amount": 100},
            headers=HEADERS,
        )
        assert resp.status_code == 422

    def test_loan_negative_amount(self):
        resp = client.post(
            f"{API_PREFIX}/predict/loan-default",
            json={"loan_amount": -1000, "interest_rate": 5},
            headers=HEADERS,
        )
        assert resp.status_code == 422

    def test_forecast_invalid_metric(self):
        resp = client.get(
            f"{API_PREFIX}/forecast/invalid_metric?horizon=30",
            headers=HEADERS,
        )
        # This should return 500 (PredictionError) since the metric is invalid
        assert resp.status_code == 500


# ═══════════════════════════════════════════════════════════════════
#  PREDICTION TESTS (End-to-End)
# ═══════════════════════════════════════════════════════════════════
class TestPredictions:
    def test_fraud_prediction(self):
        payload = {
            "transaction_amount": 4500.00,
            "merchant_category": "electronics",
            "transaction_hour": 2,
            "transaction_day_of_week": 5,
            "is_international": 1,
            "is_weekend": 1,
            "customer_age": 34,
            "account_age_days": 180,
            "avg_transaction_amount": 250.00,
            "transaction_count_30d": 12,
            "amount_std_30d": 350.00,
            "distance_from_home": 850.5,
        }
        resp = client.post(f"{API_PREFIX}/predict/fraud", json=payload, headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "prediction" in data
        assert "fraud_probability" in data["prediction"]
        assert 0 <= data["prediction"]["fraud_probability"] <= 1
        assert data["prediction"]["risk_level"] in ["Low", "Medium", "High", "Critical"]
        assert "metadata" in data
        assert data["metadata"]["latency_ms"] >= 0

    def test_loan_default_prediction(self):
        payload = {
            "loan_amount": 25000.00,
            "interest_rate": 7.5,
            "loan_term_months": 60,
            "customer_age": 42,
            "annual_income": 85000.00,
            "credit_score": 720,
            "debt_to_income_ratio": 0.35,
            "employment_length_years": 8.0,
            "number_of_accounts": 5,
            "previous_defaults": 0,
        }
        resp = client.post(f"{API_PREFIX}/predict/loan-default", json=payload, headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "prediction" in data
        assert data["prediction"]["risk_band"] in ["Low", "Medium", "High"]
        assert data["prediction"]["recommended_action"] in ["Approve", "Review", "Decline"]

    def test_segmentation_prediction(self):
        payload = {
            "avg_balance": 45000.00,
            "total_transactions": 320,
            "avg_transaction_amount": 512.75,
            "tenure_days": 1825,
            "num_products": 4,
            "credit_score": 760,
        }
        resp = client.post(f"{API_PREFIX}/predict/segmentation", json=payload, headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "prediction" in data
        assert "cluster_id" in data["prediction"]
        assert "persona" in data["prediction"]

    def test_forecast_revenue(self):
        resp = client.get(f"{API_PREFIX}/forecast/revenue?horizon=30", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["target_metric"] == "revenue"
        assert data["horizon_days"] == 30
        assert len(data["forecast"]) == 30
        assert data["cumulative_total"] >= 0

    def test_fraud_batch(self):
        txn = {
            "transaction_amount": 100.00,
            "merchant_category": "grocery",
            "transaction_hour": 10,
            "transaction_day_of_week": 2,
            "is_international": 0,
            "is_weekend": 0,
            "customer_age": 45,
            "account_age_days": 900,
            "avg_transaction_amount": 120.00,
            "transaction_count_30d": 25,
            "amount_std_30d": 40.00,
            "distance_from_home": 5.0,
        }
        resp = client.post(
            f"{API_PREFIX}/predict/fraud/batch",
            json={"transactions": [txn, txn]},
            headers=HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_scored"] == 2


# ═══════════════════════════════════════════════════════════════════
#  RUNNER
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
