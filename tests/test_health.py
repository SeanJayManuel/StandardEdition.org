"""A thin edition is still published, and the maintainer is told."""

import json

from standardedition import config, health
from tests.test_run import workflow


def edition(stories=6, down=(), sources=8, writer="claude-test"):
    return {"sources": {f"s{i}": {} for i in range(sources)}, "feeds_down": list(down),
            "stories": [{"headline": f"Story {i}", "written_by": writer} for i in range(stories)]}


def test_a_normal_edition_raises_nothing():
    assert health.problems(edition(down=["s1", "s2"])) == []


def test_the_first_live_edition_is_healthy():
    assert health.problems(json.loads((config.ROOT / "archive" / "2026-11-13.json").read_text())) == []


def test_many_unreadable_feeds_are_reported_by_name():
    assert health.problems(edition(down=["s3", "s1", "s2"])) == ["3 of 8 feeds couldn't be read: s1, s2, s3."]


def test_too_few_stories_are_reported():
    assert health.problems(edition(stories=4)) == ["The edition has 4 stories. Fewer than 5 is unusual."]


def test_fallback_stories_are_counted_without_their_headlines():
    found = health.problems(edition(writer="fallback"))
    assert found == ["6 of 6 stories were written by the fallback writer, not a model."]


def test_the_command_prints_one_line_per_problem(tmp_path, capsys):
    (tmp_path / "2026-11-01.json").write_text(json.dumps(edition()))
    (tmp_path / "2026-11-02.json").write_text(json.dumps(edition(stories=1)))
    (tmp_path / "index.json").write_text("[]")  # not an edition file, so never the newest
    assert health.main(["--archive", str(tmp_path)]) == 0
    assert capsys.readouterr().out == "- The edition has 1 story. Fewer than 5 is unusual.\n"


def test_the_alert_job_can_only_write_issues():
    flow = workflow("nightly.yml")
    alert = flow["jobs"]["alert"]
    assert flow["permissions"] == {"contents": "read"} and alert["permissions"] == {"issues": "write"}
    assert alert["needs"] == ["build", "archive", "deploy"] and "always()" in alert["if"]
    assert "secrets." not in json.dumps(alert)
    steps = flow["jobs"]["build"]["steps"]
    names = [s.get("name") for s in steps]
    assert names.index("Check the edition for thin coverage") == names.index("Build today's edition") + 1
