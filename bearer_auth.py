from fastapi import Request
from fastapi.responses import JSONResponse

from jwt_auth import verify_access_token


class BearerAuthMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        if request.url.path.startswith("/products"):

            authorization = request.headers.get("Authorization")

            if not authorization:
                response = JSONResponse(
                    status_code=401,
                    content={"detail": "Authorization header missing"}
                )

                await response(scope, receive, send)
                return

            try:
                scheme, token = authorization.split(" ", 1)

            except ValueError:
                response = JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid authorization header"}
                )

                await response(scope, receive, send)
                return

            if scheme.lower() != "bearer":
                response = JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid authentication scheme"}
                )

                await response(scope, receive, send)
                return

            payload = verify_access_token(token)

            if payload is None:
                response = JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token"}
                )

                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)