import base64
import json
from typing import Dict


def get_user_email_from_token(token: str) -> str:
    """Get the user email from the jwt token"""
    token = token.split(sep=" ")[1]
    token = token.split(sep=".")[1]
    token_decoded = base64.b64decode(token + "==").decode("UTF-8")
    token_json: Dict = json.loads(token_decoded)
    email: str = token_json.get("email")

    if not email:
        preferred_username: str = token_json.get("preferred_username")

        if not preferred_username:
            return ""

        email = (
            preferred_username
            if preferred_username.endswith("@ssb.no")
            else f"{preferred_username}@ssb.no"
        )

    return email
