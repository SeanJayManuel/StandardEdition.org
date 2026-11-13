"""One day's edition, and the only module that knows its shape.

The pipeline builds an Edition and saves it. From there it has three forms:
the database (a local cache), the edition file (archive/YYYY-MM-DD.json, the
project's storage) and the page data (edition.json, which web/core.js and
web/app.js read). All three are written and read here.

An edition file holds everything needed to check or reproduce an edition:
  - the rubric (version, weights, thresholds) and hashes of the style guide
    and banned-word list in force that day
  - every source with its lean, weight and role
  - every article read in the edition window
  - how articles were grouped into stories, each story's id, score parts and
    fact-check log, and which writer produced it
  - what the rules left out, and the rule that did it, under `left_out`

Edition files are committed to the repo and published on the site (/archive/).
`restore` rebuilds the database from them.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from . import config, db, ledger, rubric
from .db import Article, Story
from .reposts import reposts
from .sources import Source
from .topics import LEGACY, TOPIC_DESCRIPTIONS, TOPICS

FORMAT = 3  # 3 adds article action identities and collection context; reads formats 1 and 2.


class NoEdition(LookupError):
    """The database has no edition, or none for the date asked for."""


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def _rubric() -> dict:
    return {
        "version": rubric.VERSION, "weights": rubric.WEIGHTS, "thresholds": rubric.THRESHOLDS,
        "coverage_cap": rubric.COVERAGE_CAP, "min_outlets": rubric.MIN_OUTLETS, "spotlight": rubric.SPOTLIGHT,
        "blindspot_outlets": rubric.BLINDSPOT_OUTLETS,
    }


def _page_articles(articles: list[Article]) -> list[dict]:
    copies = reposts(articles)
    return [{"source_id": a.source_id, "title": a.title, "url": a.url, "published_at": a.published_at,
             "copy_of": copies[a.url].source_id if a.url in copies else None} for a in articles]


def article_record(a: Article) -> dict:
    return {"key": a.key, "source_id": a.source_id, "url": a.url, "event_id": a.event_id,
            "title": a.title, "summary": a.summary, "published_at": a.published_at}


def _record_coverage(clusters: list[list[Article]], sources: dict) -> dict:
    coverage = {}
    for group in clusters:
        outlets = {a.source_id for a in group if sources.get(a.source_id, {}).get("type") not in (None, "primary")}
        for a in group:
            if sources.get(a.source_id, {}).get("type") == "primary":
                coverage[a.key] = len(outlets)
    return coverage


def sources_from_records(records: dict) -> dict[str, Source]:
    """A historical display snapshot, never used to fetch current feeds."""
    return {sid: Source(id=sid, url="", **{k: v for k, v in item.items()
            if k in {"name", "lean", "type", "role", "weight", "ratings"}})
            for sid, item in records.items()}


def _sources(sources: dict[str, Source]) -> dict:
    return {sid: s.record() for sid, s in sources.items()}


@dataclass
class Edition:
    date: str
    stories: list[Story]
    sources: dict[str, Source]
    markets: list[dict] = field(default_factory=list)
    feeds_down: list[str] = field(default_factory=list)  # sources we couldn't read that day

    collection_window: dict | None = None
    coverage_known: bool = True

    @classmethod
    def load(cls, conn, sources: dict[str, Source], date: str | None = None) -> "Edition":
        """The edition for `date`, or the latest one."""
        dates = db.editions(conn)
        if not dates:
            raise NoEdition("No editions yet. Run: python -m boringnews.pipeline run")
        date = date or dates[0]
        if date not in dates:
            raise NoEdition(f"No edition for {date}")
        snapshot = db.load_extra(conn, date, "sources")
        return cls(date, db.load_edition(conn, date), sources_from_records(snapshot) if snapshot is not None else sources,
                   db.load_extra(conn, date, "markets", []), db.load_extra(conn, date, "feeds_down", []),
                   db.load_extra(conn, date, "collection_window"), snapshot is not None)

    def save(self, conn, articles: list[Article] | None = None, clusters: list[list[Article]] | None = None) -> None:
        """Store it, replacing any earlier run for the same date. Sets story ids."""
        db.replace_edition(conn, self.date, self.stories)
        db.save_extra(conn, self.date, "markets", self.markets)
        db.save_extra(conn, self.date, "feeds_down", self.feeds_down)
        db.save_extra(conn, self.date, "sources", _sources(self.sources))
        db.save_extra(conn, self.date, "collection_window", self.collection_window)
        if articles is not None:
            db.save_extra(conn, self.date, "articles", [article_record(a) for a in articles])
        if clusters is not None:
            db.save_extra(conn, self.date, "record_coverage", _record_coverage(clusters, _sources(self.sources)))

    def page_data(self, base_url: str, sample: bool = False, data_url: str | None = None,
                  corrections: list[dict] | None = None, research_url: str | None = None,
                  research: dict | None = None) -> dict:
        """What the reader page and the feed function work from."""
        return {
            "edition": self.date,
            "sample": sample,
            "base_url": base_url,
            "repo_url": config.REPO_URL,
            "contact_email": config.CONTACT_EMAIL,
            "data_url": data_url,
            "corrections": corrections or [],
            "ledger": ledger.load(),
            "markets": self.markets,
            "feeds_down": self.feeds_down,
            "collection_window": self.collection_window,
            "coverage_known": self.coverage_known,
            "research_url": research_url,
            "research": research,
            "rubric": _rubric(),
            "topics": TOPICS,
            "topic_descriptions": TOPIC_DESCRIPTIONS,
            "topic_aliases": LEGACY,
            "sources": _sources(self.sources),
            "stories": [
                {
                    "id": s.id,
                    "headline": s.headline,
                    "bullets": s.bullets,
                    "whats_next": s.whats_next,
                    "topic": s.topic,
                    "checks": s.checks,
                    "written_by": s.written_by,
                    "day": s.day,
                    "sides": s.sides,
                    "articles": _page_articles(s.articles),
                }
                for s in self.stories
            ],
        }

    def public_sources(self) -> dict:
        """The outlets and the rubric, as edition files hold them."""
        return {"rubric": _rubric(), "sources": _sources(self.sources)}

    def _left_out(self, sports: list[list[Article]]) -> dict:
        """Groups that passed the score and were not written, and why."""
        return {"sports": {
            "rule": {"outlets_in_sections": "more than half", "official_source": "never left out",
                     "sections": list(rubric.SPORTS_SECTIONS), "keep_words": list(rubric.HARD_NEWS_WORDS)},
            "groups": [
                {
                    "titles": [a.title for a in g],
                    "articles": [a.url for a in g],
                    "from_sports_sections": [a.url for a in g if rubric.in_sports_section(a.url)],
                    "score": rubric.score(self.sources[a.source_id] for a in g).to_dict(),
                }
                for g in sports
            ],
        }}

    def file_data(self, articles: list[Article], clusters: list[list[Article]], model: str,
                  usage: dict | None = None, sports: list[list[Article]] = (), grouping: dict | None = None) -> dict:
        """The public record of the run. Needs saved stories, for their ids."""
        return {
            "format": FORMAT,
            "edition": self.date,
            "generated_at": db.now_iso(),
            "rubric": _rubric(),
            "editorial": {
                "style_guide_sha256": _sha(config.STYLE_GUIDE_PATH),
                "banned_words_sha256": _sha(config.BANNED_WORDS_PATH),
                "model": model,
                "usage": usage,  # input and output tokens across the run; null if no model reported any
                "grouping": grouping,  # how articles were grouped: method, model and threshold
            },
            "sources": _sources(self.sources),
            "articles": [article_record(a) for a in articles],
            "clusters": [[a.key for a in g] for g in clusters],
            "collection_window": self.collection_window,
            "left_out": self._left_out(sports),
            "feeds_down": self.feeds_down,
            "markets": self.markets,
            "stories": [
                {
                    "id": s.id,
                    "headline": s.headline, "bullets": s.bullets, "whats_next": s.whats_next,
                    "topic": s.topic, "region": s.region, "written_by": s.written_by,
                    "checks": s.checks, "thread_id": s.thread_id, "day": s.day, "sides": s.sides,
                    "articles": [a.key for a in s.articles],
                    "reposts": {url: first.url for url, first in reposts(s.articles).items()},
                    "score": rubric.score(self.sources[a.source_id] for a in s.articles
                                          if a.source_id in self.sources).to_dict(),
                }
                for s in self.stories
            ],
        }

    def write_file(self, directory: Path, articles: list[Article], clusters: list[list[Article]], model: str,
                   usage: dict | None = None, sports: list[list[Article]] = (), grouping: dict | None = None) -> Path:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.date}.json"
        path.write_text(json.dumps(self.file_data(articles, clusters, model, usage, sports, grouping), ensure_ascii=False, indent=1))
        return path


def _restore_file(conn, data: dict) -> None:
    if data.get("format", 1) > FORMAT:
        raise ValueError(f"edition {data['edition']} has format {data['format']}; this code reads up to {FORMAT}")
    by_key = {}
    for raw in data["articles"]:
        a = Article(raw["source_id"], raw["url"], raw["title"], raw["summary"], raw["published_at"],
                    event_id=raw.get("event_id", ""))
        by_key[raw.get("key", raw["url"])] = a
    db.upsert_articles(conn, list(by_key.values()))
    for a in by_key.values():
        a.id = conn.execute("SELECT id FROM articles WHERE url=? AND event_id=?",
                            (a.url, a.event_id)).fetchone()[0]
    stories = [
        Story(
            edition_date=data["edition"],
            headline=s["headline"],
            bullets=s["bullets"],
            whats_next=s["whats_next"],
            topic=s["topic"],
            region=s["region"],
            written_by=s["written_by"],
            articles=[by_key[key] for key in s["articles"] if key in by_key],
            id=s.get("id"),
            checks=s.get("checks", {}),
            thread_id=s.get("thread_id"),
            day=s.get("day", 1),
            sides=s.get("sides", {}),
        )
        for s in data["stories"]
    ]
    db.replace_edition(conn, data["edition"], stories)
    db.save_extra(conn, data["edition"], "markets", data.get("markets", []))
    db.save_extra(conn, data["edition"], "feeds_down", data.get("feeds_down", []))
    if "sources" in data:
        db.save_extra(conn, data["edition"], "sources", data["sources"])
    db.save_extra(conn, data["edition"], "articles", [article_record(a) for a in by_key.values()])
    db.save_extra(conn, data["edition"], "collection_window", data.get("collection_window"))
    if "clusters" in data:
        groups = [[by_key[key] for key in group if key in by_key] for group in data["clusters"]]
        db.save_extra(conn, data["edition"], "record_coverage", _record_coverage(groups, data.get("sources", {})))


def restore(directory: Path, db_path: Path) -> int:
    """Rebuild the database from edition files, oldest first. Returns editions restored."""
    conn = db.connect(db_path)
    files = sorted(Path(directory).glob("*.json"))
    for f in files:
        _restore_file(conn, json.loads(f.read_text()))
    conn.close()
    return len(files)
