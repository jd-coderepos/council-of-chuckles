from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "app.py",
    "README.md",
    "requirements.txt",
    "data/advisors.json",
    "utils/models.py",
    "utils/audio.py",
]
REQUIRED_TAGS = {"build-small", "thousand-token-wood", "gradio", "zerogpu"}
SUBMISSION_LINK_LABELS = ["Live Space", "GitHub repo", "Demo video", "Social post"]


def ok(message: str) -> None:
    print(f"[OK] {message}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"[WARN] {message}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        fail(f"Missing required files: {', '.join(missing)}")
    ok("required project files exist")


def check_readme_front_matter() -> None:
    readme = read("README.md")
    if not readme.startswith("---\n"):
        fail("README.md must start with YAML front matter")
    front_matter = readme.split("---", 2)[1]
    for field in ["title:", "sdk: gradio", "python_version:", "app_file: app.py"]:
        if field not in front_matter:
            fail(f"README.md front matter missing {field}")
    tags = set(re.findall(r"^\s*-\s*([a-z0-9-]+)\s*$", front_matter, flags=re.MULTILINE))
    missing_tags = sorted(REQUIRED_TAGS - tags)
    if missing_tags:
        fail(f"README.md missing tags: {', '.join(missing_tags)}")
    ok("README.md front matter has required Space metadata and tags")


def check_zerogpu_hooks() -> None:
    models = read("utils/models.py")
    audio = read("utils/audio.py")
    requirements = read("requirements.txt")
    if "spaces" not in requirements:
        fail("requirements.txt must include spaces for ZeroGPU")
    if "@spaces.GPU" not in models:
        fail("utils/models.py is missing @spaces.GPU")
    if "@spaces.GPU" not in audio:
        fail("utils/audio.py is missing @spaces.GPU")
    ok("ZeroGPU package and decorators are present")


def check_app_fallback() -> None:
    sys.path.insert(0, str(ROOT))
    app = importlib.import_module("app")
    result = app.generate(
        "I am afraid to submit my paper because it might not be good enough.",
        app.DEFAULT_SELECTED_IDS,
        "English",
        "",
        "Campfire Council Mode",
        "Balanced Council",
        5,
        [],
        "Academic panic room",
        6,
        3,
        5,
        True,
        True,
        False,
        [],
    )
    status = result[4]
    output_html = result[2]
    verdict_html = result[3]
    if len(app.ADVISORS) < 50:
        fail("Expected the advisor dataset to load")
    if "Fallback mode active" not in status:
        fail(f"Expected fallback status, got: {status}")
    if not output_html or not verdict_html:
        fail("Expected generated council output and verdict HTML")
    ok("app imports and fallback council generation works")


def check_submission_placeholders() -> None:
    readme = read("README.md")
    for label in SUBMISSION_LINK_LABELS:
        match = re.search(rf"^- {re.escape(label)}:\s*(.+)$", readme, flags=re.MULTILINE)
        if not match:
            warn(f"README.md does not list submission link: {label}")
            continue
        value = match.group(1).strip().lower()
        if "add the" in value or "after " in value:
            warn(f"README.md still has placeholder for {label}")
    if "Best Use of Codex" not in readme and "Codex" not in readme:
        warn("README.md does not mention Codex; add it if targeting Best Use of Codex")


def main() -> None:
    check_required_files()
    check_readme_front_matter()
    check_zerogpu_hooks()
    check_app_fallback()
    check_submission_placeholders()
    print("[OK] submission preflight passed")


if __name__ == "__main__":
    main()
