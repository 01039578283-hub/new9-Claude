from __future__ import annotations

import random
import re
import struct
from pathlib import Path

import generate_middle_math_pages as shared

SITE = shared.SITE
COMMON = shared.COMMON
SITE_NAME = shared.SITE_NAME
PHONE_DISPLAY = shared.PHONE_DISPLAY
PHONE_LINK = shared.PHONE_LINK
PUBLISH_DATE = shared.PUBLISH_DATE
MODIFIED_DATE = getattr(shared, "MODIFIED_DATE", PUBLISH_DATE)
CONSULT_FORM_URL = shared.CONSULT_FORM_URL
CATEGORY = "와와학습코칭센터"

ALL_CATEGORIES = shared.ALL_CATEGORIES

esc = shared.esc
slug_ko = shared.slug_ko
split_items = shared.split_items
seed_for = shared.seed_for
school_type = shared.school_type
nav_html = shared.nav_html
footer_html = shared.footer_html
head_html = shared.head_html
page_shell = shared.page_shell
find_map = shared.find_map
pick = shared.pick
fmt_pair = shared.fmt_pair
school_names = shared.school_names
# ---------------------------------------------------------------------------
# Content banks for the all-subject 와와학습코칭센터 category. The learning
# cases below are explicitly hypothetical consultation prompts, not testimonials
# or claims about a student's result.
# ---------------------------------------------------------------------------

FAQ_OPENER_BANK: list[tuple[str, str]] = [
    ("{title}는 어떤 학생들이 많이 찾나요?",
     "영어, 수학, 국어 중 한 과목만 필요하신 경우부터 세 과목을 함께 관리받고 싶으신 경우까지 다양하게 상담받고 계십니다."),
    ("{title}에 처음 방문하면 어떤 순서로 진행되나요?",
     "먼저 학생의 현재 학년과 고민을 편하게 들은 뒤, 필요하면 간단한 진단으로 시작 지점을 확인합니다."),
    ("{title}는 몇 명이 함께 수업받나요?",
     "학생 개개인에게 충분한 설명과 피드백이 갈 수 있는 인원으로 반을 운영합니다."),
    ("{title}에 형제자매가 같이 다닐 수 있나요?",
     "네, 각자 학년과 과목 상황에 맞춰 따로 진단하고 관리해드립니다."),
    ("{title} 상담은 예약이 꼭 필요한가요?",
     "네, 상담 시간을 여유 있게 확보하기 위해 미리 연락 주시면 좋습니다."),
    ("{title}를 다른 학원과 비교하고 있는데 무엇이 다른가요?",
     "과목을 따로 보기보다 학생 한 명의 전체 학습 흐름을 기준으로 관리한다는 점이 다릅니다."),
]

FAQ_BANK: list[tuple[str, str]] = [
    ("{title}는 초등학생도 다닐 수 있나요?",
     "네, 초등학생은 기초 학습 습관과 독해력을 중심으로, 중고등학생은 내신과 시험 대비를 중심으로 각각 관리합니다."),
    ("학년이 올라갈 때 미리 준비할 게 있을까요?",
     "다음 단계에서 필요한 기초를 미리 점검하고, 급하게 선행하기보다 지금 과정을 얼마나 소화했는지부터 확인합니다."),
    ("국어도 함께 봐주시나요?",
     "네, 독해 태도와 문제 접근 방식을 중심으로 국어도 함께 관리할 수 있습니다. 필요한 과목만 선택하셔도 괜찮습니다."),
    ("소수정예로 운영되나요?",
     "학생별 질문과 피드백이 충분히 오갈 수 있는 인원으로 제한해서 운영합니다."),
    ("학생마다 다른 교재로 공부하나요?",
     "공통 개념은 함께 배우되, 학생 수준에 따라 보충 자료나 심화 자료를 다르게 제공합니다."),
    ("숙제는 어느 정도 나오나요?",
     "학생의 학습 속도와 학교 일정을 고려해서 무리하지 않는 선에서 과제량을 조절합니다."),
    ("결석하면 보강이 가능한가요?",
     "사전에 말씀해 주시면 진도에 맞춰 보강 방법을 안내해드립니다."),
    ("학원이 처음인 아이도 잘 적응할 수 있을까요?",
     "수업 방식과 규칙을 천천히 안내하고, 처음 적응하는 기간에는 특히 더 세심하게 살펴봅니다."),
    ("학습 상담은 비용이 있나요?",
     "기본적인 입학 상담은 무료로 진행합니다. 별도 진단 프로그램은 상담 시 안내해드립니다."),
    ("성적표를 꼭 가져가야 하나요?",
     "꼭 필요하지는 않지만, 최근 성적표나 시험지가 있으면 상담이 더 구체적으로 진행됩니다."),
    ("레벨테스트는 어떻게 진행되나요?",
     "현재 학년의 핵심 개념과 이전 학년 필수 내용을 중심으로 간단히 확인합니다."),
    ("자기주도학습이 어려운 아이도 괜찮을까요?",
     "처음에는 구체적인 학습량과 방법을 제시하고, 익숙해지면 스스로 계획을 세우도록 단계적으로 지도합니다."),
    ("학부모님과는 어떻게 소통하나요?",
     "전화, 문자로 학습 상황을 정기적으로 안내하며, 궁금한 점은 언제든 편하게 문의하실 수 있습니다."),
    ("{local}에서 다니는 학교가 다른 학생들도 함께 배우나요?",
     "기본 개념은 함께 배우되, 학교별 시험 범위에 맞춘 자료는 따로 준비합니다."),
    ("여러 과목을 한 번에 등록하면 시간표가 겹치지 않을까요?",
     "과목 간 이동 부담이 적도록 시간표를 최대한 조정해드립니다."),
    ("선행학습도 가능한가요?",
     "현재 학년 개념이 충분히 다져진 경우에 한해 단계적으로 진행합니다. 무리한 선행은 권하지 않습니다."),
    ("{title}는 시험 기간에 특별히 더 챙겨주시나요?",
     "학교별 시험 범위에 맞춰 과목별 우선순위를 정하고 집중적으로 관리합니다."),
    ("여러 번 학원을 옮겼는데 진도가 다르면 어떻게 하나요?",
     "이전에 다닌 학원들의 진도와 자료를 확인한 뒤 지금 수준에 맞는 시작점을 다시 정리해드립니다."),
]

