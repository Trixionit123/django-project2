import time
import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse


logger = logging.getLogger(__name__)


class RequestTimingMiddleware:
	def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
		self.get_response = get_response

	def __call__(self, request: HttpRequest) -> HttpResponse:
		start = time.perf_counter()
		response = self.get_response(request)
		duration_ms = (time.perf_counter() - start) * 1000.0
		logger.info("request_time url=%s method=%s duration_ms=%.2f", request.path, request.method, duration_ms)
		return response





