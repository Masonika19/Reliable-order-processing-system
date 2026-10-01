from fastapi import APIRouter, Depends, Header,Query,HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import create_order


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=201
)
def create_new_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(...),
    failure_mode: str = Query("none")
):
    try:
        return create_order(
            db,
            order_data,
            idempotency_key,
            failure_mode
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Order processing failed. Transaction rolled back."
        )