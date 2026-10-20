import re

class CpfValidator:
    _ALLOWED_FORMAT = re.compile(r"^[\d.\-\s]+$")

    @staticmethod
    def normalize(raw_cpf: str) -> str:
        return re.sub(r"\D", "", raw_cpf)

    @classmethod
    def is_valid(cls, raw_cpf: str) -> bool:
        if not cls._ALLOWED_FORMAT.match(raw_cpf):
            return False

        cpf = cls.normalize(raw_cpf)

        if len(cpf) != 11 or cpf == cpf[0] * 11:  # e.g. 111.111.111-11
            return False

        digits = [int(char) for char in cpf]

        return (
            digits[9] == cls._check_digit(digits[:9])
            and digits[10] == cls._check_digit(digits[:10])
        )

    @staticmethod
    def _check_digit(digits: list[int]) -> int:
        weight = len(digits) + 1
        total = sum(digit * (weight - index) for index, digit in enumerate(digits))
        
        return (total * 10 % 11) % 10