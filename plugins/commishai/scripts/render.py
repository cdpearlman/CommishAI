"""Output helpers: compact aligned tables by default, JSON on demand.

Default output is plain text because it costs a fraction of the tokens JSON does
for the same rows, and stays readable when a human runs the CLI directly.
"""

import json
from typing import Any, Dict, Iterable, List, Optional, Sequence

_JSON_MODE = False
_PAYLOAD: Dict[str, Any] = {}


def set_json_mode(enabled: bool) -> None:
    global _JSON_MODE
    _JSON_MODE = enabled


def json_mode() -> bool:
    return _JSON_MODE


def collect(key: str, value: Any) -> None:
    """Stash a section for --json output."""
    _PAYLOAD[key] = value


def flush() -> None:
    """In JSON mode, emit everything collected this run."""
    if _JSON_MODE:
        print(json.dumps(_PAYLOAD, indent=2, default=str))


def heading(text: str) -> None:
    if _JSON_MODE:
        return
    print(f"\n{text}")
    print("-" * len(text))


def line(text: str = "") -> None:
    if not _JSON_MODE:
        print(text)


def fmt(value: Any, places: int = 1, dash: str = "-") -> str:
    """Format a number for a table cell, collapsing missing/sentinel values."""
    if value is None:
        return dash
    if isinstance(value, (int, float)):
        if value < 0:  # espn-api uses -1 for "unknown"
            return dash
        return f"{value:.{places}f}"
    return str(value)


def table(
    rows: Sequence[Dict[str, Any]],
    columns: Sequence[str],
    headers: Optional[Sequence[str]] = None,
    empty: str = "(none)",
) -> None:
    """Print an aligned table. Numeric columns right-align, text left-aligns."""
    if _JSON_MODE:
        return
    if not rows:
        print(empty)
        return

    headers = list(headers or columns)
    cells: List[List[str]] = [
        [_cell(row.get(col)) for col in columns] for row in rows
    ]
    widths = [
        max(len(headers[i]), max(len(r[i]) for r in cells))
        for i in range(len(columns))
    ]
    numeric = [
        all(_is_num(row.get(col)) for row in rows)
        for col in columns
    ]

    def render(values: Sequence[str]) -> str:
        parts = [
            values[i].rjust(widths[i]) if numeric[i] else values[i].ljust(widths[i])
            for i in range(len(values))
        ]
        return "  ".join(parts).rstrip()

    print(render(headers))
    print("  ".join("-" * w for w in widths))
    for row in cells:
        print(render(row))


def _cell(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def _is_num(value: Any) -> bool:
    return value is None or isinstance(value, (int, float))
