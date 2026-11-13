"""Render the reader page. The page is one self-contained HTML file: the page
data is embedded as JSON, and web/core.js and web/app.js filter it by the
reader's settings in the browser."""

from __future__ import annotations

import html
import json

import yaml

from . import config

WEB = config.ROOT / "web"


def load_corrections() -> list[dict]:
    if not config.CORRECTIONS_PATH.exists():
        return []
    data = yaml.safe_load(config.CORRECTIONS_PATH.read_text()) or {}
    return [{k: str(v) for k, v in c.items()} for c in (data.get("corrections") or [])]


def render_page(data: dict) -> str:
    template = (WEB / "index.html").read_text()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    # Progressive fallback: the daily news remains readable when scripts fail
    # or are disabled. Interactive filtering is an enhancement.
    import re
    fallback = '<noscript><main class="page"><h1>Edition of ' + html.escape(data["edition"]) + '</h1>'
    fallback += '<p>Showing the published edition. Reader settings need JavaScript.</p>'
    for story in data.get("stories", []):
        fallback += '<article class="story"><h2><a href="' + story_path(data["edition"], story["id"]) + '">' + html.escape(story["headline"]) + '</a></h2><ul>'
        fallback += ''.join('<li>' + html.escape(b) + '</li>' for b in story.get("bullets", [])) + '</ul></article>'
    fallback += '<p><a href="/editions/">Past editions</a></p></main></noscript>'
    template = re.sub(r"<noscript>.*?</noscript>", lambda _: fallback, template, flags=re.S)
    return (
        template.replace("__REPO_URL__", html.escape(data["repo_url"]))
        .replace("__BASE_URL__", html.escape(data["base_url"]))
        .replace("/*__CSS__*/", (WEB / "style.css").read_text())
        .replace("/*__CORE__*/", (WEB / "core.js").read_text())
        .replace("/*__EVIDENCE__*/", (WEB / "evidence.js").read_text())
        .replace("/*__SETTINGS__*/", (WEB / "settings.js").read_text())
        .replace("/*__APP__*/", (WEB / "app.js").read_text())
        .replace('"__DATA__"', payload)
    )


def story_path(date: str, story_id: int) -> str:
    """Public citation identity includes the edition date, not just a cache row id."""
    return f"/editions/{date}/stories/{int(story_id)}/"


def _escape(value) -> str:
    return html.escape(str(value), quote=True)


def _source_link(article: dict, sources: dict) -> str:
    from urllib.parse import urlsplit
    title = _escape(article.get("title", "Source"))
    url = article.get("url", "")
    if urlsplit(url).scheme in {"http", "https"}:
        title = f'<a href="{_escape(url)}" rel="noopener">{title}</a>'
    source = sources.get(article.get("source_id"), {})
    return f'<li>{title} <span class="hint">— {_escape(source.get("name", article.get("source_id", "Unknown source")))}</span></li>'


def _document(title: str, description: str, path: str, body: str, base_url: str) -> str:
    """A complete reading surface, with no JavaScript or external asset dependency."""
    css = (WEB / "style.css").read_text()
    canonical = _escape(base_url.rstrip("/") + path)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_escape(title)} | The Standard Edition</title>
