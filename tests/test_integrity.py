"""Regression cases for verification and immutable historical evidence."""
import json
from datetime import datetime, timezone

import pytest

from boringnews import db, research
from boringnews.edition import Edition, restore
from boringnews.ingest import congress_items
from boringnews.rewrite import Draft, check_facts
from boringnews.sources import Source

SOURCES = {'wire': Source('wire', 'Wire', '', 'center', 'wire'),
           'gov': Source('gov', 'Congress', '', 'unrated', 'primary', role='record')}

@pytest.mark.parametrize('reply', [[], [{'n': 1}], [{'n': 1, 'supported': 'false'}],
    [{'n': 1, 'supported': True}, {'n': 1, 'supported': False}], [{'n': 2, 'supported': True}]])
def test_invalid_verdicts_never_count_as_verified(reply):
    class Writer:
        checks_facts = True
        def complete(self, *args, **kwargs):
            return json.dumps(reply)
    d = Draft('A statement', ['The bill passed.'], None, 'government', 'us', 'test')
    a = db.Article('wire', 'https://example.org/news', 'The bill passed.', '', '2026-11-01T12:00:00+00:00')
    result = check_facts(d, [a], SOURCES, Writer())
    assert result.checks['method'] != 'numbers+model'
    assert result.checks['claims'][0]['status'] == 'unchecked'


def bill(day, action):
    return congress_items({'bills': [{'type': 'HR', 'number': '1', 'congress': 119,
        'title': 'A bill', 'latestAction': {'actionDate': day, 'text': action}}]}, 'gov',
        datetime(2026, 1, 1, tzinfo=timezone.utc))[0]


def test_bill_actions_are_distinct_and_restore_without_changing_history(tmp_path):
    conn = db.connect(tmp_path / 'a.db')
    first = bill('2026-11-01', 'Passed House')
    second = bill('2026-11-10', 'Became Public Law No: 119-1.')
    assert first.url == second.url
    assert db.upsert_articles(conn, [first, second, second]) == 2
    early = db.articles_between(conn, '2026-11-01', '2026-11-02')[0]
    late = db.articles_between(conn, '2026-11-10', '2026-11-11')[0]
    assert early.summary != late.summary
    for a, day in [(early, '2026-11-01'), (late, '2026-11-10')]:
        story = db.Story(day, a.title, [a.summary], None, 'government', 'us', 'fallback', [a])
        edition = Edition(day, [story], SOURCES)
        edition.save(conn, [a])
        edition.write_file(tmp_path / 'archive', [a], [[a]], 'fallback')
    restore(tmp_path / 'archive', tmp_path / 'restored.db')
    restored = db.connect(tmp_path / 'restored.db')
    assert db.load_edition(restored, '2026-11-01')[0].articles[0].summary == early.summary
    assert db.load_edition(restored, '2026-11-10')[0].articles[0].summary == late.summary


def test_research_includes_unwritten_records_and_historical_context(tmp_path):
    conn = db.connect(tmp_path / 'a.db')
    a = db.Article('gov', 'https://example.org/record', 'A rule', 'A public rule.', '2026-11-01T12:00:00+00:00')
    db.upsert_articles(conn, [a])
    a = db.articles_between(conn, '2026-11-01', '2026-11-02')[0]
    edition = Edition('2026-11-01', [], SOURCES, feeds_down=['wire'])
    edition.save(conn, [a])
    idx = research.build(conn, {})
    assert len(idx['records']) == 1
    assert idx['records'][0]['story'] is None
    assert idx['editions']['2026-11-01']['sources']['wire']['lean'] == 'center'
    assert idx['editions']['2026-11-01']['feeds_down'] == ['wire']


def test_citations_must_quote_a_supplied_article_verbatim():
    class Writer:
        checks_facts = True
        def complete(self, *args, **kwargs):
            return json.dumps([{'n': 1, 'supported': True, 'sources': [
                {'article': 1, 'quote': 'The bill passed.'},
                {'article': 2, 'quote': 'The bill passed.'},
                {'article': 1, 'quote': 'The governor signed it.'}]}])
    a = db.Article('wire', 'https://example.org/news', 'The bill passed.', '', '2026-11-01T12:00:00+00:00')
    d = Draft('A statement', ['The bill passed.'], None, 'government', 'us', 'test')
    result = check_facts(d, [a], SOURCES, Writer())
    assert result.checks['claims'] == [{'text': 'The bill passed.', 'status': 'model-supported',
        'sources': [{'source_id': 'wire', 'url': a.url, 'quote': 'The bill passed.'}]}]


def test_legacy_database_migration_preserves_story_article_links(tmp_path):
    import sqlite3
    path = tmp_path / 'legacy.db'
    old = sqlite3.connect(path)
    legacy_schema = db.SCHEMA.replace("    event_id     TEXT NOT NULL DEFAULT '',\n", '').replace(
        'url          TEXT NOT NULL,', 'url          TEXT NOT NULL UNIQUE,').replace(
        "fetched_at   TEXT NOT NULL,\n    UNIQUE(url, event_id)", 'fetched_at   TEXT NOT NULL')
    old.executescript(legacy_schema)
    old.execute("INSERT INTO articles VALUES (1, 'wire', 'https://example.org/a', 'Old title', 'Old text', '2026-11-01', '2026-11-01')")
    old.execute("INSERT INTO stories (id,edition_date,headline,bullets,topic,region,written_by,created_at) VALUES (1,'2026-11-01','Old title','[]','world','us','fallback','2026-11-01')")
    old.execute('INSERT INTO story_articles VALUES (1,1)')
    old.commit()
    old.close()
    conn = db.connect(path)
    assert db.load_edition(conn, '2026-11-01')[0].articles[0].summary == 'Old text'
    assert conn.execute('PRAGMA foreign_key_check').fetchall() == []
    assert conn.execute('PRAGMA foreign_keys').fetchone()[0] == 1


