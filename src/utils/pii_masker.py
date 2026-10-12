import re
from typing import Any, Dict


def mask_email(email: str) -> str:
    """
    Masks an email address for privacy.
    Example: 'alexander@example.com' -> 'a***r@example.com'
             'me@test.com' -> 'm*e@test.com'
    """
    if not email or "@" not in email:
        return email

    parts = email.strip().split("@")
    if len(parts) != 2:
        return email

    username, domain = parts[0], parts[1]

    if len(username) <= 1:
        masked_user = "*"
    elif len(username) == 2:
        masked_user = username[0] + "*"
    else:
        masked_user = username[0] + "***" + username[-1]

    return f"{masked_user}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Masks a phone number while preserving country prefix and last 4 digits.
    Example: '+1-555-839-2019' -> '+1-***-***-2019'
             '9876543210' -> '******3210'
    """
    if not phone:
        return phone

    clean_digits = re.sub(r"\D", "", phone)
    if len(clean_digits) < 4:
        return "***"

    last_four = clean_digits[-4:]

    if phone.startswith("+"):
        prefix = phone.split()[0] if " " in phone else phone[:3]
        return f"{prefix}-***-***-{last_four}"
    elif len(clean_digits) == 10:
        return f"***-***-{last_four}"
    else:
        return f"{'*' * (len(clean_digits) - 4)}{last_four}"


def mask_address(address: str) -> str:
    """
    Masks building numbers / apt numbers from street address.
    Example: '742 Evergreen Terrace, Springfield' -> '*** Evergreen Terrace, Springfield'
    """
    if not address:
        return address

    # Mask leading street numbers
    masked = re.sub(r"^\d+([A-Za-z]?)(\s+)", r"***\2", address.strip())
    # Mask Apt/Suite numbers
    masked = re.sub(r"(?i)\b(apt|suite|unit|#)\s*\d+[a-z]?", r"\1 ***", masked)
    return masked


def mask_pii_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deeply masks sensitive keys in a dictionary before logging or LLM transmission.
    """
    if not isinstance(data, dict):
        return data

    masked_data = {}
    for key, value in data.items():
        key_lower = key.lower()
        if isinstance(value, dict):
            masked_data[key] = mask_pii_dict(value)
        elif isinstance(value, list):
            masked_data[key] = [
                mask_pii_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, str):
            if "email" in key_lower:
                masked_data[key] = mask_email(value)
            elif any(k in key_lower for k in ["phone", "mobile", "tel"]):
                masked_data[key] = mask_phone(value)
            elif any(k in key_lower for k in ["address", "street"]):
                masked_data[key] = mask_address(value)
            else:
                masked_data[key] = value
        else:
            masked_data[key] = value

    return masked_data
