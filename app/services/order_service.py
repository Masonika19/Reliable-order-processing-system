import uuid
import time

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.idempotency import IdempotencyKey
from app.models.audit_log import AuditLog
from app.schemas.order import OrderCreate


MAX_RETRIES = 3


def create_order(
    db: Session,
    order_data: OrderCreate,
    idempotency_key: str,
    failure_mode: str = "none"
):
    # Check whether this request was already processed
    existing_key = (
        db.query(IdempotencyKey)
        .filter(IdempotencyKey.key == idempotency_key)
        .first()
    )

    if existing_key:
        existing_order = (
            db.query(Order)
            .filter(Order.order_id == existing_key.order_id)
            .first()
        )

        return existing_order

    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            print(f"Processing attempt {attempt}/{MAX_RETRIES}")

            order = Order(
                order_id=order_id,
                product=order_data.product,
                side=order_data.side,
                quantity=order_data.quantity,
                price=order_data.price,
                status="COMPLETED"
            )

            db.add(order)

            key_record = IdempotencyKey(
                key=idempotency_key,
                order_id=order_id,
                status="COMPLETED"
            )

            db.add(key_record)

            # Simulate failure
            # Simulate a temporary failure on the first attempt
            # Simulate failures for reliability testing
            if failure_mode == "temporary" and attempt == 1:
                raise RuntimeError("Simulated temporary failure")

            if failure_mode == "permanent":
                raise RuntimeError("Simulated permanent failure")
            # Success audit log
            audit_log = AuditLog(
                order_id=order_id,
                event_type="ORDER_CREATED",
                message=f"Order processed successfully on attempt {attempt}"
            )

            db.add(audit_log)

            db.commit()
            db.refresh(order)

            print(f"Order completed on attempt {attempt}")

            return order

        except Exception as error:

            db.rollback()

            print(
                f"Attempt {attempt} failed: {str(error)}"
            )

            if attempt < MAX_RETRIES:

                retry_log = AuditLog(
                    order_id=order_id,
                    event_type="RETRY",
                    message=f"Retrying order processing after attempt {attempt}"
                )

                db.add(retry_log)
                db.commit()

                time.sleep(1)

            else:

                failure_log = AuditLog(
                    order_id=order_id,
                    event_type="ORDER_FAILED",
                    message=(
                        f"Order failed after {MAX_RETRIES} attempts: "
                        f"{str(error)}"
                    )
                )

                db.add(failure_log)
                db.commit()

                raise