"""Measure a fixture export with a year of durable pages; no live integrations."""
import argparse
import contextlib
import gzip
import io
import json
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from boringnews.pipeline import main as pipeline
from boringnews.export_static import main as export


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=int, default=365)
    args = parser.parse_args()
    if not 1 <= args.days <= 3660:
        parser.error('--days must be between 1 and 3660')
    with tempfile.TemporaryDirectory(prefix='standard-edition-perf-') as temp:
        root = Path(temp)
        archive, db, site = root / 'archive', root / 'data.db', root / 'site'
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline(['run', '--fixtures', '--mock-llm', '--date', '2026-11-04', '--db', str(db), '--archive', str(archive)])
            sample = json.loads((archive / '2026-11-04.json').read_text())
            for offset in range(1, args.days):
                snapshot = json.loads(json.dumps(sample))
                day = str(date(2026, 11, 4) - timedelta(days=offset))
                snapshot['edition'] = day
                for story in snapshot['stories']:
                    story['id'] += offset * 1000
                (archive / f'{day}.json').write_text(json.dumps(snapshot))
            start = time.perf_counter()
            export(['--db', str(db), '--archive', str(archive), '--out', str(site), '--sample'])
            elapsed = time.perf_counter() - start
        files = [p for p in site.rglob('*') if p.is_file()]
        result = {'synthetic_archive_days': args.days, 'export_seconds': round(elapsed, 3),
                  'files': len(files), 'total_bytes': sum(p.stat().st_size for p in files),
                  'gzip_bytes': {name: len(gzip.compress((site / name).read_bytes(), mtime=0))
                                 for name in ['index.html', 'edition.json', 'research.json', 'story-index.json']}}
        print(json.dumps(result, indent=2))
        if result['gzip_bytes']['index.html'] > 100_000:
            raise SystemExit('Fixture homepage exceeds 100 KB gzip budget')


if __name__ == '__main__':
    main()
