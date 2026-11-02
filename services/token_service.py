from datetime import datetime, timedelta, timezone

import jwt

from config.exceptions import UnauthorizedError
from config.security import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET

class TokenService:
    def __init__(
        self,
        secret: str = JWT_SECRET,
        algorithm: str = JWT_ALGORITHM,
        expire_minutes: int = JWT_EXPIRE_MINUTES,
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    @property
    def expires_in_seconds(self) -> int:
        return self._expire_minutes * 60

    def create_access_token(self, client_id: int) -> str:
        issued_at = datetime.now(timezone.utc)
        payload = {
            "sub": str(client_id),
            "iat": issued_at,
            "exp": issued_at + timedelta(minutes=self._expire_minutes),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def read_client_id(self, token: str) -> int:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"require": ["exp", "sub"]},
            )

            return int(payload["sub"])
        
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token expired. Please log in again.")
        
        except (jwt.InvalidTokenError, ValueError, TypeError):
            raise UnauthorizedError("Invalid token.")