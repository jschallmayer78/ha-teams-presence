"""Minimal Microsoft Graph client for Teams presence."""

from __future__ import annotations

import re
from typing import Any

from aiohttp import ClientError, ClientResponse

from homeassistant.helpers import config_entry_oauth2_flow

from .const import GRAPH_BASE_URL


class GraphError(Exception):
    """Generic Graph API error."""


class GraphAuthError(GraphError):
    """Authentication/authorization failed."""


class GraphRateLimitError(GraphError):
    """Request throttled by Graph."""

    def __init__(self, retry_after: int | None) -> None:
        super().__init__(f"Throttled by Microsoft Graph (retry after {retry_after}s)")
        self.retry_after = retry_after


def to_snake_case(value: str | None) -> str | None:
    """Convert Graph PascalCase values (e.g. 'DoNotDisturb') to snake_case."""
    if not value:
        return None
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


class GraphClient:
    """Wrapper around an OAuth2 session for Graph calls."""

    def __init__(self, session: config_entry_oauth2_flow.OAuth2Session) -> None:
        self._session = session

    async def _get(self, path: str) -> dict[str, Any]:
        try:
            resp: ClientResponse = await self._session.async_request(
                "get", f"{GRAPH_BASE_URL}{path}"
            )
        except ClientError as err:
            raise GraphError(f"Error talking to Microsoft Graph: {err}") from err

        if resp.status in (401, 403):
            raise GraphAuthError(f"Graph returned {resp.status}: {await resp.text()}")
        if resp.status == 429:
            retry_after = resp.headers.get("Retry-After")
            raise GraphRateLimitError(
                int(retry_after) if retry_after and retry_after.isdigit() else None
            )
        if resp.status >= 400:
            raise GraphError(f"Graph returned {resp.status}: {await resp.text()}")
        return await resp.json()

    async def async_get_me(self) -> dict[str, Any]:
        """Return the signed-in user's profile."""
        return await self._get("/me?$select=id,displayName,userPrincipalName,mail")

    async def async_get_presence(self) -> dict[str, Any]:
        """Return the signed-in user's presence."""
        return await self._get("/me/presence")
