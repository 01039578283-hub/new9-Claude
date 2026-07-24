from __future__ import annotations

import hashlib
import re
from collections import Counter
from itertools import permutations
from pathlib import Path
from zipfile import ZipFile

import generate_middle_math_pages as shared


SITE = shared.SITE
COMMON = shared.COMMON
SITE_NAME = shared.SITE_NAME
PHONE_DISPLAY = shared.PHONE_DISPLAY
PARENT = "과목별학원"
CATEGORY = "고1수학학원"
SUBJECT_LABEL = "고1 수학"
SUBJECT = "수학"
SUBJECT_EN = "MATH"
FOCUS_LABEL = "내신·오답관리"
GRADE_NUMBER = 1
GRADE_EN = "GRADE 10"
ZIP_PATH = (
    Path.home()
    / "Desktop"
    / "스터디와와.com 추가 원고"
    / "고1 수학학원.zip"
)

esc = shared.esc
read_csv = shared.read_csv
slug_ko = shared.slug_ko
split_items = shared.split_items
absolute_url = shared.absolute_url
json_script = shared.json_script
nav_html = shared.nav_html
footer_html = shared.footer_html
head_html = shared.head_html
page_shell = shared.page_shell
find_map = shared.find_map
image_size = shared.image_size
center_entity_id = shared.center_entity_id
region_blocks_html = shared.region_blocks_html
directory_filter_script = shared.directory_filter_script

SECTION_RE = re.compile(
    r"^\[(페이지타이틀|메타설명|본문|FAQ|학부모후기|JSON-LD 요약)\]\s*$",
    re.MULTILINE,
)
FAQ_RE = re.compile(
    r"Q\d+\.\s*(.+?)\s*\nA\d+\.\s*(.+?)(?=\nQ\d+\.|\Z)",
    re.DOTALL,
)


