"""Export the latest edition as a static site.

    python -m boringnews.export_static --out site

Writes index.html (settings work in the browser), edition.json (the data),
one ready-made feed per topic under feeds/, and the public data under api/v1/
(boringnews/public_api.py).

Custom feed addresses (/feed.xml?topics=...) are built on request by the
Cloudflare Pages function in functions/feed.xml.js, which reads edition.json.
Pass --static-feed to also write a fixed feed.xml for hosts without functions
(GitHub Pages, any plain file host); that file ignores feed settings.
functions/mcp.js serves /mcp from the files under api/v1/.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from . import config, public_api, research
from .db import connect
from .edition import Edition, NoEdition
from .reader import feeds
from .render import (load_corrections, render_page, render_archived_story,
                     render_archived_edition, render_archive_index, story_path)
from .sources import load_sources
from .topics import TOPICS

BRAND = config.ROOT / "web" / "brand"


def export(edition: Edition, research_index: dict, out: Path, base_url: str, sample: bool = False,
           cname: str | None = None, static_feed: bool = False, archive_dir: Path | None = None,
           inline_research: bool = False) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    (out / "feeds").mkdir(exist_ok=True)
    written = []

    # Publish the edition files so anyone can download and re-check them.
    data_url = None
    if archive_dir and Path(archive_dir).is_dir():
        (out / "archive").mkdir(exist_ok=True)
        for f in sorted(Path(archive_dir).glob("*.json")):
            shutil.copy(f, out / "archive" / f.name)
            written.append(out / "archive" / f.name)
        if (out / "archive" / f"{edition.date}.json").exists():
            data_url = f"{base_url}/archive/{edition.date}.json"
    # Research tab: the last 30 days, fetched by the page when the tab opens.
    (out / "research.json").write_text(json.dumps(research_index, ensure_ascii=False))
    written.append(out / "research.json")

    corrections = load_corrections()
    written += public_api.write(out, edition, research_index, base_url, sample, corrections)

    data = edition.page_data(base_url, sample=sample, data_url=data_url, corrections=corrections,
                             research_url="research.json", research=research_index if inline_research else None)
    (out / "index.html").write_text(render_page(data))
    (out / "edition.json").write_text(json.dumps(data, ensure_ascii=False))
    written += [out / "index.html", out / "edition.json"]

    # Every published snapshot gets permanent, readable pages, independently of
    # the rolling research index. The live edition also works before archiving.
    snapshots = {}
    for f in sorted((out / "archive").glob("*.json")):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", f.name):
            snapshot = json.loads(f.read_text())
            if snapshot.get("edition") != f.stem:
                raise ValueError(f"Archive date does not match filename: {f.name}")
            snapshots[f.stem] = snapshot
    if edition.date not in snapshots:
        snapshots[edition.date] = {**data, "articles": [], "stories": [
            {**s, "written_by": original.written_by} for s, original in zip(data["stories"], edition.stories)
        ]}
    story_index = {}
    urls = [base_url + "/", base_url + "/editions/"]
    for date, snapshot in snapshots.items():
        snapshot = {**snapshot, "sample": sample or snapshot.get("sample", False)}
        folder = out / "editions" / date
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "index.html"
        path.write_text(render_archived_edition(snapshot, base_url))
        written.append(path)
        urls.append(base_url + f"/editions/{date}/")
        for story in snapshot["stories"]:
            if story.get("id") is None:  # pre-format-2 archives had no stable identity
                continue
            path = out / story_path(date, story["id"]).lstrip("/") / "index.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render_archived_story(snapshot, story, base_url))
            written.append(path)
            story_index[str(story["id"])] = story_path(date, story["id"])
            urls.append(base_url + story_path(date, story["id"]))
    archive_index = out / "editions" / "index.html"
    archive_index.write_text(render_archive_index(list(snapshots), base_url, sample))
    (out / "story-index.json").write_text(json.dumps(story_index, sort_keys=True))
    from xml.sax.saxutils import escape
    (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
        ''.join('<url><loc>' + escape(u) + '</loc></url>' for u in urls) + '</urlset>')
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n")
    written += [archive_index, out / "story-index.json", out / "sitemap.xml", out / "robots.txt"]

    # The favicon and the image a shared link previews with.
    (out / "brand").mkdir(exist_ok=True)
    for f in sorted(BRAND.rglob("*")):
        if f.is_file() and f.suffix in {".png", ".woff2", ".woff", ".txt"}:
            target = out / "brand" / f.relative_to(BRAND)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, target)
            written.append(target)

    if cname:  # GitHub Pages custom domain
        (out / "CNAME").write_text(cname.strip() + "\n")
        written.append(out / "CNAME")

    paths = {out / "feeds" / f"{topic}.xml": f"topics={topic}" for topic in TOPICS}
    if static_feed:
        paths[out / "feed.xml"] = ""
    for path, xml in zip(paths, feeds(data, list(paths.values()))):
        path.write_text(xml)
        written.append(path)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(prog="boringnews.export_static")
    ap.add_argument("--out", default="site")
    ap.add_argument("--db", default=str(config.DB_PATH))
    ap.add_argument("--sample", action="store_true", help="label the page as sample data")
    ap.add_argument("--base-url", default=config.BASE_URL)
    ap.add_argument("--cname", help="custom domain for GitHub Pages, e.g. standardedition.org")
    ap.add_argument("--archive", default=str(config.ARCHIVE_DIR), help="folder of edition files to publish")
    ap.add_argument("--inline-research", action="store_true",
                    help="embed the research index in the page (for a single-file preview)")
    ap.add_argument("--static-feed", action="store_true", help="also write a fixed feed.xml (hosts without functions)")
    args = ap.parse_args(argv)
    conn = connect(args.db)
    sources = load_sources(config.sources_path(args.sample))
    try:
        edition = Edition.load(conn, sources)
    except NoEdition as exc:
        raise SystemExit(str(exc))
    for p in export(edition, research.build(conn, sources), Path(args.out), args.base_url.rstrip("/"), args.sample,
                    args.cname, args.static_feed, Path(args.archive), args.inline_research):
        print("wrote", p)


if __name__ == "__main__":
    main()
