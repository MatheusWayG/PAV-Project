from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from controllers.rule_controller import RuleController
from repositories.rule_repository import RuleRepository
from schemas.rule_schema import RuleCreate, RuleOut, RuleUpdate
from services.rule_service import RuleService

router = APIRouter(prefix="/rules", tags=["Rules"])

def get_rule_controller(db: Session = Depends(get_db)) -> RuleController:
    return RuleController(RuleService(RuleRepository(db)))

@router.post("", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(
    data: RuleCreate,
    controller: RuleController = Depends(get_rule_controller),
):
    return controller.create_rule(data)

@router.get("", response_model=list[RuleOut])
def list_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    controller: RuleController = Depends(get_rule_controller),
):
    return controller.list_rules(skip, limit)

@router.get("/{rule_id}", response_model=RuleOut)
def get_rule(
    rule_id: int,
    controller: RuleController = Depends(get_rule_controller),
):
    return controller.get_rule(rule_id)

@router.put("/{rule_id}", response_model=RuleOut)
def update_rule(
    rule_id: int,
    data: RuleUpdate,
    controller: RuleController = Depends(get_rule_controller),
):
    return controller.update_rule(rule_id, data)

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int,
    controller: RuleController = Depends(get_rule_controller),
):
    controller.delete_rule(rule_id)