ANSWER_BANK: list[tuple[str, str]] = [
    ("여러 과목을 같이 보는 학원과 과목별 전문학원, 어떤 게 나을까요?",
     "여러 과목에서 비슷한 어려움(시간관리, 자기주도학습 부족)을 겪고 있다면 통합 관리가 도움이 되고, 한 과목만 크게 부족하다면 그 과목에 집중하는 것도 방법입니다."),
    ("초등학생인데 벌써 학원을 다녀야 할까요?",
     "성적보다 학습 습관과 독해력, 기초 연산을 다지는 시기로 보시면 좋습니다. 억지로 선행하기보다 기초를 편하게 다지는 것이 우선입니다."),
    ("중학교 입학을 앞두고 무엇을 준비해야 하나요?",
     "과목별 기초 개념을 점검하고, 스스로 시간을 계획하는 연습을 시작하기 좋은 시기입니다."),
    ("고등학교 진학 후 성적이 갑자기 떨어졌다면?",
     "중학교와 다른 학습량과 평가 방식 때문일 수 있습니다. 과목별로 무엇이 부족한지 먼저 나누어 확인합니다."),
    ("여러 과목 숙제가 겹쳐서 아이가 힘들어한다면?",
     "과목별 학습량과 우선순위를 조정해 부담을 나누는 것이 먼저입니다. 무조건 줄이기보다 순서를 정리하는 방식이 효과적입니다."),
    ("학원을 여러 번 옮겨서 걱정된다면?",
     "이전 학원들의 진도와 자료를 확인하고, 지금까지 쌓인 학습 공백을 먼저 점검합니다."),
    ("아이가 공부에 흥미를 잃은 것 같다면?",
     "과목마다 원인이 다를 수 있습니다. 어떤 과목에서 자신감을 잃었는지부터 확인하는 것이 먼저입니다."),
    ("학원을 고를 때 기준이 궁금하다면?",
     "설명이 화려한 곳보다, 아이의 현재 상태를 얼마나 구체적으로 진단해주는 곳인지를 먼저 보시는 것이 좋습니다."),
    ("형제자매를 같은 학원에 보내도 될까요?",
     "학년과 성향이 다르면 관리 방식도 다르게 적용되니, 각자에게 맞는 방향을 따로 확인하시면 됩니다."),
    ("학습관리와 성적 향상 중 무엇을 먼저 봐야 할까요?",
     "성적은 결과이고 학습관리는 과정입니다. 과정이 자리 잡으면 성적은 자연스럽게 따라오는 경우가 많습니다."),
]

CHECKLIST_BANK: list[tuple[str, str]] = [
    ("현재 다니는 학교", "학교별 시험 범위와 진도를 확인해 상담 방향을 잡습니다."),
    ("과목별 최근 성적", "과목마다 강점과 약점이 다르기 때문에 따로 확인합니다."),
    ("공부 습관", "숙제, 복습, 자기주도학습 정도를 살펴봅니다."),
    ("희망 과목", "영어, 수학, 국어 중 지금 필요한 과목을 알려주세요."),
    ("학원 이력", "이전에 다닌 학원이 있다면 진도와 방식을 확인합니다."),
    ("목표 시기", "내신 대비, 선행, 습관 형성 중 지금 우선순위를 정합니다."),
    ("형제자매 여부", "함께 상담받을 형제자매가 있다면 각자 학년을 알려주세요."),
    ("선호하는 상담 방식", "전화, 방문 상담 중 편하신 방식을 말씀해주세요."),
]

CASE_BANK: list[tuple[str, str]] = [
    ("여러 과목 과제가 같은 날 몰리는 경우",
     "상담 준비 예시로, 과목별 과제량과 하루에 사용할 수 있는 시간을 적어 우선순위를 확인할 수 있습니다."),
    ("학년 전환을 앞두고 시작점을 정하기 어려운 경우",
     "상담 준비 예시로, 다음 학년에서 필요한 내용과 현재 이해한 내용을 나누어 질문 목록을 만들 수 있습니다."),
    ("최근 시험지에서 공통 원인을 찾고 싶은 경우",
     "상담 준비 예시로, 틀린 문제를 개념·계산·독해·시간 배분처럼 원인별로 구분해 가져갈 수 있습니다."),
    ("학교별 시험 범위와 일정 확인이 필요한 경우",
     "상담 준비 예시로, 학교명과 학년, 시험 예정일, 과목별 범위를 함께 전달할 수 있습니다."),
    ("계획의 실행 여부를 점검할 방법이 필요한 경우",
     "상담 준비 예시로, 계획한 분량과 실제로 마친 분량을 일주일 단위로 비교해 볼 수 있습니다."),
    ("과목별 학습 시간이 한쪽으로 치우친 경우",
     "상담 준비 예시로, 일주일 동안 과목마다 사용한 시간을 기록해 조정이 필요한 지점을 질문할 수 있습니다."),
    ("학원 이동 뒤 시작점을 다시 확인해야 하는 경우",
     "상담 준비 예시로, 이전 교재와 최근 학습 범위, 아직 어려운 단원을 함께 정리해 가져갈 수 있습니다."),
    ("형제자매가 서로 다른 학년으로 상담하는 경우",
     "상담 준비 예시로, 학생별 학년·희망 과목·가능 시간을 각각 적어 수업 가능 여부를 문의할 수 있습니다."),
    ("특정 과목의 공부 순서를 정하기 어려운 경우",
     "상담 준비 예시로, 현재 교재와 학교 진도, 복습이 필요한 단원을 구분해 질문할 수 있습니다."),
    ("상담 전에 준비할 자료가 궁금한 경우",
     "상담 준비 예시로, 최근 시험지·사용 중인 교재·학교 일정 가운데 준비 가능한 자료를 확인할 수 있습니다."),
]

COMPARE_ROWS: list[dict[str, tuple[str, str]]] = [
    {"label": "과목 관리", "A": ("과목마다 다른 학원에 따로 다녀야 함", "한 곳에서 과목별 진행 상황을 함께 확인"),
     "B": ("과목별로 상담을 각각 받아야 함", "한 번의 상담으로 전체 과목 확인 가능")},
    {"label": "학년 전환", "A": ("전환기 준비를 따로 챙겨야 함", "초·중·고 전환 시기마다 필요한 부분을 미리 안내"),
     "B": ("각 학원에서 따로 판단", "다음 단계 기준으로 지금 상태를 미리 점검")},
    {"label": "형제자매 관리", "A": ("각자 다른 곳에 등록해야 함", "형제자매도 한 곳에서 각자에 맞게 관리"),
     "B": ("정보 공유가 어려움", "가족 단위로 학습 상황을 함께 파악")},
    {"label": "학부모 소통", "A": ("성적 결과만 전달", "과목별 진행 상황과 다음 계획까지 안내"),
     "B": ("정기 안내만 제공", "필요할 때마다 편하게 상담 가능")},
]

