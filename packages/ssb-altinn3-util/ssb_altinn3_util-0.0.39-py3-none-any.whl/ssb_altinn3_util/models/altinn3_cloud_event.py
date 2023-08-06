import os
from pydantic import BaseModel, validator, root_validator
from typing import Optional


class Altinn3CloudEvent(BaseModel):
    alternativesubject: Optional[str]
    data: Optional[str]
    datacontenttype: Optional[str]
    id: str
    source: str
    specversion: str
    subject: Optional[str]
    time: Optional[str]
    type: str

    @validator("source")
    def validate_event_source(cls, v: str):
        expected: str = os.getenv("APPROVED_EVENT_SOURCE_URL")
        if not expected:
            raise ValueError(
                "Environment variable 'APPROVED_EVENT_SOURCE_URL' not found!"
            )
        options = expected.split(",")

        for option in options:
            if v.startswith(option):
                return v

        raise ValueError(
            f"Provided event source '{v}' did not match expected source '{expected}'"
        )

    @root_validator
    def validate_optionals(cls, values):
        t = values.get("type")
        if t == "platform.events.validatesubscription":
            return values

        if not values.get("time"):
            raise ValueError(
                "Field 'time' must have a value for all non-validation events."
            )

        if not values.get("subject"):
            raise ValueError(
                "Field 'subject' must have a value for all non-validation events."
            )

        if not values.get("alternativesubject"):
            raise ValueError(
                "Field 'alternativesubject' must have a value for all non-validation events."
            )

        return values
