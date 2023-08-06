import json
from uuid import UUID
from enum import Enum
from dataclasses import asdict, is_dataclass
from datetime import date, datetime

from pydantic import BaseModel


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, BaseModel):
            return o.dict(by_alias=True, exclude_unset=True)
        return super().default(o)


def try_str_to_float(text: str) -> any:
    try:
        return float(text)
    except ValueError:
        return text
