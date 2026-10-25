from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from controllers.client_controller import ClientController
from repositories.client_repository import ClientRepository
from schemas.client_schema import ClientCreate, ClientOut, ClientUpdate
from services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["Clients"])

def get_client_controller(db: Session = Depends(get_db)) -> ClientController:
    return ClientController(ClientService(ClientRepository(db)))

@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    controller: ClientController = Depends(get_client_controller),
):
    return controller.create_client(data)

@router.get("", response_model=list[ClientOut])
def list_clients(
    skip: int = Query(0, ge=0, le=2_147_483_647),
    limit: int = Query(100, ge=1, le=500),
    controller: ClientController = Depends(get_client_controller),
):
    return controller.list_clients(skip, limit)

@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: int,
    controller: ClientController = Depends(get_client_controller),
):
    return controller.get_client(client_id)

@router.put("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    data: ClientUpdate,
    controller: ClientController = Depends(get_client_controller),
):
    return controller.update_client(client_id, data)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    controller: ClientController = Depends(get_client_controller),
):
    controller.delete_client(client_id)