import os
from enum import Enum, EnumMeta

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")


class BaseMetadataEnum(EnumMeta):
    def __contains__(self, other):
        try:
            self(other)
        except ValueError:
            return False
        else:
            return True


class BaseEnum(str, Enum, metaclass=BaseMetadataEnum):
    """Base enum class."""


class PythonVersion(BaseEnum):
    THREE_DOT_SEVEN = "3.7"
    THREE_DOT_EIGHT = "3.8"
    THREE_DOT_NINE = "3.9"
    THREE_DOT_TEN = "3.10"
    THREE_DOT_ELEVEN = "3.11"


class Database(BaseEnum):
    POSTGRES = "Postgres"
    MYSQL = "MySQL"
