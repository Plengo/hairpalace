"""
NotificationService — unit tests (dev mode: no real SMTP required).
Tests verify correct subject generation, recipient resolution, and
that email failures never raise (they must log and continue).
"""
from unittest.mock import MagicMock, patch

import pytest

from app.features.notifications.service import NotificationService


def _mock_order(reference: str = "HP-TEST1", email: str = "buyer@hairpalace.co.za") -> MagicMock:
    order = MagicMock()
    order.reference = reference
    order.shipping_name = "Test Buyer"
    order.user = MagicMock()
    order.user.email = email
    item = MagicMock()
    item.product_name = "Body Wave Bundles"
    item.quantity = 2
    item.unit_price = "650.00"
    order.items = [item]
    order.total = "1380.00"
    order.shipping_address = "12 Long Street"
    order.shipping_city = "Cape Town"
    order.shipping_postal_code = "8001"
    return order


# ── Positive ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_order_confirmation_sent_in_dev_mode(caplog) -> None:
    """In dev (no SMTP_HOST), the service logs the email instead of sending."""
    svc = NotificationService()
    order = _mock_order()

    with patch.object(svc, "_send", wraps=svc._send):
        # SMTP_HOST is empty in test env — _send logs, does not raise
        await svc.send_order_confirmation(order)


@pytest.mark.asyncio
async def test_admin_alert_sent_in_dev_mode() -> None:
    """Alert-admin path executes without error in dev mode."""
    svc = NotificationService()
    order = _mock_order()
    # Should complete without raising
    await svc.alert_admin_new_order(order)


@pytest.mark.asyncio
async def test_confirmation_uses_correct_subject() -> None:
    """Email subject must contain the order reference and brand name."""
    svc = NotificationService()
    order = _mock_order(reference="HP-XYZ999")
    captured: dict = {}

    def _capture(to: str, subject: str, html_body: str) -> None:
        captured["subject"] = subject
        captured["to"] = to

    svc._send = _capture  # type: ignore[method-assign]
    await svc.send_order_confirmation(order)

    assert "HP-XYZ999" in captured["subject"]
    assert "Hair Palace" in captured["subject"]


@pytest.mark.asyncio
async def test_confirmation_sent_to_buyer_email() -> None:
    """Confirmation goes to the buyer's email, not admin."""
    svc = NotificationService()
    order = _mock_order(email="vip@example.com")
    captured: dict = {}

    def _capture(to: str, subject: str, html_body: str) -> None:
        captured["to"] = to

    svc._send = _capture  # type: ignore[method-assign]
    await svc.send_order_confirmation(order)

    assert captured["to"] == "vip@example.com"


@pytest.mark.asyncio
async def test_admin_alert_subject_signals_action_required() -> None:
    """Admin alert subject must convey urgency (new order, action needed)."""
    svc = NotificationService()
    order = _mock_order(reference="HP-URGENT")
    captured: dict = {}

    def _capture(to: str, subject: str, html_body: str) -> None:
        captured["subject"] = subject

    svc._send = _capture  # type: ignore[method-assign]
    await svc.alert_admin_new_order(order)

    assert "HP-URGENT" in captured["subject"]
    assert "Action Required" in captured["subject"]


# ── Negative ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_smtp_failure_does_not_raise() -> None:
    """SMTP errors must be swallowed — email failures cannot break order flow."""
    svc = NotificationService()
    order = _mock_order()

    with patch("smtplib.SMTP") as mock_smtp_cls, \
         patch("app.features.notifications.service.settings") as mock_settings:
        # Simulate a configured SMTP host so the send path is exercised
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user"
        mock_settings.SMTP_PASSWORD = "pass"
        mock_settings.EMAIL_FROM = "noreply@hairpalace.co.za"

        mock_smtp_cls.return_value.__enter__.return_value.sendmail.side_effect = Exception(
            "Connection refused"
        )

        # Must not raise
        await svc.send_order_confirmation(order)


# ── Edge cases ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_order_with_multiple_items_in_admin_alert() -> None:
    """Admin alert must not raise when order contains multiple line items."""
    svc = NotificationService()
    order = _mock_order()

    item2 = MagicMock()
    item2.product_name = "Lace Front Wig"
    item2.quantity = 1
    item2.unit_price = "1200.00"
    order.items = [order.items[0], item2]

    # Should complete without raising
    await svc.alert_admin_new_order(order)
