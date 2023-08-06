from typing import Optional
from pydantic import BaseModel, ValidationError, validator


class FormAccessRequest(BaseModel):
    """
    Request model used when requesting a change in form access privileges for a group.
    Possible access type are "r" (read), "w" (write) and None (remove access to form).
    """

    group_name: str
    ra_number: str
    survey_number: int
    access_type: Optional[str]
    performed_by: str

    @validator("access_type")
    def valid_access_type(cls, v):
        if v and v not in ["r", "w"]:
            raise ValidationError(
                "Access type must be either 'r' (read), 'w' (write) or None (revoke access)."
            )
        return v
