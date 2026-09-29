import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from product import VERSION,DISPLAY_VERSION

class BetaVersioning(unittest.TestCase):
    def test_registry_starts_at_zero_and_matches_application(self):
        data=json.loads((ROOT/'docs/versions.json').read_text('utf-8'))
        rows=data['versions'];self.assertEqual(data['stage'],'beta')
        self.assertEqual([r['beta'] for r in rows],[f'0.0.{i}' for i in range(len(rows))])
        self.assertEqual(VERSION,rows[-1]['beta']+'-beta')
        self.assertEqual(DISPLAY_VERSION,'Beta '+rows[-1]['beta'])
        self.assertEqual(rows[-1]['tag'],'v'+VERSION)
        self.assertTrue(any(r['original']=='MacroPescaSlayers2.ahk' for r in rows))
        self.assertEqual(len({r['original'] for r in rows}),len(rows))
        self.assertEqual(next(r for r in rows if r['original']=='v7.4.0')['beta'],'0.0.30')

    def test_local_links_and_all_three_historical_tables(self):
        rows=json.loads((ROOT/'docs/versions.json').read_text('utf-8'))['versions']
        for name in ('VERSIONAMENTO.md','VERSIONING.en.md','VERSIONING.es.md'):
            text=(ROOT/'docs'/name).read_text('utf-8')
            for row in rows:self.assertIn('| Beta '+row['beta']+' |',text)
        for file in [ROOT/'README.md',ROOT/'CHANGELOG.md',*list((ROOT/'docs').glob('*.md'))]:
            for target in re.findall(r'\]\(([^)]+)\)',file.read_text('utf-8')):
                if '://' in target or target.startswith('#'):continue
                self.assertTrue((file.parent/target.split('#')[0]).exists(),(file.name,target))
