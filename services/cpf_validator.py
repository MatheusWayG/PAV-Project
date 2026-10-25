import re

class CpfValidator:
    _ALLOWED_FORMAT = re.compile(r"[0-9.\-\s]+", re.ASCII)

    @staticmethod
    def normalize(raw_cpf: str) -> str:
        """Keeps only the digits: '529.982.247-25' -> '52998224725'."""
        return re.sub(r"[^0-9]", "", raw_cpf)

    @classmethod
    def is_valid(cls, raw_cpf: str) -> bool:
        if not cls._ALLOWED_FORMAT.fullmatch(raw_cpf):
            return False

        cpf = cls.normalize(raw_cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:  # ex: 111.111.111-11
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