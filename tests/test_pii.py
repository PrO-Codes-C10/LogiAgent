from src.utils.pii_masker import (
    mask_email,
    mask_phone,
    mask_address,
    mask_pii_dict,
)


def test_mask_email_formats():
    """
    Test 7: Verifies email masking preserving domain and first/last characters of user handle.
    """
    # Standard email
    assert mask_email("alice.johnson@example.com") == "a***n@example.com"
    # Short handles
    assert mask_email("ab@domain.com") == "a*@domain.com"
    assert mask_email("a@domain.com") == "*@domain.com"
    # Malformed strings should be returned safely without crash
    assert mask_email("plainaddress") == "plainaddress"


def test_mask_phone_number_formats():
    """
    Test 8: Verifies phone masking preserving last 4 digits and country prefix.
    """
    # International phone with country prefix
    assert mask_phone("+1 (555) 349-8812") == "+1-***-***-8812"
    # 10-digit standard format
    assert mask_phone("5551234567") == "***-***-4567"
    # Short string safety
    assert mask_phone("12") == "***"


def test_mask_pii_dictionary_recursive():
    """
    Test 9: Verifies deep recursive masking of customer dictionaries containing nested PII.
    """
    customer_payload = {
        "customer_id": 101,
        "name": "Bob Smith",
        "email": "bob.smith@corporate.org",
        "phone": "+1 (555) 782-9901",
        "shipping_address": "1004 Elm Street, Apt 4B, Chicago, IL",
        "items": [
            {"item_id": "A1", "price": 49.99}
        ],
        "metadata": {
            "backup_email": "backup@test.com",
            "contact_phone": "3125550199"
        }
    }

    masked = mask_pii_dict(customer_payload)

    # Non-PII fields remain intact
    assert masked["customer_id"] == 101
    assert masked["name"] == "Bob Smith"
    assert masked["items"] == [{"item_id": "A1", "price": 49.99}]

    # PII fields are properly obscured
    assert masked["email"] == "b***h@corporate.org"
    assert masked["phone"] == "+1-***-***-9901"
    assert "1004" not in masked["shipping_address"]
    assert "*** Elm Street, Apt ***" in masked["shipping_address"]

    # Nested metadata dictionary is also masked
    assert masked["metadata"]["backup_email"] == "b***p@test.com"
    assert masked["metadata"]["contact_phone"] == "***-***-0199"