def parse_manuscript(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    parsed: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        parsed[match.group(1)] = text[match.end() : end].strip()
    required = {"페이지타이틀", "메타설명", "본문", "FAQ", "학부모후기", "JSON-LD 요약"}
    missing = required - parsed.keys()
    if missing:
        raise ValueError(f"원고 구역 누락: {sorted(missing)}")
    return parsed


def public_copy(value: str) -> str:
    """제작 과정의 용어를 학부모가 읽는 자연스러운 안내 문장으로 바꾼다."""
    replacements = (
        ("D열에 제공된 수업학교", "제공 자료에 정리된 수업 가능 학교"),
        ("D열 수업학교", "제공된 수업 가능 학교"),
        ("D열에 제공된 학교", "제공 자료에 정리된 학교"),
        ("D열에 제공된", "제공 자료에 정리된"),
        ("D열에", "제공 자료에"),
        ("D열", "제공 자료"),
        ("AEO형 답변", "질문 중심의 안내"),
        ("AEO형", "질문 중심의"),
        ("GEO 관점의 지역 정보", "실제 통학을 판단하는 지역 정보"),
        ("GEO형", "지역 맥락을 반영한"),
        ("정보성 교육 페이지", "학습 안내 페이지"),
        ("정보성 페이지", "학습 안내 페이지"),
        ("FAQ에서는", "자주 묻는 질문에서는"),
        ("원고에서는", "안내에서는"),
        ("원고에는", "안내에는"),
        ("원고에서", "안내에서"),
        ("원고는", "안내는"),
        ("원고를", "안내를"),
        ("원고가", "안내가"),
        ("원고", "안내"),
    )
    result = value
    for source, target in replacements:
        result = result.replace(source, target)
    return result


def load_manuscripts() -> dict[str, dict[str, str]]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(ZIP_PATH)
    manuscripts: dict[str, dict[str, str]] = {}
    with ZipFile(ZIP_PATH) as archive:
        names = sorted(name for name in archive.namelist() if name.lower().endswith(".txt"))
        for name in names:
            text = archive.read(name).decode("utf-8-sig")
            parsed = parse_manuscript(text)
            title = parsed["페이지타이틀"].strip()
            suffix = f" {SUBJECT_LABEL}학원"
            if not title.endswith(suffix):
                raise ValueError(f"예상하지 못한 페이지 제목: {title}")
            local = title[: -len(suffix)].strip()
            if local in manuscripts:
                raise ValueError(f"중복 원고: {local}")
            parsed = {
                key: value if key == "페이지타이틀" else public_copy(value)
                for key, value in parsed.items()
            }
            manuscripts[local] = parsed
    return manuscripts


def parse_body(value: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    intro: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_title = ""
    current_paragraphs: list[str] = []

    def flush() -> None:
        nonlocal current_title, current_paragraphs
        if current_title:
            sections.append((current_title, current_paragraphs))
        current_title = ""
        current_paragraphs = []

    chunks = re.split(r"\n\s*\n", value.strip())
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.startswith("## "):
            flush()
            lines = chunk.splitlines()
            current_title = lines[0][3:].strip()
            rest = "\n".join(lines[1:]).strip()
            if rest:
                current_paragraphs.append(rest)
        elif current_title:
            current_paragraphs.append(chunk)
        else:
            intro.append(chunk)
    flush()
    return intro, sections


def parse_faq(value: str) -> list[tuple[str, str]]:
    faqs = [(q.strip(), re.sub(r"\s+", " ", a).strip()) for q, a in FAQ_RE.findall(value)]
    if not faqs:
        raise ValueError("FAQ 질문·답변을 해석하지 못했습니다.")
    return faqs


def paragraph_list(value: str) -> list[str]:
    return [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", value) if part.strip()]


def paragraph_signature(value: str, local: str) -> str:
    normalized = re.sub(r"\s+", " ", value).strip()
    normalized = re.sub(re.escape(local), "<LOCAL>", normalized)
    return re.sub(r"\d+(?:-\d+)*", "<NUM>", normalized)


def repeated_body_signatures(
    manuscripts: dict[str, dict[str, str]],
) -> set[str]:
    counts: Counter[str] = Counter()
    for local, manuscript in manuscripts.items():
        intro, sections = parse_body(manuscript["본문"])
        for paragraph in intro:
            counts[paragraph_signature(paragraph, local)] += 1
        for _, paragraphs in sections:
            for paragraph in paragraphs:
                counts[paragraph_signature(paragraph, local)] += 1
    return {signature for signature, count in counts.items() if count > 1}


def order_sections_for_page(
    sections: list[tuple[str, list[str]]],
    local: str,
) -> list[tuple[str, list[str]]]:
    if len(sections) < 6:
        return sections
    flexible_count = 4
    patterns = list(permutations(range(flexible_count)))
    digest = hashlib.sha256(f"{CATEGORY}|{local}|section-order".encode("utf-8")).digest()
    pattern = patterns[int.from_bytes(digest[:2], "big") % len(patterns)]
    return [sections[index] for index in pattern] + sections[flexible_count:]


def school_names(row: dict[str, str]) -> list[str]:
    result: list[str] = []
    for key in ("타깃학교\n(초)", "타깃학교\n(중)", "타깃학교\n(고)"):
        for name in split_items(row.get(key, "")):
            if name not in result:
                result.append(name)
    return result


def compact_meta_description(
    value: str,
    row: dict[str, str],
    title: str,
    index: int,
) -> str:
    description = re.sub(r"\s+", " ", value).strip()
    description = description.replace(
        "학부모를 위한 정보성 원고입니다.",
        "학부모가 확인할 선택 기준을 안내합니다.",
    )
    description = description.replace("정보성 원고", "학습 안내")
    if 80 <= len(description) <= 155:
        return description

    local = row["근처 수업가능 동네"].strip()
    schools = school_names(row)
    school_reference = (
        f"{schools[0]} 등 제공 학교 자료"
        if schools
        else "학생이 준비한 실제 학교 자료"
    )
    first_sentence_match = re.match(r"(.+?[.!?])(?:\s|$)", description)
    first_sentence = (
        first_sentence_match.group(1).strip()
        if first_sentence_match
        else f"{title} 선택 기준을 안내합니다."
    )
    variants = [
        f"학생 진단, {school_reference}, {FOCUS_LABEL} 관련 상담 전 확인 항목을 정리했습니다.",
        f"최근 오답과 {school_reference}를 바탕으로 {FOCUS_LABEL} 관련 상담 질문과 위치 정보를 안내합니다.",
        f"{school_reference}, 학생의 반복 오류와 {FOCUS_LABEL} 관련 상담 전 점검 항목을 확인할 수 있습니다.",
        f"{local} 학생의 학습 기록, {school_reference}, {FOCUS_LABEL} 관련 상담 기준을 함께 살펴봅니다.",
    ]
    candidate = f"{first_sentence} {variants[index % len(variants)]}"
    if len(candidate) <= 155:
        return candidate

    suffix = " 핵심 학습관리와 상담 기준을 정리했습니다."
    allowed = 155 - len(suffix)
    shortened = candidate[:allowed].rstrip(" ,·")
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0].rstrip(" ,·")
    result = f"{shortened}{suffix}"
    if len(result) < 80:
        result = (
            f"{title}의 학생 진단, 학교 자료 확인, 오답 재학습과 "
            f"{FOCUS_LABEL} 상담 기준을 정리했습니다."
        )
    return result[:155].rstrip(" ,·")


def contextualize_repeated_paragraph(
    value: str,
    *,
    row: dict[str, str],
    local: str,
    section_title: str,
    section_index: int,
    paragraph_index: int,
    repeated_signatures: set[str],
    force: bool = False,
) -> str:
    if not force and paragraph_signature(value, local) not in repeated_signatures:
        return value

    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    seed = (
        f"{CATEGORY}|{local}|{section_title}|{section_index}|{paragraph_index}"
    ).encode("utf-8")
    digest = hashlib.sha256(seed).digest()
    evidence = [
        "최근 시험지의 오답 표시",
        "학교 범위표와 교과서 진도",
        "주간 과제 완료 기록",
        "해설 없이 다시 푼 결과",
        "단원별 풀이 시간",
        "서술 과정에서 빠진 조건",
        "수업 뒤에 남긴 질문 목록",
        "시험 전 남은 학습일",
        "교재별 완료 범위",
        "오답을 다시 확인할 날짜",
        "학생이 설명한 풀이 근거",
    ][digest[0] % 11]
    outcome = [
        "다음 점검 시점",
        "우선 복습 단원",
        "혼자 다시 풀 문제",
        "질문 순서",
        "시험 전 완료 범위",
        "과제량 조절 시점",
        "보충 설명이 필요한 개념",
        "재풀이 성공 여부",
        "학교 자료 복습 순서",
        "주간 최소 학습량",
        "상담 후 점검 항목",
    ][digest[1] % 11]
    location = " ".join(part for part in (region, district, local) if part)
    templates = [
        f"{location} 상담에서는 {evidence} 항목과 {outcome} 항목을 함께 정리해야 이 기준을 실제 학습 계획으로 옮기기 쉽습니다.",
        f"이 기준을 {local} 학생에게 적용할 때는 확인 자료로 {evidence} 항목을 살핀 뒤, 후속 계획으로 {outcome} 항목을 정하는 순서가 적절합니다.",
        f"{local}의 실제 계획에는 {evidence} 점검과 {outcome} 설정이 함께 들어가야 상담 내용이 수업 후에도 이어집니다.",
        f"학부모가 {local}에서 이 항목을 비교한다면 {evidence} 관리 방식과 {outcome} 설정 기준을 물어볼 수 있습니다.",
        f"{location}에서는 {evidence} 자료를 판단 근거로 삼고, 상담 후에는 {outcome} 내용을 짧게 정리해 두는 편이 좋습니다.",
        f"학생의 설명을 들은 뒤 {evidence} 항목을 확인하고 {outcome} 기준을 함께 정하면 {local}의 학습 계획이 더 구체적으로 바뀝니다.",
        f"{section_title} 내용을 점검할 때 {local}에서는 {evidence} 점검과 {outcome} 설정을 한 흐름으로 연결해 보는 것이 좋습니다.",
    ]
    base = value.rstrip()
    separator = "" if base.endswith((".", "?", "!", "다.", "요.")) else "."
    return f"{base}{separator} {templates[digest[2] % len(templates)]}"


def representative_asset(index: int) -> str:
    matches = sorted(
        (SITE / "assets" / "representative").glob(f"rep-{index + 1:03d}.*")
    )
    if len(matches) != 1:
        raise FileNotFoundError(
            f"대표 이미지 대응 실패 index={index + 1}, matches={matches}"
        )
    return f"assets/representative/{matches[0].name}"


def page_ld(
    *,
    row: dict[str, str],
    title: str,
    description: str,
    summary: str,
    canonical: str,
    rep_image: str,
    center_image: str,
    map_image: str,
    faqs: list[tuple[str, str]],
    sections: list[tuple[str, list[str]]],
    nearby: list[tuple[str, str]],
) -> dict:
    local = row["근처 수업가능 동네"].strip()
    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    center = row.get("센터명", "").strip() or f"{local} 학습코칭센터"
    address = row.get("센터 주소", "").strip()
    schools = school_names(row)
    org_id = center_entity_id(center, address)
    page_id = f"{canonical}#webpage"
    service_id = f"{canonical}#service"
    topics = [
        title,
        SUBJECT_LABEL,
        f"고등학교 {GRADE_NUMBER}학년 {SUBJECT}",
        f"{SUBJECT} 내신",
        "오답 재학습",
        region,
        district,
        local,
    ]
    section_names = [name for name, _ in sections]
    related_items = [
        {
            "@type": "ListItem",
            "position": index + 1,
            "name": name,
            "url": url,
        }
        for index, (name, url) in enumerate(nearby)
    ]
    grade_value = row.get(f"가능학년\n({SUBJECT})", "").strip()
    offer = {
        "@type": "Offer",
        "url": canonical,
        "availability": "https://schema.org/InStock",
        "itemOffered": {"@id": service_id},
    }
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": page_id,
                "url": canonical,
                "name": title,
                "description": description,
                "inLanguage": "ko-KR",
                "primaryImageOfPage": {"@id": f"{canonical}#primaryimage"},
                "breadcrumb": {"@id": f"{canonical}#breadcrumb"},
                "mainEntity": {"@id": service_id},
                "about": [{"@type": "Thing", "name": topic} for topic in topics[:5]],
                "mentions": [{"@type": "Thing", "name": topic} for topic in topics],
                "hasPart": [
                    {"@type": "WebPageElement", "name": name} for name in section_names
                ]
                + [
                    {"@type": "WebPageElement", "name": "센터 위치 안내"},
                    {"@type": "WebPageElement", "name": "자주 묻는 질문"},
                    {"@type": "WebPageElement", "name": "학부모 상담 후기"},
                ],
            },
            {
                "@type": "ImageObject",
                "@id": f"{canonical}#primaryimage",
                "contentUrl": rep_image,
                "url": rep_image,
                "caption": f"{title} {SITE_NAME} 대표",
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "홈", "item": "/"},
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": PARENT,
                        "item": f"/{PARENT}/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": CATEGORY,
                        "item": f"/{PARENT}/{CATEGORY}/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 4,
                        "name": title,
                        "item": canonical,
                    },
                ],
            },
            {
                "@type": ["EducationalOrganization", "LocalBusiness"],
                "@id": org_id,
                "name": center,
                "alternateName": SITE_NAME,
                "url": canonical,
                "telephone": PHONE_DISPLAY,
                "image": [rep_image, center_image, map_image],
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": address,
                    "addressLocality": district,
                    "addressRegion": region,
                    "addressCountry": "KR",
                },
                "areaServed": {
                    "@type": "AdministrativeArea",
                    "name": f"{region} {district} {local}".strip(),
                },
                "knowsAbout": topics[:6],
                "makesOffer": [offer],
            },
            {
                "@type": "Service",
                "@id": service_id,
                "name": title,
                "description": summary,
                "serviceType": f"{SUBJECT_LABEL} 학습관리",
                "provider": {"@id": org_id},
                "url": canonical,
                "areaServed": {
                    "@type": "AdministrativeArea",
                    "name": f"{region} {district} {local}".strip(),
                },
                "audience": {
                    "@type": "EducationalAudience",
                    "educationalRole": f"고등학교 {GRADE_NUMBER}학년 학생",
                },
                "about": [{"@type": "Thing", "name": topic} for topic in topics[:5]],
                "mentions": [{"@type": "Thing", "name": topic} for topic in topics[5:]],
                "offers": offer,
            },
            {
                "@type": "Article",
                "@id": f"{canonical}#article",
                "headline": title,
                "description": summary,
                "image": [rep_image, center_image, map_image],
                "inLanguage": "ko-KR",
                "mainEntityOfPage": {"@id": page_id},
                "author": {"@id": org_id},
                "publisher": {"@id": org_id},
                "articleSection": section_names,
                "about": [{"@type": "Thing", "name": topic} for topic in topics[:5]],
                "mentions": [{"@type": "Thing", "name": topic} for topic in topics],
                "hasPart": [
                    {"@type": "WebPageElement", "name": name} for name in section_names
                ],
            },
            {
                "@type": "FAQPage",
                "@id": f"{canonical}#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {"@type": "Answer", "text": answer},
                    }
                    for question, answer in faqs
                ],
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#schools",
                "name": f"{title} 수업 가능 학교 참고",
                "numberOfItems": len(schools),
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": school}
                    for i, school in enumerate(schools)
                ],
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#related",
                "name": f"{title} 관련 내부링크",
                "itemListElement": related_items,
            },
            {
                "@type": "PropertyValue",
                "name": f"{SUBJECT} 수업 가능 학년",
                "value": grade_value or "상담 시 확인",
            },
        ],
    }


