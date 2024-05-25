from jose import jwt
from fastapi import HTTPException, Request, Depends, FastAPI
from fastapi.security.oauth2 import OAuth2AuthorizationCodeBearer
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
from starlette.types import Scope, Receive, Send
from typing import List
from jose.exceptions import JWTError
import os
from starlette.responses import JSONResponse

# Okta details
OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
AUDIENCE = os.getenv("AUDIENCE")
ALGORITHMS = ["RS256"]

# Define the bearer scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/login/oauth/authorize",
    tokenUrl="/login/oauth/access_token",
    refreshUrl="/login/oauth/refresh_token",
    scopes={"users": "Access to user details"}
)

# Define the middleware
class OktaJWTMiddleware:
    def __init__(self, app: FastAPI, algorithms: List[str] = ALGORITHMS, audience: str = AUDIENCE):
        self.app = app
        self.algorithms = algorithms
        self.audience = audience

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        authorization: str = request.headers.get("Authorization")
        try:
            if not authorization:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Missing Authorization header."
                )
            scheme, param = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Invalid authorization scheme."
                )
            token = param
            try:
                payload = jwt.decode(
                    token,
                    OKTA_DOMAIN,
                    algorithms=self.algorithms,
                    audience=self.audience
                )
            except JWTError:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token."
                )
            except Exception as e:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials."
                )
            request.state.payload = payload
        except HTTPException as e:
            response = JSONResponse({'detail': e.detail}, status_code=e.status_code)
            await response(scope, receive, send)
            return
        return await self.app(scope, receive, send)

