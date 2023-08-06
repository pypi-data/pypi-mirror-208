import os
import time

from helios.defaults import DEFAULT_HS_API_ENDPOINT
from logging import LogRecord
from opentelemetry.trace import INVALID_SPAN, INVALID_SPAN_CONTEXT, Span
from typing import Optional, Tuple

HS_API_ENDPOINT = os.environ.get('HS_API_ENDPOINT') or DEFAULT_HS_API_ENDPOINT


class Configurations:
    STEP_FUNCTION_MODE = False


def encode_id_as_hex_string(id: int, length: int = 16) -> str:
    return id.to_bytes(length=length, byteorder="big", signed=False).hex()


def get_trace_vis_url(trace_id, source, span_id='') -> str:
    url = f'{HS_API_ENDPOINT}?actionTraceId={trace_id}'
    if bool(source):
        url += f'&source={source}'

    if bool(span_id):
        url += f'&spanId={span_id}'

    current_timestamp = int(round(time.time() * 1000))
    url += f'&timestamp={current_timestamp}'

    return url


def extract_span_from_exc_info(exc_info: Optional[Tuple]) -> Optional[Span]:
    if type(exc_info) is tuple:
        for item in exc_info:
            if isinstance(item, Exception) and hasattr(item, 'span'):
                return getattr(item, 'span')

    return None


def inject_span_context_to_log_record(log_record: LogRecord, span: Optional[Span]) -> None:
    if span is None or span == INVALID_SPAN:
        return

    span_context = span.get_span_context()

    if span_context is None or span_context == INVALID_SPAN_CONTEXT:
        return

    setattr(log_record, 'otelSpanID', encode_id_as_hex_string(span_context.span_id, 8))
    setattr(log_record, 'otelTraceID', encode_id_as_hex_string(span_context.trace_id))


def inject_span_to_exception(exception: Optional[Exception], span: Optional[Span]) -> Optional[Exception]:
    if exception is not None:
        setattr(exception, 'span', span)

    return exception


def lambda_step_function_mode():
    return Configurations.STEP_FUNCTION_MODE
