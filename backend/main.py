from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from lifeline.core.config import settings
from lifeline.models import create_tables
from lifeline.routers import (
    auth,
    users,
    products,
    sales,
    customers,
    suppliers,
    goods_received,
    inventory,
    expenses,
    cash,
    held_sales,
    reports,
    assistant,
    sync,
    settings as settings_router,
)

app = FastAPI(
    title="LIFELINE POS",
    description=(
        "Offline-first, AI-assisted point-of-sale and small-business management "
        "backend for independent retail shops."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def human_readable_error_handler(request: Request, exc: Exception):
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our side. Please try again, and if it keeps happening, contact support."},
    )


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(customers.router)
app.include_router(suppliers.router)
app.include_router(goods_received.router)
app.include_router(inventory.router)
app.include_router(expenses.router)
app.include_router(cash.router)
app.include_router(held_sales.router)
app.include_router(reports.router)
app.include_router(assistant.router)
app.include_router(sync.router)
app.include_router(settings_router.router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "LIFELINE POS",
        "sync_channel": "ready",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
