from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:  # Optional dependency for now
    import yaml
except Exception:  # pragma: no cover - best effort stub
    yaml = None  # type: ignore


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config(
    version: str, profile: str = "dev", overrides: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Load layered configuration: defaults -> version -> profile -> overrides."""
    root = Path(__file__).resolve().parent
    cfg: dict[str, Any] = {}
    cfg.update(_read_yaml(root / "defaults.yaml"))
    cfg.update(_read_yaml(root / f"{version}.yaml"))
    cfg.update(_read_yaml(root / "profiles" / f"{profile}.yaml"))

    # Apply simple top-level overrides
    if overrides:
        for k, v in overrides.items():
            cfg[k] = v

    # Expose env vars for common settings as fallbacks
    cfg.setdefault("mlflow_uri", os.getenv("MLFLOW_TRACKING_URI", ""))
    cfg.setdefault("google_api_key", os.getenv("GOOGLE_API_KEY", ""))
    return cfg
