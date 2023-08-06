from pydantic import BaseModel, validator, ValidationError


class PostFormRequest(BaseModel):
    ra_number: str
    survey_number: int


class PostGroupRequest(BaseModel):
    group_name: str


class PostGroupFormAccess(BaseModel):
    form_id: int
    group_id: int
    access_type: str
    user: str

    @validator("access_type")
    def valid_access_type(cls, v):
        if v not in ["r", "w"]:
            raise ValidationError("Access type must be either 'r' (read), 'w' (write).")
        return v


class PostGroupRoleAccess(BaseModel):
    role_id: int
    group_id: int
    user: str
