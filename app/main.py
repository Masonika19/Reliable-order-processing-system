from fastapi import FastAPI

from app.database import Base, engine
from app.models import order
from app.api.orders import router as order_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Reliable Order Processing System",
    description="A fault-tolerant REST API for reliable order processing.",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ROPS"
    }


# Register Orders API
app.include_router(order_router)