"""Published citations survive beyond the research window without JavaScript."""
import json
from html.parser import HTMLParser

from boringnews import render


SNAPSHOT = {
    "edition": "2025-01-02", "sources": {"old": {"name": "Historical outlet", "lean": "left", "type": "national"}},
    "articles": [{"source_id": "old", "url": "https://example.org/report", "title": "Original report"}],
    "stories": [{"id": 7, "headline": "An old <story>", "bullets": ["A durable fact."], "articles": ["https://example.org/report"], "written_by": "test-model", "checks": {"method": "numbers"}}],
    "feeds_down": [],
}


def test_story_is_readable_and_has_its_own_metadata_without_javascript():
    page = render.render_archived_story(SNAPSHOT, SNAPSHOT["stories"][0], "https://news.example")
    assert "A durable fact." in page and "Historical outlet" in page
    assert '<script' not in page
    assert '<title>An old &lt;story&gt; | The Standard Edition</title>' in page
    assert 'rel="canonical" href="https://news.example/editions/2025-01-02/stories/7/"' in page
    assert 'property="og:title" content="An old &lt;story&gt;"' in page
    assert "AI-generated" in page and "test-model" in page
    assert "Number presence" in page


def test_archive_keeps_historical_sources_and_safe_links():
    snapshot = json.loads(json.dumps(SNAPSHOT))
    snapshot["articles"][0]["url"] = "javascript:bad()"
    snapshot["stories"][0]["articles"] = ["javascript:bad()"]
    page = render.render_archived_story(snapshot, snapshot["stories"][0], "https://news.example")
    assert 'href="javascript:' not in page
    assert "Historical outlet" in page


def test_archive_index_and_edition_link_to_durable_pages():
    page = render.render_archived_edition(SNAPSHOT, "https://news.example")
    assert '/editions/2025-01-02/stories/7/' in page
    assert "A durable fact." in page
    index = render.render_archive_index(["2025-01-02"], "https://news.example")
    assert '/editions/2025-01-02/' in index


def test_versioned_article_references_and_claim_evidence_are_preserved():
    snapshot = json.loads(json.dumps(SNAPSHOT))
    snapshot["articles"][0]["key"] = "https://example.org/report#bn-event-signed"
    snapshot["stories"][0]["articles"] = [snapshot["articles"][0]["key"]]
    snapshot["stories"][0]["checks"]["claims"] = [{"text": "A durable fact.", "status": "model-supported", "sources": [{"source_id": "old", "url": "https://example.org/report", "quote": "The original quoted evidence."}]}]
    page = render.render_archived_story(snapshot, snapshot["stories"][0], "https://news.example")
    assert "Original report" in page
    assert "The original quoted evidence." in page
    assert 'href="https://example.org/report"' in page
    assert '#bn-event-' not in page


def test_export_retains_pages_older_than_research_and_copies_fonts(tmp_path):
    from boringnews.pipeline import main as run
    from boringnews.export_static import main as export
    archive, db, site = tmp_path / "archive", tmp_path / "data.db", tmp_path / "site"
    run(["run", "--fixtures", "--mock-llm", "--date", "2026-11-04", "--db", str(db), "--archive", str(archive)])
    (archive / "2025-01-02.json").write_text(json.dumps({**SNAPSHOT, "format": 2}))
    export(["--db", str(db), "--archive", str(archive), "--out", str(site), "--sample", "--base-url", "https://news.example"])
    old = site / "editions/2025-01-02/stories/7/index.html"
    assert old.exists() and "A durable fact." in old.read_text()
    assert "2025-01-02" in (site / "editions/index.html").read_text()
    assert "2025-01-02" not in (site / "research.json").read_text()
    assert "/editions/2025-01-02/stories/7/" in (site / "sitemap.xml").read_text()
    assert (site / "brand/fonts/Literata.woff").exists() or list((site / "brand/fonts").glob("*.woff"))
    html = (site / "index.html").read_text()
    assert "Reader settings need JavaScript" in html


def test_local_preview_serves_archived_story_without_restoring_database(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from boringnews import config, web
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "2025-01-02.json").write_text(json.dumps(SNAPSHOT))
    monkeypatch.setattr(config, "ARCHIVE_DIR", archive)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "empty.db")
    client = TestClient(web.app)
    page = client.get("/editions/2025-01-02/stories/7/")
    assert page.status_code == 200 and "A durable fact." in page.text
    assert client.get("/editions/2025-01-02/stories/999/").status_code == 404
    assert client.get("/editions/../../").status_code == 404
    assert client.get("/story-index.json").json()["7"] == "/editions/2025-01-02/stories/7/"
    assert "2025-01-02" in client.get("/editions/").text
    assert client.get("/archive/2025-01-02.json").json()["edition"] == "2025-01-02"
    assert client.get("/archive/2025-01-03.json").status_code == 404
