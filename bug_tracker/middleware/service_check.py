from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from ..utils.service_health import service_health

class ServiceCheckMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip health checks
        if request.url.path in ["/health", "/services/status"]:
            return await call_next(request)

        # Check if the service is available
        try:
            service_health.raise_if_service_unavailable("bug_tracker")
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )

        # If service is available, proceed with the request
        response = await call_next(request)
        return response 