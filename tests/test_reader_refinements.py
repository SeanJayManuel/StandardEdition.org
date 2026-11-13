"""Reader contracts exercised with the actual rendered scripts and shared core."""
import json
import subprocess
from pathlib import Path

from boringnews import config
from boringnews.render import render_page
from tests.test_published_site import site, edition  # shared fixture, exported through the real pipeline


def node(script, *args):
    result = subprocess.run(['node', '-e', script, *map(str, args)], cwd=config.ROOT, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_historical_absence_requires_monitored_readable_sources():
    result = node(r'''
require('./web/core.js');
const src=(name,lean='center')=>({name,lean,type:'national'});
const old={read:src('Read'),down:src('Failed'),removed:src('Removed')};
const current={read:old.read,down:old.down,added:src('New')};
const st={date:'2026-01-01',articles:[{source_id:'read'}]};
const c=BoringCore.research.coverageContext({editions:{'2026-01-01':{sources:old,coverage_known:true,feeds_down:['down']}}},st,current);
const unknown=BoringCore.research.coverageContext({},st,current);
console.log(JSON.stringify({c,unknown}));
''')
    assert result['c']['not_observed'] == ['removed']
    assert result['c']['unavailable'] == ['down']
    assert result['c']['not_monitored'] == ['added']
    assert result['unknown']['not_observed'] == []
    assert result['unknown']['known'] is False


def test_categories_preserve_focus_and_recipe_typing_does_not_rebuild_news(site, tmp_path):
    page = tmp_path / 'reader.html'
    page.write_text(render_page(edition(site)))
    result = node(r'''
const {JSDOM}=require('jsdom'), fs=require('fs');
const dom=new JSDOM(fs.readFileSync(process.argv[1],'utf8'), {url:'https://news.example/',runScripts:'dangerously',pretendToBeVisual:true,
 beforeParse(w){w.scrollTo=()=>{};w.HTMLElement.prototype.scrollIntoView=()=>{};}});
const d=dom.window.document, world=d.getElementById('topics-world');
world.focus();world.click();
const narrowed={focus:d.activeElement.id,all:d.getElementById('all-topics').checked,world:world.checked};
d.getElementById('reset').click();
const all=[...d.querySelectorAll('#topics input')].every(x=>x.checked);
const lead=d.querySelector('#spotlight article');
const name=d.getElementById('recipe-name');name.value='My morning';name.dispatchEvent(new dom.window.Event('input'));
setTimeout(()=>{console.log(JSON.stringify({narrowed,all,advanced:d.querySelector('.advanced-settings').open,
 stable:lead===d.querySelector('#spotlight article'),recipe:d.getElementById('recipe-link').value}));dom.window.close();},180);
''', page)
    assert result['narrowed'] == {'focus': 'topics-world', 'all': False, 'world': False}
    assert result['all'] and not result['advanced']
    assert result['stable'] and 'recipe=My%20morning' in result['recipe']


def test_fonts_are_local_and_published(site):
    html = (site / 'index.html').read_text()
    assert 'fonts.googleapis.com' not in html and 'fonts.gstatic.com' not in html
    assert '/brand/fonts/literata-400.woff' in html
    assert (site / 'brand/fonts/literata-400.woff').stat().st_size > 1000
    assert (site / 'brand/fonts/Literata-OFL.txt').is_file()


def test_sample_archive_discloses_invented_content(site):
    for path in [site / 'editions/index.html', site / 'editions/2026-11-04/index.html',
                 next((site / 'editions/2026-11-04/stories').glob('*/index.html'))]:
        assert 'invented' in path.read_text()


def test_initial_reader_asset_budget_and_lazy_research(site):
    import gzip
    html = (site / 'index.html').read_bytes()
    assert len(gzip.compress(html, mtime=0)) <= 100_000
    assert edition(site)['research'] is None
    assert edition(site)['research_url'] == 'research.json'
    fonts = list((site / 'brand/fonts').glob('*.woff'))
    assert sum(p.stat().st_size for p in fonts) <= 400_000
