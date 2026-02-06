"""Data masking utilities for sensitive information."""


def mask_email(email: str) -> str:
    """Mask email address."""
    if not email or '@' not in email:
        return email
    local, domain = email.split('@')
    return f"{local[:2]}***@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone number."""
    if not phone or len(phone) < 4:
        return phone
    return f"***{phone[-4:]}"


def mask_card(card: str) -> str:
    """Mask card number."""
    if not card or len(card) < 4:
        return card
    return f"****-****-****-{card[-4:]}"
