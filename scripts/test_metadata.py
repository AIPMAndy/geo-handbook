"""SEO/GEO consistency test for every URL published in the GEO sitemap."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BASE = "https://aipmandy.github.io/geo-handbook/"


class PublicMetadataTests(unittest.TestCase):
    def test_every_sitemap_page_has_one_correct_canonical_and_real_jsonld(self):
        sitemap = ET.parse(DOCS / "sitemap.xml")
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [node.text for node in sitemap.findall(".//sm:loc", namespace)]
        self.assertGreaterEqual(len(urls), 60)
        self.assertEqual(len(urls), len(set(urls)), "Duplicate URLs in sitemap")
        self.assertIn(BASE, urls, "Homepage canonical root omitted")
        self.assertNotIn(BASE + "index.html", urls, "Duplicate homepage canonical")
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(url.startswith(BASE))
                relative = url.removeprefix(BASE) or "index.html"
                path = DOCS / relative
                self.assertTrue(path.exists(), relative)
                html = path.read_text(encoding="utf-8")
                title = re.findall(r"<title>(.*?)</title>", html, re.S | re.I)
                self.assertEqual(len(title), 1, relative)
                self.assertTrue(title[0].strip())
                canonical = re.findall(r"<link\s+rel=['\"]canonical['\"]\s+href=['\"]([^'\"]+)['\"]", html)
                self.assertEqual(canonical, [url], relative)
                schema = re.findall(r"<script\s+type=['\"]application/ld\+json['\"]>(.*?)</script>", html, re.S)
                self.assertEqual(len(schema), 1, relative)
                data = json.loads(schema[0])
                self.assertEqual(data["@context"], "https://schema.org")
                self.assertEqual(data["@type"], "WebSite" if url == BASE else "WebPage")
                self.assertEqual(data["url"], url)
                self.assertEqual(data["publisher"]["name"], "星觉科技")
                self.assertEqual(data["publisher"]["url"], "https://www.a6no1.cn/")
                for text in ("AIPMAndy", "https://metaver.vip/", "https://www.a6no1.cn/", "downloads/geo-handbook-guide.pdf"):
                    self.assertIn(text, html)

    def test_robot_and_download_distribution(self):
        robots = (DOCS / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap: " + BASE + "sitemap.xml", robots)
        homepage = (DOCS / "index.html").read_text(encoding="utf-8")
        self.assertIn("download", homepage)
        self.assertIn("downloads/geo-handbook-guide.pdf", homepage)


if __name__ == "__main__":
    unittest.main()
