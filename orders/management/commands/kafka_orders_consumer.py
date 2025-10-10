from django.core.management.base import BaseCommand
from django.conf import settings
from confluent_kafka import Consumer
import json


class Command(BaseCommand):
	help = 'Kafka consumer for orders topic'

	def handle(self, *args, **options):
		consumer = Consumer({
			'bootstrap.servers': settings.KAFKA_BROKER_URL,
			'group.id': 'orders-consumer-group',
			'auto.offset.reset': 'earliest',
		})
		consumer.subscribe([settings.KAFKA_ORDERS_TOPIC])
		self.stdout.write(self.style.SUCCESS('Orders consumer started'))
		try:
			while True:
				msg = consumer.poll(1.0)
				if msg is None:
					continue
				if msg.error():
					self.stderr.write(str(msg.error()))
					continue
				data = json.loads(msg.value().decode('utf-8'))
				self.stdout.write(f"event received: {data}")
		finally:
			consumer.close()


