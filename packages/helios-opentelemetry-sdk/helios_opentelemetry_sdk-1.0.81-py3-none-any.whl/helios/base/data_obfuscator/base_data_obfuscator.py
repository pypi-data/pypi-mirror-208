import hashlib
import hmac
from dataclasses import dataclass
from json import JSONDecodeError, dumps, loads
from logging import getLogger
from typing import Any, List, Optional, Tuple, Union

from jsonpath_ng.ext import parse
from jsonpath_ng.jsonpath import DatumInContext, JSONPath
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.util.types import AttributeValue, Attributes

from helios.base.span_attributes import SpanAttributes

_LOG = getLogger(__name__)
DATA_TO_OBFUSCATE = [
    SpanAttributes.DB_QUERY_RESULT,
    SpanAttributes.DB_STATEMENT,
    SpanAttributes.HTTP_REQUEST_BODY,
    SpanAttributes.HTTP_RESPONSE_BODY,
    SpanAttributes.MESSAGING_PAYLOAD,
]
HTTP_HEADERS_ATTRIBUTE_KEYS = [SpanAttributes.HTTP_REQUEST_HEADERS, SpanAttributes.HTTP_RESPONSE_HEADERS]
IS_DATA_OBFUSCATED_KEY = 'hs_data_obfuscated'

ExpectedValueType = Optional[Union[str, float, int, bool]]
Mode = Optional[str]
Rules = Optional[List[Union[Tuple[str, ExpectedValueType], str]]]


@dataclass
class DataObfuscatorConfiguration:
    hmac_key: str
    mode: Mode
    rules: Rules
    http_headers_mode: Mode
    http_headers_rules: Optional[List[str]]


