from __future__ import annotations

import csv
import html
import json
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Iterator
from urllib.parse import quote, unquote, urljoin, urlparse
from xml.etree import ElementTree as ET


SITE = Path(__file__).resolve().parents[1]
COMMON = SITE.parent / "참고자료" / "공통자료"
CSV_PATH = COMMON / "센터정보 정리.csv"
SITEMAP_PATH = SITE / "sitemap.xml"
DOMAIN = "https://xn--2z1b50xixca111l.com"
DOMAIN_HOST = urlparse(DOMAIN).netloc
PARENT = "과목별학원"
SITE_NAME = "코칭아카데미"
EXPECTED_LOCALS = 371
SIMILARITY_LIMIT = 0.75
MAX_EXAMPLES = 12


@dataclass(frozen=True)
class Category:
    slug: str
    grade: int
    subject: str

    @property
    def label(self) -> str:
        return f"중{self.grade} {self.subject}"


CATEGORIES = (
    Category("중1수학학원", 1, "수학"),
    Category("중1영어학원", 1, "영어"),
    Category("중2수학학원", 2, "수학"),
    Category("중2영어학원", 2, "영어"),
)

ALL_SUBJECT_CATEGORIES = (
    "고1수학학원",
    "고1영어학원",
    "고2수학학원",
    "고2영어학원",
    "중1수학학원",
    "중1영어학원",
    "중2수학학원",
    "중2영어학원",
)

REQUIRED_DETAIL_TYPES = {
    "EducationalOrganization",
    "LocalBusiness",
    "Article",
    "Service",
    "FAQPage",
    "BreadcrumbList",
    "ItemList",
}

FORBIDDEN_SCHEMA_TYPES = {"Review", "AggregateRating"}
FORBIDDEN_SCHEMA_KEYS = {
    "aggregateRating",
    "review",
    "reviewRating",
    "ratingValue",
}

AUTHORING_PATTERNS = (
    ("D열 제작 메모", re.compile(r"D열")),
    ("원고 제작 메모", re.compile(r"(?:이|본|해당)?\s*원고(?:에|는|를|가|에서|로)?")),
    ("AEO/GEO 제작 용어", re.compile(r"(?:AEO|GEO)\s*(?:형|관점|최적화)?", re.I)),
    ("JSON-LD 제작 용어", re.compile(r"JSON\s*-?\s*LD", re.I)),
    ("메타 제작 용어", re.compile(r"메타\s*(?:설명|요소|태그)")),
    ("프롬프트 흔적", re.compile(r"프롬프트|생성형\s*AI|챗GPT|ChatGPT", re.I)),
    ("복사·재작성 흔적", re.compile(r"다른\s*사이트|기존\s*글|복사한\s*내용|재작성한\s*내용")),
)

OVERCLAIM_PATTERNS = (
    ("성적 보장", re.compile(r"성적(?:이|을)?\s*(?:바로|반드시|무조건|확실히)\s*(?:오르|올리|향상)|성적\s*보장")),
    ("절대 표현", re.compile(r"(?:무조건|반드시)\s*(?:성공|합격|향상|상승|해결)")),
    ("과도한 최상급", re.compile(r"업계\s*1위|전국\s*1위|최고의\s*학원|유일한\s*학원|완벽한\s*성적")),
    ("수치 보장", re.compile(r"100\s*%\s*(?:보장|향상|성공|합격)")),
    ("단기 결과 단정", re.compile(r"단기간에\s*(?:성적|점수).{0,12}(?:상승|향상|오르)")),
)

RAW_COPY_PATTERNS = (
    ("원본 article-* 클래스", re.compile(
        r'class=["\'][^"\']*\barticle-(?:main|hero|intro|section|local-feature-section|subject-card|target-card|closing)\b',
        re.I,
    )),
    ("원본 영문 표제", re.compile(r"LOCAL\s+ACADEMY\s+GUIDE", re.I)),
    ("참고 사이트 도메인", re.compile(
        r"(?:전문수업|전국학원|소수정예학원|코칭센터)\.(?:com|kr)|학습코칭\.kr",
        re.I,
    )),
)

DISCLOSURE_PATTERNS = (
    re.compile(r"특정\s*학생.{0,80}(?:후기|성과).{0,120}예시"),
    re.compile(r"(?:실제|특정)\s*(?:학생\s*)?후기.{0,100}(?:아니|않).{0,100}예시"),
    re.compile(r"실제.{0,40}후기.{0,80}성과.{0,80}(?:아니|않).{0,120}(?:가상\s*)?예시"),
    re.compile(r"상담에서.{0,100}(?:상황|질문|사례).{0,100}예시"),
    re.compile(r"상담\s*예시.{0,100}(?:후기|성과).{0,100}(?:아니|않)"),
)

ALLOWED_SHARED_SENTENCES = (
    re.compile(r"특정\s*학생.{0,100}(?:후기|성과).{0,140}예시"),
    re.compile(r"실제.{0,40}후기.{0,80}성과.{0,80}(?:아니|않).{0,140}(?:가상\s*)?예시"),
    re.compile(r"센터정보.{0,120}(?:등록|정리).{0,120}(?:반영|확인)"),
    re.compile(r"실제\s*수업\s*가능\s*여부.{0,100}상담"),
    re.compile(r"방문\s*전.{0,100}(?:이동\s*동선|상담\s*가능\s*시간).{0,80}확인"),
)

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
SKIP_TEXT_TAGS = {"script", "style", "template", "noscript"}


def normalize_text(value: object) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()


def slug_ko(value: str) -> str:
    result = re.sub(r"\s+", "", value.strip())
    return re.sub(r'[\\/:*?"<>|#%&+]', "", result)


def split_items(value: str) -> list[str]:
    if not value:
        return []
    result: list[str] = []
    for part in re.split(r"[,/·.\s]+", value):
        name = part.strip()
        if name.endswith("중학교"):
            name = name[:-2]
        if name and name not in result:
            result.append(name)
    return result


def school_names(row: dict[str, str]) -> list[str]:
    result: list[str] = []
    for name in split_items(row.get("타깃학교\n(중)", "")):
        if name not in result:
            result.append(name)
    return result


def all_school_names(row: dict[str, str]) -> list[str]:
    result: list[str] = []
    generic_tokens = {
        "지역내",
        "모든",
        "가능",
        "학교",
        "초",
        "중",
        "고",
        "초등학교",
        "중학교",
        "고등학교",
    }
    for key in ("타깃학교\n(초)", "타깃학교\n(중)", "타깃학교\n(고)"):
        for name in split_items(row.get(key, "")):
            if name not in generic_tokens and name not in result:
                result.append(name)
    return result


def absolute_url(path: str) -> str:
    return DOMAIN + quote(path, safe="/:#?&=%")


def detail_path(category: Category, local: str) -> str:
    return f"/{PARENT}/{category.slug}/{slug_ko(local)}/"