SUMMARY_INTROS: list[str] = [
    "{local} 학생과 학부모님께 필요한 것은 과목마다 다른 곳을 오가는 것이 아니라, 한 곳에서 전체 학습 흐름을 확인하는 일입니다.",
    "{local}에서 학원을 고르실 때는 지금 어떤 과목이, 어떤 이유로 어려운지부터 정리하고 시작하시는 것이 좋습니다.",
    "{local} 학생마다 강한 과목과 약한 과목이 다르기 때문에, 같은 학년이라도 먼저 봐야 할 과목의 순서는 달라질 수 있습니다.",
]

MANUSCRIPT_INTRO: list[str] = [
    "많은 경우 영어, 수학, 국어를 각각 다른 학원에 맡기다 보면 정작 아이의 전체적인 학습 상태를 파악하기가 어려워집니다. 과목을 나누어 보되, 관리의 기준은 하나로 모으는 것이 중요합니다.",
    "초등에서 중등, 중등에서 고등으로 넘어가는 시기마다 학습량과 평가 방식이 크게 달라집니다. 지금 학년만 보지 않고 다음 단계를 함께 준비하는 것이 필요합니다.",
    "학생마다 과목별로 막히는 지점이 다릅니다. 어떤 학생은 수학 개념에서, 어떤 학생은 영어 문장 구조에서, 또 어떤 학생은 국어 지문 해석에서 어려움을 겪습니다.",
    "형제자매를 같은 학원에 보내더라도 학년과 성향이 다르면 필요한 관리도 달라집니다. 한 곳에서 관리하더라도 각자에게 맞는 방향을 따로 확인하는 것이 좋습니다.",
    "숙제와 복습이 여러 과목에 걸쳐 쌓이면 아이가 정작 어디에 집중해야 할지 놓치기 쉽습니다. 과목별 우선순위를 정리해주는 과정이 필요한 이유입니다.",
    "성적이 좋은 과목도 계속 관리가 필요합니다. 지금 잘하고 있는 과목의 흐름을 유지하면서 부족한 과목을 함께 끌어올리는 균형이 중요합니다.",
]

MANUSCRIPT_OUTRO: list[str] = [
    "학원을 고르실 때는 화려한 커리큘럼보다, 지금 우리 아이의 상태를 얼마나 구체적으로 봐주는지를 기준으로 삼으시길 권합니다.",
    "성적 향상은 결과일 뿐입니다. 그 결과를 만드는 과정이 아이에게 맞는지를 먼저 확인해보시길 바랍니다.",
    "상담은 등록을 결정하는 자리가 아니라, 지금 아이에게 어떤 관리가 필요한지 함께 확인해보는 자리로 생각해주시면 좋겠습니다.",
    "여러 과목을 한 번에 완벽하게 관리하기는 어렵습니다. 우선순위를 정하고 하나씩 자리를 잡아가는 과정이라는 점을 이해해주시면 도움이 됩니다.",
    "무엇보다 아이가 여러 과목 사이에서 지치지 않는지를 살펴보는 것이 꾸준한 학습으로 이어지는 데 중요합니다.",
    "지금 당장의 점수보다, 과목마다 필요한 습관이 하나씩 자리 잡고 있는지를 함께 지켜봐 주시길 바랍니다.",
]


def choose_rep_images(rows: list[dict[str, str]]) -> list[str]:
    """Return the existing deterministic representative assets without writing them."""
    images = [
        p for p in (COMMON / "대표이미지").iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    ]
    images.sort(key=lambda p: p.name)
    rng = random.Random(8283)
    rng.shuffle(images)
    result = [
        f"assets/representative/rep-{i + 1:03d}{images[i % len(images)].suffix.lower()}"
        for i in range(len(rows))
    ]
    missing = [rel for rel in result if not (SITE / rel).exists()]
    if missing:
        raise FileNotFoundError(f"missing representative image: {missing[0]}")
    return result


def page_head(*args: object) -> str:
    """Use the shared non-blocking system-font head."""
    return head_html(*args)


def page_nav(depth: int) -> str:
    """Expose the visual active state to assistive technology."""
    markup = nav_html(depth)
    if 'class="active" aria-current=' in markup:
        return markup
    return markup.replace(
        '<a class="active"',
        '<a class="active" aria-current="page"',
        1,
    )


