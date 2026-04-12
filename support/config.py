"""Loads config.yaml and exposes a frozen CONFIG singleton."""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml


_PROJECT_ROOT = Path(__file__).parent.parent
_CONFIG_PATH = Path(os.environ.get("CONFIG_FILE", _PROJECT_ROOT / "config.yaml"))


def _load_yaml() -> dict:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)


@dataclass(frozen=True)
class Config:
    # UI settings
    ui_base_url: str
    ui_default_timeout_ms: int
    ui_browsers: tuple[str, ...]

    # API settings
    api_base_url: str
    api_postman_collection_url: str
    api_postman_fetch_timeout_s: int

    # Logging
    log_dir: str
    log_file: str

    @classmethod
    def from_yaml(cls, data: dict) -> "Config":
        ui = data.get("ui", {})
        api = data.get("api", {})
        log = data.get("logging", {})

        # The YAML multiline string for postman URL may have newlines/spaces — clean it
        postman_url = api.get("postman_collection_url", "")
        postman_url = postman_url.replace("\n", "").replace(" ", "")

        return cls(
            ui_base_url=ui.get("base_url", "https://www.demoblaze.com"),
            ui_default_timeout_ms=ui.get("default_timeout_ms", 10_000),
            ui_browsers=tuple(ui.get("browsers", ["chromium"])),
            api_base_url=api.get("base_url", "https://thinking-tester-contact-list.herokuapp.com"),
            api_postman_collection_url=postman_url,
            api_postman_fetch_timeout_s=api.get("postman_fetch_timeout_s", 10),
            log_dir=log.get("dir", "logs"),
            log_file=log.get("file", "logs/test_run.log"),
        )


CONFIG = Config.from_yaml(_load_yaml())
