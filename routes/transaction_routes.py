from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from controllers.transaction_controller import TransactionController
from dependencies import get_current_client
from entities.client import Client
from entities.transaction import Classification
from repositories.client_repository import ClientRepository
from repositories.rule_repository import RuleRepository
from repositories.transaction_repository import TransactionRepository
from schemas.transaction_schema import (
    TransactionCreate,
    TransactionOut,
    TransactionUpdate,
)
from services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def get_transaction_controller(
    db: Session = Depends(get_db),
) -> TransactionController:
    service = TransactionService(
        TransactionRepository(db), ClientRepository(db), RuleRepository(db)
    )

    return TransactionController(service)

@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    current_client: Client = Depends(get_current_client),
    controller: TransactionController = Depends(get_transaction_controller),
):
    return controller.create_transaction(data, client=current_client)

@router.get("", response_model=list[TransactionOut])
def list_transactions(
    client_id: int | None = Query(None, gt=0),
    classification: Classification | None = Query(None),
    skip: int = Query(0, ge=0, le=2_147_483_647),
    limit: int = Query(100, ge=1, le=500),
    current_client: Client = Depends(get_current_client),
    controller: TransactionController = Depends(get_transaction_controller),
):
    effective_client_id = client_id if client_id is not None else current_client.id
    return controller.list_transactions(effective_client_id, classification, skip, limit)

@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: int,
    current_client: Client = Depends(get_current_client),
    controller: TransactionController = Depends(get_transaction_controller),
):
    return controller.get_transaction(transaction_id)

@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    current_client: Client = Depends(get_current_client),
    controller: TransactionController = Depends(get_transaction_controller),
):
    return controller.update_transaction(transaction_id, data)

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_client: Client = Depends(get_current_client),
    controller: TransactionController = Depends(get_transaction_controller),
):
    controller.delete_transaction(transaction_id)
