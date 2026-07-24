from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote

SITE = Path(__file__).resolve().parents[1]
CATEGORY = "중등수학학원"
CAT_DIR = SITE / "전국학원" / CATEGORY
DOMAIN = "https://xn--2z1b50xixca111l.com"

report_lines: list[str] = []


def log(msg: str) -> None:
    report_lines.append(msg)


files = sorted(CAT_DIR.glob("*/index.html"))
log(f"local pages found: {len(files)}")

h1_bad = []
canonical_mismatch = []
og_mismatch = []
json_errors = []
missing_images = []
broken_internal_links = []
titles = []
descriptions = []
faq_first_q = []

IMG_RE = re.compile(r'src="([^"]+)"')
CANON_RE = re.compile(r'<link rel="canonical" href="([^"]+)">')
OGURL_RE = re.compile(r'<meta property="og:url" content="([^"]+)">')
TITLE_RE = re.compile(r"<title>([^<]+)</title>")
DESC_RE = re.compile(r'<meta name="description" content="([^"]+)">')
H1_RE = re.compile(r"<h1[ >]")
HREF_RE = re.compile(r'href="([^"]+)"')
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
FAQ_SUMMARY_RE = re.compile(r"<summary>([^<]+)</summary>")

for f in files:
    text = f.read_text(encoding="utf-8")
    slug = f.parent.name

    h1_count = len(H1_RE.findall(text))
    if h1_count != 1:
        h1_bad.append((slug, h1_count))

    m = CANON_RE.search(text)
    canonical = m.group(1) if m else None
    expected = DOMAIN + quote(f"/전국학원/{CATEGORY}/{slug}/", safe="/")
    if canonical != expected:
        canonical_mismatch.append((slug, canonical))

    m = OGURL_RE.search(text)
    og_url = m.group(1) if m else None
    if og_url != expected:
        og_mismatch.append((slug, og_url))

    m = TITLE_RE.search(text)
    titles.append(m.group(1) if m else f"MISSING::{slug}")

    m = DESC_RE.search(text)
    descriptions.append(m.group(1) if m else f"MISSING::{slug}")

    m = FAQ_SUMMARY_RE.search(text)
    faq_first_q.append(m.group(1) if m else f"MISSING::{slug}")

    for ld_block in LD_RE.findall(text):
        try:
            json.loads(ld_block)
        except Exception as e:  # noqa: BLE001
            json_errors.append((slug, str(e)))

    for src in IMG_RE.findall(text):
        if src.startswith("http"):
            continue
        resolved = (f.parent / src).resolve()
        if not resolved.exists():
            missing_images.append((slug, src))

    for href in HREF_RE.findall(text):
        if href.startswith(("http", "tel:", "sms:", "#")):
            continue
        if href.startswith("/"):
            resolved = (SITE / href.lstrip("/")).resolve()
            if href.endswith("/"):
                resolved = resolved / "index.html"
        else:
            resolved = (f.parent / href).resolve()
        if not resolved.exists():
            broken_internal_links.append((slug, href))

log(f"H1 != 1: {len(h1_bad)} -> {h1_bad[:10]}")
log(f"canonical mismatch: {len(canonical_mismatch)} -> {canonical_mismatch[:5]}")
log(f"og:url mismatch: {len(og_mismatch)} -> {og_mismatch[:5]}")
log(f"JSON-LD parse errors: {len(json_errors)} -> {json_errors[:5]}")
log(f"missing images referenced: {len(missing_images)} -> {missing_images[:10]}")
log(f"broken internal links: {len(broken_internal_links)} -> {broken_internal_links[:10]}")

title_dupes = {k: v for k, v in Counter(titles).items() if v > 1}
desc_dupes = {k: v for k, v in Counter(descriptions).items() if v > 1}
log(f"duplicate <title> values: {len(title_dupes)}")
log(f"duplicate <meta description> values: {len(desc_dupes)}")

faq_first_counter = Counter(faq_first_q)
most_common_faq_q = faq_first_counter.most_common(5)
log(f"most common FIRST faq question across pages (top5 w/ counts): {most_common_faq_q}")

# hub pages check
hub = SITE / "전국학원" / "index.html"
cat_hub = SITE / "전국학원" / CATEGORY / "index.html"
log(f"hub index exists: {hub.exists()}, category hub exists: {cat_hub.exists()}")

for hub_file in (hub, cat_hub):
    text = hub_file.read_text(encoding="utf-8")
    for ld_block in LD_RE.findall(text):
        try:
            json.loads(ld_block)
        except Exception as e:  # noqa: BLE001
            log(f"hub JSON-LD error in {hub_file}: {e}")
    h1c = len(H1_RE.findall(text))
    log(f"{hub_file.name} ({hub_file.parent.name}) H1 count: {h1c}")

Path("C:/Users/얼짱김종범/AppData/Local/Temp/validate_report.txt").write_text("\n".join(report_lines), encoding="utf-8")
print("done")
