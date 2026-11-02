from pydantic import BaseModel, Field

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until the token expires

class LoginRequest(BaseModel):
    cpf: str = Field(min_length=11, max_length=14)
    password: str = Field(min_length=1, max_length=128)
