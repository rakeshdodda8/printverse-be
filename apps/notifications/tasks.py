import json
import logging
from celery import shared_task
from django.conf import settings
from .models import Notification

logger = logging.getLogger(__name__)


def _init_firebase():
    if not settings.FCM_CREDENTIALS_JSON:
        return None
    try:
        import firebase_admin
        from firebase_admin import credentials
        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(settings.FCM_CREDENTIALS_JSON))
            firebase_admin.initialize_app(cred)
        return firebase_admin
    except Exception as e:
        logger.warning("Firebase init failed: %s", e)
        return None


@shared_task
def send_push_notification(user_id: str, title: str, body: str, data: dict = None):
    from apps.users.models import User
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return
    Notification.objects.create(user=user, title=title, body=body, data=data or {}, channel="push")

    fb = _init_firebase()
    if not fb or not user.fcm_token:
        return
    from firebase_admin import messaging
    msg = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=user.fcm_token,
        data={k: str(v) for k, v in (data or {}).items()},
    )
    try:
        messaging.send(msg)
    except Exception as e:
        logger.error("FCM send failed: %s", e)


@shared_task
def send_order_status_notification(order_id: str, new_status: str):
    from apps.orders.models import Order
    try:
        order = Order.objects.select_related("user").get(id=order_id)
    except Order.DoesNotExist:
        return
    title = "Order Update"
    body = f"Order {order.order_number} is now {new_status.replace('_', ' ').title()}"
    send_push_notification.delay(str(order.user_id), title, body, {"order_id": str(order.id), "status": new_status})

