"""
Email notification service — keeps email logic out of business layers (SoC).
Sends transactional emails for order lifecycle events.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger("strands.notifications")
settings = get_settings()


class NotificationService:

    def _send(self, to: str, subject: str, html_body: str) -> None:
        if not settings.SMTP_HOST:
            # Dev mode — log instead of sending
            logger.info("[EMAIL] To=%s | Subject=%s", to, subject)
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                smtp.sendmail(settings.EMAIL_FROM, to, msg.as_string())
        except Exception as exc:
            # Log and continue — email failure must never break the order flow
            logger.exception("Email send failed: %s", exc)

    async def send_order_confirmation(self, order) -> None:
        subject = f"Order Confirmed — {order.reference} | STRANDS"
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
          <h2 style="color:#C9A96E">Your order is confirmed</h2>
          <p>Hi {order.shipping_name},</p>
          <p>We've received your order <strong>{order.reference}</strong> 
             and your payment has been processed.</p>
          <p>We're now sourcing your items. Allow <strong>3–5 business days</strong> 
             for preparation before dispatch.</p>
          <p>We'll notify you as soon as your order ships.</p>
          <hr/>
          <p style="color:#888;font-size:12px">STRANDS · Premium Hair &amp; Beauty</p>
        </div>
        """
        self._send(order.user.email if hasattr(order, "user") else settings.ADMIN_EMAIL, subject, html)

    async def alert_admin_new_order(self, order) -> None:
        """Alerts the store owner to go buy stock — core of the order-first model."""
        subject = f"🛒 New Order — {order.reference} | Action Required"
        items_html = "".join(
            f"<li>{item.product_name} × {item.quantity} @ R{item.unit_price}</li>"
            for item in order.items
        )
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
          <h2 style="color:#C9A96E">New Paid Order — Go Source Stock</h2>
          <p><strong>Reference:</strong> {order.reference}</p>
          <p><strong>Total:</strong> R{order.total}</p>
          <p><strong>Ship to:</strong> {order.shipping_name}, {order.shipping_address}, 
             {order.shipping_city}, {order.shipping_province} {order.shipping_postal_code}</p>
          <h3>Items to buy:</h3>
          <ul>{items_html}</ul>
          <p>Log into the admin dashboard to update the order status after sourcing.</p>
        </div>
        """
        self._send(settings.ADMIN_EMAIL, subject, html)

    async def send_order_status_update(self, order) -> None:
        status_messages = {
            "shipped": f"Your order {order.reference} has been shipped!"
                       + (f" Tracking: {order.tracking_number}" if order.tracking_number else ""),
            "delivered": f"Your order {order.reference} has been delivered. Enjoy! 🖤",
        }
        message = status_messages.get(order.status.value, f"Order {order.reference} updated.")
        subject = f"Order Update — {order.reference} | STRANDS"
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
          <h2 style="color:#C9A96E">Order Update</h2>
          <p>{message}</p>
          <hr/>
          <p style="color:#888;font-size:12px">STRANDS · Premium Hair &amp; Beauty</p>
        </div>
        """
        email = getattr(getattr(order, "user", None), "email", settings.ADMIN_EMAIL)
        self._send(email, subject, html)
