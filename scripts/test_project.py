import sys,unittest,csv,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
from chapters import CHAPTERS,DAYS,SOURCES
class TestProject(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(CHAPTERS),26);self.assertEqual(len(DAYS),30)
        self.assertEqual(len(list((ROOT/'templates').iterdir())),25)
    def test_distinct_lesson_pages(self):
        for no,*_ in CHAPTERS:
            f=ROOT/'docs'/'lessons'/f'{no}.html'
            self.assertTrue(f.exists());self.assertGreater(f.stat().st_size,2000)
    def test_real_steps(self):
        for x in CHAPTERS:
            self.assertEqual(len(x[4]),5);self.assertGreaterEqual(len(x[5]),10)
    def test_sitemap(self):
        s=(ROOT/'docs/sitemap.xml').read_text()
        self.assertEqual(s.count('<loc>'),60)
        self.assertTrue(s.startswith('<?xml'))
    def test_urls_and_citation_distinction(self):
        s=(ROOT/'docs/tools.html').read_text()
        self.assertIn('品牌提及',s);self.assertIn('引用',s)
        self.assertTrue(all(x[1].startswith('https://') for x in SOURCES))
    def test_question_sample_count(self):
        with (ROOT/'templates/02-question-bank-30.csv').open(encoding='utf-8-sig') as f:
            self.assertEqual(len(list(csv.reader(f)))-1,30)
    def test_v2_labs_and_cases(self):
        self.assertEqual(len(list((ROOT/'labs').glob('*.md'))),16)
        self.assertEqual(len(list((ROOT/'cases').glob('*.md'))),6)
        self.assertTrue((ROOT/'docs/diagnose.html').exists())
        self.assertTrue((ROOT/'docs/measure.html').exists())
    def test_source_data_rebuildable(self):
        self.assertTrue((ROOT/'scripts/build.py').exists())
        self.assertTrue((ROOT/'.github/workflows/pages.yml').exists())
if __name__=='__main__':unittest.main()
