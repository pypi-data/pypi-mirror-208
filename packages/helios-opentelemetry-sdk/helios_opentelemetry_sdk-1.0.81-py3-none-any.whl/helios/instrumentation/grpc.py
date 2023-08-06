from logging import getLogger
from re import Pattern, search, compile

from helios.base.span_attributes import SpanAttributes
from helios.instrumentation.base import HeliosBaseInstrumentor
from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor

_LOG = getLogger(__name__)


def full_method_regex(regex: Pattern):
    """Returns a filter function that return True if
    request's gRPC method name matches the given regex pattern.

    Args:
        regex (Pattern): method regex to match

    Returns:
        A filter function that returns True if request's gRPC method
        name matches a regex
    """

    def filter_fn(metadata):
        from helios.grpc_instrumentation.filters import _full_method
        method = _full_method(metadata)
        return bool(search(regex, method))

    return filter_fn


def request_hook(span, request) -> None:
    try:
        if span is None:
            return

        HeliosBaseInstrumentor.set_payload_attribute(
            span, SpanAttributes.RPC_REQUEST_BODY, str(request))

    except Exception as error:
        _LOG.debug('grpc request instrumentation error: %s.', error)


def response_hook(span, response) -> None:
    try:
        if span is None:
            return

        HeliosBaseInstrumentor.set_payload_attribute(
            span, SpanAttributes.RPC_RESPONSE_BODY, str(response))

    except Exception as error:
        _LOG.debug('grpc response instrumentation error: %s.', error)


def get_filter(excluded_grpc_methods: str):
    if excluded_grpc_methods is None:
        return
    excluded_methods = excluded_grpc_methods.split(',')
    regex_pattern = compile("|".join(excluded_methods))
    return full_method_regex(regex_pattern)


class HeliosGrpcClientInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'helios.grpc_instrumentation'
    INSTRUMENTOR_NAME = 'GrpcInstrumentorClient'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        instrumentor = self.get_instrumentor()
        if instrumentor is None:
            return

        excluded_grpc_methods = kwargs.get('excluded_grpc_methods')
        filter_ = get_filter(excluded_grpc_methods)
        instrumentor._filter = filter_
        instrumentor.instrument(
            tracer_provider=tracer_provider,
            request_hook=request_hook,
            response_hook=response_hook)


class HeliosGrpcServerInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'helios.grpc_instrumentation'
    INSTRUMENTOR_NAME = 'GrpcInstrumentorServer'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        instrumentor = self.get_instrumentor()
        if instrumentor is None:
            return

        excluded_grpc_methods = kwargs.get('excluded_grpc_methods')
        filter_ = get_filter(excluded_grpc_methods)
        instrumentor._filter = filter_
        instrumentor.instrument(tracer_provider=tracer_provider)


class HeliosGrpcAioClientInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'helios.grpc_instrumentation'
    INSTRUMENTOR_NAME = 'GrpcAioInstrumentorClient'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        instrumentor = self.get_instrumentor()
        if instrumentor is None:
            return

        excluded_grpc_methods = kwargs.get('excluded_grpc_methods')
        filter_ = get_filter(excluded_grpc_methods)
        instrumentor._filter = filter_
        instrumentor.instrument(
            tracer_provider=tracer_provider,
            request_hook=request_hook,
            response_hook=response_hook)


class HeliosGrpcAioServerInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'helios.grpc_instrumentation'
    INSTRUMENTOR_NAME = 'GrpcAioInstrumentorServer'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None, **kwargs):
        instrumentor = self.get_instrumentor()
        if instrumentor is None:
            return

        excluded_grpc_methods = kwargs.get('excluded_grpc_methods')
        filter_ = get_filter(excluded_grpc_methods)
        instrumentor._filter = filter_
        instrumentor.instrument(tracer_provider=tracer_provider)
