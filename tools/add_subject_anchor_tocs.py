#!/usr/bin/env python3
"""Add page-specific anchor TOCs to subject academy detail pages.

The top-level ``과목별학원`` hub and its category hubs are intentionally left
untouched. TOC labels are read from each page's existing H2 headings so visible
copy stays page-specific and generator reruns remain consistent.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBJECT_ROOT = ROOT / "과목별학원"

SUBJECT_CATEGORIES = (
    "고1수학학원",
    "고1영어학원",
    "고2수학학원",
    "고2영어학원",
    "중1수학학원",
    "중1영어학원",
    "중2수학학원",
    "중2영어학원",
    "중3수학학원",
    "중3영어학원",
    "초3수학학원",
    "초3영어학원",
    "초4수학학원",
    "초4영어학원",
    "초5수학학원",
    "초5영어학원",
    "초6수학학원",
    "초6영어학원",
)
EXPECTED_PER_CATEGORY = 371
DETAIL_STYLESHEET_VERSION = "20260829-1"
FIXED_TARGET_IDS = (
    "center-information",
    "faq",
    "consultation-example",
    "related-pages",
)
KNOWN_TARGET_IDS = (
    "quick-summary",
    "study-guide",
    "section-01",
    "section-02",
    "section-03",
    "section-04",
    "section-05",
    "section-06",
    "section-07",
    *FIXED_TARGET_IDS,
)

TOC_START = "<!-- subject-page-anchor-toc:start -->"
TOC_END = "<!-- subject-page-anchor-toc:end -->"
TOC_BLOCK_RE = re.compile(
    rf"{re.escape(TOC_START)}.*?{re.escape(TOC_END)}",
    re.IGNORECASE | re.DOTALL,
)
TOC_REMOVE_RE = re.compile(
    rf"^[ \t]*{re.escape(TOC_START)}[ \t]*\n.*?"
    rf"^[ \t]*{re.escape(TOC_END)}[ \t]*(?:\n\s*\n)?",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)
OPEN_TAG_RE = re.compile(
    r"<(?P<tag>section|article)\b(?P<attrs>[^>]*)>", re.IGNORECASE
)
ID_RE = re.compile(r"\bid\s*=\s*([\"'])(?P<id>[^\"']+)\1", re.IGNORECASE)
ANY_ID_RE = re.compile(r"\bid\s*=\s*([\"'])(?P<id>[^\"']+)\1", re.IGNORECASE)
H2_RE = re.compile(r"<h2\b[^>]*>(?P<body>.*?)</h2>", re.IGNORECASE | re.DOTALL)
MAP_IMG_RE = re.compile(
    r'<img\b(?P<attrs>[^>]*\bsrc\s*=\s*["\'][^"\']*assets/maps/[^"\']+["\'][^>]*)>',
    re.IGNORECASE,
)
TOC_LINK_RE = re.compile(
    r"<li>\s*<a\s+href=[\"']#(?P<id>[^\"']+)[\"']>.*?"
    r"<span>(?P<label>.*?)</span>\s*</a>\s*</li>",
    re.IGNORECASE | re.DOTALL,
)
SITE_CSS_HREF_RE = re.compile(
    r"(?P<before><link\b[^>]*\bhref\s*=\s*[\"']"
    r"(?P<path>[^\"']*assets/site\.css))"
    r"(?:\?v=[^\"']*)?(?P<after>[\"'][^>]*>)",
    re.IGNORECASE,
)
BODY_RE = re.compile(r"<body(?P<attrs>[^>]*)>", re.IGNORECASE)
CLASS_RE = re.compile(r"\bclass\s*=\s*([\"'])(?P<classes>[^\"']*)\1", re.IGNORECASE)


@dataclass(frozen=True)
class PageEnhancement:
    source: str
    link_count: int
    map_aspect_added: int


def visible_text(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    return " ".join(html.unescape(text).split())


def detail_pages() -> tuple[list[Path], dict[str, int]]:
    pages: list[Path] = []
    counts: dict[str, int] = {}
    for category in SUBJECT_CATEGORIES:
        category_pages = sorted(
            (SUBJECT_ROOT / category).glob("*/index.html"),
            key=lambda path: path.as_posix(),
        )
        counts[category] = len(category_pages)
        pages.extend(category_pages)
    return pages, counts


def ensure_body_class(source: str) -> str:
    matches = list(BODY_RE.finditer(source))
    if len(matches) != 1:
        raise ValueError(f"Expected one body tag, found {len(matches)}")
    match = matches[0]
    tag = match.group(0)
    class_match = CLASS_RE.search(tag)
    if class_match:
        classes = class_match.group("classes").split()
        if "subject-detail-page" in classes:
            return source
        replacement = (
            tag[: class_match.start("classes")]
            + " ".join([*classes, "subject-detail-page"])
            + tag[class_match.end("classes") :]
        )
    else:
        replacement = tag[:-1] + ' class="subject-detail-page">'
    return source[: match.start()] + replacement + source[match.end() :]


def update_stylesheet_version(source: str) -> str:
    matches = list(SITE_CSS_HREF_RE.finditer(source))
    if len(matches) != 1:
        raise ValueError(f"Expected one site stylesheet link, found {len(matches)}")
    return SITE_CSS_HREF_RE.sub(
        rf"\g<before>?v={DETAIL_STYLESHEET_VERSION}\g<after>", source, count=1
    )


def ensure_map_aspect_ratio(source: str) -> tuple[str, int]:
    matches = list(MAP_IMG_RE.finditer(source))
    if len(matches) != 1:
        raise ValueError(f"Expected one map image, found {len(matches)}")
    match = matches[0]
    tag = match.group(0)
    width_match = re.search(r'\bwidth\s*=\s*["\'](?P<value>\d+)["\']', tag, re.IGNORECASE)
    height_match = re.search(r'\bheight\s*=\s*["\'](?P<value>\d+)["\']', tag, re.IGNORECASE)
    if not width_match or not height_match:
        raise ValueError("Map image intrinsic dimensions missing")
    desired = f"aspect-ratio: {width_match.group('value')} / {height_match.group('value')};"
    style_match = re.search(r'\bstyle\s*=\s*["\'](?P<value>[^"\']*)["\']', tag, re.IGNORECASE)
    if style_match:
        if style_match.group("value").strip() != desired:
            raise ValueError("Map image has an unexpected existing style")
        return source, 0
    replacement = tag[:-1] + f' style="{desired}">'
    return source[: match.start()] + replacement + source[match.end() :], 1


def add_id_to_match(source: str, match: re.Match[str], target_id: str) -> str:
    tag = match.group(0)
    id_match = ID_RE.search(tag)
    if id_match:
        current_id = id_match.group("id")
        if current_id != target_id:
            raise ValueError(
                f"Refusing to replace existing id {current_id!r} with {target_id!r}"
            )
        return source
    replacement = tag[:-1] + f' id="{target_id}">'
    return source[: match.start()] + replacement + source[match.end() :]


def unique_match(pattern: re.Pattern[str], source: str, label: str) -> re.Match[str]:
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise ValueError(f"Expected one {label}, found {len(matches)}")
    return matches[0]


def ensure_target_ids(source: str) -> str:
    quick_pattern = re.compile(
        r'<section\b(?P<attrs>[^>]*)\bclass="[^"]*\banswer-section\b[^"]*"[^>]*>',
        re.IGNORECASE,
    )
    quick_matches = list(quick_pattern.finditer(source))
    if len(quick_matches) > 1:
        raise ValueError(f"Expected zero or one quick-answer section, found {len(quick_matches)}")
    if quick_matches:
        source = add_id_to_match(source, quick_matches[0], "quick-summary")

    manuscript_pattern = re.compile(
        r'<section\b(?P<attrs>[^>]*)\bclass="[^"]*\bmanuscript-section\b[^"]*"[^>]*>',
        re.IGNORECASE,
    )
    source = add_id_to_match(
        source,
        unique_match(manuscript_pattern, source, "manuscript section"),
        "study-guide",
    )

    cards = list(
        re.finditer(
            r'<article\b[^>]*\bclass="[^"]*\bmanuscript-card\b[^"]*"[^>]*>',
            source,
            re.IGNORECASE,
        )
    )
    if len(cards) not in {6, 7}:
        raise ValueError(f"Expected six or seven manuscript cards, found {len(cards)}")
    for index in range(len(cards), 0, -1):
        source = add_id_to_match(source, cards[index - 1], f"section-{index:02d}")

    marker_targets = (
        (r"CENTER &amp; SCHOOL", "CENTER & SCHOOL", "center-information"),
        (r"FAQ", "FAQ", "faq"),
        (
            r"(?:CONSULTATION SCENARIO|PARENT REVIEW)",
            "consultation/review",
            "consultation-example",
        ),
        (r"RELATED ACADEMIES", "RELATED ACADEMIES", "related-pages"),
    )
    for marker_pattern, marker_label, target_id in marker_targets:
        pattern = re.compile(
            r'<section\b[^>]*\bclass="[^"]*\bsection\b[^"]*"[^>]*>'
            r'(?:(?!</section>).)*?'
            rf'<p\s+class="eyebrow">{marker_pattern}</p>',
            re.IGNORECASE | re.DOTALL,
        )
        match = unique_match(pattern, source, f"{marker_label} section")
        opening = OPEN_TAG_RE.match(match.group(0))
        if not opening:
            raise ValueError(f"Opening tag missing for {marker_label}")
        absolute_opening = re.match(OPEN_TAG_RE, source[match.start() :])
        if not absolute_opening:
            raise ValueError(f"Opening tag position missing for {marker_label}")
        shifted = _ShiftedMatch(absolute_opening, match.start())
        source = add_id_to_match(source, shifted, target_id)
    return source


class _ShiftedMatch:
    """Expose absolute offsets for a match created from a source slice."""

    def __init__(self, match: re.Match[str], offset: int) -> None:
        self._match = match
        self._offset = offset

    def group(self, *args: object) -> str:
        return self._match.group(*args)

    def start(self) -> int:
        return self._match.start() + self._offset

    def end(self) -> int:
        return self._match.end() + self._offset


def target_ids_for_source(source: str) -> list[str]:
    present_ids = {
        match.group("id")
        for match in ANY_ID_RE.finditer(source)
        if match.group("id") in KNOWN_TARGET_IDS
    }
    target_ids: list[str] = []
    if "quick-summary" in present_ids:
        target_ids.append("quick-summary")
    target_ids.append("study-guide")
    card_ids = [
        f"section-{index:02d}"
        for index in range(1, 8)
        if f"section-{index:02d}" in present_ids
    ]
    if len(card_ids) not in {6, 7}:
        raise ValueError(f"Expected six or seven manuscript target ids, found {len(card_ids)}")
    target_ids.extend(card_ids)
    target_ids.extend(FIXED_TARGET_IDS)
    return target_ids


def target_headings(source: str) -> list[tuple[str, str]]:
    target_ids = target_ids_for_source(source)
    openings: dict[str, re.Match[str]] = {}
    for opening in OPEN_TAG_RE.finditer(source):
        id_match = ID_RE.search(opening.group("attrs"))
        if id_match and id_match.group("id") in target_ids:
            target_id = id_match.group("id")
            if target_id in openings:
                raise ValueError(f"Duplicate target id {target_id!r}")
            openings[target_id] = opening

    missing = [target_id for target_id in target_ids if target_id not in openings]
    if missing:
        raise ValueError("Missing target ids: " + ", ".join(missing))

    ordered_openings = [openings[target_id] for target_id in target_ids]
    positions = [opening.start() for opening in ordered_openings]
    if positions != sorted(positions):
        raise ValueError("Target ids are not in the expected document order")

    headings: list[tuple[str, str]] = []
    for index, (target_id, opening) in enumerate(zip(target_ids, ordered_openings)):
        boundary = (
            ordered_openings[index + 1].start()
            if index + 1 < len(ordered_openings)
            else len(source)
        )
        heading = H2_RE.search(source, opening.end(), boundary)
        if not heading:
            raise ValueError(f"No H2 found for target {target_id!r}")
        label = visible_text(heading.group("body"))
        if not label:
            raise ValueError(f"Empty H2 found for target {target_id!r}")
        headings.append((target_id, label))
    return headings


def toc_markup(headings: list[tuple[str, str]]) -> str:
    items = []
    for number, (target_id, label) in enumerate(headings, start=1):
        items.append(
            "          <li>"
            f'<a href="#{html.escape(target_id, quote=True)}">'
            f'<span class="subject-page-toc-number" aria-hidden="true">{number:02d}</span>'
            f"<span>{html.escape(label)}</span>"
            "</a></li>"
        )
    return (
        f"    {TOC_START}\n"
        '    <nav class="section subject-page-toc" aria-labelledby="subject-page-toc-title">\n'
        '      <div class="subject-page-toc-panel">\n'
        '        <div class="subject-page-toc-heading">\n'
        '          <p class="eyebrow">PAGE CONTENTS</p>\n'
        '          <strong id="subject-page-toc-title">이 페이지에서 확인할 내용</strong>\n'
        '          <p>원하는 항목을 누르면 해당 내용으로 바로 이동합니다.</p>\n'
        "        </div>\n"
        '        <ol class="subject-page-toc-list">\n'
        + "\n".join(items)
        + "\n        </ol>\n"
        + "      </div>\n"
        + "    </nav>\n"
        + f"    {TOC_END}\n\n"
    )


def enhance_detail_html_with_stats(original: str) -> PageEnhancement:
    source = original.replace("\r\n", "\n").replace("\r", "\n")
    source = TOC_REMOVE_RE.sub("", source, count=1)
    source = ensure_body_class(source)
    source = update_stylesheet_version(source)
    source, map_aspect_added = ensure_map_aspect_ratio(source)
    source = ensure_target_ids(source)
    headings = target_headings(source)

    media_section = unique_match(
        re.compile(
            r'<section\b[^>]*\bclass="[^"]*\blocal-media-section\b[^"]*"[^>]*>',
            re.IGNORECASE,
        ),
        source,
        "local-media section",
    )
    insertion_point = source.rfind("\n", 0, media_section.start()) + 1
    source = source[:insertion_point] + toc_markup(headings) + source[insertion_point:]
    return PageEnhancement(source, len(headings), map_aspect_added)


def enhance_detail_html(original: str) -> str:
    """Return one generated detail page with its anchor TOC."""
    return enhance_detail_html_with_stats(original).source


def validate_page(source: str) -> list[str]:
    errors: list[str] = []
    if source.count(TOC_START) != 1 or source.count(TOC_END) != 1:
        errors.append("TOC marker count is not exactly one")
        return errors

    toc_match = TOC_BLOCK_RE.search(source)
    if not toc_match:
        errors.append("TOC block missing")
        return errors

    try:
        headings = target_headings(source)
    except Exception as exc:
        errors.append(str(exc))
        return errors

    toc_links = [
        (match.group("id"), visible_text(match.group("label")))
        for match in TOC_LINK_RE.finditer(toc_match.group(0))
    ]
    if toc_links != headings:
        errors.append("TOC link order or label does not match page H2 headings")

    stylesheet_matches = list(SITE_CSS_HREF_RE.finditer(source))
    if len(stylesheet_matches) != 1:
        errors.append(
            f"Expected one site stylesheet link, found {len(stylesheet_matches)}"
        )
    elif f"site.css?v={DETAIL_STYLESHEET_VERSION}" not in stylesheet_matches[0].group(0):
        errors.append("Detail stylesheet version is not current")

    body_match = BODY_RE.search(source)
    if not body_match or "subject-detail-page" not in body_match.group(0):
        errors.append("Detail-page body class missing")

    map_matches = list(MAP_IMG_RE.finditer(source))
    if len(map_matches) != 1:
        errors.append(f"Expected one map image, found {len(map_matches)}")
    else:
        map_tag = map_matches[0].group(0)
        width_match = re.search(r'\bwidth\s*=\s*["\'](\d+)["\']', map_tag)
        height_match = re.search(r'\bheight\s*=\s*["\'](\d+)["\']', map_tag)
        style_match = re.search(r'\bstyle\s*=\s*["\']([^"\']*)["\']', map_tag)
        if not width_match or not height_match or not style_match:
            errors.append("Map image aspect-ratio reservation missing")
        else:
            expected_style = f"aspect-ratio: {width_match.group(1)} / {height_match.group(1)};"
            if style_match.group(1).strip() != expected_style:
                errors.append("Map image aspect-ratio does not match its dimensions")

    all_ids = [match.group("id") for match in ANY_ID_RE.finditer(source)]
    if len(all_ids) != len(set(all_ids)):
        errors.append("Duplicate id found")
    for target_id, _label in headings:
        if all_ids.count(target_id) != 1:
            errors.append(
                f"Anchor target count for {target_id!r} is {all_ids.count(target_id)}"
            )

    media_position = source.find("local-media-section")
    first_target_position = source.find(f'id="{headings[0][0]}"')
    if media_position < 0 or toc_match.start() > media_position:
        errors.append("TOC is not before the local-media section")
    if first_target_position < 0 or toc_match.start() > first_target_position:
        errors.append("TOC is not before the first linked section")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Write changes to disk")
    parser.add_argument(
        "--check", action="store_true", help="Fail when detail pages are not current"
    )
    args = parser.parse_args()

    pages, category_counts = detail_pages()
    failures: list[str] = []
    for category, count in category_counts.items():
        if count != EXPECTED_PER_CATEGORY:
            failures.append(
                f"{category}: expected {EXPECTED_PER_CATEGORY} details, found {count}"
            )

    expected_total = len(SUBJECT_CATEGORIES) * EXPECTED_PER_CATEGORY
    if len(pages) != expected_total:
        failures.append(f"Expected {expected_total} detail pages, found {len(pages)}")

    for hub in [SUBJECT_ROOT / "index.html"] + [
        SUBJECT_ROOT / category / "index.html" for category in SUBJECT_CATEGORIES
    ]:
        if not hub.is_file():
            failures.append(f"Hub missing: {hub.relative_to(ROOT)}")
        elif TOC_START in hub.read_text(encoding="utf-8"):
            failures.append(f"Hub unexpectedly contains a TOC: {hub.relative_to(ROOT)}")

    changed = 0
    link_counts: dict[int, int] = {}
    map_aspect_added = 0
    for path in pages:
        original = path.read_bytes().decode("utf-8")
        newline = "\r\n" if "\r\n" in original else "\n"
        try:
            enhancement = enhance_detail_html_with_stats(original)
            validation_errors = validate_page(enhancement.source)
        except Exception as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        if validation_errors:
            failures.append(
                f"{path.relative_to(ROOT)}: " + "; ".join(validation_errors)
            )
            continue

        link_counts[enhancement.link_count] = (
            link_counts.get(enhancement.link_count, 0) + 1
        )
        map_aspect_added += enhancement.map_aspect_added
        serialized = enhancement.source.replace("\n", newline)
        if serialized != original:
            changed += 1
            if args.write:
                path.write_bytes(serialized.encode("utf-8"))

    distribution = ",".join(
        f"{count}:{pages_with_count}"
        for count, pages_with_count in sorted(link_counts.items())
    )
    total_links = sum(count * total for count, total in link_counts.items())
    print(
        f"pages={len(pages)} categories={len(SUBJECT_CATEGORIES)} "
        f"per_category={EXPECTED_PER_CATEGORY}"
    )
    print(f"toc_link_distribution={distribution} total_links={total_links}")
    print(f"map_aspect_added={map_aspect_added}")
    print(
        f"changed={changed} mode={'write' if args.write else 'check' if args.check else 'dry-run'}"
    )

    if failures:
        print(f"failures={len(failures)}", file=sys.stderr)
        for failure in failures[:50]:
            print(failure, file=sys.stderr)
        return 1
    if args.check and changed:
        print("Target pages are not up to date. Run with --write.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
