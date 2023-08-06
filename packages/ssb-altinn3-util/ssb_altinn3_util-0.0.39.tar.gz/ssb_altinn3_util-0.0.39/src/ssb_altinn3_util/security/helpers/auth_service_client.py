import json
import os
import requests

from ssb_altinn3_util.security.authorization_request import AuthorizationRequest
from ssb_altinn3_util.security.authorization_result import AuthorizationResult

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")


def verify_access(user_email: str, requested_role: str) -> AuthorizationResult:
    auth_request = AuthorizationRequest(
        user_email=user_email, requested_role=requested_role
    )

    url = f"{AUTH_SERVICE_URL}/auth/authorize"

    response = requests.post(url=url, data=auth_request.json())
    decoded = response.content.decode("UTF-8")
    return AuthorizationResult(**json.loads(decoded))