def detail_page(
    row: dict[str, str],
    index: int,
    manuscript: dict[str, str],
    rows: list[dict[str, str]],
    repeated_signatures: set[str],
) -> str:
    local = row["근처 수업가능 동네"].strip()
    slug = slug_ko(local)
    title = manuscript["페이지타이틀"].strip()
    description = compact_meta_description(
        manuscript["메타설명"],
        row,
        title,
        index,
    )
    summary = re.sub(r"\s+", " ", manuscript["JSON-LD 요약"]).strip()
    intro, sections = parse_body(manuscript["본문"])
    sections = order_sections_for_page(sections, local)
    faqs = parse_faq(manuscript["FAQ"])
    reviews = paragraph_list(manuscript["학부모후기"])
    canonical = f"/{PARENT}/{CATEGORY}/{slug}/"

    rep_asset = representative_asset(index)
    rep_image = f"/{rep_asset}"
    center_asset = (
        "assets/centers/common/seoul6839.webp"
        if row.get("지역", "").strip() == "서울"
        else "assets/centers/common/local6839.webp"
    )
    center_mobile_asset = center_asset.replace(".webp", "-mobile.webp")
    map_asset = find_map(row)
    center_image = f"/{center_asset}"
    map_image = f"/{map_asset}"
    rep_size = image_size(rep_asset)
    center_size = image_size(center_asset)
    map_size = image_size(map_asset)

    nearby_rows = [
        rows[(index + offset) % len(rows)] for offset in (-2, -1, 1, 2)
    ]
    nearby = [
        (
            f"{item['근처 수업가능 동네']} {SUBJECT_LABEL}학원",
            f"/{PARENT}/{CATEGORY}/{slug_ko(item['근처 수업가능 동네'])}/",
        )
        for item in nearby_rows
    ]
    related_for_schema = [
        (CATEGORY, f"/{PARENT}/{CATEGORY}/"),
        (PARENT, f"/{PARENT}/"),
        *nearby,
    ]
    ld = page_ld(
        row=row,
        title=title,
        description=description,
        summary=summary,
        canonical=canonical,
        rep_image=rep_image,
        center_image=center_image,
        map_image=map_image,
        faqs=faqs,
        sections=sections,
        nearby=related_for_schema,
    )
    head = head_html(
        f"{title} | {SITE_NAME}",
        description,
        3,
        canonical,
        "article",
        rep_image,
        ld,
    )

    rendered_intro = [
        contextualize_repeated_paragraph(
            paragraph,
            row=row,
            local=local,
            section_title=f"{title} 핵심 요약",
            section_index=-1,
            paragraph_index=paragraph_index,
            repeated_signatures=repeated_signatures,
        )
        for paragraph_index, paragraph in enumerate(intro)
    ]
    rendered_sections = [
        (
            section_title,
            [
                contextualize_repeated_paragraph(
                    paragraph,
                    row=row,
                    local=local,
                    section_title=section_title,
                    section_index=section_index,
                    paragraph_index=paragraph_index,
                    repeated_signatures=repeated_signatures,
                )
                for paragraph_index, paragraph in enumerate(paragraphs)
            ],
        )
        for section_index, (section_title, paragraphs) in enumerate(sections)
    ]
    intro_html = "".join(
        f"<p>{esc(paragraph)}</p>" for paragraph in rendered_intro
    )
    section_html = "\n".join(
        f"""      <article class="manuscript-card">
        <h2>{esc(section_title)}</h2>
        {''.join(f'<p>{esc(paragraph)}</p>' for paragraph in paragraphs)}
      </article>"""
        for section_title, paragraphs in rendered_sections
    )
    faq_html = "\n".join(
        f'<details class="faq-item"{" open" if i == 0 else ""}><summary>{esc(question)}</summary><p>{esc(answer)}</p></details>'
        for i, (question, answer) in enumerate(faqs)
    )
    review_html = "\n".join(
        f'<article class="review-card"><span class="tag">학부모 상담 후기</span><p>{esc(review)}</p></article>'
        for review in reviews
    )
    schools = school_names(row)
    school_html = (
        "".join(f"<span>{esc(name)}</span>" for name in schools)
        if schools
        else "<span>상담 시 학교 확인</span>"
    )
    fee_link = row.get("센터 교습비", "").strip()
    fee_action = (
        f'<a class="btn btn-primary" href="{esc(fee_link)}" target="_blank" rel="noopener noreferrer">센터 교습비 공개 자료 확인</a>'
        if fee_link
        else '<a class="btn btn-ghost" href="../../../상담문의/index.html">교습비 문의하기</a>'
    )
    nearby_html = "".join(
        f'<a href="../{slug_ko(item["근처 수업가능 동네"])}/index.html"><strong>{esc(item["근처 수업가능 동네"])} {esc(SUBJECT_LABEL)}학원</strong><small>인근 지역 안내</small></a>'
        for item in nearby_rows
    )
    subject_links = []
    subject_labels = {
        "고1수학학원": "고1 수학학원",
        "고1영어학원": "고1 영어학원",
        "고2수학학원": "고2 수학학원",
        "고2영어학원": "고2 영어학원",
    }
    for category, label in subject_labels.items():
        if category == CATEGORY:
            continue
        target = SITE / PARENT / category / slug
        if target.exists():
            subject_links.append(
                f'<a href="../../{category}/{slug}/index.html"><strong>{esc(local)} {esc(label)}</strong><small>같은 동네 다른 과목 안내</small></a>'
            )
    nationwide_links = []
    for category in ("중등수학학원", "중등영어학원", "와와학습코칭센터"):
        target = SITE / "전국학원" / category / slug
        if target.exists():
            nationwide_links.append(
                f'<a href="../../../전국학원/{category}/{slug}/index.html"><strong>{esc(local)} {esc(category)}</strong><small>같은 동네 전국학원 안내</small></a>'
            )

    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    center = row.get("센터명", "").strip()
    address = row.get("센터 주소", "").strip()
    grade = row.get(f"가능학년\n({SUBJECT})", "").strip() or "상담 시 확인"
    registration = row.get("교육지원청 등록번호", "").strip()
    education_name = row.get("교육지원청명칭", "").strip()

    body = f"""{nav_html(3, PARENT)}
  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../../index.html">홈</a><span>/</span><a href="../../index.html">{PARENT}</a><span>/</span><a href="../index.html">{CATEGORY}</a><span>/</span><span>{esc(title)}</span></p>
      <p class="eyebrow">{GRADE_EN} {SUBJECT_EN} LOCAL GUIDE</p>
      <h1>{esc(title)}</h1>
      <p class="lead">{esc(description)}</p>
      <div class="badge-row"><span>{esc(region)}</span><span>{esc(district)}</span><span>{esc(SUBJECT_LABEL)}</span><span>{esc(FOCUS_LABEL)}</span></div>
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">전화 상담하기</a>
        <a class="btn btn-ghost" href="../../../상담문의/index.html">상담문의</a>
      </div>
    </section>

    <section class="section local-media-section">
      <img src="../../../{rep_image.lstrip('/')}" alt="{esc(title + ' ' + SITE_NAME + ' 대표')}" width="{rep_size[0]}" height="{rep_size[1]}" style="display:none;">
      <div class="media-row">
        <figure class="frame"><picture><source media="(max-width: 640px)" srcset="../../../{center_mobile_asset}"><img src="../../../{center_asset}" alt="{esc(title + ' 본문 ' + SITE_NAME)}" width="{center_size[0]}" height="{center_size[1]}" decoding="async" fetchpriority="high"></picture></figure>
        <figure class="frame"><img src="../../../{map_asset}" alt="{esc(title + ' 지도 ' + SITE_NAME)}" width="{map_size[0]}" height="{map_size[1]}" loading="lazy" decoding="async"></figure>
      </div>
      <p class="lead">{esc(center)}의 위치와 {esc(local)} 생활권을 기준으로 {esc(SUBJECT_LABEL)} 상담 정보를 확인합니다. 방문 전 실제 이동 동선과 상담 가능 시간을 함께 확인해 주세요.</p>
    </section>

    <section class="section manuscript-section">
      <div class="section-head">
        <p class="eyebrow">LOCAL STUDY GUIDE</p>
        <h2>{esc(title)} 선택 기준</h2>
      </div>
      <div class="manuscript-intro">{intro_html}</div>
      <div class="manuscript-grid">{section_html}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">CENTER &amp; SCHOOL</p>
        <h2>{esc(local)} 센터·수업 가능 학교 정보</h2>
        <p class="lead">센터정보 정리 자료에 등록된 내용만 반영했습니다. 실제 수업 가능 여부와 시간표는 상담 시 확인해 주세요.</p>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">센터</span><h3>{esc(center)}</h3><p>{esc(address)}</p></article>
        <article class="info-card"><span class="tag">가능 학년</span><h3>{esc(SUBJECT)} {esc(grade)}</h3><p>현재 학년과 학교 진도에 맞는 반 편성 여부를 상담에서 확인합니다.</p></article>
        <article class="info-card"><span class="tag">교육지원청</span><h3>{esc(education_name or '등록 정보')}</h3><p>{esc(registration or '상담 시 등록 정보를 확인해 주세요.')}</p></article>
      </div>
      <p class="lead" style="margin-top:18px;">수업 가능 학교 참고</p>
      <div class="chip-list">{school_html}</div>
      <div class="hero-actions" style="margin-top:20px;">{fee_action}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">FAQ</p>
        <h2>{esc(title)} 자주 묻는 질문</h2>
      </div>
      <div class="faq-list">{faq_html}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">PARENT REVIEW</p>
        <h2>{esc(local)} {esc(SUBJECT_LABEL)} 상담 후기</h2>
      </div>
      <div class="review-grid">{review_html}</div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">RELATED ACADEMIES</p>
        <h2>{esc(local)}와 주변 학원 페이지</h2>
        <p class="lead">같은 동네의 다른 학습관리 안내와 인근 {esc(SUBJECT_LABEL)}학원 페이지를 한곳에 정리했습니다.</p>
      </div>
      <div class="link-grid">
        <a href="../index.html"><strong>{esc(CATEGORY)} 전체</strong><small>과목 카테고리 허브</small></a>
        <a href="../../index.html"><strong>과목별학원</strong><small>전체 과목 허브</small></a>
        {''.join(subject_links)}
        {''.join(nationwide_links)}
        {nearby_html}
      </div>
    </section>
  </main>
{footer_html(3)}"""
    return page_shell(head, body)


