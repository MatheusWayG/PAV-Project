from entities.transaction import Classification
from schemas.alert_schema import AlertCreate, AlertOut, AlertUpdate
from services.alert_service import AlertService


class AlertController:
    def __init__(self, service: AlertService) -> None:
        self._service = service

    def list_alerts(
        self,
        transaction_id: int | None,
        rule_id: int | None,
        classification: Classification | None,
        skip: int,
        limit: int,
    ) -> list[AlertOut]:
        alerts = self._service.list_alerts(
            transaction_id, rule_id, classification, skip, limit
        )
        return [AlertOut.model_validate(alert) for alert in alerts]

    def get_alert(self, alert_id: int) -> AlertOut:
        return AlertOut.model_validate(self._service.get_alert(alert_id))

    def create_alert(self, data: AlertCreate) -> AlertOut:
        return AlertOut.model_validate(self._service.create_alert(data))

    def update_alert(self, alert_id: int, data: AlertUpdate) -> AlertOut:
        return AlertOut.model_validate(self._service.update_alert(alert_id, data))

    def delete_alert(self, alert_id: int) -> None:
        self._service.delete_alert(alert_id)