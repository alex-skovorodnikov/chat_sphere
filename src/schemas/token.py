from enum import Enum

from pydantic import BaseModel

TOKEN_TYPE_FIELD = 'type'


class TokenType(str, Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = 'Bearer'