def category_path(category: Category) -> str:
    return f"/{PARENT}/{category.slug}/"


def schema_types(node: dict[str, Any]) -> set[str]:
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def json_walk(value: Any) -> Iterator[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from json_walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from json_walk(child)


def nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    parent: Node | None = None
    children: list[Node | str] = field(default_factory=list)

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def ancestors(self) -> Iterator[Node]:
        current = self.parent
        while current is not None:
            yield current
            current = current.parent


class DOMParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(
        self,
        tag: str,
        attrs_list: list[tuple[str, str | None]],
    ) -> None:
        attrs = {key.lower(): value or "" for key, value in attrs_list}
        node = Node(tag.lower(), attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag.lower() not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(
        self,
        tag: str,
        attrs_list: list[tuple[str, str | None]],
    ) -> None:
        self.handle_starttag(tag, attrs_list)
        if tag.lower() not in VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def parse_dom(source: str) -> Node:
    parser = DOMParser()
    parser.feed(source)
    parser.close()
    return parser.root


def iter_nodes(node: Node) -> Iterator[Node]:
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from iter_nodes(child)


def node_text(node: Node, *, skip_hidden: bool = False) -> str:
    parts: list[str] = []

    def visit(current: Node | str) -> None:
        if isinstance(current, str):
            parts.append(current)
            return
        if current.tag in SKIP_TEXT_TAGS:
            return
        if skip_hidden and "display:none" in current.attrs.get("style", "").replace(" ", "").lower():
            return
        for child in current.children:
            visit(child)

    visit(node)
    return normalize_text(" ".join(parts))


def nodes_by_tag(root: Node, tag: str) -> list[Node]:
    return [node for node in iter_nodes(root) if node.tag == tag]


def nodes_by_class(root: Node, class_name: str) -> list[Node]:
    return [node for node in iter_nodes(root) if class_name in node.classes]


def first_descendant(node: Node, tag: str) -> Node | None:
    return next((item for item in iter_nodes(node) if item.tag == tag), None)


def is_descendant_of_class(node: Node, classes: set[str]) -> bool:
    return bool(node.classes & classes) or any(parent.classes & classes for parent in node.ancestors())


@dataclass
class ParsedPage:
    path: Path
    source: str
    root: Node
    title: str
    descriptions: list[str]
    canonicals: list[str]
    og_urls: list[str]
    h1s: list[str]
    graph: list[dict[str, Any]]
    json_values: list[Any]


def parse_page(path: Path, audit: Audit) -> ParsedPage | None:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        audit.fail("html_read", path, str(exc))
        return None
    root = parse_dom(source)
    titles = [node_text(node) for node in nodes_by_tag(root, "title")]
    descriptions = [
        normalize_text(node.attrs.get("content", ""))
        for node in nodes_by_tag(root, "meta")
        if node.attrs.get("name", "").lower() == "description"
    ]
    canonicals = [
        node.attrs.get("href", "").strip()
        for node in nodes_by_tag(root, "link")
        if "canonical" in node.attrs.get("rel", "").lower().split()
    ]
    og_urls = [
        node.attrs.get("content", "").strip()
        for node in nodes_by_tag(root, "meta")
        if node.attrs.get("property", "").lower() == "og:url"
    ]
    h1s = [node_text(node) for node in nodes_by_tag(root, "h1")]

    graph: list[dict[str, Any]] = []
    json_values: list[Any] = []
    json_nodes = [
        node
        for node in nodes_by_tag(root, "script")
        if node.attrs.get("type", "").lower() == "application/ld+json"
    ]
    if not json_nodes:
        audit.fail("jsonld_missing", path, "application/ld+json 블록 없음")
    for index, node in enumerate(json_nodes, 1):
        raw = "".join(child for child in node.children if isinstance(child, str)).strip()
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            audit.fail("jsonld_parse", path, f"block={index}: {exc}")
            continue
        json_values.append(value)
        candidates: list[Any]
        if isinstance(value, dict) and isinstance(value.get("@graph"), list):
            candidates = value["@graph"]
        elif isinstance(value, list):
            candidates = value
        else:
            candidates = [value]
        graph.extend(item for item in candidates if isinstance(item, dict))

    return ParsedPage(
        path=path,
        source=source,
        root=root,
        title=titles[0] if len(titles) == 1 else "",
        descriptions=descriptions,
        canonicals=canonicals,
        og_urls=og_urls,
        h1s=h1s,
        graph=graph,
        json_values=json_values,
    )


@dataclass
class Audit:
    failures: Counter[str] = field(default_factory=Counter)
    examples: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    checks: Counter[str] = field(default_factory=Counter)

    def fail(self, code: str, path: Path | str, detail: str) -> None:
        self.failures[code] += 1
        if len(self.examples[code]) < MAX_EXAMPLES:
            if isinstance(path, Path):
                try:
                    label = path.relative_to(SITE).as_posix()
                except ValueError:
                    label = str(path)
            else:
                label = path
            self.examples[code].append(f"{label}: {detail}")

    def checked(self, code: str, count: int = 1) -> None:
        self.checks[code] += count

    def finish(self, *, similarity: SimilarityResult | None = None) -> None:
        print("=== 중1·중2 과목별학원 독립 엄격 감사 ===")
        print("checks " + " ".join(f"{key}={self.checks[key]}" for key in sorted(self.checks)))
        if similarity is not None:
            print(
                "similarity "
                f"documents={similarity.documents} candidates={similarity.candidates} "
                f"max={similarity.maximum:.4f} limit<{SIMILARITY_LIMIT:.2f}"
            )
            if similarity.maximum_pair:
                print(f"similarity_max_pair={' <> '.join(similarity.maximum_pair)}")
        if self.failures:
            print("AUDIT_FAILED " + " ".join(
                f"{key}={self.failures[key]}" for key in sorted(self.failures)
            ))
            for code in sorted(self.failures):
                print(f"\n[{code}] examples")
                for example in self.examples[code]:
                    print(f"- {example}")
            raise SystemExit(1)
        print("AUDIT_OK failures=0")


def parse_iso_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip().replace("Z", "+00:00")
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            return date.fromisoformat(raw)
        return datetime.fromisoformat(raw).date()
    except ValueError:
        return None


def normalize_schema_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return normalize_text(text)


def resolve_local_asset(page: Path, value: str) -> Path | None:
    raw = value.strip().split()[0] if value.strip() else ""
    if not raw or raw.startswith(("data:", "blob:")):
        return None
    parsed = urlparse(raw)
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc != DOMAIN_HOST:
            return None
        target = SITE / unquote(parsed.path).lstrip("/")
    elif raw.startswith("/"):
        target = SITE / unquote(parsed.path).lstrip("/")
    else:
        target = page.parent / unquote(parsed.path)
    try:
        resolved = target.resolve()
        resolved.relative_to(SITE.resolve())
    except (OSError, ValueError):
        return None
    return resolved


def expected_map(row: dict[str, str]) -> Path | None:
    raw = row.get("동 영어", "").strip()
    candidates = (raw, raw.replace(" ", "-"), raw.replace(" ", ""), raw.replace("_", "-"))
    for base in candidates:
        for extension in (".jpg", ".jpeg", ".png", ".webp"):
            path = SITE / "assets" / "maps" / f"{base}{extension}"
            if path.exists():
                return path.resolve()
    return None


def validate_metadata(
    page: ParsedPage,
    *,
    expected_title: str,
    expected_h1: str,
    expected_canonical: str,
    audit: Audit,
) -> None:
    if page.title != expected_title:
        audit.fail("title_exact", page.path, f"expected={expected_title!r} actual={page.title!r}")
    if page.h1s != [expected_h1]:
        audit.fail("h1_exact", page.path, f"expected={[expected_h1]!r} actual={page.h1s!r}")
    if page.canonicals != [expected_canonical]:
        audit.fail("canonical_exact", page.path, f"expected={[expected_canonical]!r} actual={page.canonicals!r}")
    if page.og_urls != [expected_canonical]:
        audit.fail("og_url_exact", page.path, f"expected={[expected_canonical]!r} actual={page.og_urls!r}")
    if len(page.descriptions) != 1 or not page.descriptions[0]:
        audit.fail("description", page.path, f"count={len(page.descriptions)} values={page.descriptions!r}")


def breadcrumb_labels(node: Node) -> list[str]:
    labels: list[str] = []
    for item in iter_nodes(node):
        if item.tag not in {"a", "span", "li"}:
            continue
        value = node_text(item)
        if value and value not in {"/", "›", ">", "»"} and value not in labels:
            labels.append(value)
    return labels


def schema_list_items(node: dict[str, Any]) -> list[dict[str, Any]]:
    value = node.get("itemListElement", [])
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def validate_breadcrumbs(
    page: ParsedPage,
    *,
    expected_h1: str,
    expected_canonical: str,
    audit: Audit,
) -> None:
    visible = nodes_by_class(page.root, "breadcrumb")
    if len(visible) != 1:
        audit.fail("breadcrumb_visible_count", page.path, f"count={len(visible)}")
    else:
        labels = breadcrumb_labels(visible[0])
        if not labels or labels[-1] != expected_h1:
            audit.fail("breadcrumb_visible_last", page.path, f"labels={labels!r}")

    candidates = [node for node in page.graph if "BreadcrumbList" in schema_types(node)]
    if len(candidates) != 1:
        audit.fail("breadcrumb_schema_count", page.path, f"count={len(candidates)}")
        return
    items = schema_list_items(candidates[0])
    if not items:
        audit.fail("breadcrumb_schema_items", page.path, "itemListElement 없음")
        return
    last = items[-1]
    item_url = last.get("item") or last.get("url")
    if normalize_text(last.get("name")) != expected_h1 or item_url != expected_canonical:
        audit.fail(
            "breadcrumb_schema_last",
            page.path,
            f"name={last.get('name')!r} item={item_url!r}",
        )


def validate_schema(
    page: ParsedPage,
    *,
    row: dict[str, str],
    expected_h1: str,
    expected_canonical: str,
    audit: Audit,
) -> None:
    found_types: set[str] = set()
    for node in page.graph:
        found_types.update(schema_types(node))
    missing = REQUIRED_DETAIL_TYPES - found_types
    if missing:
        audit.fail("schema_required_types", page.path, f"missing={sorted(missing)} found={sorted(found_types)}")

    articles = [node for node in page.graph if "Article" in schema_types(node)]
    if len(articles) != 1:
        audit.fail("schema_article_count", page.path, f"count={len(articles)}")
    else:
        article = articles[0]
        for key in ("about", "mentions", "hasPart", "articleSection"):
            if not nonempty(article.get(key)):
                audit.fail("schema_article_semantics", page.path, f"Article.{key} 누락/비어 있음")
        published = parse_iso_date(article.get("datePublished"))
        modified = parse_iso_date(article.get("dateModified"))
        if published is None or modified is None:
            audit.fail(
                "schema_article_dates",
                page.path,
                f"datePublished={article.get('datePublished')!r} dateModified={article.get('dateModified')!r}",
            )
        elif published > modified or modified > date.today():
            audit.fail(
                "schema_article_dates",
                page.path,
                f"published={published} modified={modified} today={date.today()}",
            )

    webpages = [node for node in page.graph if "WebPage" in schema_types(node)]
    if not webpages:
        audit.fail("schema_webpage", page.path, "WebPage 노드 없음")
    else:
        if len(webpages) != 1:
            audit.fail("schema_webpage", page.path, f"WebPage count={len(webpages)}")
        for key in ("about", "mentions", "hasPart"):
            if not any(nonempty(node.get(key)) for node in webpages):
                audit.fail("schema_webpage_semantics", page.path, f"WebPage.{key} 누락/비어 있음")
        webpage = webpages[0]
        if webpage.get("url") != expected_canonical or webpage.get("@id") != f"{expected_canonical}#webpage":
            audit.fail(
                "schema_webpage_identity",
                page.path,
                f"url={webpage.get('url')!r} @id={webpage.get('@id')!r}",
            )

    organizations = [
        node
        for node in page.graph
        if schema_types(node) & {"EducationalOrganization", "LocalBusiness"}
    ]
    if not organizations or not any(nonempty(node.get("makesOffer")) for node in organizations):
        audit.fail("schema_makes_offer", page.path, "교육기관/지역사업체 makesOffer 누락")
    else:
        org = next((node for node in organizations if nonempty(node.get("makesOffer"))), organizations[0])
        if normalize_text(org.get("name")) != row.get("센터명", "").strip():
            audit.fail("schema_center_fact", page.path, f"name={org.get('name')!r}")
        address = org.get("address") if isinstance(org.get("address"), dict) else {}
        address_tokens = row.get("센터 주소", "").strip().split()
        address_region = address_tokens[0] if address_tokens else row.get("지역", "").strip()
        if address_region == "세종특별자치시":
            address_locality = address_region
        else:
            address_locality = address_tokens[1] if len(address_tokens) > 1 else row.get("시or구", "").strip()
        expected_address = {
            "streetAddress": row.get("센터 주소", "").strip(),
            "addressLocality": address_locality,
            "addressRegion": address_region,
        }
        for key, expected in expected_address.items():
            if expected and normalize_text(address.get(key)) != expected:
                audit.fail("schema_address_fact", page.path, f"{key}={address.get(key)!r} expected={expected!r}")

    for value in page.json_values:
        for item in json_walk(value):
            if not isinstance(item, dict):
                continue
            illegal_types = schema_types(item) & FORBIDDEN_SCHEMA_TYPES
            if illegal_types:
                audit.fail("schema_review_forbidden", page.path, f"types={sorted(illegal_types)}")
            illegal_keys = FORBIDDEN_SCHEMA_KEYS & item.keys()
            if illegal_keys:
                audit.fail("schema_rating_forbidden", page.path, f"keys={sorted(illegal_keys)}")

    services = [node for node in page.graph if "Service" in schema_types(node)]
    if len(services) != 1:
        audit.fail("schema_service_count", page.path, f"count={len(services)}")
    elif services[0].get("url") != expected_canonical:
        audit.fail("schema_service_url", page.path, f"url={services[0].get('url')!r}")

    if len(articles) == 1:
        article = articles[0]
        if normalize_text(article.get("headline")) != expected_h1:
            audit.fail("schema_article_headline", page.path, f"headline={article.get('headline')!r}")


def visible_faqs(page: ParsedPage) -> list[tuple[str, str]]:
    details = [node for node in nodes_by_tag(page.root, "details") if "faq-item" in node.classes]
    if not details:
        details = [
            node
            for node in nodes_by_tag(page.root, "details")
            if any("faq-list" in parent.classes for parent in node.ancestors())
        ]
    result: list[tuple[str, str]] = []
    for detail in details:
        summary = first_descendant(detail, "summary")
        if summary is None:
            continue
        question = node_text(summary)
        answer_parts = [
            node_text(node)
            for node in iter_nodes(detail)
            if node.tag in {"p", "div"} and not any(parent.tag == "summary" for parent in node.ancestors())
        ]
        answer = normalize_text(" ".join(part for part in answer_parts if part))
        if question and answer:
            result.append((question, answer))
    return result


def validate_faq(page: ParsedPage, audit: Audit) -> None:
    visible = visible_faqs(page)
    if len(visible) < 4:
        audit.fail("faq_visible_count", page.path, f"count={len(visible)}")

    faq_nodes = [node for node in page.graph if "FAQPage" in schema_types(node)]
    if len(faq_nodes) != 1:
        audit.fail("faq_schema_count", page.path, f"count={len(faq_nodes)}")
        return
    entities = faq_nodes[0].get("mainEntity", [])
    if not isinstance(entities, list):
        entities = [entities]
    schema_pairs: list[tuple[str, str]] = []
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        answer = entity.get("acceptedAnswer")
        answer_text = answer.get("text") if isinstance(answer, dict) else ""
        schema_pairs.append((
            normalize_schema_text(entity.get("name")),
            normalize_schema_text(answer_text),
        ))
    if visible != schema_pairs:
        audit.fail(
            "faq_visible_schema_mismatch",
            page.path,
            f"visible={visible[:2]!r} schema={schema_pairs[:2]!r} counts={len(visible)}|{len(schema_pairs)}",
        )


def validate_quick_answer(
    page: ParsedPage,
    *,
    expected_h1: str,
    audit: Audit,
) -> None:
    sections = nodes_by_class(page.root, "answer-section")
    if len(sections) != 1:
        audit.fail("quick_answer_section", page.path, f"answer-section count={len(sections)}")
        return
    section = sections[0]
    headings = [node_text(node) for node in iter_nodes(section) if node.tag == "h2"]
    expected_heading = f"{expected_h1} 핵심 답변"
    if headings != [expected_heading]:
        audit.fail("quick_answer_heading", page.path, f"expected={expected_heading!r} actual={headings!r}")
    items = [node for node in iter_nodes(section) if "answer-item" in node.classes]
    if len(items) != 1:
        audit.fail("quick_answer_item", page.path, f"count={len(items)}")
        return
    questions = [node_text(node) for node in iter_nodes(items[0]) if "q" in node.classes]
    answers = [node_text(node) for node in iter_nodes(items[0]) if "a" in node.classes]
    if len(questions) != 1 or len(answers) != 1 or not questions[0] or len(answers[0]) < 35:
        audit.fail(
            "quick_answer_item",
            page.path,
            f"questions={questions!r} answers={answers!r}",
        )
        return
    schema_summaries = {
        normalize_text(node.get("description"))
        for node in page.graph
        if schema_types(node) & {"Article", "Service"} and nonempty(node.get("description"))
    }
    if schema_summaries and answers[0] not in schema_summaries:
        audit.fail(
            "quick_answer_schema_summary",
            page.path,
            f"visible={answers[0]!r} schema={sorted(schema_summaries)!r}",
        )


def validate_disclosure_and_forbidden_copy(page: ParsedPage, audit: Audit) -> None:
    mains = nodes_by_tag(page.root, "main")
    visible = node_text(mains[0], skip_hidden=True) if len(mains) == 1 else node_text(page.root, skip_hidden=True)
    if not any(pattern.search(visible) for pattern in DISCLOSURE_PATTERNS):
        audit.fail("consultation_example_disclosure", page.path, "상담 예시의 비후기·비성과 고지 없음")
    for name, pattern in AUTHORING_PATTERNS:
        if pattern.search(visible):
            audit.fail("authoring_trace", page.path, name)
    for name, pattern in OVERCLAIM_PATTERNS:
        if pattern.search(visible):
            audit.fail("overclaim", page.path, name)
    for name, pattern in RAW_COPY_PATTERNS:
        if pattern.search(page.source):
            audit.fail("copy_trace", page.path, name)


def positive_dimension(node: Node, key: str) -> bool:
    value = node.attrs.get(key, "")
    return value.isdigit() and int(value) > 0


def validate_images(
    page: ParsedPage,
    *,
    row: dict[str, str],
    expected_h1: str,
    audit: Audit,
) -> Path | None:
    images = nodes_by_tag(page.root, "img")
    roles = {
        "representative": [
            node for node in images
            if "/representative/" in node.attrs.get("src", "").replace("\\", "/")
            or "대표" in node.attrs.get("alt", "")
        ],
        "body": [
            node for node in images
            if "/centers/common/" in node.attrs.get("src", "").replace("\\", "/")
            or "본문" in node.attrs.get("alt", "")
        ],
        "map": [
            node for node in images
            if "/maps/" in node.attrs.get("src", "").replace("\\", "/")
            or "지도" in node.attrs.get("alt", "")
        ],
    }
    for role, candidates in roles.items():
        if len(candidates) != 1:
            audit.fail("image_role_count", page.path, f"role={role} count={len(candidates)}")
            continue
        image = candidates[0]
        if not positive_dimension(image, "width") or not positive_dimension(image, "height"):
            audit.fail("image_dimensions", page.path, f"role={role} attrs={image.attrs!r}")
        alt = normalize_text(image.attrs.get("alt"))
        role_word = {"representative": "대표", "body": "본문", "map": "지도"}[role]
        if expected_h1 not in alt or role_word not in alt:
            audit.fail("image_alt", page.path, f"role={role} alt={alt!r}")
        target = resolve_local_asset(page.path, image.attrs.get("src", ""))
        if target is None or not target.is_file():
            audit.fail("image_missing", page.path, f"role={role} src={image.attrs.get('src')!r}")

    representative_target: Path | None = None
    if len(roles["representative"]) == 1:
        image = roles["representative"][0]
        target = resolve_local_asset(page.path, image.attrs.get("src", ""))
        representative_root = (SITE / "assets" / "representative").resolve()
        try:
            if target is None:
                raise ValueError("대표 이미지 경로를 해석하지 못함")
            target.relative_to(representative_root)
            if not target.is_file() or target.suffix.lower() not in {".gif", ".jpg", ".jpeg", ".png", ".webp"}:
                raise ValueError("대표 이미지 풀의 유효한 실파일이 아님")
        except ValueError as exc:
            audit.fail(
                "representative_rule",
                page.path,
                f"actual={target} reason={exc}",
            )
        else:
            representative_target = target
        style = image.attrs.get("style", "").replace(" ", "").lower()
        if "display:none" not in style or "loading" in image.attrs:
            audit.fail("representative_loading_rule", page.path, f"attrs={image.attrs!r}")

    if len(roles["body"]) == 1:
        image = roles["body"][0]
        target = resolve_local_asset(page.path, image.attrs.get("src", ""))
        filename = "seoul6839.webp" if row.get("지역", "").strip() == "서울" else "local6839.webp"
        expected = (SITE / "assets" / "centers" / "common" / filename).resolve()
        if target != expected:
            audit.fail("body_image_rule", page.path, f"actual={target} expected={expected}")
        picture = next((parent for parent in image.ancestors() if parent.tag == "picture"), None)
        sources = [node for node in iter_nodes(picture) if node.tag == "source"] if picture else []
        mobile = filename.replace(".webp", "-mobile.webp")
        if not any(
            (target_src := resolve_local_asset(page.path, node.attrs.get("srcset", ""))) is not None
            and target_src.name == mobile
            and target_src.is_file()
            for node in sources
        ):
            audit.fail("body_mobile_image_rule", page.path, f"expected_mobile={mobile}")

    if len(roles["map"]) == 1:
        image = roles["map"][0]
        target = resolve_local_asset(page.path, image.attrs.get("src", ""))
        expected = expected_map(row)
        if expected is None or target != expected:
            audit.fail("map_image_rule", page.path, f"actual={target} expected={expected}")

    for node in images + nodes_by_tag(page.root, "source"):
        attribute = "srcset" if node.tag == "source" else "src"
        value = node.attrs.get(attribute, "")
        target = resolve_local_asset(page.path, value)
        parsed = urlparse(value.split()[0] if value else "")
        is_local = not parsed.scheme or parsed.netloc == DOMAIN_HOST
        if value and is_local and (target is None or not target.is_file()):
            audit.fail("image_missing", page.path, f"{attribute}={value!r}")
    return representative_target


def list_item_name(item: dict[str, Any]) -> str:
    name = item.get("name")
    if isinstance(name, str):
        return normalize_text(name)
    nested = item.get("item")
    if isinstance(nested, dict):
        return normalize_text(nested.get("name"))
    return ""


def validate_facts_and_schools(
    page: ParsedPage,
    *,
    row: dict[str, str],
    known_school_pattern: re.Pattern[str] | None,
    audit: Audit,
) -> None:
    mains = nodes_by_tag(page.root, "main")
    visible = node_text(mains[0], skip_hidden=True) if len(mains) == 1 else node_text(page.root, skip_hidden=True)
    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    if row.get("센터 주소", "").strip().startswith("세종특별자치시"):
        region, district = "세종특별자치시", "세종시"
    elif district.endswith(("로", "길")):
        district = ""
    expected_visible = {
        "근처 수업가능 동네": row.get("근처 수업가능 동네", "").strip(),
        "지역": region,
        "시or구": district,
        "센터명": row.get("센터명", "").strip(),
        "센터 주소": row.get("센터 주소", "").strip(),
    }
    for key, value in expected_visible.items():
        if value and value not in visible:
            audit.fail("csv_visible_fact", page.path, f"missing {key}={value!r}")

    allowed = set(school_names(row))
    school_lists = [
        node
        for node in page.graph
        if "ItemList" in schema_types(node)
        and (
            "schools" in str(node.get("@id", "")).lower()
            or "학교" in normalize_text(node.get("name"))
        )
    ]
    if len(school_lists) != 1:
        audit.fail("school_itemlist_count", page.path, f"count={len(school_lists)}")
        schema_school_names: set[str] = set()
    else:
        schema_school_names = {
            list_item_name(item)
            for item in schema_list_items(school_lists[0])
            if list_item_name(item)
        }
        foreign = schema_school_names - allowed
        if foreign:
            audit.fail("school_whitelist", page.path, f"schema foreign={sorted(foreign)} allowed={sorted(allowed)}")
        if allowed and not schema_school_names:
            audit.fail("school_itemlist_empty", page.path, f"allowed={sorted(allowed)}")

    chip_nodes = nodes_by_class(page.root, "chip-list")
    visible_chips: set[str] = set()
    for container in chip_nodes:
        visible_chips.update(
            node_text(node)
            for node in iter_nodes(container)
            if node.tag in {"span", "li", "a"} and node_text(node)
        )
    foreign_chips = visible_chips - allowed - {"상담 시 학교 확인"}
    if foreign_chips:
        audit.fail("school_whitelist", page.path, f"visible foreign={sorted(foreign_chips)} allowed={sorted(allowed)}")
    if schema_school_names and not schema_school_names.issubset(visible_chips):
        audit.fail(
            "school_visible_schema_mismatch",
            page.path,
            f"schema={sorted(schema_school_names)} visible={sorted(visible_chips)}",
        )

    if known_school_pattern is not None:
        mentioned = set(known_school_pattern.findall(visible))
        foreign_mentions = mentioned - allowed
        if foreign_mentions:
            audit.fail(
                "school_whitelist",
                page.path,
                f"text foreign={sorted(foreign_mentions)} allowed={sorted(allowed)}",
            )


def internal_target(page: Path, canonical: str, href: str) -> tuple[str, Path] | None:
    href = href.strip()
    if not href or href.startswith(("#", "tel:", "sms:", "mailto:", "javascript:", "data:")):
        return None
    parsed_direct = urlparse(href)
    if parsed_direct.scheme in {"http", "https"} and parsed_direct.netloc != DOMAIN_HOST:
        return None
    joined = urlparse(urljoin(canonical, href))
    if joined.netloc and joined.netloc != DOMAIN_HOST:
        return None
    file_path = unquote(joined.path)
    if not file_path.startswith("/"):
        file_path = "/" + file_path
    target = SITE / file_path.lstrip("/")
    if file_path.endswith("/"):
        target = target / "index.html"
    elif not target.suffix and target.is_dir():
        target = target / "index.html"
    route_path = file_path
    if route_path == "/index.html":
        route_path = "/"
    elif route_path.endswith("/index.html"):
        route_path = route_path[: -len("index.html")]
    try:
        resolved = target.resolve()
        resolved.relative_to(SITE.resolve())
    except (OSError, ValueError):
        return route_path, target
    return route_path, resolved


def validate_internal_links(
    page: ParsedPage,
    *,
    expected_canonical: str,
    expected_category_path: str,
    audit: Audit,
) -> None:
    internal_paths: set[str] = set()
    for anchor in nodes_by_tag(page.root, "a"):
        href = anchor.attrs.get("href", "")
        target = internal_target(page.path, expected_canonical, href)
        if target is None:
            continue
        url_path, file_path = target
        internal_paths.add(url_path)
        if not file_path.is_file():
            audit.fail("broken_internal_link", page.path, f"href={href!r} target={file_path}")
    required = {"/", f"/{PARENT}/", expected_category_path}
    missing = required - internal_paths
    if missing:
        audit.fail("internal_link_structure", page.path, f"missing={sorted(missing)}")


def content_blocks(page: ParsedPage) -> list[str]:
    mains = nodes_by_tag(page.root, "main")
    if len(mains) != 1:
        return []
    # Similarity is a copy-quality gate, not a comparison of shared factual UI.
    # Limit it to the authored answer, manuscript, FAQ and consultation-example
    # blocks.  Center addresses, grade cards and related-link labels legitimately
    # repeat when one physical center serves several localities/categories.
    authored_classes = {"answer-section", "manuscript-section", "faq-list", "review-grid"}
    blocks: list[str] = []
    for node in iter_nodes(mains[0]):
        if node.tag not in {"h2", "h3", "p", "li", "summary"}:
            continue
        if not is_descendant_of_class(node, authored_classes):
            continue
        value = node_text(node, skip_hidden=True)
        if value:
            blocks.append(value)
    return blocks


@dataclass
class ContentRecord:
    label: str
    path: Path
    blocks: list[str]
    mask_values: list[str]
    shingles: set[tuple[str, ...]] = field(default_factory=set)


def mask_content(record: ContentRecord) -> str:
    value = " \n ".join(record.blocks)
    for token in sorted({item for item in record.mask_values if item}, key=len, reverse=True):
        value = re.sub(re.escape(token), " 지역정보 ", value, flags=re.I)
    value = re.sub(r"https?://\S+", " 주소정보 ", value)
    value = re.sub(r"\b\d+(?:[-.:/]\d+)*\b", " 숫자정보 ", value)
    value = re.sub(r"\s+", " ", value).lower().strip()
    return value


def make_shingles(record: ContentRecord) -> set[tuple[str, ...]]:
    masked = mask_content(record)
    tokens = re.findall(r"[가-힣A-Za-z]+", masked)
    return {tuple(tokens[index:index + 5]) for index in range(max(0, len(tokens) - 4))}


def split_sentences(block: str) -> list[str]:
    return [
        normalize_text(part)
        for part in re.split(r"(?<=[.!?])\s+|[\r\n]+", block)
        if normalize_text(part)
    ]


def allowed_shared_sentence(value: str) -> bool:
    return any(pattern.search(value) for pattern in ALLOWED_SHARED_SENTENCES)


@dataclass
class SimilarityResult:
    documents: int
    candidates: int
    maximum: float
    maximum_pair: tuple[str, str] | None


def audit_content_duplication(records: list[ContentRecord], audit: Audit) -> SimilarityResult:
    # Shared single sentences such as a safety disclaimer are legitimate
    # boilerplate.  Making every sentence unique previously encouraged noisy
    # search-label injection.  The meaningful duplicate gate is therefore a
    # complete authored paragraph/block containing at least two sentences,
    # backed by the masked 5-shingle similarity check below.
    block_pages: dict[str, set[str]] = defaultdict(set)
    document_pages: dict[str, set[str]] = defaultdict(set)
    for record in records:
        for block in record.blocks:
            normalized = normalize_text(block)
            if len(split_sentences(normalized)) < 2 or len(normalized) < 90:
                continue
            block_pages[normalized].add(record.label)
        normalized_document = normalize_text(" \n ".join(record.blocks))
        if normalized_document:
            document_pages[normalized_document].add(record.label)

    duplicate_blocks = [
        (block, pages) for block, pages in block_pages.items() if len(pages) > 1
    ]
    for block, pages in sorted(
        duplicate_blocks,
        key=lambda item: (-len(item[1]), item[0]),
    ):
        audit.fail(
            "duplicate_exact_authored_block",
            "content",
            f"pages={len(pages)} sample={sorted(pages)[:4]} block={block!r}",
        )
    duplicate_documents = [
        (document, pages)
        for document, pages in document_pages.items()
        if len(pages) > 1
    ]
    for document, pages in duplicate_documents:
        audit.fail(
            "duplicate_exact_authored_document",
            "content",
            f"pages={len(pages)} sample={sorted(pages)[:4]} text={document[:180]!r}",
        )

    for record in records:
        record.shingles = make_shingles(record)
        if len(record.shingles) < 40:
            audit.fail("similarity_content_too_short", record.path, f"5-shingles={len(record.shingles)}")

    usable = [record for record in records if record.shingles]
    frequencies: Counter[tuple[str, ...]] = Counter()
    for record in usable:
        frequencies.update(record.shingles)

    ordered = sorted(usable, key=lambda record: (len(record.shingles), record.label))
    postings: dict[tuple[str, ...], list[int]] = defaultdict(list)
    candidate_count = 0
    maximum = 0.0
    maximum_pair: tuple[str, str] | None = None

    for index, record in enumerate(ordered):
        size = len(record.shingles)
        sorted_tokens = sorted(record.shingles, key=lambda token: (frequencies[token], token))
        prefix_length = size - math.ceil(SIMILARITY_LIMIT * size) + 1
        candidates: set[int] = set()
        minimum_prior_size = math.ceil(SIMILARITY_LIMIT * size)
        for token in sorted_tokens[:prefix_length]:
            candidates.update(
                prior
                for prior in postings.get(token, [])
                if len(ordered[prior].shingles) >= minimum_prior_size
            )
        for prior in candidates:
            other = ordered[prior]
            intersection = len(record.shingles & other.shingles)
            union = size + len(other.shingles) - intersection
            score = intersection / union if union else 1.0
            candidate_count += 1
            if score > maximum:
                maximum = score
                maximum_pair = (other.label, record.label)
            if score >= SIMILARITY_LIMIT:
                audit.fail(
                    "masked_5shingle_similarity",
                    "content",
                    f"score={score:.4f} pages={other.label!r}, {record.label!r}",
                )
        for token in record.shingles:
            postings[token].append(index)

    return SimilarityResult(len(usable), candidate_count, maximum, maximum_pair)


def validate_category_hub(
    category: Category,
    rows: list[dict[str, str]],
    audit: Audit,
) -> tuple[str, str, str, str] | None:
    path = SITE / PARENT / category.slug / "index.html"
    if not path.is_file():
        audit.fail("category_hub_missing", path, "허브 출력물 없음")
        return None
    page = parse_page(path, audit)
    if page is None:
        return None
    expected_path = category_path(category)
    canonical = absolute_url(expected_path)
    title = f"{category.slug} | {SITE_NAME}"
    validate_metadata(
        page,
        expected_title=title,
        expected_h1=category.slug,
        expected_canonical=canonical,
        audit=audit,
    )
    required = {"CollectionPage", "BreadcrumbList", "ItemList"}
    found: set[str] = set()
    for node in page.graph:
        found.update(schema_types(node))
    if missing := required - found:
        audit.fail("category_hub_schema", path, f"missing={sorted(missing)}")

    item_lists = [node for node in page.graph if "ItemList" in schema_types(node)]
    expected_urls = {absolute_url(detail_path(category, row["근처 수업가능 동네"])) for row in rows}
    matching = [
        node
        for node in item_lists
        if len(schema_list_items(node)) == EXPECTED_LOCALS
        or int(node.get("numberOfItems", -1) or -1) == EXPECTED_LOCALS
    ]
    if len(matching) != 1:
        audit.fail("category_hub_itemlist", path, f"371 ItemList count={len(matching)}")
    else:
        urls = {
            item.get("url") or item.get("item")
            for item in schema_list_items(matching[0])
        }
        if urls != expected_urls:
            audit.fail(
                "category_hub_itemlist",
                path,
                f"missing={len(expected_urls - urls)} extra={len(urls - expected_urls)}",
            )

    anchor_urls: set[str] = set()
    for anchor in nodes_by_tag(page.root, "a"):
        target = internal_target(path, canonical, anchor.attrs.get("href", ""))
        if target and target[0].startswith(expected_path) and target[0] != expected_path:
            anchor_urls.add(absolute_url(target[0]))
    if anchor_urls != expected_urls:
        audit.fail(
            "category_hub_links",
            path,
            f"missing={len(expected_urls - anchor_urls)} extra={len(anchor_urls - expected_urls)}",
        )
    audit.checked("category_hubs")
    description = page.descriptions[0] if len(page.descriptions) == 1 else ""
    return title, category.slug, canonical, description


def validate_parent_hub(audit: Audit) -> None:
    path = SITE / PARENT / "index.html"
    if not path.is_file():
        audit.fail("parent_hub_missing", path, "과목별학원 부모 허브 없음")
        return
    page = parse_page(path, audit)
    if page is None:
        return
    canonical = absolute_url(f"/{PARENT}/")
    grids = nodes_by_class(page.root, "category-grid")
    if len(grids) != 1:
        audit.fail("parent_hub_cards", path, f"category-grid count={len(grids)}")
    else:
        paths: list[str] = []
        for anchor in [node for node in iter_nodes(grids[0]) if node.tag == "a"]:
            target = internal_target(path, canonical, anchor.attrs.get("href", ""))
            if target:
                paths.append(target[0])
        expected = {f"/{PARENT}/{name}/" for name in ALL_SUBJECT_CATEGORIES}
        if len(paths) != 8 or set(paths) != expected:
            audit.fail("parent_hub_cards", path, f"count={len(paths)} paths={paths!r}")

    item_lists = [node for node in page.graph if "ItemList" in schema_types(node)]
    expected_urls = {absolute_url(f"/{PARENT}/{name}/") for name in ALL_SUBJECT_CATEGORIES}
    matching: list[dict[str, Any]] = []
    for node in item_lists:
        urls = {item.get("url") or item.get("item") for item in schema_list_items(node)}
        if urls == expected_urls:
            matching.append(node)
    if len(matching) != 1 or len(schema_list_items(matching[0])) != 8:
        audit.fail("parent_hub_itemlist", path, f"matching={len(matching)}")
    audit.checked("parent_hub")


def read_rows(audit: Audit) -> list[dict[str, str]]:
    if not CSV_PATH.is_file():
        audit.fail("common_csv_missing", CSV_PATH, "공통 CSV 없음")
        return []
    try:
        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
    except (OSError, UnicodeError, csv.Error) as exc:
        audit.fail("common_csv_read", CSV_PATH, str(exc))
        return []
    locals_ = [row.get("근처 수업가능 동네", "").strip() for row in rows]
    if len(rows) != EXPECTED_LOCALS or len(set(locals_)) != EXPECTED_LOCALS or "" in locals_:
        audit.fail(
            "common_csv_contract",
            CSV_PATH,
            f"rows={len(rows)} unique_locals={len(set(locals_))} blanks={locals_.count('')}",
        )
    return rows


def parse_sitemap(audit: Audit) -> list[str]:
    if not SITEMAP_PATH.is_file():
        audit.fail("sitemap_missing", SITEMAP_PATH, "sitemap.xml 없음")
        return []
    try:
        root = ET.parse(SITEMAP_PATH).getroot()
    except (ET.ParseError, OSError) as exc:
        audit.fail("sitemap_parse", SITEMAP_PATH, str(exc))
        return []
    locations = [normalize_text(node.text) for node in root.findall(".//{*}loc") if normalize_text(node.text)]
    if len(locations) != len(set(locations)):
        audit.fail("sitemap_duplicate", SITEMAP_PATH, f"count={len(locations)} unique={len(set(locations))}")
    return locations


def validate_sitemap(
    rows: list[dict[str, str]],
    expected_canonicals: set[str],
    audit: Audit,
) -> None:
    locations = parse_sitemap(audit)
    location_set = set(locations)
    prefixes = tuple(f"/{PARENT}/{category.slug}/" for category in CATEGORIES)
    actual_scope = {
        location
        for location in locations
        if unquote(urlparse(location).path).startswith(prefixes)
    }
    if actual_scope != expected_canonicals:
        audit.fail(
            "sitemap_scope_exact",
            SITEMAP_PATH,
            f"expected={len(expected_canonicals)} actual={len(actual_scope)} "
            f"missing={len(expected_canonicals - actual_scope)} extra={len(actual_scope - expected_canonicals)}",
        )
    parent_url = absolute_url(f"/{PARENT}/")
    if parent_url not in location_set:
        audit.fail("sitemap_parent_hub", SITEMAP_PATH, f"missing={parent_url}")
    expected_count = len(CATEGORIES) * (len(rows) + 1)
    if len(expected_canonicals) != expected_count:
        audit.fail("sitemap_expected_contract", SITEMAP_PATH, f"expected_set={len(expected_canonicals)} target={expected_count}")
    audit.checked("sitemap_urls", len(actual_scope))


def main() -> None:
    audit = Audit()
    rows = read_rows(audit)
    if not rows:
        audit.finish()
        return

    all_schools = sorted(
        {name for row in rows for name in all_school_names(row) if len(name) >= 2},
        key=lambda value: (-len(value), value),
    )
    known_school_pattern = (
        re.compile("|".join(re.escape(name) for name in all_schools))
        if all_schools
        else None
    )

    metadata_values: dict[str, list[tuple[str, str]]] = {
        "title": [], "h1": [], "canonical": [], "description": [],
    }
    expected_canonicals: set[str] = set()
    records: list[ContentRecord] = []
    representative_assignments: dict[str, dict[str, Path]] = defaultdict(dict)

    for category in CATEGORIES:
        hub_values = validate_category_hub(category, rows, audit)
        if hub_values:
            for key, value in zip(metadata_values, hub_values):
                metadata_values[key].append((f"hub:{category.slug}", value))
            expected_canonicals.add(hub_values[2])

        root = SITE / PARENT / category.slug
        detail_files = sorted(root.glob("*/index.html")) if root.is_dir() else []
        expected_slugs = {slug_ko(row["근처 수업가능 동네"]) for row in rows}
        actual_slugs = {path.parent.name for path in detail_files}
        if actual_slugs != expected_slugs:
            audit.fail(
                "detail_output_set",
                root,
                f"expected={len(expected_slugs)} actual={len(actual_slugs)} "
                f"missing={len(expected_slugs - actual_slugs)} extra={len(actual_slugs - expected_slugs)}",
            )

        for row in rows:
            local = row["근처 수업가능 동네"].strip()
            path = root / slug_ko(local) / "index.html"
            if not path.is_file():
                audit.fail("detail_output_missing", path, "상세 출력물 없음")
                continue
            page = parse_page(path, audit)
            if page is None:
                continue
            expected_h1 = f"{local} {category.label}학원"
            expected_title = f"{expected_h1} | {SITE_NAME}"
            expected_path = detail_path(category, local)
            expected_canonical = absolute_url(expected_path)
            validate_metadata(
                page,
                expected_title=expected_title,
                expected_h1=expected_h1,
                expected_canonical=expected_canonical,
                audit=audit,
            )
            validate_breadcrumbs(
                page,
                expected_h1=expected_h1,
                expected_canonical=expected_canonical,
                audit=audit,
            )
            validate_schema(
                page,
                row=row,
                expected_h1=expected_h1,
                expected_canonical=expected_canonical,
                audit=audit,
            )
            validate_quick_answer(page, expected_h1=expected_h1, audit=audit)
            validate_faq(page, audit)
            validate_disclosure_and_forbidden_copy(page, audit)
            representative = validate_images(
                page,
                row=row,
                expected_h1=expected_h1,
                audit=audit,
            )
            if representative is not None:
                representative_assignments[category.slug][local] = representative
            validate_facts_and_schools(
                page,
                row=row,
                known_school_pattern=known_school_pattern,
                audit=audit,
            )
            validate_internal_links(
                page,
                expected_canonical=expected_canonical,
                expected_category_path=category_path(category),
                audit=audit,
            )

            description = page.descriptions[0] if len(page.descriptions) == 1 else ""
            for key, value in (
                ("title", page.title),
                ("h1", page.h1s[0] if len(page.h1s) == 1 else ""),
                ("canonical", page.canonicals[0] if len(page.canonicals) == 1 else ""),
                ("description", description),
            ):
                metadata_values[key].append((f"{category.slug}/{local}", value))
            expected_canonicals.add(expected_canonical)
            records.append(ContentRecord(
                label=f"{category.slug}/{local}",
                path=path,
                blocks=content_blocks(page),
                mask_values=[
                    local,
                    row.get("지역", "").strip(),
                    row.get("시or구", "").strip(),
                    row.get("센터명", "").strip(),
                    row.get("센터 주소", "").strip(),
                    category.slug,
                    category.label,
                    f"중학교 {category.grade}학년",
                    f"중{category.grade}",
                    category.subject,
                    *school_names(row),
                ],
            ))
            audit.checked("detail_pages")

    representative_pool = {
        path.resolve()
        for path in (SITE / "assets" / "representative").iterdir()
        if path.is_file() and path.suffix.lower() in {".gif", ".jpg", ".jpeg", ".png", ".webp"}
    } if (SITE / "assets" / "representative").is_dir() else set()
    if len(representative_pool) != EXPECTED_LOCALS:
        audit.fail(
            "representative_pool",
            SITE / "assets" / "representative",
            f"valid_files={len(representative_pool)} expected={EXPECTED_LOCALS}",
        )
    for category in CATEGORIES:
        assignments = representative_assignments.get(category.slug, {})
        assigned_paths = set(assignments.values())
        if len(assignments) != EXPECTED_LOCALS or len(assigned_paths) != EXPECTED_LOCALS:
            audit.fail(
                "representative_category_unique",
                SITE / PARENT / category.slug,
                f"assignments={len(assignments)} unique={len(assigned_paths)} expected={EXPECTED_LOCALS}",
            )
        elif assigned_paths != representative_pool:
            audit.fail(
                "representative_category_pool",
                SITE / PARENT / category.slug,
                f"missing_pool={len(representative_pool - assigned_paths)} outside_pool={len(assigned_paths - representative_pool)}",
            )
    for row in rows:
        local = row["근처 수업가능 동네"].strip()
        paths = [
            representative_assignments.get(category.slug, {}).get(local)
            for category in CATEGORIES
        ]
        present = [path for path in paths if path is not None]
        if len(present) == len(CATEGORIES) and len(set(present)) != len(CATEGORIES):
            audit.fail(
                "representative_locality_distinct",
                f"representatives/{local}",
                f"paths={[path.name for path in present]!r}",
            )
    audit.checked("representative_assignments", sum(len(value) for value in representative_assignments.values()))

    for key, values in metadata_values.items():
        groups: dict[str, list[str]] = defaultdict(list)
        for label, value in values:
            if value:
                groups[value].append(label)
        duplicates = {value: labels for value, labels in groups.items() if len(labels) > 1}
        for value, labels in list(duplicates.items())[:MAX_EXAMPLES]:
            audit.fail(f"{key}_unique", "metadata", f"pages={labels[:5]!r} value={value!r}")
        if len(values) != len(CATEGORIES) * (EXPECTED_LOCALS + 1):
            audit.fail(
                f"{key}_coverage",
                "metadata",
                f"values={len(values)} expected={len(CATEGORIES) * (EXPECTED_LOCALS + 1)}",
            )
        audit.checked(f"unique_{key}", len(groups))

    validate_parent_hub(audit)
    validate_sitemap(rows, expected_canonicals, audit)

    similarity: SimilarityResult | None = None
    expected_records = len(CATEGORIES) * EXPECTED_LOCALS
    if len(records) != expected_records:
        audit.fail("similarity_coverage", "content", f"records={len(records)} expected={expected_records}")
    else:
        similarity = audit_content_duplication(records, audit)
        audit.checked("similarity_documents", similarity.documents)

    audit.finish(similarity=similarity)


if __name__ == "__main__":
    main()
