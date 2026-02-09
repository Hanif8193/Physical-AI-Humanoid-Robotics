"""Simple in-memory rate limiting middleware."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

# Rate limits per endpoint pattern
RATE_LIMITS = {
    "/v1/chat": (10, 60),       # 10 per 60 seconds
    "/v1/translate": (5, 60),   # 5 per 60 seconds
    "/v1/personalize": (5, 60), # 5 per 60 seconds
    "/v1/auth": (5, 900),       # 5 per 15 minutes
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, list[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        # Find applicable rate limit
        limit, window = None, None
        for pattern, (lim, win) in RATE_LIMITS.items():
            if path.startswith(pattern):
                limit, window = lim, win
                break

        if limit is None:
            return await call_next(request)

        key = f"{client_ip}:{path}"
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window)

        async with self._lock:
            # Clean old entries
            self._requests[key] = [t for t in self._requests[key] if t > cutoff]

            if len(self._requests[key]) >= limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Rate limit exceeded. Max {limit} requests per {window}s."
                    },
                )

            self._requests[key].append(now)

        return await call_next(request)
