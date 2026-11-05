import sys,unittest,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from site_audit import audit_html
from geo_report import compute
class TestTools(unittest.TestCase):
    def test_good_html(self):
        html=(ROOT/'examples/sample-good.html').read_text()
        got=audit_html(html,'https://example.com/article')
        self.assertNotIn('noindex',[x['code'] for x in got['issues']])
        self.assertEqual(len([h for h in got['headings'] if h['level']=='h1']),1)
        self.assertTrue(got['jsonld'][0]['valid_json'])
    def test_bad_html(self):
        html=(ROOT/'examples/sample-broken.html').read_text()
        got=audit_html(html)
        codes={x['code'] for x in got['issues']}
        self.assertIn('noindex',codes)
        self.assertIn('missing_title',codes)
        self.assertIn('h1_count',codes)
        self.assertIn('missing_canonical',codes)
    def test_bad_schema(self):
        got=audit_html('<html><script type="application/ld+json">{invalid}</script></html>')
        self.assertIn('invalid_jsonld',[x['code'] for x in got['issues']])
    def test_jsonld_separate_from_regular_scripts(self):
        html='<html><body><script type="application/ld+json">{"@type":"Organization"}</script><script>console.log(1)</script></body></html>'
        a=audit_html(html)
        self.assertTrue(a['jsonld'][0]['valid_json'])
    def test_numerators_and_exclusions(self):
        rows=[dict(date='a',platform='x',region='cn',phase='baseline',question_type='natural',ai_answer_triggered='1',query='a',brand_mentioned='1',owned_url_cited='1',citation_url='https://example.com',evidence='x'),dict(date='a',platform='x',region='cn',phase='baseline',question_type='brand',ai_answer_triggered='1',query='b',brand_mentioned='1',owned_url_cited='1',citation_url='https://example.com',evidence='x'),dict(date='a',platform='x',region='cn',phase='baseline',question_type='natural',ai_answer_triggered='0',query='c',brand_mentioned='0',owned_url_cited='0',citation_url='',evidence='x')]
        report=compute(rows)
        self.assertEqual(report['valid_samples'],1)
        self.assertEqual(report['excluded']['brand'],1)
        self.assertEqual(report['excluded']['not_triggered'],1)
        self.assertEqual(report['groups'][0]['citation_rate_pct'],100.0)
    def test_synthetic_sample(self):
        with (ROOT/'examples/synthetic-visibility.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
        report=compute(rows)
        self.assertEqual(report['total_rows'],30)
        self.assertGreater(report['valid_samples'],0)
        self.assertGreater(report['excluded']['brand'],0)
        self.assertGreater(report['excluded']['not_triggered'],0)
    def test_empty_samples(self):
        r=compute([])
        self.assertEqual(r['valid_samples'],0)
        self.assertEqual(r['groups'],[])
if __name__=='__main__':unittest.main()
