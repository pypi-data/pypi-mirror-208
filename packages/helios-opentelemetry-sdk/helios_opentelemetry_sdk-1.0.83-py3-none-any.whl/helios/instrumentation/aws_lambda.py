import json
import os
from logging import getLogger

from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import INVALID_SPAN, SpanKind, set_span_in_context
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.propagate import extract, inject
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry import context, trace

from helios.instrumentation import HeliosBaseInstrumentor
from helios.utils import lambda_step_function_mode

_LOG = getLogger(__name__)

MODULE_NAME = 'opentelemetry.instrumentation.aws_lambda'
STEP_FUNCTION_CONTEXT = 'step_function_context'
coldstart = True


def _custom_event_context_extractor(event):
    ctx = None
    if 'detail-type' in event:
        # Eventbridge case
        if 'detail' in event and 'headers' in event['detail']:
            headers = event['detail']['headers']
        if headers is None and 'headers' in event:
            headers = event['headers']
        if headers is not None:
            ctx = extract(headers)

    if 'headers' in event:
        ctx = extract(event['headers'])

    if lambda_step_function_mode() and STEP_FUNCTION_CONTEXT in event:
        ctx = extract(event[STEP_FUNCTION_CONTEXT])

    if ctx is not None and trace.get_current_span(ctx) != INVALID_SPAN:
        return ctx

    return context.Context()


def extract_lambda_module_and_function():
    lambda_handler = os.environ.get('ORIG_HANDLER', os.environ.get('_HANDLER'))
    wrapped_module_name, wrapped_function_name = lambda_handler.rsplit('.', 1)
    return wrapped_module_name, wrapped_function_name


def _flush_timeout():
    flush_timeout_env = os.environ.get(
        'OTEL_INSTRUMENTATION_AWS_LAMBDA_FLUSH_TIMEOUT', None
    )
    flush_timeout = 1000
    try:
        if flush_timeout_env is not None:
            flush_timeout = int(flush_timeout_env)
    except ValueError:
        pass

    return flush_timeout


def wrap_lambda_function(original_handler, tracer_provider, meter_provider):
    wrapped_module_name, wrapped_function_name = extract_lambda_module_and_function()
    flush_timeout = _flush_timeout()

    def wrapped_lambda(*args, **kwargs):
        orig_handler_name = '.'.join([wrapped_module_name, wrapped_function_name])
        lambda_event = args[0]
        parent_context = _custom_event_context_extractor(lambda_event)

        try:
            if lambda_event['Records'][0]['eventSource'] in {
                'aws:sqs',
                'aws:s3',
                'aws:sns',
                'aws:dynamodb',
            }:
                span_kind = SpanKind.CONSUMER
            else:
                span_kind = SpanKind.SERVER
        except (IndexError, KeyError, TypeError):
            span_kind = SpanKind.SERVER

        tracer = tracer_provider.get_tracer(MODULE_NAME)

        with tracer.start_as_current_span(
                name=orig_handler_name,
                context=parent_context,
                kind=span_kind,
        ) as span:
            global coldstart
            if coldstart:
                span.set_attribute(SpanAttributes.FAAS_COLDSTART, True)
                coldstart = False
            else:
                span.set_attribute(SpanAttributes.FAAS_COLDSTART, False)

            if span.is_recording():
                lambda_context = args[1]
                span.set_attribute(
                    ResourceAttributes.FAAS_ID,
                    lambda_context.invoked_function_arn,
                )
                span.set_attribute(
                    SpanAttributes.FAAS_EXECUTION,
                    lambda_context.aws_request_id,
                )
                span.set_attribute(
                    'aws.lambda.log_group_name',
                    lambda_context.log_group_name,
                )
                span.set_attribute(
                    'aws.lambda.log_stream_name',
                    lambda_context.log_stream_name,
                )
                HeliosBaseInstrumentor.set_payload_attribute(span, 'faas.event', json.dumps(lambda_event))

            result = None
            try:
                result = original_handler(*args, **kwargs)
            except Exception as err:
                span.set_status(Status(status_code=StatusCode.ERROR, description=str(err)))
                raise err
            if type(result) == dict:
                http_status_code = result.get('statusCode') or result.get('StatusCode')
                if http_status_code:
                    span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, http_status_code)
                    span.set_attribute(SpanAttributes.FAAS_TRIGGER, 'http')
                    if http_status_code >= 500:
                        span.set_status(Status(status_code=StatusCode.ERROR))

                if lambda_step_function_mode():
                    result[STEP_FUNCTION_CONTEXT] = {}
                    inject(result[STEP_FUNCTION_CONTEXT], context=set_span_in_context(span))
            HeliosBaseInstrumentor.set_payload_attribute(span, 'faas.res', json.dumps(result))

        if hasattr(tracer_provider, 'force_flush'):
            try:
                tracer_provider.force_flush(flush_timeout)
            except Exception:  # pylint: disable=broad-except
                _LOG.exception("TracerProvider failed to flush traces")
        if meter_provider is not None:
            try:
                meter_provider.force_flush(flush_timeout)
            except Exception:  # pylint: disable=broad-except
                _LOG.exception("MeterProvider failed to flush traces")

        return result

    return wrapped_lambda
