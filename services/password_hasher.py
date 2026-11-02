import base64
import hashlib
import hmac
import os

class PasswordHasher:
    _N = 2**14
    _R = 8
    _P = 1
    _KEY_LENGTH = 32
    _SALT_BYTES = 16

    def hash(self, password: str) -> str:
        salt = os.urandom(self._SALT_BYTES)
        key = self._derive(password, salt, self._N, self._R, self._P)

        return "$".join(
            ["scrypt", str(self._N), str(self._R), str(self._P), self._b64(salt), self._b64(key)]
        )

    def verify(self, password: str, stored_hash: str) -> bool:
        try:
            scheme, n, r, p, salt, expected = stored_hash.split("$")

            if scheme != "scrypt":
                return False
            
            key = self._derive(password, base64.b64decode(salt), int(n), int(r), int(p))

            return hmac.compare_digest(key, base64.b64decode(expected))
        
        except (ValueError, TypeError):
            return False

    def _derive(self, password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
        return hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=self._KEY_LENGTH,
            maxmem=128 * n * r * p * 2,
        )

    @staticmethod
    def _b64(data: bytes) -> str:
        return base64.b64encode(data).decode("ascii")