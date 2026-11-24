import re

from app.domain.exceptions import ValidationError


def normalize_required_text(
    value: str,
    *,
    field_name: str,
    min_length: int,
    max_length: int,
) -> str:
    normalized = value.strip()
    if not min_length <= len(normalized) <= max_length:
        raise ValidationError(
            f"{field_name} должно содержать от {min_length} до {max_length} символов"
        )
    return normalized


def normalize_code(value: str, *, pattern: str, field_name: str, max_length: int) -> str:
    normalized = value.strip().lower()
    if len(normalized) > max_length or re.fullmatch(pattern, normalized) is None:
        raise ValidationError(f"Некорректное значение поля {field_name}")
    return normalized


def normalize_currency(value: str) -> str:
    normalized = value.strip().upper()
    if re.fullmatch(r"[A-Z]{3}", normalized) is None:
        raise ValidationError("Валюта должна быть трёхбуквенным ISO-кодом")
    return normalized


def normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) > 320 or re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized) is None:
        raise ValidationError("Некорректный email")
    return normalized