def hub_ld(name: str, canonical: str, description: str, items: list[dict]) -> dict:
    parts = [part for part in canonical.strip("/").split("/") if part]
    breadcrumb = [{"@type": "ListItem", "position": 1, "name": "홈", "item": "/"}]
    current = ""
    for index, part in enumerate(parts, 2):
        current += f"/{part}"
        breadcrumb.append(
            {"@type": "ListItem", "position": index, "name": part, "item": f"{current}/"}
        )
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": f"{canonical}#webpage",
                "url": canonical,
                "name": name,
                "description": description,
                "inLanguage": "ko-KR",
                "breadcrumb": {"@id": f"{canonical}#breadcrumb"},
                "about": [
                    {"@type": "Thing", "name": f"{SUBJECT_LABEL}학원"},
                    {"@type": "Thing", "name": "지역별 학원 안내"},
                ],
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical}#breadcrumb",
                "itemListElement": breadcrumb,
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#itemlist",
                "name": f"{name} 목록",
                "numberOfItems": len(items),
                "itemListElement": items,
            },
        ],
    }


def parent_hub(rows: list[dict[str, str]]) -> None:
    canonical = f"/{PARENT}/"
    description = (
        f"{SITE_NAME} 과목별학원 허브입니다. 학년과 과목을 선택한 뒤 "
        "371개 동네별 학습관리 안내를 확인할 수 있습니다."
    )
    category_meta = {
        "고1수학학원": "고1 수학 내신·오답·학습계획 안내",
        "고1영어학원": "고1 영어 어휘·문법·독해·내신 안내",
        "고2수학학원": "고2 수학 내신·오답·취약단원 학습관리 안내",
        "고2영어학원": "고2 영어 어휘·구문·독해·서술형 학습관리 안내",
    }
    available_categories = [
        name
        for name in category_meta
        if (SITE / PARENT / name).exists() or name == CATEGORY
    ]
    items = [
        {
            "@type": "ListItem",
            "position": index + 1,
            "name": name,
            "url": f"/{PARENT}/{name}/",
        }
        for index, name in enumerate(available_categories)
    ]
    ld = hub_ld(PARENT, canonical, description, items)
    head = head_html(
        f"{PARENT} | {SITE_NAME}",
        description,
        1,
        canonical,
        "website",
        "/assets/generated/academy-og.jpg",
        ld,
    )
    body = f"""{nav_html(1, PARENT)}
  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../index.html">홈</a><span>/</span><span>{PARENT}</span></p>
      <p class="eyebrow">SUBJECT ACADEMY HUB</p>
      <h1>{PARENT}</h1>
      <p class="lead">학년과 과목을 먼저 선택한 뒤, 원하는 동네의 학습관리 기준과 센터 정보를 확인할 수 있도록 정리했습니다.</p>
    </section>
    <section class="section">
      <div class="section-head">
        <p class="eyebrow">ACADEMY CATEGORY</p>
        <h2>학년·과목별 학원 안내</h2>
        <p class="lead">현재 준비된 카테고리부터 순서대로 확인해 주세요. 각 지역 페이지는 별도 원고와 실제 센터 자료를 바탕으로 구성했습니다.</p>
      </div>
      <div class="category-grid">
        {''.join(f'<a href="{esc(name)}/index.html"><strong>{esc(name)}</strong><small>전국 {len(rows)}개 동네 · {esc(category_meta[name])}</small></a>' for name in available_categories)}
      </div>
    </section>
    <section class="section">
      <div class="section-head">
        <p class="eyebrow">HOW TO USE</p>
        <h2>필요한 페이지를 찾는 순서</h2>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">01</span><h3>학년·과목 선택</h3><p>현재 필요한 학년과 과목 카테고리를 먼저 선택합니다.</p></article>
        <article class="info-card"><span class="tag">02</span><h3>동네 선택</h3><p>검색 또는 시도·시군구 필터를 이용해 가까운 동네를 찾습니다.</p></article>
        <article class="info-card"><span class="tag">03</span><h3>상담 기준 확인</h3><p>원고, 수업 가능 학교, 위치, 교습비 공개 자료를 함께 확인합니다.</p></article>
      </div>
    </section>
  </main>
{footer_html(1)}"""
    out = SITE / PARENT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_shell(head, body), encoding="utf-8")


