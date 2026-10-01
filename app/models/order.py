from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    product = Column(
        String(100),
        nullable=False
    )

    side = Column(
        String(10),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    price = Column(
        Float,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )