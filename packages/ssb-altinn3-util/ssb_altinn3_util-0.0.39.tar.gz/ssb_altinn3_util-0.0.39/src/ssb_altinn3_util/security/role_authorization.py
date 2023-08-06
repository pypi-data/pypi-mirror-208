from typing import List, Any, Tuple, Dict
from functools import wraps

from fastapi import Request, HTTPException
import ssb_altinn3_util.security.authenticator_constants as const
import ssb_altinn3_util.security.helpers.jwt_helper as jwt_helper
import ssb_altinn3_util.security.helpers.auth_service_client as auth_service_client
from ssb_altinn3_util.security.authorization_result import AuthorizationResult


def authorize(require_role: str):
    """
    Authorization component to be used as a decorator far an api-endpoint in a FastAPI application.  Requires the
    following to function properly:
    Env variable AUTH_SERVICE_URL must be set with the base url to the authorization service endpoint.
    The role-argument must be one of the roles defined in authenticator_constants (in ssb_altinn3_util.security).

    Note that form access must be validated in the actual endpoint code, calling the verify_form_read_access or
    verify_form_write_access functions implemented in the FormAccessValidator class.  Example:

    @app.get("/stuff")
    @authorize(required_role=<required_role(s)>)
    def do_stuff(form: str, request: Request):
        validator = FormAccessValidator(request=request)
        validator.verify_form_read_access(form=form)
        ....

    Multiple roles can be specified as well, if an endpoint is available for more than one role.  This is done by
    adding the roles as a string, separating the different roles with a comma.  Note that this will grant access
    if ANY of the roles are owned by the user.  Example:

    @app.get("/stuff")
    @authorize(required_role="<role1>,<role2>")
    def do_stuff(form: str, request: Request):
        validator = FormAccessValidator(request=request)
        validator.verify_form_read_access(form=form)
        ....

    """
    roles: List[str] = require_role.split(",")

    for r in roles:
        if r not in const.VALID_ROLES:
            raise ValueError(f"Supplied role '{r}' is not a valid role!")

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            # Get request object
            request = _extract_request(args, kwargs)

            # Get user from token
            user_email = _extract_email(request)

            # Verify required role
            result = _validate_role_access(user_email)

            request.state.user_email = user_email
            request.state.allowed_forms_read = result.allowed_forms_read
            request.state.allowed_forms_write = result.allowed_forms_write

            # Proceed to wrapped function
            return func(*args, **kwargs)

        def _get_from_args(args: Tuple[Any, ...]) -> Request or None:
            for arg in args:
                if isinstance(arg, Request):
                    return arg
            else:
                return None

        def _get_from_kwargs(kwargs: Dict[str, Any]) -> Request or None:
            for kwarg in kwargs.values():
                if isinstance(kwarg, Request):
                    return kwarg
            else:
                return None

        def _validate_role_access(user_email) -> AuthorizationResult:
            result: AuthorizationResult or None = None
            for role in roles:
                result = auth_service_client.verify_access(user_email, role)
                if result.access_granted:
                    return result
            if result is None:
                raise HTTPException(
                    status_code=400, detail="Unable to verify supplied roles."
                )
            if not result.access_granted:
                raise HTTPException(
                    status_code=result.status_code, detail=result.error_message
                )
            return result

        def _extract_email(request):
            auth_header = request.headers.get("authorization", None)
            if not auth_header:
                raise HTTPException(status_code=401, detail="No token provided")
            user_email = jwt_helper.get_user_email_from_token(auth_header)
            if not user_email:
                raise HTTPException(
                    status_code=401, detail="Unable to find user email in supplied token!"
                )
            return user_email

        def _extract_request(args, kwargs):
            request: Request = _get_from_args(args)
            if request is None:
                request = _get_from_kwargs(kwargs)
            if request is None:
                raise ValueError(f"Unable to extract request object!")
            return request

        return inner
    return wrapper
