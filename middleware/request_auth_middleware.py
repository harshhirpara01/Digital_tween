import os

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from common.responses import errorResponse, HEM_INTERNAL_SERVER_ERROR


class APIKeyValidatorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, mdb):
        super().__init__(app)
        self.mdb = mdb
        self.environment = os.getenv('ENVIRONMENT', 'development').lower()  # default to 'development'

    async def dispatch(self, request: Request, call_next):
        # Exclude Swagger docs, ReDoc and OpenAPI schema
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # If not production, bypass API key check
        if self.environment != 'production':
            return await call_next(request)

        apikey = request.headers.get('apikey')
        try:
            apikey_data = list(self.mdb.ApiData.find({}))
            if apikey_data and apikey_data[0]['apikey'] == str(apikey):
                return await call_next(request)
            else:
                return errorResponse(status.HTTP_403_FORBIDDEN, "Please Check your apikey")

        except Exception as e:
            return errorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, HEM_INTERNAL_SERVER_ERROR)
