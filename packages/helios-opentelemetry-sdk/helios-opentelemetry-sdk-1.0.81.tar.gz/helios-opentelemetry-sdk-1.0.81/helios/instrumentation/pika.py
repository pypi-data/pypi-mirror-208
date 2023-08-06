import json
from logging import getLogger

from opentelemetry.context import attach, detach, get_current
from opentelemetry.propagate import extract
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Span, SpanKind, get_tracer_provider, set_span_in_context

from helios.instrumentation.base import HeliosBaseInstrumentor

_LOG = getLogger(__name__)


class PikaSpanAttributes:
    MESSAGING_PAYLOAD = 'messaging.payload'
    RABBIT_MQ_HEADERS = 'rabbitmq.headers'
    RECEIVE_NAME = 'rabbitmq.receiveMessage'
    SEND_NAME = 'rabbitmq.sendMessage'


class HeliosPikaInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.pika'
    INSTRUMENTOR_NAME = 'PikaInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider, publish_hook=self.publish_hook,
                                           consume_hook=self.consume_hook)

    def publish_hook(self, span: Span, body: bytes, properties):
        try:
            span.update_name(PikaSpanAttributes.SEND_NAME)
            HeliosPikaInstrumentor.set_common_attributes(span, body, properties.headers)
            span.set_attribute('span.operation', PikaSpanAttributes.SEND_NAME)
        except Exception as error:
            _LOG.debug('pika publish instrumentation error: %s.', error)

    def consume_hook(self, span: Span, body: bytes, properties):
        HeliosPikaInstrumentor.adjust_span_properties(span, body, properties.headers)

    @staticmethod
    def adjust_span_properties(span: Span, body: bytes, headers):
        try:
            span.update_name(PikaSpanAttributes.RECEIVE_NAME)
            HeliosPikaInstrumentor.set_common_attributes(span, body, headers)
            span.set_attribute('span.operation', PikaSpanAttributes.RECEIVE_NAME)
        except Exception as error:
            _LOG.debug('pika consume instrumentation error: %s.', error)

    @staticmethod
    def set_common_attributes(span: Span, body: bytes, headers):
        string_body = None
        if type(body) == str:
            string_body = body
        elif type(body) == bytes:
            string_body = body.decode()
        else:
            _LOG.debug('Cannot parse body')
        span.set_attribute(PikaSpanAttributes.MESSAGING_PAYLOAD, string_body) if string_body else None
        span.set_attribute(PikaSpanAttributes.RABBIT_MQ_HEADERS, json.dumps(headers))
        messaging_url = span.attributes.get(SpanAttributes.NET_PEER_NAME, None)
        span.set_attribute(SpanAttributes.MESSAGING_URL, messaging_url) if messaging_url else None
        routing_key = span.attributes['span.operation'].split()[0]
        span.set_attribute(SpanAttributes.MESSAGING_RABBITMQ_ROUTING_KEY, routing_key) if routing_key else None
        span.set_attribute(SpanAttributes.MESSAGING_SYSTEM, 'rabbitmq')
        span.set_attribute(SpanAttributes.MESSAGING_DESTINATION, 'amq.topic')
        span.set_attribute(SpanAttributes.MESSAGING_DESTINATION_KIND, 'topic')
        span.set_attribute(SpanAttributes.MESSAGING_PROTOCOL, 'amqp')


class RabbitMqMessageContext:
    def __init__(self, method, headers, payload):
        self._exchange = method.exchange if method else ''
        self._routing_key = method.routing_key if method else ''
        self._headers = headers
        self._payload = payload
        self._span = None
        self._token = None

    def __enter__(self):
        from opentelemetry.instrumentation.pika import pika_instrumentor
        from opentelemetry.instrumentation.pika.utils import _PikaGetter

        headers = self._headers.headers if self._headers is not None and self._headers.headers is not None else {}
        context = extract(headers, getter=_PikaGetter())

        if not context:
            context = get_current()

        tracer = get_tracer_provider().get_tracer(pika_instrumentor.__name__)
        span_name = f"{self._exchange if self._exchange else self._routing_key}"
        span = tracer.start_span(span_name, context=context, kind=SpanKind.CONSUMER)
        if not span.is_recording():
            return

        self._span = span
        self._token = attach(set_span_in_context(self._span))
        HeliosPikaInstrumentor.adjust_span_properties(self._span, self._payload, headers)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._span is not None:
            self._span.end()

        if self._token is not None:
            detach(self._token)
