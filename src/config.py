"""Configuration loader for ISDA SIMM constants and defaults."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG_NAME = "config.json"
ENV_CONFIG_PATH = "ISDA_SIMM_CONFIG"


@lru_cache(maxsize=1)
def load_config() -> Dict[str, Any]:
    """Load the application configuration from JSON.

    The configuration path can be overridden via the ISDA_SIMM_CONFIG
    environment variable. Otherwise, it loads config.json from the repo root.
    """
    config_path = Path(os.getenv(ENV_CONFIG_PATH, "")).expanduser()
    if not config_path.as_posix():
        config_path = Path(__file__).resolve().parents[1] / DEFAULT_CONFIG_NAME

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path}. Set {ENV_CONFIG_PATH} or add config.json."
        )

    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
