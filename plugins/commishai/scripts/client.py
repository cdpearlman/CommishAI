"""Config loading, ESPN auth, and a disk-cached League handle."""

import os
import pickle
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from espn_api.football import League

CONFIG_NAME = "league.yaml"


def _find_repo_root() -> Path:
    """Locate the directory holding league.yaml.

    The scripts live inside the CommishAI plugin, while config, .env, and
    decisions/ belong at the user's project root. Walk up from the script,
    then from the working directory, so the CLI works whether it is invoked
    by a skill or by hand from anywhere.
    """
    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        if (base / CONFIG_NAME).exists():
            return base

    cwd = Path.cwd().resolve()
    for base in (cwd, *cwd.parents):
        if (base / CONFIG_NAME).exists():
            return base

    # Nothing found — point the error at the conventional location.
    return here.parents[3] if len(here.parents) > 3 else here.parent


REPO_ROOT = _find_repo_root()
CONFIG_PATH = REPO_ROOT / CONFIG_NAME
CACHE_DIR = REPO_ROOT / ".cache"
CACHE_TTL_SECONDS = 15 * 60


class ConfigError(RuntimeError):
    """Raised when league.yaml or .env is missing/incomplete."""


def load_config() -> Dict[str, Any]:
    """Read league.yaml and merge in credentials from .env."""
    if not CONFIG_PATH.exists():
        raise ConfigError(
            f"No config at {CONFIG_PATH}. Copy the template from the repo root "
            f"and fill in league_id and team_id."
        )

    with open(CONFIG_PATH, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}

    load_dotenv(REPO_ROOT / ".env")

    for key in ("league_id", "team_id", "year"):
        if not cfg.get(key):
            raise ConfigError(
                f"`{key}` is unset in {CONFIG_PATH.name}. "
                f"Run `python scripts/ff.py doctor` for help filling it in."
            )
        try:
            cfg[key] = int(cfg[key])
        except (TypeError, ValueError):
            raise ConfigError(f"`{key}` must be an integer, got {cfg[key]!r}.")

    cfg.setdefault("scoring", "PPR")
    cfg.setdefault("risk_posture", "auto")
    cfg["espn_s2"] = os.getenv("ESPN_S2") or None
    cfg["swid"] = os.getenv("SWID") or os.getenv("ESPN_SWID") or None
    return cfg


def _cache_path(cfg: Dict[str, Any]) -> Path:
    return CACHE_DIR / f"league-{cfg['league_id']}-{cfg['year']}.pkl"


def get_league(cfg: Dict[str, Any], fresh: bool = False) -> League:
    """Return a League, reusing a recent pickled fetch when one exists.

    Constructing a League is a multi-request fetch, so an analysis session that
    runs six subcommands would otherwise pay for six full league loads.
    """
    path = _cache_path(cfg)

    if not fresh and path.exists():
        age = time.time() - path.stat().st_mtime
        if age < CACHE_TTL_SECONDS:
            try:
                with open(path, "rb") as fh:
                    return pickle.load(fh)
            except Exception:
                # A corrupt or version-mismatched cache is never fatal.
                pass

    kwargs = {"league_id": cfg["league_id"], "year": cfg["year"]}
    if cfg.get("espn_s2") and cfg.get("swid"):
        kwargs["espn_s2"] = cfg["espn_s2"]
        kwargs["swid"] = cfg["swid"]

    try:
        league = League(**kwargs)
    except Exception as exc:
        raise ConfigError(_diagnose(exc, cfg)) from exc

    CACHE_DIR.mkdir(exist_ok=True)
    try:
        with open(path, "wb") as fh:
            pickle.dump(league, fh)
    except Exception:
        pass  # Caching is an optimization, never a requirement.

    return league


def _diagnose(exc: Exception, cfg: Dict[str, Any]) -> str:
    """Turn an opaque espn-api failure into something actionable."""
    msg = str(exc)
    kind = type(exc).__name__
    has_cookies = bool(cfg.get("espn_s2") and cfg.get("swid"))

    # espn-api crashes building its own 401 message when no cookies are set:
    # `self.cookies.get(...)` on a None cookie jar. That AttributeError is only
    # reachable from the 401 branch, so it means access denied, not a bug in us.
    masked_401 = isinstance(exc, AttributeError) and "'NoneType' object has no attribute 'get'" in msg

    if kind == "ESPNAccessDenied" or masked_401 or "401" in msg or "Unauthorized" in msg:
        if not has_cookies:
            return (
                f"ESPN denied access to league {cfg['league_id']} — it is private and no "
                f"cookies are set.\n"
                f"  Fix: copy .env.example to .env and paste in ESPN_S2 and SWID.\n"
                f"  Get them: log into fantasy.espn.com, press F12, open the Application tab,\n"
                f"  expand Cookies -> https://fantasy.espn.com, and copy `espn_s2` and `SWID`."
            )
        return (
            f"ESPN denied access to league {cfg['league_id']} even though cookies are set.\n"
            f"  Most likely they have expired — re-copy ESPN_S2 and SWID from your browser.\n"
            f"  Otherwise, check that this ESPN account is actually in this league."
        )

    if kind == "ESPNInvalidLeague" or "404" in msg or "does not exist" in msg:
        return (
            f"ESPN has no league {cfg['league_id']} for {cfg['year']}. "
            f"Check league_id in league.yaml, and that the {cfg['year']} season has started."
        )

    return f"Could not load league ({kind}): {msg}"


def get_my_team(league: League, cfg: Dict[str, Any]):
    """Find the configured team, with a useful error listing the alternatives."""
    for team in league.teams:
        if team.team_id == cfg["team_id"]:
            return team
    known = ", ".join(f"{t.team_id}={t.team_name}" for t in league.teams)
    raise ConfigError(
        f"team_id {cfg['team_id']} is not in this league. Teams are: {known}"
    )


def current_week(league: League, cfg: Dict[str, Any], override: Optional[int] = None) -> int:
    """Resolve the week to report on: explicit --week, else the league's current."""
    if override:
        return int(override)
    return int(getattr(league, "current_week", 1) or 1)


def die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)
