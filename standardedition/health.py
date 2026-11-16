"""Is the newest edition thin? The scheduled job runs this after building, and
raises an alert when it prints anything. A thin edition is still published.

    python -m standardedition.health              # the newest file in archive/
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import config

MAX_FEEDS_DOWN = 0.25  # More than a quarter of the feeds unreadable.
MIN_STORIES = 5


def problems(edition: dict) -> list[str]:
    """What's thin about an edition file, in plain sentences. Empty when it's healthy."""
    found = []
    sources, down = edition.get("sources") or {}, edition.get("feeds_down") or []
    if sources and len(down) / len(sources) > MAX_FEEDS_DOWN:
        found.append(f"{len(down)} of {len(sources)} feeds couldn't be read: {', '.join(sorted(down))}.")
    stories = edition.get("stories") or []
    if len(stories) < MIN_STORIES:
        found.append(f"The edition has {len(stories)} {'story' if len(stories) == 1 else 'stories'}. Fewer than {MIN_STORIES} is unusual.")
    fallback = [s["headline"] for s in stories if s.get("written_by") == "fallback"]
    if fallback:
        found.append(f"{len(fallback)} of {len(stories)} stories were written by the fallback writer, not a model.")
    return found


def newest(directory: Path) -> Path | None:
    # Edition files only: the folder may hold other JSON, such as an index.
    files = sorted(Path(directory).glob("????-??-??.json"))
    return files[-1] if files else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="standardedition.health")
    ap.add_argument("--archive", default=str(config.ARCHIVE_DIR))
    args = ap.parse_args(argv)
    path = newest(Path(args.archive))
    if path is None:
        print("No edition file was written.")
        return 0
    edition = json.loads(path.read_text())
    for line in problems(edition):
        print(f"- {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
