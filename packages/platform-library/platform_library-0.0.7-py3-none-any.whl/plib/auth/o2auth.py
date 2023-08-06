from typing import Optional, Tuple


def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param


class OAuth2PasswordBearer:

    async def __call__(self, request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization") or request.headers.get("authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise Exception("Could not validate credentials")
        return param
