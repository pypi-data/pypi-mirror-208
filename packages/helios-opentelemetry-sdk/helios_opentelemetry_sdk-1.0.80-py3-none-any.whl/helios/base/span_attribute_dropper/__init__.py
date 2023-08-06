from logging import getLogger
from opentelemetry.sdk.trace import ReadableSpan
from helios.base.span_attributes import SpanAttributes
from helios.instrumentation.botocore.consts import AwsAttribute

_LOG = getLogger(__name__)
ATTRIBUTES_TO_DROP = [
    SpanAttributes.DB_QUERY_RESULT,
    SpanAttributes.DB_STATEMENT,
    SpanAttributes.HTTP_REQUEST_BODY,
    SpanAttributes.HTTP_RESPONSE_BODY,
    SpanAttributes.MESSAGING_PAYLOAD,
    SpanAttributes.HTTP_REQUEST_HEADERS,
    SpanAttributes.HTTP_RESPONSE_HEADERS,
]

AWS_ATTRIBUTES_TO_DROP = [
    AwsAttribute.SES_BCC_RECIPIENTS,
    AwsAttribute.SES_CC_RECIPIENTS,
    AwsAttribute.SES_HTML_BODY,
    AwsAttribute.SES_RECIPIENTS,
    AwsAttribute.SES_SENDER,
    AwsAttribute.SES_SUBJECT,
    AwsAttribute.SES_TEXT_BODY,
    AwsAttribute.SQS_MESSAGE_ATTRIBUTES,
]


class SpanAttributeDropper:
    def __init__(self):
        _LOG.debug('Metadata only mode enabled - no payloads or extra data will be collected')

    def drop_non_metadata_attributes(self, span: ReadableSpan) -> None:
        attributes = span._attributes
        for attribute in [*ATTRIBUTES_TO_DROP, *AWS_ATTRIBUTES_TO_DROP]:
            attributes.pop(attribute, None)