def category_hub(rows: list[dict[str, str]]) -> None:
    canonical = f"/{PARENT}/{CATEGORY}/"
    description = (
        f"전국 {len(rows)}개 동네의 {SUBJECT_LABEL}학원 페이지를 지역별로 정리했습니다. "
        "동네별 내신 준비, 학교 참고 정보, 상담 기준과 센터 위치를 확인할 수 있습니다."
    )
    items = [
        {
            "@type": "ListItem",
            "position": index + 1,
            "name": f"{row['근처 수업가능 동네']} {SUBJECT_LABEL}학원",
            "url": f"{canonical}{slug_ko(row['근처 수업가능 동네'])}/",
        }
        for index, row in enumerate(rows)
    ]
    ld = hub_ld(CATEGORY, canonical, description, items)
    head = head_html(
        f"{CATEGORY} | {SITE_NAME}",
        description,
        2,
        canonical,
        "website",
        "/assets/generated/academy-og.jpg",
        ld,
    )
    directory = region_blocks_html(rows, SUBJECT_LABEL)
    body = f"""{nav_html(2, PARENT)}
  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../index.html">홈</a><span>/</span><a href="../index.html">{PARENT}</a><span>/</span><span>{CATEGORY}</span></p>
      <p class="eyebrow">{GRADE_EN} {SUBJECT_EN} DIRECTORY</p>
      <h1>{CATEGORY}</h1>
      <p class="lead">지역별 {esc(SUBJECT_LABEL)} {esc(FOCUS_LABEL)} 기준을 찾을 수 있도록 {len(rows)}개 동네 페이지를 시도·시군구별로 정리했습니다.</p>
    </section>
    <section class="section">
      <div class="section-head">
        <p class="eyebrow">REGIONAL DIRECTORY</p>
        <h2>동네별 {esc(SUBJECT_LABEL)}학원 바로가기</h2>
        <p class="lead">동네명이나 시군구를 검색하거나, 시도 필터를 선택해 원하는 지역을 찾을 수 있습니다.</p>
      </div>
      {directory}
    </section>
  </main>
{footer_html(2)}
{directory_filter_script()}"""
    out = SITE / PARENT / CATEGORY / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_shell(head, body), encoding="utf-8")


