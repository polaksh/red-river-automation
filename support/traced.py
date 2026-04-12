"""Dynamic proxy wrappers that log all Playwright interactions.

Wraps Page and APIRequestContext via __getattr__, intercepts action calls,
and logs them with timing. Tests and page objects use these exactly like
the raw Playwright objects.
"""

from __future__ import annotations

import logging
import time

from playwright.sync_api import Page, APIRequestContext

from support.api_discovery import EndpointRegistry


logger = logging.getLogger("traced")

_TRACED_PAGE_ACTIONS = frozenset({
    "goto", "click", "fill", "check", "uncheck", "select_option",
    "type", "press", "hover", "focus", "dblclick",
    "wait_for_selector", "wait_for_load_state", "wait_for_url",
    "screenshot", "evaluate",
})

_TRACED_API_METHODS = frozenset({
    "get", "post", "put", "patch", "delete", "head",
})


def _mask_sensitive(name: str, args: tuple, kwargs: dict) -> str:
    parts = [repr(a) for a in args]
    for k, v in kwargs.items():
        display = "***" if "pass" in k.lower() else repr(v)
        parts.append(f"{k}={display}")
    return f"{name}({', '.join(parts)})"


class TracedPage:
    """Logging proxy for Playwright Page."""

    def __init__(self, page: Page) -> None:
        self._page = page

    def __getattr__(self, name: str):
        attr = getattr(self._page, name)

        if name not in _TRACED_PAGE_ACTIONS or not callable(attr):
            return attr

        def traced_call(*args, **kwargs):
            label = _mask_sensitive(name, args, kwargs)
            logger.info("[TracedPage] %s", label)
            start = time.perf_counter()
            try:
                result = attr(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.debug("[TracedPage] %s -> %.0fms", name, elapsed_ms)
                return result
            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.error("[TracedPage] %s FAILED (%.0fms)", label, elapsed_ms)
                raise

        return traced_call


class TracedAPIClient:
    """Logging proxy for Playwright APIRequestContext.

    Also handles Bearer token management and endpoint name resolution
    via the discovery registry.
    """

    def __init__(self, context: APIRequestContext,
                 registry: EndpointRegistry | None = None) -> None:
        self._context = context
        self._registry = registry
        self._token: str | None = None

    @property
    def registry(self) -> EndpointRegistry | None:
        return self._registry

    @property
    def token(self) -> str | None:
        return self._token

    @token.setter
    def token(self, value: str | None) -> None:
        self._token = value

    def _headers(self) -> dict[str, str]:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    def _resolve_endpoint_name(self, method: str, url: str) -> str:
        if not self._registry:
            return ""
        endpoint = self._registry.lookup(method, url)
        if endpoint:
            return endpoint.name
        logger.warning(
            "[TracedAPI] Unknown endpoint: %s %s — not in API spec",
            method.upper(), url,
        )
        return "unknown"

    def __getattr__(self, name: str):
        attr = getattr(self._context, name)

        if name not in _TRACED_API_METHODS or not callable(attr):
            return attr

        def traced_call(url: str, **kwargs):
            kwargs.setdefault("headers", {}).update(self._headers())
            ep_name = self._resolve_endpoint_name(name, url)
            ep_label = f" [{ep_name}]" if ep_name else ""

            logger.info("[TracedAPI] %s %s%s", name.upper(), url, ep_label)
            start = time.perf_counter()
            try:
                response = attr(url, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    "[TracedAPI] %s %s%s -> %s (%.0fms)",
                    name.upper(), url, ep_label, response.status, elapsed_ms,
                )
                return response
            except Exception:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    "[TracedAPI] %s %s%s FAILED (%.0fms)",
                    name.upper(), url, ep_label, elapsed_ms,
                )
                raise

        return traced_call

    def call_endpoint(self, endpoint, data=None, path_params=None):
        """Call an API endpoint by its Endpoint object (from discovery).

        Resolves the method and path from the endpoint spec. Path params
        like :id are substituted from the path_params dict.
        """
        path = endpoint.path
        if path_params:
            for key, val in path_params.items():
                path = path.replace(f":{key}", str(val))

        method_fn = getattr(self, endpoint.method.lower())
        kwargs = {}
        if data is not None:
            kwargs["data"] = data
        return method_fn(path, **kwargs)

    def dispose(self) -> None:
        self._context.dispose()
