"""
Binary UUID Class
"""
from abc import ABC
from uuid import UUID
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.types import TypeDecorator


class BinaryUUID(TypeDecorator, ABC):
    """Optimize UUID keys. Store as 16 bit binary, retrieve as uuid.
    inspired by:
        https://mysqlserverteam.com/storing-uuid-values-in-mysql-tables/
    """

    impl = BINARY(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """
        Process create data
        """
        try:
            return value.bytes
        except AttributeError:
            try:
                return UUID(value).bytes
            except TypeError:
                # for some reason we ended up with the byte string
                # ¯\_(ツ)_/¯
                # I'm not sure why you would do that,
                # but here you go anyway.
                return value

    def process_result_value(self, value, dialect):
        """
        Process result data
        """
        return UUID(bytes=value)