def image_dimensions(relative_path: str) -> tuple[int, int]:
    """Read PNG, JPEG, or WebP dimensions without adding an image dependency."""
    path = SITE / relative_path
    data = path.read_bytes()

    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])

    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        chunk = data[12:16]
        if chunk == b"VP8X" and len(data) >= 30:
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
            return width, height
        if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
            bits = int.from_bytes(data[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if chunk == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
            width = int.from_bytes(data[26:28], "little") & 0x3FFF
            height = int.from_bytes(data[28:30], "little") & 0x3FFF
            return width, height

    if data.startswith(b"\xff\xd8"):
        offset = 2
        sof_markers = {
            0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
        }
        while offset + 9 < len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            while offset < len(data) and data[offset] == 0xFF:
                offset += 1
            if offset >= len(data):
                break
            marker = data[offset]
            offset += 1
            if marker in {0x01, *range(0xD0, 0xDA)}:
                continue
            if offset + 2 > len(data):
                break
            segment_length = int.from_bytes(data[offset:offset + 2], "big")
            if marker in sof_markers and offset + 7 <= len(data):
                height = int.from_bytes(data[offset + 3:offset + 5], "big")
                width = int.from_bytes(data[offset + 5:offset + 7], "big")
                return width, height
            if segment_length < 2:
                break
            offset += segment_length

    raise ValueError(f"unsupported or invalid image: {path}")


def provider_id(center: str, address: str) -> str:
    """Give repeated service-area pages one identity for the same real center."""
    if hasattr(shared, "center_entity_id"):
        return shared.center_entity_id(center, address)
    identity = f"{center.strip()}|{address.strip()}"
    return f"/#center-{seed_for(identity):08x}"


def local_page(row: dict[str, str], idx: int, rep_image: str, all_rows: list[dict[str, str]]) -> str:
    local = row["근처 수업가능 동네"].strip()
    slug = slug_ko(local)
    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    center = row.get("센터명", "").strip() or f"{local} 학습관리"
    address = row.get("센터 주소", "").strip()
    title = f"{local} {CATEGORY}"
    description = f"{region} {district} {local} 학생을 위한 {CATEGORY} 안내입니다. 영어·수학·국어 학습 진단, 통합 플래너, 오답 재학습 기준을 상담 전에 확인할 수 있습니다."
    canonical = f"/전국학원/{CATEGORY}/{slug}/"
    provider_node_id = provider_id(center, address)
    webpage_id = f"{canonical}#webpage"
    article_id = f"{canonical}#article"
    service_id = f"{canonical}#service"
    breadcrumb_id = f"{canonical}#breadcrumb"
    faq_id = f"{canonical}#faq"
    rep_root = "/" + rep_image.replace("\\", "/")
    center_img = "assets/centers/common/seoul6839.webp" if region == "서울" else "assets/centers/common/local6839.webp"
    map_img = find_map(row)
    center_width, center_height = image_dimensions(center_img)
    map_width, map_height = image_dimensions(map_img)

    middle_schools = split_items(row.get("타깃학교\n(중)", ""))
    elementary_schools = split_items(row.get("타깃학교\n(초)", ""))
    high_schools = split_items(row.get("타깃학교\n(고)", ""))
    schools = school_names(row)

    fee_link = row.get("센터 교습비", "").strip()
    reg_no = row.get("교육지원청 등록번호", "").strip()
    education_name = row.get("교육지원청명칭", "").strip()

    opener = fmt_pair(pick(FAQ_OPENER_BANK, 1, local, "wawa-faq-opener")[0],
                       local=local, district=district, title=title, region=region)
    faqs = [opener] + [fmt_pair(p, local=local, district=district, title=title, region=region)
                        for p in pick(FAQ_BANK, 5, local, "wawa-faq")]
    answers = [fmt_pair(p, local=local, district=district, title=title, region=region)
               for p in pick(ANSWER_BANK, 4, local, "wawa-answer")]
    checklist = [fmt_pair(p, local=local, district=district, title=title, region=region)
                 for p in pick(CHECKLIST_BANK, 4, local, "wawa-checklist")]
    learning_cases = pick(CASE_BANK, 6, local, "wawa-learning-cases")
    summary_intro = pick(SUMMARY_INTROS, 1, local, "wawa-summary")[0].format(local=local)
    manu_intro = pick(MANUSCRIPT_INTRO, 1, local, "wawa-manu-intro")[0]
    manu_outro = pick(MANUSCRIPT_OUTRO, 1, local, "wawa-manu-outro")[0]
    location_ref = address if address else "상담 시 안내되는 위치"
    variant = "A" if seed_for(local, "wawa-compare") % 2 == 0 else "B"

    related_source = [r for r in all_rows if r.get("시or구") == district and r.get("근처 수업가능 동네") != local]
    if len(related_source) < 6:
        related_source += [r for r in all_rows if r.get("지역") == region and r.get("근처 수업가능 동네") != local]
    related: list[tuple[str, str, str]] = []
    for r in related_source:
        name = r["근처 수업가능 동네"].strip()
        if name and name not in [x[0] for x in related]:
            related.append((name, f"/전국학원/{CATEGORY}/{slug_ko(name)}/", r.get("시or구", "")))
        if len(related) >= 6:
            break

    cross_related = [
        (
            f"{local} {name}",
            f"/전국학원/{name}/{slug}/",
            "같은 지역 다른 카테고리 바로가기",
            "cross-link",
        )
        for name, _ in ALL_CATEGORIES
        if name != CATEGORY and (SITE / "전국학원" / name / slug).exists()
    ]
    related_items = (
        cross_related
        + [
            (f"{CATEGORY} 전체", f"/전국학원/{CATEGORY}/", "카테고리 전체 보기", ""),
            ("전국학원", "/전국학원/", "전체 카테고리 보기", ""),
        ]
        + [
            (
                f"{name} {CATEGORY}",
                url,
                f"{area} 지역 페이지",
                "",
            )
            for name, url, area in related
        ]
    )

    provider_node: dict[str, object] = {
        "@type": ["EducationalOrganization", "LocalBusiness"],
        "@id": provider_node_id,
        "name": center,
    }
    if address:
        provider_node["address"] = {
            "@type": "PostalAddress",
            "streetAddress": address,
            "addressRegion": region,
            "addressLocality": district,
            "addressCountry": "KR",
        }
    provider_properties = []
    if education_name:
        provider_properties.append({
            "@type": "PropertyValue",
            "name": "교육지원청 등록 명칭",
            "value": education_name,
        })
    if reg_no:
        provider_properties.append({
            "@type": "PropertyValue",
            "name": "교육지원청 등록번호",
            "value": reg_no,
        })
    if provider_properties:
        provider_node["additionalProperty"] = provider_properties

    about = [
        {"@type": "Thing", "name": title},
        {"@type": "Place", "name": local},
        {"@type": "Thing", "name": "영어 학습관리"},
        {"@type": "Thing", "name": "수학 학습관리"},
        {"@type": "Thing", "name": "국어 학습관리"},
        {"@type": "Thing", "name": "통합 플래너 관리"},
        {"@type": "Thing", "name": "오답 재학습"},
    ]
    mentions = [
        {"@type": "Place", "name": region},
        {"@type": "Place", "name": district},
        {"@id": provider_node_id},
    ] + [{"@type": school_type(s), "name": s} for s in schools]
    has_part = [
        "핵심 요약", "학원 선택 가이드", "답변형 안내", "지역·학년·추천학생 기준",
        "일반 학원과의 차이", "센터 기준 정보", "교습비 확인", "상담 전 체크리스트",
        "자주 묻는 질문", "상담에서 자주 확인하는 학습 사례", "근처 학원페이지",
    ]

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": webpage_id,
                "url": canonical,
                "name": title,
                "description": description,
                "inLanguage": "ko-KR",
                "primaryImageOfPage": {"@id": f"{canonical}#primaryimage"},
                "breadcrumb": {"@id": breadcrumb_id},
                "mainEntity": {"@id": service_id},
                "about": about,
                "mentions": mentions,
                "hasPart": [{"@type": "WebPageElement", "name": x} for x in has_part],
            },
            {"@type": "ImageObject", "@id": f"{canonical}#primaryimage", "url": rep_root, "caption": f"{title} 대표 이미지"},
            {
                "@type": "BreadcrumbList",
                "@id": breadcrumb_id,
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "홈", "item": "/"},
                    {"@type": "ListItem", "position": 2, "name": "전국학원", "item": "/전국학원/"},
                    {"@type": "ListItem", "position": 3, "name": CATEGORY, "item": f"/전국학원/{CATEGORY}/"},
                    {"@type": "ListItem", "position": 4, "name": local, "item": canonical},
                ],
            },
            provider_node,
            {
                "@type": "Article",
                "@id": article_id,
                "headline": title,
                "description": description,
                "image": [rep_root, "/" + center_img, "/" + map_img],
                "inLanguage": "ko-KR",
                "datePublished": PUBLISH_DATE,
                "dateModified": MODIFIED_DATE,
                "author": {"@type": "Organization", "name": SITE_NAME, "url": "/"},
                "publisher": {"@type": "Organization", "name": SITE_NAME, "url": "/"},
                "mainEntityOfPage": {"@id": webpage_id},
                "about": about,
                "mentions": mentions,
                "articleSection": has_part,
            },
            {
                "@type": "Service",
                "@id": service_id,
                "name": f"{title} 학습관리",
                "serviceType": "TutoringService",
                "description": description,
                "provider": {"@id": provider_node_id},
                "areaServed": {"@type": "Place", "name": local},
                "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
                "about": about,
                "mentions": mentions,
            },
            {
                "@type": "FAQPage",
                "@id": faq_id,
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faqs
                ],
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#target-schools",
                "name": f"{title} 수업 가능 여부를 확인할 학교",
                "numberOfItems": len(schools) if schools else 1,
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": s}
                    for i, s in enumerate(schools or ["상담 시 학교 확인"])
                ],
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#related",
                "name": f"{local} {CATEGORY} 관련 내부링크",
                "numberOfItems": len(related_items),
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": name, "url": url}
                    for i, (name, url, _, _) in enumerate(related_items)
                ],
            },
        ],
    }

    center_rel = "../../../" + center_img
    center_mobile_rel = center_rel.replace(".webp", "-mobile.webp")
    map_rel = "../../../" + map_img
    head = page_head(f"{title} | {SITE_NAME}", description, 3, canonical, "article", rep_root, ld)

    badge_row = f'<div class="badge-row"><span>{esc(region)}</span><span>{esc(district)}</span><span>전과목</span><span>영어·수학·국어 통합관리</span></div>'

    media_section = f"""    <section class="section">
      <div class="media-row">
        <figure class="frame"><picture><source media="(max-width: 640px)" srcset="{esc(center_mobile_rel)}"><img src="{esc(center_rel)}" alt="{esc(title + ' 센터 학습 안내')}" width="{center_width}" height="{center_height}" decoding="async" loading="eager" fetchpriority="high"></picture></figure>
        <figure class="frame"><img src="{esc(map_rel)}" alt="{esc(title + ' 위치 지도')}" width="{map_width}" height="{map_height}" decoding="async" loading="lazy" fetchpriority="low"></figure>
      </div>
      <p class="lead">{esc(center)} 기준으로 {esc(local)} 학생의 상담 범위를 확인합니다. 실제 방문·상담 전에는 주소와 이동 동선을 함께 확인해 주세요.</p>
    </section>"""

    summary_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">핵심 요약</p>
        <h2>{esc(local)} {esc(CATEGORY)} 선택 전 확인할 기준</h2>
        <p class="lead">{esc(summary_intro)}</p>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">01</span><h3>과목별 진단</h3><p>영어, 수학, 국어 중 지금 어느 과목의 어떤 부분이 부족한지 먼저 나누어 확인합니다.</p></article>
        <article class="info-card"><span class="tag">02</span><h3>통합 플래너</h3><p>과목별 학습량을 한 플래너에 담아 서로 밀리지 않도록 조율하고 실행 여부를 확인합니다.</p></article>
        <article class="info-card"><span class="tag">03</span><h3>오답 재학습</h3><p>과목마다 다른 오답 원인을 분류하고, 비슷한 유형을 다시 풀며 반복 실수를 줄입니다.</p></article>
      </div>
    </section>"""

    manuscript_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">학원 선택 가이드</p>
        <h2>{esc(local)} {esc(CATEGORY)}, 무엇을 기준으로 볼까요</h2>
      </div>
      <p class="lead">{esc(manu_intro)}</p>
      <p class="lead">{esc(center)}의 주소 정보는 {esc(location_ref)}입니다. 상담 전에 수업 가능 여부를 확인할 학교 목록: {esc(', '.join(schools) if schools else local + ' 인근 학교')}. 학교명과 학년을 함께 전달해 현재 가능한 과목과 시간을 확인해 주세요.</p>
      <p class="lead">{esc(manu_outro)}</p>
    </section>"""

    answer_html = "\n".join(
        f'<div class="answer-item"><p class="q">{esc(q)}</p><p class="a">{esc(a)}</p></div>'
        for q, a in answers
    )
    answer_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">답변형 안내 · AEO ANSWER</p>
        <h2>{esc(title)}는 어떤 학생에게 필요할까요?</h2>
      </div>
      <div class="answer-list">
        {answer_html}
      </div>
    </section>"""

    school_chip_html = "".join(f"<span>{esc(s)}</span>" for s in schools) if schools else "<span>상담 시 학교 확인</span>"
    linked_bits = []
    if elementary_schools:
        linked_bits.append(f"초등학교: {', '.join(elementary_schools)}")
    if middle_schools:
        linked_bits.append(f"중학교: {', '.join(middle_schools)}")
    if high_schools:
        linked_bits.append(f"고등학교: {', '.join(high_schools)}")
    linked_schools = ""
    if linked_bits:
        linked_schools = f'<article class="info-card"><span class="tag">학교</span><h3>학교급별 확인 대상</h3><p>{esc(" · ".join(linked_bits))}</p></article>'
    fit_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">LOCAL &amp; STUDENT FIT</p>
        <h2>지역·학년·추천학생 기준</h2>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">지역</span><h3>{esc(region)} {esc(district)} {esc(local)}</h3><p>주소와 이동 동선을 확인하고, 학교 일정과 희망 과목을 상담 시 함께 전달해 주세요.</p></article>
        <article class="info-card"><span class="tag">학년</span><h3>과목별 가능 학년 확인</h3><p>등록 가능한 학년과 과정은 센터·과목·시간표에 따라 달라질 수 있으므로 상담 시 현재 정보를 확인해 주세요.</p></article>
        <article class="info-card"><span class="tag">상담</span><h3>준비할 학습 정보</h3><p>학생의 학년, 희망 과목, 최근 학습 범위, 가능한 요일을 준비하면 수업 가능 여부를 구체적으로 문의할 수 있습니다.</p></article>
        {linked_schools}
      </div>
      <p class="lead" style="margin-top:18px;">수업 가능 여부를 확인할 학교</p>
      <div class="chip-list" aria-label="수업 가능 여부를 확인할 학교">{school_chip_html}</div>
    </section>"""

    row = COMPARE_ROWS
    compare_rows_html = "\n".join(
        f'<div class="compare-row"><div class="other">{esc(r[variant][0])}</div><div class="label">{esc(r["label"])}</div><div class="ours">{esc(r[variant][1])}</div></div>'
        for r in row
    )
    compare_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">일반 학원과의 차이</p>
        <h2>{esc(local)} {esc(CATEGORY)}, 무엇이 다른가요</h2>
        <p class="lead">일반적인 학원 운영 방식과 {esc(SITE_NAME)}의 통합 학습관리 방식을 같은 기준으로 비교했습니다.</p>
      </div>
      <div class="compare-table">
        <div class="compare-head"><div>일반적인 학원</div><div>기준</div><div class="ours">{esc(SITE_NAME)}</div></div>
        {compare_rows_html}
      </div>
    </section>"""

    center_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">CENTER INFO</p>
        <h2>센터 기준 정보</h2>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">센터명</span><h3>{esc(center)}</h3><p>{esc(region)} {esc(district)} {esc(local)} 학생 상담 기준으로 안내합니다.</p></article>
        <article class="info-card"><span class="tag">주소</span><h3>위치 안내</h3><p>{esc(address) if address else "상담 시 위치 정보를 확인해 주세요."}</p></article>
        <article class="info-card"><span class="tag">등록</span><h3>{esc(education_name) if education_name else "교육지원청 등록 정보"}</h3><p>{esc(reg_no) if reg_no else "상담 시 교육지원청 등록 정보를 확인할 수 있습니다."}</p></article>
      </div>
    </section>"""

    if fee_link:
        fee_content = f"""        <p class="fee-caption">센터별 공식 공개자료 확인</p>
        <p class="lead">과정·학년·수업 횟수에 따른 교습비는 아래 센터별 공개자료에서 확인해 주세요. 등록 전에는 적용 과정과 기타 비용을 상담 시 다시 확인하는 것이 좋습니다.</p>
        <div class="hero-actions">
          <a class="btn btn-ghost" href="{esc(fee_link)}" target="_blank" rel="noopener noreferrer">공식 교습비 자료 확인</a>
        </div>
        <p class="fee-note">* 링크 문서의 게시 상태와 최신 기준은 열람 시점에 확인해 주세요.</p>"""
    else:
        fee_content = """        <p class="fee-caption">상담 또는 공개자료 확인</p>
        <p class="lead">현재 연결된 센터별 교습비 공개자료가 없습니다. 과정별 교습비와 기타 비용은 상담 또는 관할 교육청 공개자료에서 확인해 주세요.</p>
        <p class="fee-note">* 학년·과정·수업 횟수에 따라 확인할 항목이 달라질 수 있습니다.</p>"""
    fee_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">TUITION</p>
        <h2>{esc(local)} {esc(CATEGORY)} 교습비 확인</h2>
        <p class="lead">고정 금액 대신 센터별로 공개된 자료와 상담 시점의 안내를 기준으로 확인해 주세요.</p>
      </div>
      <div class="fee-table-wrap">
{fee_content}
      </div>
    </section>"""

    checklist_html = "".join(
        f'<article class="info-card"><span class="tag">{i + 1}</span><h3>{esc(q)}</h3><p>{esc(a)}</p></article>'
        for i, (q, a) in enumerate(checklist)
    )
    checklist_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">CHECKLIST</p>
        <h2>상담 전 체크리스트</h2>
      </div>
      <div class="card-grid">
        {checklist_html}
      </div>
    </section>"""

    faq_html = "\n".join(
        f'<details class="faq-item"{" open" if i == 0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>'
        for i, (q, a) in enumerate(faqs)
    )
    faq_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">FAQ</p>
        <h2>{esc(title)} 자주 묻는 질문</h2>
      </div>
      <div class="faq-list">
        {faq_html}
      </div>
    </section>"""

    case_html = "\n".join(
        f'<article class="info-card"><span class="tag">예시 {i + 1:02d}</span><h3>{esc(case_title)}</h3><p>{esc(case_body)}</p></article>'
        for i, (case_title, case_body) in enumerate(learning_cases)
    )
    case_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">LEARNING CASE EXAMPLES</p>
        <h2>상담에서 자주 확인하는 학습 사례</h2>
        <p class="lead">아래 내용은 실제 상담 기록이나 성과 사례가 아니라, 상담 전에 질문을 정리할 수 있도록 만든 가상의 상황 예시입니다.</p>
      </div>
      <div class="card-grid">
        {case_html}
      </div>
    </section>"""

    related_html = "\n".join(
        f'<a href="{esc(url)}"{f" class={chr(34)}{css_class}{chr(34)}" if css_class else ""}><strong>{esc(name)}</strong><small>{esc(detail)}</small></a>'
        for name, url, detail, css_class in related_items
    )
    link_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">근처 학원페이지</p>
        <h2>{esc(local)} 주변 {esc(CATEGORY)} 페이지</h2>
        <p class="lead">같은 지역의 다른 과목과, 가까운 지역 페이지로 이동할 수 있도록 정리했습니다.</p>
      </div>
      <div class="link-grid">
        {related_html}
      </div>
    </section>"""

    body = f"""{page_nav(3)}

  <main>
    <section class="page-hero">
      <nav class="breadcrumb" aria-label="현재 위치"><a href="../../../index.html">홈</a><span aria-hidden="true">/</span><a href="../../index.html">전국학원</a><span aria-hidden="true">/</span><a href="../index.html">{esc(CATEGORY)}</a><span aria-hidden="true">/</span><span aria-current="page">{esc(local)}</span></nav>
      <p class="eyebrow">ALL-SUBJECT LEARNING COACHING</p>
      <h1>{esc(title)}</h1>
      <p class="lead">{esc(description)}</p>
      {badge_row}
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">전화 상담하기</a>
        <a class="btn btn-ghost" href="../../../상담문의/index.html">상담문의</a>
      </div>
    </section>