def main() -> None:
    rows = read_csv(COMMON / "센터정보 정리.csv")
    manuscripts = load_manuscripts()
    locals_in_csv = {row["근처 수업가능 동네"].strip() for row in rows}
    if len(rows) != 371 or len(manuscripts) != 371:
        raise ValueError(f"예상 개수 불일치: csv={len(rows)}, manuscripts={len(manuscripts)}")
    if locals_in_csv != manuscripts.keys():
        missing = sorted(locals_in_csv - manuscripts.keys())
        extra = sorted(manuscripts.keys() - locals_in_csv)
        raise ValueError(f"지역 대응 불일치: missing={missing}, extra={extra}")

    repeated_signatures = repeated_body_signatures(manuscripts)
    parent_hub(rows)
    category_hub(rows)
    for index, row in enumerate(rows):
        local = row["근처 수업가능 동네"].strip()
        out = SITE / PARENT / CATEGORY / slug_ko(local) / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            detail_page(
                row,
                index,
                manuscripts[local],
                rows,
                repeated_signatures,
            ),
            encoding="utf-8",
        )
    print(
        f"generated parent={PARENT} category={CATEGORY} "
        f"local_pages={len(rows)} contextualized_patterns={len(repeated_signatures)}"
    )


if __name__ == "__main__":
    main()
