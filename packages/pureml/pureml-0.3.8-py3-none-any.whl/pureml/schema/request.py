from pydantic import BaseModel
from enum import Enum


class ContentTypeHeader(Enum):
    APP_FORM_URL_ENCODED = "application/x-www-form-urlencoded"
    APP_JSON = "application/json"
    ALL = "*/*"
    MULTIPART_FORMDATA = "multipart/form-data"


class AcceptHeader(Enum):
    APP_JSON = "application/json"
