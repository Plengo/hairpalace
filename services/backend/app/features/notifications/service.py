"""
Email notification service — keeps email logic out of business layers (SoC).
Sends transactional emails for all user-facing communications.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger("hairpalace.notifications")
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
            if settings.SMTP_USE_SSL:
                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                    smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    smtp.sendmail(settings.EMAIL_FROM, to, msg.as_string())
            else:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    smtp.sendmail(settings.EMAIL_FROM, to, msg.as_string())
        except Exception as exc:
            # Log and continue — email failure must never break the request flow
            logger.exception("Email send failed: %s", exc)

    # ── Order lifecycle ──────────────────────────────────────────────────────

    async def send_order_confirmation(self, order) -> None:
        subject = f"Order Confirmed — {order.reference} | Hair Palace"
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
          <p style="color:#888;font-size:12px">Hair Palace &middot; Premium Hair</p>
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
        subject = f"Order Update — {order.reference} | Hair Palace"
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
          <h2 style="color:#C9A96E">Order Update</h2>
          <p>{message}</p>
          <hr/>
          <p style="color:#888;font-size:12px">Hair Palace &middot; Premium Hair</p>
        </div>
        """
        email = getattr(getattr(order, "user", None), "email", settings.ADMIN_EMAIL)
        self._send(email, subject, html)

    # ── Registration ─────────────────────────────────────────────────────────

    async def send_welcome_email(self, to_email: str, full_name: str) -> None:
        subject = "Welcome to Hair Palace 🖤"
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
          <h2 style="color:#C9A96E">Welcome, {full_name}!</h2>
          <p>Your Hair Palace account is ready. We stock premium hair for every style.</p>
          <p style="margin:24px 0">
            <a href="https://hairpalace.co.za/shop"
               style="background:#C9A96E;color:#fff;padding:12px 24px;border-radius:4px;text-decoration:none">
              Shop Now
            </a>
          </p>
          <hr/>
          <p style="color:#888;font-size:12px">Hair Palace &middot; Premium Hair</p>
        </div>
        """
        self._send(to_email, subject, html)

    # ── Password reset ───────────────────────────────────────────────────────

    async def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        subject = "Reset your Hair Palace password"
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
          <h2 style="color:#C9A96E">Password Reset</h2>
          <p>Click the button below to reset your password.
             This link expires in <strong>30 minutes</strong>.</p>
          <p style="margin:24px 0">
            <a href="{reset_link}"
               style="background:#C9A96E;color:#fff;padding:12px 24px;border-radius:4px;text-decoration:none">
              Reset Password
            </a>
          </p>
          <p style="font-size:12px;color:#888">If you didn't request this, you can safely ignore this email.</p>
          <hr/>
          <p style="color:#888;font-size:12px">Hair Palace &middot; Premium Hair</p>
        </div>
        """
        self._send(to_email, subject, html)

    # ── Contact form ─────────────────────────────────────────────────────────

    async def alert_admin_contact(self, name: str, email: str, message: str) -> None:
        subject = f"Contact Form — {name}"
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
          <h2 style="color:#C9A96E">New Contact Message</h2>
          <p><strong>Name:</strong> {name}</p>
          <p><strong>Email:</strong> {email}</p>
          <p><strong>Message:</strong></p>
          <p style="background:#f5f5f5;padding:12px;border-radius:4px;white-space:pre-wrap">{message}</p>
        </div>
        """
        self._send(settings.ADMIN_EMAIL, subject, html)

    async def send_contact_auto_reply(self, to_email: str, name: str) -> None:
        subject = "We received your message — Hair Palace"
        html = f"""
        <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
          <h2 style="color:#C9A96E">Thanks for reaching out, {name}!</h2>
          <p>We've received your message and will get back to you within
             <strong>1–2 business days</strong>.</p>
          <hr/>
          <p style="color:#888;font-size:12px">Hair Palace &middot; Premium Hair</p>
        </div>
        """
        self._send(to_email, subject, html)
