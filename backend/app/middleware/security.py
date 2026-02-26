"""Middleware sécurité OWASP — B6-01.

Headers de sécurité HTTP :
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Strict-Transport-Security (HSTS)
- Content-Security-Policy
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy

CORS configuré strictement (pas de wildcard en prod).
Rate limiting via slowapi.
"""

from __future__ import annotations

import os
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send


class SecurityHeadersMiddleware:
    """Injecte les headers de sécurité sur chaque réponse."""

    HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "object-src 'none';"
        ),
    }

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                for k, v in self.HEADERS.items():
                    headers[k.lower().encode()] = v.encode()
                # HSTS uniquement en HTTPS
                if os.environ.get("APP_ENV") == "production":
                    headers[b"strict-transport-security"] = (
                        b"max-age=31536000; includeSubDomains"
                    )
                message = {
                    **message,
                    "headers": list(headers.items()),
                }
            await send(message)

        await self.app(scope, receive, send_with_headers)