<meta name="description" content="{_escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{_escape(title)}">
<meta property="og:description" content="{_escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{_escape(base_url.rstrip('/'))}/brand/social.png">
<link rel="icon" href="/brand/favicon.png"><style>{css}
.archive-reading {{ max-width: 760px; margin: 0 auto; padding: 32px 20px 64px; }}
.archive-reading h1 {{ font: 500 clamp(28px,5vw,42px)/1.2 var(--read); overflow-wrap: anywhere; }}
.archive-reading h2 {{ font: 500 26px/1.3 var(--read); }}
.archive-reading article {{ padding-block: 24px; border-bottom: 1px solid var(--line); }}
.archive-reading .archive-nav {{ display:flex; flex-wrap:wrap; gap: 8px 24px; margin-block:16px 32px; }}
.archive-reading .archive-nav a {{ display:inline-flex; align-items:center; min-height:44px; }}
.archive-reading li {{ margin-block:8px; overflow-wrap:anywhere; }}
.archive-reading details {{ margin-block:24px; }}
.archive-reading summary {{ cursor:pointer; padding-block:12px; }}
</style></head><body><div class="archive-reading">
<header><a href="/" class="headline">The Standard Edition</a><nav class="archive-nav" aria-label="Sections"><a href="/">Today</a><a href="/editions/">Past editions</a><a href="/#how-it-works">How it works</a></nav></header>
<main id="main">{body}</main><footer><p>100% transparent. 100% free. Always.</p></footer>
</div></body></html>'''


def _snapshot_articles(snapshot: dict, story: dict) -> list[dict]:
    # Format 2 stores URLs; later formats may store event identifiers. Prefer
    # explicit article snapshots whenever supplied, preserving old archives.
    articles = snapshot.get("articles", [])
    by_key = {a.get("key", a.get("url")): a for a in articles}
    by_key.update({a.get("url"): a for a in articles})
    return [a if isinstance(a, dict) else by_key[a] for a in story.get("articles", [])
            if isinstance(a, dict) or a in by_key]


def _story_body(snapshot: dict, story: dict) -> str:
    date = snapshot["edition"]
    sources = snapshot.get("sources", {})
    parts = [f'<p class="hint">Edition of {_escape(date)}</p>',
             f'<h1>{_escape(story["headline"])}</h1>']
    if snapshot.get("sample") or story.get("written_by") == "mock":
        parts.insert(0, '<p class="note">Sample edition. These stories and outlets are invented.</p>')
    writer = story.get("written_by", "")
    provenance = "Sample summary" if writer == "mock" else "Automated fallback summary" if writer == "fallback" else "AI-generated summary" if writer else "Summary provenance not recorded"
    parts.append('<p class="hint">' + provenance + (f' · {_escape(writer)}' if writer else '') +
                 '. Read the original reporting below.</p>')
    parts.append('<ul class="bullets">' + ''.join(f'<li>{_escape(b)}</li>' for b in story.get("bullets", [])) + '</ul>')
    if story.get("whats_next"):
        parts.append(f'<p class="next"><b>What’s next:</b> {_escape(story["whats_next"])}</p>')
    checks = story.get("checks", {})
    method = checks.get("method", "")
    label = "Number presence was checked; this does not establish that a claim is true."
    if method == "numbers+model":
        label += " A model also checked the summary against source text."
    elif "failed" in method:
        label += " The model check did not complete."
    elif not method:
        label = "No verification details were recorded for this edition."
    parts.append(f'<details><summary>How this summary was checked</summary><p>{_escape(label)}</p>')
    if checks.get("dropped"):
        parts.append('<p>Removed statements:</p><ul>' + ''.join(
            f'<li>{_escape(d.get("text", ""))}: {_escape(d.get("reason", ""))}</li>' for d in checks["dropped"]) + '</ul>')
    parts.append('</details>')
    claims = checks.get("claims", [])
    if claims:
        parts.append('<section><h2>Evidence for each statement</h2>')
        for claim in claims:
            parts.append(f'<details><summary>{_escape(claim.get("text", ""))}</summary>')
            parts.append(f'<p>Status: {_escape(claim.get("status", "unchecked"))}. Model support is not independent verification.</p>')
            evidence = claim.get("sources", [])
            if not evidence:
                parts.append('<p>No claim-level source evidence was recorded.</p>')
            for source in evidence:
                parts.append('<blockquote>' + _escape(source.get("quote", "")) + '</blockquote><ul>' +
                             _source_link({**source, "title": "Read the source"}, sources) + '</ul>')
            parts.append('</details>')
        parts.append('</section>')
    else:
        parts.append('<p class="hint">Claim-level source evidence was not recorded for this edition.</p>')
    parts.append('<section><h2>Original reporting and records</h2><ul>' + ''.join(
        _source_link(a, sources) for a in _snapshot_articles(snapshot, story)) + '</ul></section>')
    parts.append('<p class="hint">Coverage describes the feeds monitored for this edition, not everything an outlet published. Labels reflect that edition’s source list.</p>')
    down = snapshot.get("feeds_down", [])
    if down:
        parts.append('<p>Feeds unavailable: ' + _escape(', '.join(sources.get(s, {}).get('name', s) for s in down)) + '.</p>')
    parts.append(f'<p><a href="/archive/{_escape(date)}.json">Download this edition’s evidence</a></p>')
    return ''.join(parts)


def render_archived_story(snapshot: dict, story: dict, base_url: str) -> str:
    return _document(story["headline"], ' '.join(story.get("bullets", []))[:240],
                     story_path(snapshot["edition"], story["id"]), _story_body(snapshot, story), base_url)


def render_archived_edition(snapshot: dict, base_url: str) -> str:
    date = snapshot["edition"]
    body = f'<h1>Edition of {_escape(date)}</h1><p>The published edition, before reader settings. Source labels reflect the saved edition where available.</p>'
    if snapshot.get("sample") or any(s.get("written_by") == "mock" for s in snapshot.get("stories", [])):
        body = '<p class="note">Sample edition. These stories and outlets are invented.</p>' + body
    for story in snapshot.get("stories", []):
        heading = _escape(story["headline"])
        if story.get("id") is not None:
            heading = f'<a href="{story_path(date, story["id"])}">{heading}</a>'
        body += f'<article><h2>{heading}</h2>'
        body += '<ul class="bullets">' + ''.join(f'<li>{_escape(b)}</li>' for b in story.get("bullets", [])) + '</ul></article>'
    if not snapshot.get("stories"):
        body += '<p>No stories were published in this edition.</p>'
    return _document(f"Edition of {date}", "The complete daily edition and its original sources.", f"/editions/{date}/", body, base_url)


def render_archive_index(dates: list[str], base_url: str, sample: bool = False) -> str:
    body = '<h1>Past editions</h1><p>Permanent editions and story links. No account or JavaScript needed.</p><ul>'
    body += ''.join(f'<li><a href="/editions/{_escape(d)}/">{_escape(d)}</a></li>' for d in sorted(dates, reverse=True))
    body += '</ul>'
    if sample:
        body = '<p class="note">Sample archive. Stories and outlets are invented.</p>' + body
    return _document("Past editions", "Browse the complete Standard Edition archive.", "/editions/", body, base_url)
