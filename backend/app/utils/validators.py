"""Small reusable validation helpers."""


def is_valid_application_id(value: str) -> bool:
    return bool(value) and value.startswith("LN-") and value[3:].isdigit()
