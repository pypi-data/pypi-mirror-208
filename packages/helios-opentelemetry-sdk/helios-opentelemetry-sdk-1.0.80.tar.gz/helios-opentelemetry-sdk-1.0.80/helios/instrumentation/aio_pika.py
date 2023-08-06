from logging import getLogger

from opentelemetry.propagate import extract
from opentelemetry.context import attach, detach, get_current
from opentelemetry.trace import get_tracer_provider, set_span_in_context
from opentelemetry.semconv.trace import (
    MessagingOperationValues,
)

from helios.instrumentation.base import HeliosBaseInstrumentor

_LOG = getLogger(__name__)


class HeliosAioPikaInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.aio_pika'
    INSTRUMENTOR_NAME = 'AioPikaInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider)


class AioPikaMessageContext:
    def __init__(self, message, queue=None):
        self._message = message
        self._queue = queue
        self._span = None
        self._token = None

    def __enter__(self):
        from opentelemetry.instrumentation import aio_pika
        from opentelemetry.instrumentation.aio_pika.span_builder import SpanBuilder

        headers = self._message.headers or {}
        ctx = extract(headers)
        if not ctx:
            ctx = get_current()

        tracer = get_tracer_provider().get_tracer(aio_pika.__name__)
        builder = SpanBuilder(tracer)
        builder.set_as_consumer()
        builder.set_operation(MessagingOperationValues.RECEIVE)
        builder.set_destination(self._message.exchange or self._message.routing_key)
        builder.set_channel(self._queue.channel) if self._queue else None
        builder.set_message(self._message)
        token = attach(ctx)
        try:
            span = builder.build()
        finally:
            detach(token)

        if not span or not span.is_recording():
            return

        self._span = span
        self._token = attach(set_span_in_context(self._span))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._span is not None:
            self._span.end()

        if self._token is not None:
            detach(self._token)
