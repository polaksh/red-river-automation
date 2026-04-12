"""Fetches the Postman collection and builds a structured endpoint registry.

TracedAPIClient uses this to enrich logs with endpoint names and warn on
unknown routes. Falls back to a bundled spec if the remote fetch fails.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError


from support.config import CONFIG


logger = logging.getLogger("api_discovery")

_FALLBACK_SPEC = Path(__file__).parent / "api_spec_fallback.json"


@dataclass(frozen=True)
class Endpoint:
    name: str
    method: str
    path: str
    auth: bool
    body_fields: list[str]
    response_status: int


@dataclass
class EndpointRegistry:
    source: str                        # Where the spec came from
    endpoints: list[Endpoint] = field(default_factory=list)

    def lookup(self, method: str, url: str) -> Endpoint | None:
        """Match a method+URL to a known endpoint. Handles path params like :id."""
        path = re.sub(r"https?://[^/]+", "", url)

        for ep in self.endpoints:
            if ep.method != method.upper():
                continue
            # :id -> [^/]+ for pattern matching
            pattern = re.sub(r":[^/]+", r"[^/]+", ep.path)
            if re.fullmatch(pattern, path):
                return ep
        return None

    def by_name(self, name: str) -> Endpoint:
        """Find endpoint by its human name (e.g., "Add Contact"). Raises if not found."""
        for ep in self.endpoints:
            if ep.name.lower() == name.lower():
                return ep
        known = [ep.name for ep in self.endpoints]
        raise ValueError(f"Unknown endpoint '{name}'. Known: {known}")

    def summary(self) -> str:
        lines = [f"API Spec loaded from: {self.source}"]
        lines.append(f"Discovered {len(self.endpoints)} endpoints:")
        for ep in self.endpoints:
            auth_marker = "[auth]" if ep.auth else "[open]"
            body_info = f" body: {ep.body_fields}" if ep.body_fields else ""
            lines.append(
                f"  {ep.method:6s} {ep.path:<20s} {auth_marker} "
                f"-> {ep.response_status}{body_info}  # {ep.name}"
            )
        return "\n".join(lines)

    @classmethod
    def discover(cls) -> "EndpointRegistry":
        """Try remote Postman collection first, fall back to bundled spec."""
        try:
            return cls._from_postman_remote()
        except Exception as exc:
            logger.warning(
                "Remote Postman fetch failed (%s), using fallback spec", exc
            )

        return cls._from_fallback()

    @classmethod
    def _from_postman_remote(cls) -> "EndpointRegistry":
        logger.info("Fetching Postman collection from remote...")
        # Cloudflare sits in front of Postman's gateway and may 403 bare urllib requests
        req = Request(CONFIG.api_postman_collection_url, headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; RedRiverAutomation/1.0)",
        })
        with urlopen(req, timeout=CONFIG.api_postman_fetch_timeout_s) as resp:
            data = json.loads(resp.read())

        endpoints = []
        for folder in data.get("item", []):
            for request_item in folder.get("item", []):
                ep = cls._parse_postman_item(request_item)
                if ep:
                    endpoints.append(ep)

        registry = cls(source="Postman collection (remote)", endpoints=endpoints)
        logger.info(registry.summary())
        return registry

    @classmethod
    def _from_fallback(cls) -> "EndpointRegistry":
        logger.info("Loading bundled API spec fallback...")
        with open(_FALLBACK_SPEC) as f:
            data = json.load(f)

        endpoints = [
            Endpoint(
                name=ep["name"],
                method=ep["method"],
                path=ep["path"],
                auth=ep["auth"],
                body_fields=ep["body_fields"],
                response_status=ep["response_status"],
            )
            for ep in data["endpoints"]
        ]

        registry = cls(source=data["source"], endpoints=endpoints)
        logger.info(registry.summary())
        return registry

    @classmethod
    def _parse_postman_item(cls, item: dict) -> Endpoint | None:
        request = item.get("request", {})
        if not request:
            return None

        method = request.get("method", "").upper()
        name = item.get("name", "Unknown")

        url_obj = request.get("urlObject", {})
        path_parts = url_obj.get("path", [])
        # keep empty parts — a trailing "" means Postman intended a path param slot
        raw_path = "/" + "/".join(path_parts)
        has_trailing_slash = raw_path.endswith("/") and raw_path != "/"
        path = raw_path.rstrip("/") or "/"

        # Postman represents /contacts/:id as /contacts/ (trailing slash, empty segment).
        # If a non-POST method targets /contacts with a trailing slash, it's the :id variant.
        if has_trailing_slash and path == "/contacts" and method != "POST":
            path = "/contacts/:id"

        # Disambiguate duplicate names: Postman names both PUT and PATCH "Update Contact"
        if method in ("PUT", "PATCH") and name == "Update Contact":
            name = f"Update Contact ({method})"

        headers = request.get("header", [])
        auth = any(h.get("key") == "Authorization" for h in headers)

        body_fields = []
        body = request.get("body", {})
        if body.get("mode") == "raw" and body.get("raw"):
            try:
                body_json = json.loads(body["raw"])
                if isinstance(body_json, dict):
                    body_fields = list(body_json.keys())
            except json.JSONDecodeError:
                pass

        response_status = 200
        responses = item.get("response", [])
        if responses and responses[0].get("code"):
            response_status = responses[0]["code"]

        return Endpoint(
            name=name,
            method=method,
            path=path,
            auth=auth,
            body_fields=body_fields,
            response_status=response_status,
        )
