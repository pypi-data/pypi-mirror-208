"""
Model Utils
"""
import json
from abc import ABC

from sqlalchemy import TypeDecorator, Text, Integer

from .func_date import convert_date_to_timestamp, convert_timestamp_to_date


class JsonEncodeDict(TypeDecorator, ABC):
    """
    Enables JSON storage by encoding and decoding on the fly.
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """
        :param value:
        :param dialect:
        :return:
        """
        return '{}' if value is None else json.dumps(value)

    def process_result_value(self, value, dialect):
        """
        :param value:
        :param dialect:
        :return:
        """
        return {} if value is None else json.loads(value)


class TimestampField(TypeDecorator, ABC):
    """
    Enables JSON storage by encoding and decoding on the fly.
    """
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """
        :param value:
        :param dialect:
        :return:
        """
        return convert_date_to_timestamp(value)

    def process_result_value(self, value, dialect):
        """
        :param value:
        :param dialect:
        :return:
        """
        return convert_timestamp_to_date(value)


def generic_get_serialize_data(schema_object, query):
    """
    Get Serialize data
    :param schema_object:
    :param query:
    :return:
    """
    return schema_object.dump(query)
