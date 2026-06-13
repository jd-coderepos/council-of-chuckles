"""Advisor loading, normalization, and filtering."""

from __future__ import annotations

import json
from pathlib import Path

from .archetypes import assign_archetypes


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ADVISORS_PATH = ROOT / "data" / "advisors.json"


def normalize_advisor(raw: dict) -> dict:
    advisor = dict(raw)
    advisor["id"] = str(advisor.get("id") or advisor.get("name", "advisor")).strip().lower().replace(" ", "_")
    advisor["name"] = advisor.get("name") or advisor["id"].replace("_", " ").title()
    advisor["category"] = advisor.get("category") or "Uncategorized"
    advisor["era"] = advisor.get("era") or "Timeless"
    advisor["role"] = advisor.get("role") or "Advisor"
    advisor["core_wisdom"] = advisor.get("core_wisdom") or "Offer grounded perspective and a small next step."
    advisor["signature_style"] = advisor.get("signature_style") or "warm, clear, practical"
    advisor["mastermind_voice"] = advisor.get("mastermind_voice") or "A practical advisor with compassionate perspective."
    advisor["comic_voice"] = advisor.get("comic_voice") or advisor.get("jokester_voice") or "Warm, non-cruel humor."
    advisor["catchphrase"] = advisor.get("catchphrase") or "Begin with one honest step."
    advisor["best_for"] = advisor.get("best_for") if isinstance(advisor.get("best_for"), list) else []
    advisor["avoid"] = advisor.get("avoid") or "Do not be cruel, dismissive, or overconfident."
    advisor["avatar"] = advisor.get("avatar") or ""
    advisor["avatar_alt"] = advisor.get("avatar_alt") or get_initials(advisor["name"])
    advisor["archetypes"] = assign_archetypes(advisor)
    return advisor


def load_advisors(path: Path | str = DEFAULT_ADVISORS_PATH) -> list[dict]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("advisors.json must contain a list of advisor objects")
    return [normalize_advisor(item) for item in data if isinstance(item, dict)]


def get_initials(name: str) -> str:
    parts = [part for part in name.replace("-", " ").split() if part]
    if not parts:
        return "??"
    return "".join(part[0].upper() for part in parts[:2])


def advisor_by_id(advisors: list[dict], advisor_id: str) -> dict | None:
    return next((advisor for advisor in advisors if advisor["id"] == advisor_id), None)


def filter_advisors(advisors: list[dict], search: str = "", category: str = "All") -> list[dict]:
    query = (search or "").strip().lower()
    filtered = advisors
    if category and category != "All":
        filtered = [advisor for advisor in filtered if advisor.get("category") == category]
    if query:
        filtered = [
            advisor
            for advisor in filtered
            if query in " ".join(
                [
                    advisor.get("name", ""),
                    advisor.get("category", ""),
                    advisor.get("role", ""),
                    " ".join(advisor.get("best_for", [])),
                ]
            ).lower()
        ]
    return filtered


def category_options(advisors: list[dict]) -> list[str]:
    return ["All"] + sorted({advisor.get("category", "Uncategorized") for advisor in advisors})

