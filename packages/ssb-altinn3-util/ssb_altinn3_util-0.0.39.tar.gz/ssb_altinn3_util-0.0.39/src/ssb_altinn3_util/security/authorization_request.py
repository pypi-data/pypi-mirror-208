from pydantic import BaseModel


class AuthorizationRequest(BaseModel):
    user_email: str
    requested_role: str
