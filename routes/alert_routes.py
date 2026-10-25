from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from controllers.alert_controller import AlertController
from entities.transaction import Classification
from repositories.alert_repository import AlertRepository
from repositories.rule_repository import RuleRepository
from repositories.transaction_repository import TransactionRepository
from schemas.alert_schema import AlertCreate, AlertOut, AlertUpdate
from services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def get_alert_controller(db: Session = Depends(get_db)) -> AlertController:
    service = AlertService(
        AlertRepository(db), TransactionRepository(db), RuleRepository(db)
    )

    return AlertController(service)

@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(
    data: AlertCreate,
    controller: AlertController = Depends(get_alert_controller),
):
    return controller.create_alert(data)

@router.get("", response_model=list[AlertOut])
def list_alerts(
    transaction_id: int | None = Query(None, gt=0),
    rule_id: int | None = Query(None, gt=0),
    classification: Classification | None = Query(None),
    skip: int = Query(0, ge=0, le=2_147_483_647),
    limit: int = Query(100, ge=1, le=500),
    controller: AlertController = Depends(get_alert_controller),
):
    return controller.list_alerts(
        transaction_id, rule_id, classification, skip, limit
    )

@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: int,
    controller: AlertController = Depends(get_alert_controller),
):
    return controller.get_alert(alert_id)

@router.put("/{alert_id}", response_model=AlertOut)
def update_alert(
    alert_id: int,
    data: AlertUpdate,
    controller: AlertController = Depends(get_alert_controller),
):
    return controller.update_alert(alert_id, data)

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    controller: AlertController = Depends(get_alert_controller),
):
    controller.delete_alert(alert_id)