{media_section}

{summary_section}

{manuscript_section}

{answer_section}

{fit_section}

{compare_section}

{center_section}

{fee_section}

{checklist_section}

{faq_section}

{case_section}

{link_section}
  </main>

{footer_html(3)}
"""
    return page_shell(head, body)


def category_directory(rows: list[dict[str, str]]) -> str:
    regions: dict[str, dict[str, list[dict[str, str]]]] = {}
    for row in rows:
        region = row.get("지역", "").strip() or "기타"
        district = row.get("시or구", "").strip() or "기타"
        regions.setdefault(region, {}).setdefault(district, []).append(row)

    options = "".join(
        f'<option value="{esc(region)}">{esc(region)}</option>'
        for region in regions
    )
    jump_links = "".join(
        f'<a href="#region-{slug_ko(region)}">{esc(region)}</a>'
        for region in regions
    )

    region_html = []
    for region, districts in regions.items():
        district_html = []
        for district, items in districts.items():
            links = "\n".join(
                (
                    f'<a href="{slug_ko(item["근처 수업가능 동네"])}/" '
                    f'data-directory-item data-region="{esc(region)}" '
                    f'data-search="{esc(" ".join([region, district, item["근처 수업가능 동네"], item.get("센터명", "")]))}" '
                    f'aria-label="{esc(item["근처 수업가능 동네"] + " " + CATEGORY + " 안내 보기")}">'
                    f'{esc(item["근처 수업가능 동네"])}</a>'
                )
                for item in items
            )
            district_html.append(
                f'<div class="district-block" data-district-block>'
                f'<p class="district-title">{esc(district)}<small data-district-count>{len(items)}곳</small></p>'
                f'<div class="local-button-grid">{links}</div></div>'
            )
        region_html.append(
            f'<div class="region-block" id="region-{slug_ko(region)}" data-region-block>'
            f'<div class="region-title"><h3>{esc(region)}</h3>'
            f'<span data-region-count>{len(districts)}개 시군구 · {sum(len(v) for v in districts.values())}개 지역</span></div>'
            f'<div class="district-grid">{"".join(district_html)}</div></div>'
        )

    return f"""      <div class="directory-controls" aria-label="지역 안내 검색">
        <label class="directory-field" for="directory-search">
          <span>지역 또는 동네 검색</span>
          <input id="directory-search" type="search" inputmode="search" autocomplete="off" placeholder="예: 서울, 강동구, 명일동" aria-controls="directory-list" enterkeyhint="search">
        </label>
        <label class="directory-field" for="directory-region">
          <span>시·도 필터</span>
          <select id="directory-region" aria-controls="directory-list">
            <option value="">전체 시·도</option>
            {options}
          </select>
        </label>
        <button class="btn btn-ghost directory-reset" id="directory-reset" type="button">검색 초기화</button>
      </div>
      <p class="directory-status" id="directory-status" role="status" aria-live="polite" aria-atomic="true">{len(rows)}개 지역을 안내합니다.</p>
      <div class="region-jump" aria-label="시·도 바로가기">{jump_links}</div>
      <div id="directory-list">
        {"".join(region_html)}
      </div>
      <p class="directory-empty" id="directory-empty" hidden>조건에 맞는 지역이 없습니다. 검색어 또는 시·도 필터를 다시 확인해 주세요.</p>"""


CATEGORY_DIRECTORY_CSS = """
  .directory-controls {
    display: grid;
    grid-template-columns: minmax(0, 2fr) minmax(190px, 1fr) auto;
    gap: 12px;
    align-items: end;
    margin-bottom: 14px;
    padding: clamp(18px, 4vw, 26px);
    border: 1px solid var(--line);
    background: var(--card);
  }
  .directory-field {
    display: grid;
    gap: 8px;
    color: var(--ink-soft);
    font-size: 13px;
    font-weight: 800;
  }
  .directory-field input,
  .directory-field select {
    width: 100%;
    min-height: 48px;
    padding: 0 14px;
    border: 1px solid var(--line);
    border-radius: 0;
    color: var(--ink);
    background: var(--paper);
    font: inherit;
    font-size: 16px;
  }
  .directory-field input:focus-visible,
  .directory-field select:focus-visible,
  .directory-reset:focus-visible {
    outline: 3px solid var(--gold-line);
    outline-offset: 2px;
  }
  .directory-reset {
    min-height: 48px;
    white-space: nowrap;
  }
  .directory-status,
  .directory-empty {
    margin: 0 0 22px;
    color: var(--ink-soft);
    font-size: 14px;
    font-weight: 700;
  }
  .directory-empty {
    padding: 22px;
    border: 1px solid var(--line);
    background: var(--card);
  }
  [data-directory-item][hidden],
  [data-district-block][hidden],
  [data-region-block][hidden],
  .directory-empty[hidden] {
    display: none !important;
  }
  @media (max-width: 760px) {
    .directory-controls {
      grid-template-columns: 1fr;
    }
    .directory-reset {
      width: 100%;
    }
  }
