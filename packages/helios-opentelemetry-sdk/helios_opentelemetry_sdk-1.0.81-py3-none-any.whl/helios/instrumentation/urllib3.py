from logging import getLogger
from typing import Dict
from opentelemetry.trace import Span
from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor
from opentelemetry.instrumentation.requests import _SUPPRESS_HTTP_INSTRUMENTATION_KEY
from opentelemetry import context

_LOG = getLogger(__name__)


class HeliosUrllib3Instrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.urllib3'
    INSTRUMENTOR_NAME = 'URLLib3Instrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(
            tracer_provider=tracer_provider, response_hook=self.response_hook, request_hook=self.request_hook)

    def is_instrumented_by_requests(self):
        return context.get_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY)

    def is_url_ignored(self, span: Span):
        url = span.attributes.get(SpanAttributes.HTTP_URL)
        if url and any(hostname in url for hostname in self.ignored_hostnames):
            return True
        return False

    def request_hook(self, span: Span, connection_pool, headers: Dict, body: str) -> None:
        try:
            if self.is_instrumented_by_requests():
                return

            if self.is_url_ignored(span):
                return

            HeliosUrllib3Instrumentor.base_request_hook(span, headers, body)
        except Exception as error:
            _LOG.debug('urllib3 request instrumentation error: %s.', error)

    def response_hook(self, span: Span, connection_pool, response) -> None:
        try:
            # connection_pool is an object of type urllib3.connectionpool.HTTPConnectionPool
            # response is an object of type urllib3.response.HTTPResponse
            if self.is_instrumented_by_requests():
                return

            if self.is_url_ignored(span):
                return

            if hasattr(response, 'headers'):
                response_headers = response.headers
            else:
                response_headers = response.getHeaders()
            response_payload = response.data
            HeliosUrllib3Instrumentor.base_response_hook(span, response_headers, response_payload)
        except Exception as error:
            _LOG.debug('urllib3 response instrumentation error: %s.', error)
