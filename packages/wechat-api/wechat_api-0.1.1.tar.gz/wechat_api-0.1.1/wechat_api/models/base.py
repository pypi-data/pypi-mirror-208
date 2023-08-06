import datetime
from typing import TypedDict, Optional

from pydantic import BaseModel


class Token(BaseModel):
    token: str
    expires_on: datetime.datetime


class TimedeltaParams(TypedDict):
    days: Optional[int]
    weeks: Optional[int]
    hours: Optional[int]
    minutes: Optional[int]
    seconds: Optional[int]
    microseconds: Optional[int]
    milliseconds: Optional[int]
