from opentelemetry.semconv.trace import SpanAttributes as OpenTelemetrySpanAttributes


class SpanAttributes(OpenTelemetrySpanAttributes):
    DB_QUERY_RESULT = 'db.query_result'
    HTTP_REQUEST_BODY = 'http.request.body'
    HTTP_REQUEST_HEADERS = 'http.request.headers'
    HTTP_RESPONSE_BODY = 'http.response.body'
    HTTP_RESPONSE_HEADERS = 'http.response.headers'
    MESSAGING_PAYLOAD = 'messaging.payload'
    RPC_REQUEST_BODY = 'rpc.request.body'
    RPC_RESPONSE_BODY = 'rpc.response.body'
