from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.botocore.consts import AwsParam, AwsAttribute, AwsService


class S3Instrumentor(object):

    def __init__(self):
        pass

    def request_hook(self, span, operation_name, api_params):
        if api_params is None:
            return

        bucket = api_params.get(AwsParam.BUCKET)
        key = api_params.get(AwsParam.KEY)

        attributes = dict({
            SpanAttributes.DB_SYSTEM: AwsService.S3
        })
        if bucket:
            attributes[AwsAttribute.S3_BUCKET] = bucket
        if key:
            attributes[AwsAttribute.S3_KEY] = key

        span.set_attributes(attributes)

    def response_hook(self, span, operation_name, result):
        attributes = dict({
            SpanAttributes.DB_SYSTEM: AwsService.S3
        })
        # TODO: fix how we read the body. The code below drains it and so customers get an empty body
        # https://botocore.amazonaws.com/v1/documentation/api/latest/reference/response.html#botocore.response.StreamingBody
        body_stream = result.get(AwsParam.BODY)
        if body_stream:
            content_length = getattr(body_stream, '_content_length', None)
            if type(content_length) == int:
                attributes[SpanAttributes.MESSAGING_MESSAGE_PAYLOAD_SIZE_BYTES] = content_length
            elif type(content_length) == str and content_length.isdigit():
                attributes[SpanAttributes.MESSAGING_MESSAGE_PAYLOAD_SIZE_BYTES] = int(content_length)

        span.set_attributes(attributes)
