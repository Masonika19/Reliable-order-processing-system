from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    key = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    order_id = Column(
        String(50),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )