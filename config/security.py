import os

JWT_SECRET = os.getenv(
    "JWT_SECRET", "faeterj-pav-secret-token"
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))