from fastapi import Depends, FastAPI

from config.error_handlers import register_error_handlers
from dependencies import get_current_client
from entities.client import Client
from routes import (
    alert_routes,
    auth_routes,
    client_routes,
    rule_routes,
    transaction_routes,
)
from schemas.client_schema import ClientOut

app = FastAPI(
    title="Financial Anomaly Detection API",
    description="Registers transactions and flags out-of-pattern operations.",
    version="0.1.0",
)

register_error_handlers(app)

app.include_router(auth_routes.router)
app.include_router(client_routes.router)
app.include_router(rule_routes.router)
app.include_router(transaction_routes.router)
app.include_router(alert_routes.router)

@app.get("/me", response_model=ClientOut, tags=["Auth"])
def get_me(current_client: Client = Depends(get_current_client)):
    return ClientOut.model_validate(current_client)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok"}
