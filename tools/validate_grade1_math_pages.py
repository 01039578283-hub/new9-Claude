from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

import generate_middle_math_pages as shared
import generate_grade1_math_pages as grade1


SITE = shared.SITE
ROOT = SITE / grade1.PARENT / grade1.CATEGORY
REQUIRED_TYPES = {
    "WebPage",
    "ImageObject",
    "BreadcrumbList",
    "EducationalOrganization",
    "LocalBusiness",
    "Article",
    "Service",
    "FAQPage",
    "ItemList",
}
VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.captures: list[dict[str, object]] = []
        self.h1s: list[str] = []
        self.h2s: list[str] = []
        self.crumbs: list[str] = []
        self.nav_labels: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.json_scripts: list[str] = []
        self.faq_count = 0
        self.review_count = 0
        self.media_first: tuple[str, dict[str, str]] | None = None

    @staticmethod
    def classes(attrs: dict[str, str]) -> set[str]:
        return set(attrs.get("class", "").split())

    def start_capture(self, kind: str, tag: str) -> None:
        self.captures.append({"kind": kind, "tag": tag, "depth": len(self.stack), "text": []})

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        parent_attrs = self.stack[-1][1] if self.stack else {}
        parent_classes = self.classes(parent_attrs)

        if tag == "meta":
            self.metas.append(attrs)
        elif tag == "link":
            self.links.append(attrs)
        elif tag == "img":
            self.images.append(attrs)

        classes = self.classes(attrs)
        if "faq-item" in classes:
            self.faq_count += 1
        if "review-card" in classes:
            self.review_count += 1
        if "local-media-section" in parent_classes and self.media_first is None:
            self.media_first = (tag, attrs)

        if tag == "h1":
            self.start_capture("h1", tag)
        elif tag == "h2":
            self.start_capture("h2", tag)
        elif tag in {"a", "span"} and "breadcrumb" in parent_classes:
            self.start_capture("crumb", tag)
        elif tag == "a" and "nav-links" in parent_classes:
            self.start_capture("nav", tag)
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self.start_capture("json", tag)

        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, attrs))

    def handle_data(self, data: str) -> None:
        for capture in self.captures:
            capture["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        for capture in list(self.captures):
            if capture["tag"] == tag and capture["depth"] == len(self.stack) - 1:
                text = " ".join("".join(capture["text"]).split())
                kind = capture["kind"]
                if kind == "h1":
                    self.h1s.append(text)
                elif kind == "h2":
                    self.h2s.append(text)
                elif kind == "crumb":
                    self.crumbs.append(text)
                elif kind == "nav":
                    self.nav_labels.append(text)
                elif kind == "json":
                    self.json_scripts.append("".join(capture["text"]))
                self.captures.remove(capture)
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()


def parse_html(value: str) -> PageParser:
    parser = PageParser()
    parser.feed(value)
    parser.close()
    return parser


def schema_types(graph: list[dict]) -> set[str]:
    found: set[str] = set()
    for node in graph:
        value = node.get("@type")
        if isinstance(value, list):
            found.update(value)
        elif isinstance(value, str):
            found.add(value)
    return found


def expected_path(local: str) -> str:
    return f"/{grade1.PARENT}/{grade1.CATEGORY}/{shared.slug_ko(local)}/"


def validate_page(path: Path, local: str) -> list[str]:
    errors: list[str] = []
    html = path.read_text(encoding="utf-8")
    parsed = parse_html(html)
    title = f"{local} {grade1.SUBJECT_LABEL}학원"

    if len(parsed.h1s) != 1 or parsed.h1s[0] != title:
        errors.append(f"H1={len(parsed.h1s)}:{parsed.h1s}")

    crumb_texts = [item for item in parsed.crumbs if item not in {"/", "›", ">"}]
    if crumb_texts != ["홈", grade1.PARENT, grade1.CATEGORY, title]:
        errors.append(f"breadcrumb={crumb_texts}")

    canonical = next((item for item in parsed.links if item.get("rel") == "canonical"), None)
    og_url = next((item for item in parsed.metas if item.get("property") == "og:url"), None)
    canonical_path = unquote(urlparse(canonical.get("href", "")).path) if canonical else ""
    og_path = unquote(urlparse(og_url.get("content", "")).path) if og_url else ""
    if canonical_path != expected_path(local) or og_path != canonical_path:
        errors.append(f"url={canonical_path}|{og_path}")

    descriptions = [item for item in parsed.metas if item.get("name") == "description"]
    if len(descriptions) != 1 or not descriptions[0].get("content", "").strip():
        errors.append("meta_description")

    if len(parsed.h2s) < 10:
        errors.append(f"h2_count={len(parsed.h2s)}")

    if parsed.faq_count != 5:
        errors.append(f"faq_count={parsed.faq_count}")
    if parsed.review_count < 1:
        errors.append("review_missing")

    first_element = parsed.media_first
    if (
        not first_element
        or first_element[0] != "img"
        or first_element[1].get("style", "").replace(" ", "") != "display:none;"
        or "loading" in first_element[1]
        or first_element[1].get("alt") != f"{title} {shared.SITE_NAME} 대표"
    ):
        errors.append("representative_image")

    for image in parsed.images:
        src = image.get("src", "")
        if not src or src.startswith(("http://", "https://", "data:")):
            continue
        target = (path.parent / src).resolve()
        if not target.exists():
            errors.append(f"missing_image={src}")

    if len(parsed.json_scripts) != 1:
        errors.append(f"jsonld_count={len(parsed.json_scripts)}")
    else:
        try:
            ld = json.loads(parsed.json_scripts[0])
            graph = ld.get("@graph", [])
            missing = REQUIRED_TYPES - schema_types(graph)
            if missing:
                errors.append(f"jsonld_types={sorted(missing)}")
            breadcrumbs = [node for node in graph if node.get("@type") == "BreadcrumbList"]
            final_name = breadcrumbs[0]["itemListElement"][-1]["name"] if breadcrumbs else ""
            if final_name != title:
                errors.append(f"jsonld_breadcrumb={final_name}")
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            errors.append(f"jsonld_parse={exc}")

    if any(token in html for token in ("#ERROR!", "�")):
        errors.append("unresolved_token")
    return errors


def main() -> None:
    rows = shared.read_csv(shared.COMMON / "센터정보 정리.csv")
    expected = {shared.slug_ko(row["근처 수업가능 동네"]): row["근처 수업가능 동네"].strip() for row in rows}
    pages = {
        path.parent.name: path
        for path in ROOT.glob("*/index.html")
    }
    if pages.keys() != expected.keys():
        raise SystemExit(
            f"지역 집합 불일치 missing={sorted(expected.keys() - pages.keys())} "
            f"extra={sorted(pages.keys() - expected.keys())}"
        )

    all_errors: list[str] = []
    descriptions: list[str] = []
    for slug, local in expected.items():
        path = pages[slug]
        errors = validate_page(path, local)
        if errors:
            all_errors.append(f"{local}: {'; '.join(errors)}")
        parsed = parse_html(path.read_text(encoding="utf-8"))
        descriptions.append(
            next(item for item in parsed.metas if item.get("name") == "description").get("content", "")
        )

    all_site_pages = [
        path for path in SITE.rglob("index.html")
        if not any(part in {".git", ".vercel", "node_modules"} for part in path.parts)
    ]
    nav_errors = []
    for path in all_site_pages:
        parsed = parse_html(path.read_text(encoding="utf-8"))
        if parsed.nav_labels != ["홈", "학습가이드", "상담문의", grade1.PARENT, "전국학원"]:
            nav_errors.append(str(path.relative_to(SITE)))

    if all_errors or nav_errors:
        print("\n".join(all_errors[:30]))
        if nav_errors:
            print(f"nav_errors={nav_errors[:20]}")
        raise SystemExit(
            f"validation_failed detail_errors={len(all_errors)} nav_errors={len(nav_errors)}"
        )
    print(
        "validation_ok "
        f"local_pages={len(pages)} "
        f"site_pages={len(all_site_pages)} "
        f"unique_descriptions={len(set(descriptions))}"
    )


if __name__ == "__main__":
    main()
