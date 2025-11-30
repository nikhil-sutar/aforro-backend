from core.celery import app
from django.core.mail import send_mail
from django.conf import settings

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_email(self, email, username, order_id, store_name, total_amount):
    subject = f"Order Confirmation - #{order_id}"

    message = f"""
    Hi {username},

    Your order #{order_id} has been confirmed!

    Store: {store_name}
    Total Amount: ₹{total_amount}

    Thank you for shopping with Aforro.
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)