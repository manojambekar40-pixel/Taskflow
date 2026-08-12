"""
middleware.py
--------------
Logs method, path, and processing time (ms) for every request.
Visible both in local terminal output and in Render's log stream
(both write to stdout).
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("taskflow.requests")
logging.basicConfig(level=logging.INFO, format="%(message)s")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %.2f ms [%s]",
            request.method,
            request.url.path,
            duration_ms,
            response.status_code,
        )
        return response
