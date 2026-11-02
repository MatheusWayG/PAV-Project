from fastapi import APIRouter, Depends, Request

from config.exceptions import UnauthorizedError
from controllers.auth_controller import AuthController
from dependencies import get_auth_service, get_current_client
from entities.client import Client
from schemas.auth_schema import TokenOut
from schemas.client_schema import ClientOut
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_auth_controller(
    service: AuthService = Depends(get_auth_service),
) -> AuthController:
    return AuthController(service)

@router.post(
    "/login",
    response_model=TokenOut,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "CPF (digits or formatted)"},
                            "password": {"type": "string", "format": "password"},
                        },
                        "required": ["username", "password"],
                    }
                },
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "cpf": {"type": "string", "description": "CPF (digits or formatted)"},
                            "password": {"type": "string"},
                        },
                        "required": ["password"],
                    }
                },
            }
        }
    },
)
async def login(
    request: Request,
    controller: AuthController = Depends(get_auth_controller),
):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        username = body.get("cpf") or body.get("username")
        password = body.get("password")
    else:
        form = await request.form()
        username = form.get("username") or form.get("cpf")
        password = form.get("password")

    if not username or not password:
        raise UnauthorizedError("Invalid CPF or password.")

    return controller.login(str(username), str(password))

@router.get("/me", response_model=ClientOut)
def get_me(
    current_client: Client = Depends(get_current_client),
    controller: AuthController = Depends(get_auth_controller),
):
    return controller.get_me(current_client)