class BaseDataObfuscator:
    _hmac_key: str
    _mode: Mode
    _global_rules: List[Tuple[JSONPath, ExpectedValueType]]
    _local_rules: List[JSONPath]
    _http_headers_mode: Mode
    _http_headers_rules: List[str]

    def __init__(self, data_obfuscator_configuration: DataObfuscatorConfiguration):
        self._hmac_key = data_obfuscator_configuration.hmac_key
        self._mode = data_obfuscator_configuration.mode
        self._http_headers_mode = data_obfuscator_configuration.http_headers_mode
        global_rules: List[Tuple[str, ExpectedValueType]] = []
        local_rules: List[str] = []
        http_headers_rules: List[str] = []

        if data_obfuscator_configuration.rules is not None:
            for rule in data_obfuscator_configuration.rules:
                if BaseDataObfuscator._is_global_rule(rule):
                    global_rules.append(rule)
                elif isinstance(rule, str):
                    local_rules.append(rule)
                else:
                    _LOG.debug(f'Ignoring invalid rule {rule}.')

        if data_obfuscator_configuration.http_headers_rules is not None:
            for http_header_key in data_obfuscator_configuration.http_headers_rules:
                http_headers_rules.append(http_header_key.lower())

        _LOG.debug(f'Data obfuscation mode: {self._mode}, global rules: {global_rules}, local rules: {local_rules}.')
        _LOG.debug(f'HTTP headers obfuscation mode: {self._http_headers_mode}, rules: {http_headers_rules}.')
        self._global_rules = BaseDataObfuscator._parse_global_rules(global_rules)
        self._local_rules = BaseDataObfuscator._parse_local_rules(local_rules)
        self._http_headers_rules = http_headers_rules

    def obfuscate_data(self, attributes: Attributes, span_id: str) -> None:
        for datum_to_obfuscate in DATA_TO_OBFUSCATE:
            if datum_to_obfuscate in attributes:
                value = attributes[datum_to_obfuscate]
                # noinspection PyUnresolvedReferences
                attributes[datum_to_obfuscate] = self._obfuscate_datum(value, span_id)

        self._obfuscate_http_headers(attributes)

    @staticmethod
    def hash(key: str, msg: Any, length: int = 8) -> str:
        return hmac.new(key.encode(), str(msg).encode(), hashlib.sha256).hexdigest()[:length]

    @staticmethod
    def _is_global_rule(rule: Tuple[str, ExpectedValueType]) -> bool:
        if isinstance(rule, (list, tuple)) and len(rule) == 2:
            path_expression, expected_value = rule
            is_valid_path_expression = isinstance(path_expression, str)
            is_valid_expected_value = expected_value is None or isinstance(expected_value, (str, float, int, bool))
            return is_valid_path_expression and is_valid_expected_value

        return False

    @staticmethod
    def _parse_global_rules(
            global_rules: List[Tuple[str, ExpectedValueType]]
    ) -> List[Tuple[JSONPath, ExpectedValueType]]:
        parsed_global_rules: List[Tuple[JSONPath, ExpectedValueType]] = []

        for path_expression, expected_value in global_rules:
            try:
                parsed_path_expression = parse(path_expression)
                _LOG.debug(f'Added global rule: {path_expression}')
            except Exception as exception:
                _LOG.debug(f'Ignoring invalid path expression {path_expression}: {exception}')
                parsed_path_expression = None

            if parsed_path_expression is not None:
                parsed_global_rules.append((parsed_path_expression, expected_value))

        return parsed_global_rules

    @staticmethod
    def _parse_local_rules(local_rules: List[str]) -> List[JSONPath]:
        parsed_local_rules: List[JSONPath] = []

        for path_expression in local_rules:
            try:
                parsed_local_rules.append(parse(path_expression))
                _LOG.debug(f'Added local rule: {path_expression}')
            except Exception as exception:
                _LOG.debug(f'Ignoring invalid path expression {path_expression}: {exception}')

        return parsed_local_rules

    @staticmethod
    def inject_data_obfuscation_flag(span: ReadableSpan) -> None:
        try:
            # noinspection PyProtectedMember, PyUnresolvedReferences
            span.resource.attributes._dict[IS_DATA_OBFUSCATED_KEY] = True
        except Exception as exception:
            _LOG.debug('Cannot inject data obfuscation flag.', exception)

    def _obfuscate_datum(self, value: AttributeValue, span_id: str) -> AttributeValue:
        _LOG.debug(f'global rules for span_id {span_id} are {self._global_rules}')
        _LOG.debug(f'local rules for span_id {span_id} are {self._local_rules}')
        _LOG.debug(f'mode for span_id {span_id} are {self._mode}')
        if isinstance(value, str):
            dict_or_list: Optional[Union[dict, list]]

            try:
                dict_or_list = loads(value)
            except JSONDecodeError:
                dict_or_list = None

            if dict_or_list is not None:
                if self._mode == 'allowlist':
                    return self._obfuscate_dict_or_list_in_allowlist_mode(value, dict_or_list)
                elif self._mode is None or self._mode == 'blocklist':
                    return self._obfuscate_dict_or_list_in_blocklist_mode(dict_or_list, span_id)
                else:
                    raise ValueError(f'Unsupported mode {self._mode}.')

        return self._obfuscate_primitive(value)

    def _obfuscate_dict_or_list_in_allowlist_mode(self, value: str, dict_or_list: Union[dict, list]) -> str:
        if self._match_global_rules(dict_or_list):
            return value
        else:
            nodes = self._extract_nodes(dict_or_list)
            obfuscated_dict_or_list = self._obfuscate_object(dict_or_list)
            self._insert_nodes(obfuscated_dict_or_list, nodes, False)
            return dumps(obfuscated_dict_or_list)

    def _obfuscate_dict_or_list_in_blocklist_mode(self, dict_or_list: Union[dict, list], span_id: str) -> str:
        if self._match_global_rules(dict_or_list):
            obfuscated_dict_or_list = self._obfuscate_object(dict_or_list)
            return dumps(obfuscated_dict_or_list)
        else:
            nodes = self._extract_nodes(dict_or_list)
            _LOG.debug(f'number of nodes to be obfuscated: {len(nodes)} for span_id: {span_id}')
            self._insert_nodes(dict_or_list, nodes, True)
            return dumps(dict_or_list)

    def _match_global_rules(self, dict_or_list: Union[dict, list]) -> bool:
        for parsed_path_expression, expected_value in self._global_rules:
            try:
                nodes = parsed_path_expression.find(dict_or_list)
            except Exception as exception:
                _LOG.debug(f'Cannot extract nodes of parsed path expression {parsed_path_expression}.', exception)
                nodes = []

            for node in nodes:
                if node.value == expected_value:
                    return True

        return False

    def _extract_nodes(self, dict_or_list: Union[dict, list]) -> List[DatumInContext]:
        nodes: List[DatumInContext] = []

        for parsed_path_expression in self._local_rules:
            try:
                nodes.extend(parsed_path_expression.find(dict_or_list))
            except Exception as exception:
                _LOG.debug(f'Cannot extract nodes of parsed path expression {parsed_path_expression}.', exception)

        return nodes

    def _insert_nodes(
            self, dict_or_list: Union[dict, list], nodes: List[DatumInContext], obfuscate_values: bool
    ) -> None:
        for node in nodes:
            try:
                node.full_path.update(
                    dict_or_list, self._obfuscate_object(node.value) if obfuscate_values else node.value
                )
            except Exception as exception:
                _LOG.debug(f'Cannot insert node {node} into dictionary or list.', exception)

    def _obfuscate_object(self, object_to_obfuscate: Any) -> Any:
        if isinstance(object_to_obfuscate, dict):
            return {key: self._obfuscate_object(value) for key, value in object_to_obfuscate.items()}
        elif isinstance(object_to_obfuscate, list):
            return [self._obfuscate_object(value) for value in object_to_obfuscate]
        else:
            return self._obfuscate_primitive(object_to_obfuscate)

    def _obfuscate_primitive(self, primitive: Any) -> Any:
        if primitive is None or isinstance(primitive, bool):
            return primitive

        try:
            return BaseDataObfuscator.hash(self._hmac_key, primitive)
        except Exception as exception:
            _LOG.debug(f'Cannot hash primitive {primitive}.', exception)
            return '********'

    def _obfuscate_http_headers(self, attributes: Attributes) -> None:
        if self._skip_http_headers_obfuscation():
            return

        for http_headers_attribute_key in HTTP_HEADERS_ATTRIBUTE_KEYS:
            http_headers: Optional[dict]

            try:
                http_headers = loads(attributes[http_headers_attribute_key])
            except (JSONDecodeError, KeyError):
                http_headers = None

            if http_headers is not None:
                for http_header_key in http_headers.keys():
                    http_header_key_in_lowercase = http_header_key.lower()

                    if self._obfuscate_http_header(http_header_key_in_lowercase):
                        http_header_value = http_headers[http_header_key]
                        http_headers[http_header_key] = self._obfuscate_primitive(http_header_value)

                # noinspection PyUnresolvedReferences
                attributes[http_headers_attribute_key] = dumps(http_headers)

    def _skip_http_headers_obfuscation(self) -> bool:
        if self._http_headers_mode is None or self._http_headers_mode == 'blocklist':
            if len(self._http_headers_rules) == 0:
                return True

        return False

    def _obfuscate_http_header(self, http_header_key_in_lowercase: str) -> bool:
        if self._http_headers_mode == 'allowlist':
            if http_header_key_in_lowercase not in self._http_headers_rules:
                return True

        if self._http_headers_mode is None or self._http_headers_mode == 'blocklist':
            if http_header_key_in_lowercase in self._http_headers_rules:
                return True

        return False