def test_legacy_research_never_claims_historical_monitoring(tmp_path):
    conn = db.connect(tmp_path / 'a.db')
    db.replace_edition(conn, '2026-11-01', [db.Story('2026-11-01', 'A story', ['Text'], None, 'world', 'us', 'fallback')])
    context = research.build(conn, SOURCES)['editions']['2026-11-01']
    assert context['coverage_known'] is False
    assert context['records_complete'] is False


def test_unwritten_records_keep_observed_coverage_and_deduplicate_windows(tmp_path):
    conn = db.connect(tmp_path / 'a.db')
    record = db.Article('gov', 'https://example.org/record', 'A rule', 'A public rule.', '2026-11-01T12:00:00+00:00')
    report = db.Article('wire', 'https://example.org/report', 'A rule', 'The rule passed.', '2026-11-01T12:00:00+00:00')
    db.upsert_articles(conn, [record, report])
    arts = db.articles_between(conn, '2026-11-01', '2026-11-02')
    for date in ['2026-11-01', '2026-11-02']:
        edition = Edition(date, [], SOURCES)
        edition.save(conn, arts, [arts])
    idx = research.build(conn, SOURCES)
    assert len(idx['records']) == 1
    assert idx['records'][0]['outlets'] == 1
    assert idx['records'][0]['story'] is None


def test_incomplete_side_verdicts_are_not_published():
    class Writer:
        checks_facts = True
        def complete(self, *args, **kwargs):
            return '[]'
    src = dict(SOURCES, left=Source('left', 'Left', '', 'left', 'national'))
    arts = [db.Article(s, f'https://example.org/{s}', 'The bill passed.', '', '2026-11-01T12:00:00+00:00')
            for s in ('wire', 'left')]
    d = Draft('A statement', ['The bill passed.'], None, 'government', 'us', 'test',
              sides={'center': ['The bill passed.'], 'left': ['The bill passed.']})
    result = check_facts(d, arts, src, Writer())
    assert result.sides == {}
    assert len(result.checks['dropped']) == 2


def test_historical_edition_uses_saved_labels_after_source_removal(tmp_path):
    conn = db.connect(tmp_path / 'a.db')
    a = db.Article('wire', 'https://example.org/report', 'A report', 'Text.', '2026-11-01T12:00:00+00:00')
    db.upsert_articles(conn, [a])
    a = db.articles_between(conn, '2026-11-01', '2026-11-02')[0]
    story = db.Story('2026-11-01', 'A report', ['Text.'], None, 'world', 'us', 'fallback', [a])
    Edition('2026-11-01', [story], SOURCES).save(conn, [a])
    changed = {'new': Source('new', 'New outlet', '', 'right', 'national')}
    historical = Edition.load(conn, changed, '2026-11-01')
    assert historical.sources['wire'].lean == 'center'
    assert 'new' not in historical.sources
    idx = research.build(conn, changed)
    assert idx['stories'][0]['articles'][0]['source_id'] == 'wire'
    assert 'new' not in idx['editions']['2026-11-01']['sources']


def test_two_actions_in_one_archive_roundtrip_by_event_key(tmp_path):
    conn = db.connect(tmp_path / 'a.db')
    first = bill('2026-11-10', 'Passed House')
    second = bill('2026-11-10', 'Became Public Law No: 119-1.')
    db.upsert_articles(conn, [first, second])
    arts = db.articles_between(conn, '2026-11-10', '2026-11-11')
    stories = [db.Story('2026-11-10', a.title, [a.summary], None, 'government', 'us', 'fallback', [a]) for a in arts]
    edition = Edition('2026-11-10', stories, SOURCES)
    edition.save(conn, arts, [[a] for a in arts])
    edition.write_file(tmp_path / 'archive', arts, [[a] for a in arts], 'fallback')
    restore(tmp_path / 'archive', tmp_path / 'r.db')
    restored = db.load_edition(db.connect(tmp_path / 'r.db'), '2026-11-10')
    assert len({s.articles[0].event_id for s in restored}) == 2
    assert {s.articles[0].summary for s in restored} == {a.summary for a in arts}


def test_duplicate_feed_urls_share_one_archive_identity(tmp_path):
    conn = db.connect(tmp_path / 'duplicates.db')
    first = db.Article('wire', 'https://example.org/shared', 'Original', '', '2026-11-01')
    other_feed = db.Article('other', first.url, 'Reposted', '', '2026-11-01')
    assert db.upsert_articles(conn, [first, other_feed]) == 1
    articles = db.articles_between(conn, '2026-11-01', '2026-11-02')
    assert len({a.key for a in articles}) == len(articles)
