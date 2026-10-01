from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.order import Order
from app.models.audit_log import AuditLog


client = TestClient(app)


def test_create_order():
    response = client.post(
        "/orders",
        headers={
            "idempotency-key": "test-order-001"
        },
        json={
            "product": "Test Laptop",
            "side": "BUY",
            "quantity": 1,
            "price": 50000
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["product"] == "Test Laptop"
    assert data["side"] == "BUY"
    assert data["quantity"] == 1
    assert data["price"] == 50000
    assert data["status"] == "COMPLETED"
def test_idempotency():
    headers = {
        "idempotency-key": "test-idempotency-001"
    }

    order_data = {
        "product": "Test Phone",
        "side": "BUY",
        "quantity": 2,
        "price": 30000
    }

    # First request
    response1 = client.post(
        "/orders",
        headers=headers,
        json=order_data
    )

    # Same request again with the same idempotency key
    response2 = client.post(
        "/orders",
        headers=headers,
        json=order_data
    )

    assert response1.status_code == 201
    assert response2.status_code == 201

    data1 = response1.json()
    data2 = response2.json()

    # Both responses should refer to the same order
    assert data1["order_id"] == data2["order_id"]
def test_retry_recovery():
    headers = {
        "idempotency-key": "test-retry-recovery-001"
    }

    order_data = {
        "product": "Retry Product",
        "side": "BUY",
        "quantity": 1,
        "price": 1000
    }

    response = client.post(
        "/orders?simulate_failure=true",
        headers=headers,
        json=order_data
    )

    assert response.status_code == 201

    data = response.json()

    assert data["product"] == "Retry Product"
    assert data["status"] == "COMPLETED"
def test_permanent_failure():
    headers = {
        "idempotency-key": "test-permanent-failure-001"
    }

    order_data = {
        "product": "Failure Product",
        "side": "BUY",
        "quantity": 1,
        "price": 1000
    }

    response = client.post(
        "/orders?failure_mode=permanent",
        headers=headers,
        json=order_data
    )

    assert response.status_code == 500
def test_invalid_order_quantity():
    headers = {
        "idempotency-key": "test-invalid-quantity-001"
    }

    order_data = {
        "product": "Invalid Product",
        "side": "BUY",
        "quantity": -1,
        "price": 1000
    }

    response = client.post(
        "/orders",
        headers=headers,
        json=order_data
    )

    assert response.status_code == 422
def test_invalid_order_side():
    headers = {
        "idempotency-key": "test-invalid-side-001"
    }

    order_data = {
        "product": "Invalid Side Product",
        "side": "HOLD",
        "quantity": 1,
        "price": 1000
    }

    response = client.post(
        "/orders",
        headers=headers,
        json=order_data
    )

    assert response.status_code == 422
def test_database_rollback():
    headers = {
        "idempotency-key": "test-db-rollback-001"
    }

    order_data = {
        "product": "Rollback Verification",
        "side": "BUY",
        "quantity": 1,
        "price": 999
    }

    response = client.post(
        "/orders?failure_mode=permanent",
        headers=headers,
        json=order_data
    )

    assert response.status_code == 500

    db = SessionLocal()

    try:
        order = (
            db.query(Order)
            .filter(Order.product == "Rollback Verification")
            .first()
        )

        assert order is None

        failure_log = (
            db.query(AuditLog)
            .filter(
                AuditLog.event_type == "ORDER_FAILED",
                AuditLog.order_id.isnot(None)
            )
            .order_by(AuditLog.id.desc())
            .first()
        )

        assert failure_log is not None

    finally:
        db.close()