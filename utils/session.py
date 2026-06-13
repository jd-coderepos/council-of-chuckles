"""Session transcript helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path


def append_session_entry(session: list[dict] | None, entry: dict) -> list[dict]:
    updated = list(session or [])
    updated.append(entry)
    return updated


def export_session_markdown(session: list[dict] | None) -> str | None:
    if not session:
        return None
    lines = ["# Council of Chuckles Session", ""]
    for index, entry in enumerate(session, start=1):
        lines.extend(
            [
                f"## Exchange {index}",
                "",
                f"**Question:** {entry.get('topic', '')}",
                "",
                f"**Mode:** {entry.get('mode', '')}",
                "",
                f"**Analysis:** {entry.get('analysis_summary', '')}",
                "",
                "### Output",
                "",
                entry.get("plain_output", ""),
                "",
            ]
        )
    path = Path(tempfile.gettempdir()) / "council_of_chuckles_session.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)

