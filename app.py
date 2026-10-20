from fastapi import FastAPI

from config.error_handlers import register_error_handlers
from routes import client_routes, rule_routes, transaction_routes

app = FastAPI(
    title="Financial Anomaly Detection API",
    description="Registers transactions and flags out-of-pattern operations.",
    version="0.1.0",
)

register_error_handlers(app)
app.include_router(client_routes.router)
app.include_router(rule_routes.router)
app.include_router(transaction_routes.router)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok"}