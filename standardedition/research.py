"""Historical research with edition-specific source and availability context.

Records are indexed from all ingested edition inputs, independently of whether
selection wrote a summary. Absence from a feed is never evidence of noncoverage
when the historical source/health snapshot is unavailable.
"""
from __future__ import annotations

from .db import editions, load_edition, load_extra
from .edition import article_record
from .sources import Source

DAYS = 30


def build(conn, sources: dict[str, Source], days: int = DAYS) -> dict:
    dates = editions(conn)[:days]
    stories, records, contexts = [], [], {}
    seen_records = set()
    for d in dates:
        snapshot = load_extra(conn, d, "sources")
        known = snapshot is not None
        historical = snapshot if known else {sid: src.record() for sid, src in sources.items()}
        contexts[d] = {"sources": historical, "feeds_down": load_extra(conn, d, "feeds_down", []),
                       "coverage_known": known, "collection_window": load_extra(conn, d, "collection_window")}
        record_coverage = load_extra(conn, d, "record_coverage", {})
        associations, attached = {}, {}
        for s in load_edition(conn, d):
            key = f"{d}-{s.id}"
            arts = s.articles
            outlet_ids = {a.source_id for a in arts if historical.get(a.source_id, {}).get("type") not in (None, "primary")}
            stories.append({
                "key": key, "id": s.id, "date": d, "headline": s.headline, "bullets": s.bullets,
                "topic": s.topic, "day": s.day, "thread_id": s.thread_id, "written_by": s.written_by,
                "checks": s.checks, "whats_next": s.whats_next, "sides": s.sides,
                "articles": [{"source_id": a.source_id, "title": a.title, "url": a.url,
                              "published_at": a.published_at} for a in arts],
            })
            for a in arts:
                attached[a.key] = article_record(a)
                associations[a.key] = {"story": key, "story_headline": s.headline, "outlets": len(outlet_ids)}
        inputs = load_extra(conn, d, "articles")
        # Legacy caches cannot reconstruct unselected inputs. Retain attached
        # records and expose corpus completeness instead of inventing evidence.
        contexts[d]["records_complete"] = inputs is not None
        for a in inputs if inputs is not None else attached.values():
            src = historical.get(a["source_id"], {})
            identity = (a["source_id"], a["url"], a.get("event_id", ""))
            if src.get("type") != "primary" or identity in seen_records:
                continue
            seen_records.add(identity)
            article_key = a.get("key", a["url"])
            association = associations.get(article_key, {"story": None, "story_headline": None,
                                                         "outlets": record_coverage.get(article_key, 0)})
            records.append({
                "date": d, "published_at": a["published_at"], "source_id": a["source_id"],
                "source": src, "role": src.get("role"), "title": a["title"],
                "summary": a["summary"], "url": a["url"],
                **association,
            })
    return {"days": dates, "stories": stories, "records": records, "editions": contexts}