"""


CATEGORY_DIRECTORY_SCRIPT = """
  <script>
  (() => {
    const search = document.getElementById("directory-search");
    const region = document.getElementById("directory-region");
    const reset = document.getElementById("directory-reset");
    const status = document.getElementById("directory-status");
    const empty = document.getElementById("directory-empty");
    const items = [...document.querySelectorAll("[data-directory-item]")];
    const districts = [...document.querySelectorAll("[data-district-block]")];
    const regions = [...document.querySelectorAll("[data-region-block]")];
    const normalize = (value) => (value || "").normalize("NFC").toLocaleLowerCase("ko-KR").replace(/\\s+/g, "");

    const update = () => {
      const query = normalize(search.value);
      const selectedRegion = region.value;
      let visibleCount = 0;

      items.forEach((item) => {
        const matchesQuery = !query || normalize(item.dataset.search).includes(query);
        const matchesRegion = !selectedRegion || item.dataset.region === selectedRegion;
        item.hidden = !(matchesQuery && matchesRegion);
        if (!item.hidden) visibleCount += 1;
      });

      districts.forEach((district) => {
        const visibleItems = district.querySelectorAll("[data-directory-item]:not([hidden])").length;
        district.hidden = visibleItems === 0;
        const count = district.querySelector("[data-district-count]");
        if (count) count.textContent = `${visibleItems}곳`;
      });

      regions.forEach((regionBlock) => {
        const visibleItems = regionBlock.querySelectorAll("[data-directory-item]:not([hidden])").length;
        const visibleDistricts = regionBlock.querySelectorAll("[data-district-block]:not([hidden])").length;
        regionBlock.hidden = visibleItems === 0;
        const count = regionBlock.querySelector("[data-region-count]");
        if (count) count.textContent = `${visibleDistricts}개 시군구 · ${visibleItems}개 지역`;
      });

      empty.hidden = visibleCount !== 0;
      status.textContent = visibleCount === items.length
        ? `${visibleCount}개 지역을 안내합니다.`
        : `${visibleCount}개 지역이 검색되었습니다.`;
    };

    search.addEventListener("input", update);
    region.addEventListener("change", update);
    reset.addEventListener("click", () => {
      search.value = "";
      region.value = "";
      update();
      search.focus();
    });
  })();
  </script>"""


def category_hub(rows: list[dict[str, str]]) -> None:
    rep = "/assets/generated/academy-og.jpg"
    directory = category_directory(rows)
    ld_cat = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": f"/전국학원/{CATEGORY}/#webpage", "url": f"/전국학원/{CATEGORY}/", "name": CATEGORY, "description": f"{CATEGORY} 지역별 안내입니다.", "inLanguage": "ko-KR", "breadcrumb": {"@id": f"/전국학원/{CATEGORY}/#breadcrumb"}, "mainEntity": {"@id": f"/전국학원/{CATEGORY}/#itemlist"}},
            {"@type": "BreadcrumbList", "@id": f"/전국학원/{CATEGORY}/#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": "/"}, {"@type": "ListItem", "position": 2, "name": "전국학원", "item": "/전국학원/"}, {"@type": "ListItem", "position": 3, "name": CATEGORY, "item": f"/전국학원/{CATEGORY}/"}]},
            {"@type": "ItemList", "@id": f"/전국학원/{CATEGORY}/#itemlist", "name": f"{CATEGORY} 지역 목록", "numberOfItems": len(rows), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": r["근처 수업가능 동네"], "url": f"/전국학원/{CATEGORY}/{slug_ko(r['근처 수업가능 동네'])}/"} for i, r in enumerate(rows)]},
        ],
    }
    head = page_head(f"{CATEGORY} | {SITE_NAME}", f"전국 {len(rows)}개 지역의 {CATEGORY} 센터 안내를 지역과 동네별로 확인할 수 있습니다.", 2, f"/전국학원/{CATEGORY}/", "website", rep, ld_cat)
    head = head.replace("</head>", f"  <style>{CATEGORY_DIRECTORY_CSS}</style>\n</head>")
    body = f"""{page_nav(2)}
  <main>
    <section class="page-hero">
      <nav class="breadcrumb" aria-label="현재 위치"><a href="../../index.html">홈</a><span aria-hidden="true">/</span><a href="../index.html">전국학원</a><span aria-hidden="true">/</span><span aria-current="page">{esc(CATEGORY)}</span></nav>
      <p class="eyebrow">ALL-SUBJECT DIRECTORY</p>
      <h1>{esc(CATEGORY)}</h1>
      <p class="lead">가까운 지역의 센터 정보와 상담 전에 확인할 학년·과목·학교·교습비 안내를 찾아보세요.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">전화 상담하기</a>
        <a class="btn btn-ghost" href="../../상담문의/index.html">상담문의</a>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">ABOUT US</p>
        <h2>{esc(SITE_NAME)}는 영어·수학·국어를 이렇게 관리해요</h2>
        <p class="lead">과목마다 다른 곳에 맡기기보다, 한 아이의 학습 흐름을 기준으로 영어·수학·국어를 함께 놓고 봐요. 상담에서 시작해 진단, 통합 플래너, 오답 재학습까지 이어갑니다.</p>
      </div>
      <div class="timeline">
        <article class="timeline-item">
          <div class="timeline-num">01</div>
          <div class="timeline-body"><h3>상담</h3><p>과목별 성적과 학습 습관을 한 번에 듣고, 지금 가장 필요한 과목의 우선순위를 함께 정합니다.</p></div>
        </article>
        <article class="timeline-item">
          <div class="timeline-num">02</div>
          <div class="timeline-body"><h3>진단</h3><p>영어, 수학, 국어 각각 어디에서 막히는지 나누어 확인하고 균형이 무너진 부분을 찾습니다.</p></div>
        </article>
        <article class="timeline-item">
          <div class="timeline-num">03</div>
          <div class="timeline-body"><h3>통합 플래너</h3><p>과목별 학습량을 한 플래너에 담아 서로 밀리지 않도록 조율하고 실행 결과를 확인합니다.</p></div>
        </article>
        <article class="timeline-item">
          <div class="timeline-num">04</div>
          <div class="timeline-body"><h3>오답 재학습</h3><p>과목마다 다른 오답 원인을 분류하고 비슷한 문제를 다시 풀며 반복 실수를 줄입니다.</p></div>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">지역 안내 찾기</p>
        <h2>지역명과 동네명으로 센터 찾기</h2>
        <p class="lead">검색창에 시·도, 시·군·구 또는 동네명을 입력하거나 시·도 필터를 선택해 주세요.</p>
      </div>
{directory}
    </section>
  </main>
{footer_html(2)}
{CATEGORY_DIRECTORY_SCRIPT}"""
    out = SITE / "전국학원" / CATEGORY / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_shell(head, body), encoding="utf-8")


def main() -> None:
    rows = shared.read_csv(COMMON / "센터정보 정리.csv")
    reps = choose_rep_images(rows)
    category_hub(rows)
    for idx, row in enumerate(rows):
        slug = slug_ko(row["근처 수업가능 동네"])
        out = SITE / "전국학원" / CATEGORY / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(local_page(row, idx, reps[idx], rows), encoding="utf-8")
    print(f"generated category={CATEGORY} local_pages={len(rows)} category_hubs=1")


if __name__ == "__main__":
    main()
