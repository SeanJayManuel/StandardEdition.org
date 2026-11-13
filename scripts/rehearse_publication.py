"""Build or recover a fictional publication through the production interfaces.

The recovery phase needs only the saved artifact and the matching source checkout.
It never fetches feeds, calls a model, pushes archives, or deploys a website.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from boringnews import config
from boringnews.archive import main as restore
from boringnews.export_static import main as export
from boringnews.pipeline import main as pipeline

BASE_URL = 'https://rehearsal.invalid'


def fingerprints(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def build(artifact):
    if artifact.exists():
        raise ValueError('Choose a new artifact directory; existing data is never overwritten.')
    artifact.mkdir(parents=True)
    archive = artifact / 'archive'
    with tempfile.TemporaryDirectory(prefix='edition-build-') as tmp:
        db = Path(tmp) / 'build.db'
        for day in ['2026-11-03', '2026-11-04']:
            pipeline(['run', '--fixtures', '--mock-llm', '--date', day,
                      '--db', str(db), '--archive', str(archive)])
        export(['--db', str(db), '--archive', str(archive), '--out', str(artifact / 'site'),
                '--base-url', BASE_URL, '--sample'])
    shutil.copytree(config.ROOT / 'functions', artifact / 'functions')
    (artifact / 'web').mkdir()
    for name in ['package.json', 'package-lock.json', 'web/core.js']:
        shutil.copy(config.ROOT / name, artifact / name)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=config.ROOT, text=True).strip()
    (artifact / 'source-commit.txt').write_text(commit + '\n')
    (artifact / 'manifest.json').write_text(json.dumps(fingerprints(artifact), indent=2) + '\n')
    print(f'Saved fictional publication to {artifact}')


def recover(artifact):
    expected = json.loads((artifact / 'manifest.json').read_text())
    actual = fingerprints(artifact)
    actual.pop('manifest.json', None)
    if actual != expected:
        raise ValueError('Saved artifact failed its integrity check.')
    # A brand-new temporary directory models loss of the runner and its SQLite cache.
    with tempfile.TemporaryDirectory(prefix='edition-recovery-') as tmp:
        root = Path(tmp)
        db, site = root / 'recovered.db', root / 'site'
        restore(['restore', '--from', str(artifact / 'archive'), '--db', str(db)])
        export(['--db', str(db), '--archive', str(artifact / 'archive'), '--out', str(site),
                '--base-url', BASE_URL, '--sample'])
        original, rebuilt = fingerprints(artifact / 'site'), fingerprints(site)
        changed = sorted(name for name in original.keys() | rebuilt.keys() if original.get(name) != rebuilt.get(name))
        if changed:
            raise ValueError('Recovery changed published files: ' + ', '.join(changed))
        print(f'Recovery passed: {len(original)} published files match byte for byte.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['build', 'recover'])
    parser.add_argument('artifact', type=Path)
    args = parser.parse_args()
    {'build': build, 'recover': recover}[args.phase](args.artifact)


if __name__ == '__main__':
    main()
