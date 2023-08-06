from wrapt import wrap_function_wrapper

from helios.base.span_attributes import SpanAttributes
from helios.instrumentation.base import HeliosBaseInstrumentor
from opentelemetry import context, propagate, trace
from opentelemetry.trace import SpanKind
from opentelemetry.semconv.trace import MessagingOperationValues


class HeliosConfluentKafkaInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.confluent_kafka'
    INSTRUMENTOR_NAME = 'ConfluentKafkaInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        if self.get_instrumentor() is None:
            return

        wrap_function_wrapper(
            self.MODULE_NAME, 'ConfluentKafkaInstrumentor.instrumentation_dependencies', instrumentation_dependencies
        )
        wrap_function_wrapper(self.MODULE_NAME, 'ConfluentKafkaInstrumentor.wrap_poll', wrap_poll)
        wrap_function_wrapper(self.MODULE_NAME, 'ConfluentKafkaInstrumentor.wrap_produce', wrap_produce)
        self.get_instrumentor().instrument(tracer_provider=tracer_provider)


def instrumentation_dependencies(wrapped, instance, args, kwargs):
    return ('confluent-kafka >= 1.8.2, <= 2.1.1',)


def wrap_poll(wrapped, instance, args, kwargs):
    from opentelemetry.instrumentation.confluent_kafka.utils import _kafka_getter, _enrich_span

    func, instance, tracer, args, kwargs = args

    if instance._current_consume_span:
        context.detach(instance._current_context_token)
        instance._current_context_token = None
        instance._current_consume_span.end()
        instance._current_consume_span = None

    record = func(*args, **kwargs)
    if record is None:
        return record
    ctx = propagate.extract(record.headers(), getter=_kafka_getter)

    with tracer.start_as_current_span(
            "recv", end_on_exit=True, kind=trace.SpanKind.CONSUMER, context=ctx
    ) as span:
        span.set_attribute(SpanAttributes.MESSAGING_PAYLOAD, record.value().decode())
        instance._current_consume_span = tracer.start_span(
            name=f"{record.topic()} process",
            kind=SpanKind.CONSUMER,
        )

        _enrich_span(
            instance._current_consume_span,
            record.topic(),
            record.partition(),
            record.offset(),
            operation=MessagingOperationValues.PROCESS,
        )
    instance._current_context_token = context.attach(
        trace.set_span_in_context(instance._current_consume_span)
    )

    return record


def wrap_produce(wrapped, instance, args, kwargs):
    from opentelemetry.instrumentation.confluent_kafka import _get_span_name
    from opentelemetry.instrumentation.confluent_kafka import KafkaPropertiesExtractor
    from opentelemetry.instrumentation.confluent_kafka.utils import _kafka_setter, _enrich_span

    func, instance, tracer, args, kwargs = args

    topic = kwargs.get("topic")
    if not topic:
        topic = args[0]

    span_name = _get_span_name("send", topic)
    with tracer.start_as_current_span(
            name=span_name, kind=trace.SpanKind.PRODUCER
    ) as span:
        headers = KafkaPropertiesExtractor.extract_produce_headers(
            args, kwargs
        )
        if headers is None:
            headers = []
            kwargs["headers"] = headers

        topic = KafkaPropertiesExtractor.extract_produce_topic(args)
        _enrich_span(
            span,
            topic,
            operation=MessagingOperationValues.RECEIVE,
        )  # Replace
        span.set_attribute(SpanAttributes.MESSAGING_PAYLOAD, kwargs['value'].decode())
        propagate.inject(
            headers,
            setter=_kafka_setter,
        )
        return func(*args, **kwargs)
