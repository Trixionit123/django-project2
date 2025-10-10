import json
from typing import Any, Dict
from confluent_kafka import Producer
from django.conf import settings


_producer: Producer | None = None


def get_kafka_producer() -> Producer:
	global _producer
	if _producer is None:
		config = {
			'bootstrap.servers': settings.KAFKA_BROKER_URL,
			'enable.idempotence': True,
			'retries': 5,
		}
		_producer = Producer(config)
	return _producer


def publish_order_created(event: Dict[str, Any]) -> None:
	producer = get_kafka_producer()
	producer.produce(
		topic=settings.KAFKA_ORDERS_TOPIC,
		value=json.dumps(event, ensure_ascii=False).encode('utf-8'),
	)
	producer.flush()


