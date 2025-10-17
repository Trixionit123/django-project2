from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from pathlib import Path
from datetime import timedelta
import os
from .models import Order
from myproject.kafka_utils import publish_order_created


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=5)
def send_order_confirmation(self, order_id: int, to_email: str) -> str:
	order = Order.objects.get(pk=order_id)
	context = {
		'order': order,
		'items': list(order.items.all()),
		'user': order.user,
		'timestamp': timezone.now(),
		'to_email': to_email,
	}

	# Render confirmation content to a file in an outbox directory
	outbox_dir = Path(getattr(settings, 'ORDER_CONFIRMATION_OUTBOX', settings.BASE_DIR / 'outbox'))
	outbox_dir.mkdir(parents=True, exist_ok=True)
	filename = outbox_dir / f"order_{order.id}_confirmation.txt"
	content = render_to_string('emails/order_confirmation.txt', context)
	filename.write_text(content, encoding='utf-8')

	return f"rendered:{order.id}:{filename}"


@shared_task
def cancel_stale_pending_orders() -> int:
	max_age_hours = int(getattr(settings, 'ORDER_PENDING_MAX_AGE_HOURS', 24))
	threshold = timezone.now() - timedelta(hours=max_age_hours)
	updated = Order.objects.filter(status='pending', created_at__lt=threshold).update(status='cancelled')
	return int(updated)


@shared_task
def auto_ship_processing_orders() -> int:
	max_age_hours = int(getattr(settings, 'ORDER_PROCESSING_TO_SHIPPED_HOURS', 12))
	threshold = timezone.now() - timedelta(hours=max_age_hours)
	updated = Order.objects.filter(status='processing', created_at__lt=threshold).update(status='shipped')
	return int(updated)


@shared_task
def clean_old_outbox_files() -> int:
	outbox_dir = Path(getattr(settings, 'ORDER_CONFIRMATION_OUTBOX', settings.BASE_DIR / 'outbox'))
	if not outbox_dir.exists():
		return 0
	max_age_days = int(getattr(settings, 'OUTBOX_FILE_MAX_AGE_DAYS', 7))
	threshold_ts = (timezone.now() - timedelta(days=max_age_days)).timestamp()
	removed = 0
	for entry in outbox_dir.iterdir():
		try:
			if entry.is_file():
				stat = entry.stat()
				# Remove by modification time
				if stat.st_mtime < threshold_ts:
					entry.unlink(missing_ok=True)
					removed += 1
		except Exception:
			# Ignore individual file errors to avoid failing the whole task
			continue
	return removed


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=5)
def publish_order_event(self, payload: dict) -> str:
	# Публикация ивента заказа в Kafka
	publish_order_created(payload)
	return f"published:{payload.get('type')}:{payload.get('order_id')}"
