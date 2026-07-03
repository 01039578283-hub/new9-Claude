from __future__ import annotations

import random
from pathlib import Path

import generate_middle_math_pages as shared

SITE = shared.SITE
COMMON = shared.COMMON
SITE_NAME = shared.SITE_NAME
PHONE_DISPLAY = shared.PHONE_DISPLAY
PHONE_LINK = shared.PHONE_LINK
PUBLISH_DATE = shared.PUBLISH_DATE
CONSULT_FORM_URL = shared.CONSULT_FORM_URL
CATEGORY = "와와학습코칭센터"

ALL_CATEGORIES = shared.ALL_CATEGORIES
cross_category_links_html = shared.cross_category_links_html

esc = shared.esc
slug_ko = shared.slug_ko
split_items = shared.split_items
seed_for = shared.seed_for
json_script = shared.json_script
rel_prefix = shared.rel_prefix
school_type = shared.school_type
eul_reul = shared.eul_reul
nav_html = shared.nav_html
footer_html = shared.footer_html
head_html = shared.head_html
page_shell = shared.page_shell
find_map = shared.find_map
pick = shared.pick
fmt_pair = shared.fmt_pair
school_names = shared.school_names
FEE_TABLE_SEOUL = shared.FEE_TABLE_SEOUL
FEE_TABLE_OTHER = shared.FEE_TABLE_OTHER


# ---------------------------------------------------------------------------
# content banks (freshly written for 코칭아카데미 / 와와학습코칭센터 — this
# category covers ALL subjects (영어·수학·국어) at the general brand level,
# unlike 중등수학학원/중등영어학원 which are subject-specific. Informed by
# 상담방식.txt, FAQ.txt, 학부모 후기.txt, 경쟁사분석, and the
# "와와학습코칭센터 원고.xlsx" manuscript (themes reused, wording rewritten —
# not copied verbatim). Verified to have zero overlap with the math/english
# category banks.
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

REVIEW_BANK: list[str] = [
    "영어, 수학을 따로 보지 않고 한 번에 봐주셔서 상담이 훨씬 편했습니다.",
    "아이 학년이 올라갈 때마다 필요한 것을 미리 알려주셔서 도움이 되었습니다.",
    "국어까지 함께 봐주셔서 세 과목을 따로 다닐 필요가 없어졌습니다.",
    "형제 둘의 성향이 달랐는데 각자에 맞게 다르게 봐주셨습니다.",
    "처음 상담 때 아이 상태를 있는 그대로 말씀해 주셔서 신뢰가 갔습니다.",
    "학원을 여러 번 옮겼는데 이전 진도를 잘 확인하고 이어주셨습니다.",
    "숙제량을 아이에 맞게 조절해 주셔서 부담이 줄었습니다.",
    "자기주도학습을 어려워했는데 단계적으로 잘 이끌어주셨습니다.",
    "학교마다 시험 범위가 다른데 그 부분까지 챙겨주셨습니다.",
    "선생님들이 아이 성향을 잘 파악하고 계셔서 안심이 되었습니다.",
    "초등학생인 첫째도 재미있게 다니고 있습니다.",
    "중학교 입학 전에 미리 준비할 수 있어서 좋았습니다.",
    "고등학교에 올라가서도 이어서 관리받을 수 있어 든든합니다.",
    "과목별로 무엇이 부족한지 구체적으로 설명해주셨습니다.",
    "학부모 상담 때 과장 없이 솔직하게 말씀해주셔서 좋았습니다.",
    "레벨테스트도 부담스럽지 않게 진행해주셨습니다.",
    "여러 과목 시간표를 겹치지 않게 잘 짜주셨습니다.",
    "성적보다 공부 습관이 먼저 자리 잡은 것이 느껴집니다.",
    "결석했을 때 보강을 편하게 챙겨주셨습니다.",
    "아이가 학원 가는 것을 부담스러워하지 않습니다.",
    "소수 인원으로 봐주셔서 질문하기 편하다고 합니다.",
    "선행보다 지금 필요한 것부터 챙겨주셔서 믿음이 갔습니다.",
    "학원을 옮긴 뒤에도 적응이 빨랐습니다.",
    "여러 과목을 챙기다 지쳐 있었는데 한 번에 정리가 되었습니다.",
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
    # same seed/pool as the other categories so the SAME dong keeps the SAME
    # representative photo across all categories (consistent location branding)
    return shared.choose_rep_images(rows)


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
    org_id = f"{canonical}#organization"
    webpage_id = f"{canonical}#webpage"
    article_id = f"{canonical}#article"
    service_id = f"{canonical}#service"
    breadcrumb_id = f"{canonical}#breadcrumb"
    faq_id = f"{canonical}#faq"
    rep_root = "/" + rep_image.replace("\\", "/")
    center_img = "assets/centers/common/seoul6839.jpg" if region == "서울" else "assets/centers/common/local6839.jpg"
    map_img = find_map(row)

    middle_schools = split_items(row.get("타깃학교\n(중)", ""))
    elementary_schools = split_items(row.get("타깃학교\n(초)", ""))
    high_schools = split_items(row.get("타깃학교\n(고)", ""))
    schools = school_names(row)

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
    review_lines = pick(REVIEW_BANK, 6, local, "wawa-review")
    summary_intro = pick(SUMMARY_INTROS, 1, local, "wawa-summary")[0].format(local=local)
    manu_intro = pick(MANUSCRIPT_INTRO, 1, local, "wawa-manu-intro")[0]
    manu_outro = pick(MANUSCRIPT_OUTRO, 1, local, "wawa-manu-outro")[0]
    location_ref = address if address else "상담 시 안내되는 위치"
    variant = "A" if seed_for(local, "wawa-compare") % 2 == 0 else "B"

    rng = random.Random(seed_for(local, "wawa-review-rating"))
    reviews = []
    for i, text in enumerate(review_lines):
        rating = 4 if i == len(review_lines) - 1 and rng.random() < 0.4 else 5
        reviews.append({"body": text, "rating": rating})

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
        {"@type": "EducationalOrganization", "name": center},
    ] + [{"@type": school_type(s), "name": s} for s in schools]
    has_part = [
        "핵심 요약", "학원 선택 가이드", "답변형 안내", "지역·학년·추천학생",
        "일반 학원과의 차이", "센터 기준 정보", "학습료 안내", "상담 전 체크리스트", "FAQ", "학부모 후기", "근처 학원페이지",
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
            {
                "@type": ["EducationalOrganization", "LocalBusiness"],
                "@id": org_id,
                "name": title,
                "alternateName": [SITE_NAME, center, f"{local} 학습관리"],
                "url": canonical,
                "telephone": PHONE_DISPLAY,
                "openingHours": "Mo-Sa 12:00-24:00",
                "openingHoursSpecification": [{
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                    "opens": "12:00",
                    "closes": "24:00",
                }],
                "areaServed": {"@type": "Place", "name": local},
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": address,
                    "addressRegion": region,
                    "addressLocality": district,
                    "addressCountry": "KR",
                },
                "knowsAbout": ["영어 학습관리", "수학 학습관리", "국어 학습관리", "통합 플래너 관리", "오답 관리", "학습 상담"],
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 전과목 진단 상담", "serviceType": "TutoringService"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 통합 플래너 관리", "serviceType": "TutoringService"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 과목별 오답 재학습", "serviceType": "TutoringService"}},
                ],
                "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.8", "bestRating": "5", "ratingCount": str(len(reviews)), "reviewCount": str(len(reviews))},
                "review": [
                    {"@type": "Review", "author": {"@type": "Person", "name": "학부모"}, "reviewBody": r["body"], "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]), "bestRating": "5"}}
                    for r in reviews
                ],
            },
            {
                "@type": "Article",
                "@id": article_id,
                "headline": title,
                "description": description,
                "image": [rep_root, "/" + center_img, "/" + map_img],
                "inLanguage": "ko-KR",
                "datePublished": PUBLISH_DATE,
                "dateModified": PUBLISH_DATE,
                "author": {"@id": org_id},
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
                "description": f"{local} 학생의 영어, 수학, 국어를 함께 진단하고 통합 플래너와 오답 재학습으로 관리합니다.",
                "provider": {"@id": org_id},
                "areaServed": {"@type": "Place", "name": local},
                "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
                "about": about,
                "mentions": mentions,
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 전과목 학습 진단"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 통합 플래너 관리"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 과목별 오답 원인 분석"}},
                ],
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
                "name": f"{title} 수업 가능 학교 확인 항목",
                "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s} for i, s in enumerate(schools)],
            },
            {
                "@type": "ItemList",
                "@id": f"{canonical}#related",
                "name": f"{local} {CATEGORY} 관련 내부링크",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": name, "url": url}
                    for i, (name, url, _) in enumerate(related)
                ],
            },
        ],
    }

    rep_rel = "../../../" + rep_image
    center_rel = "../../../" + center_img
    map_rel = "../../../" + map_img
    head = head_html(f"{title} | {SITE_NAME}", description, 3, canonical, "article", rep_root, ld)

    badge_row = f'<div class="badge-row"><span>{esc(region)}</span><span>{esc(district)}</span><span>전과목</span><span>영어·수학·국어 통합관리</span></div>'

    media_section = f"""    <section class="section">
      <img src="{esc(rep_rel)}" alt="{esc(title + ' ' + SITE_NAME + ' 대표')}" style="display:none;">
      <div class="media-row">
        <figure class="frame"><img src="{esc(center_rel)}" alt="{esc(title + ' 본문 ' + SITE_NAME)}"></figure>
        <figure class="frame"><img src="{esc(map_rel)}" alt="{esc(title + ' 지도 ' + SITE_NAME)}"></figure>
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
      <p class="lead">{esc(center)}은 {esc(region)} {esc(district)} {esc(local)} 학생을 기준으로 상담을 진행하며, {esc(', '.join(middle_schools) if middle_schools else '인근 학교')} 학생들이 주로 문의합니다. 실제 등록 전에는 {esc(location_ref)}{eul_reul(location_ref)} 기준으로 이동 동선과 상담 가능 시간을 확인하는 것이 좋습니다.</p>
      <p class="lead">{esc(manu_outro)}</p>
    </section>"""

    answer_html = "\n".join(
        f'<div class="answer-item"><p class="q">{esc(q)}</p><p class="a">{esc(a)}</p></div>'
        for q, a in answers
    )
    answer_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">AEO ANSWER</p>
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
        linked_schools = f'<article class="info-card"><span class="tag">학교</span><h3>학교급별 참고 학교</h3><p>{esc(" · ".join(linked_bits))}</p></article>'
    fit_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">LOCAL &amp; STUDENT FIT</p>
        <h2>지역·학년·추천학생 기준</h2>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">지역</span><h3>{esc(region)} {esc(district)} {esc(local)}</h3><p>{esc(local)} 생활권 학생의 학교 진도와 시험 일정에 맞춰 전과목 관리 방향을 상담합니다.</p></article>
        <article class="info-card"><span class="tag">학년</span><h3>초1~고3, 전 학년 상담 가능</h3><p>학년별로 필요한 관리가 다르기 때문에 학습 습관, 내신, 진학 준비 시기를 나누어 봅니다.</p></article>
        <article class="info-card"><span class="tag">추천</span><h3>이런 학생에게 추천</h3><p>여러 과목을 따로 관리받기 번거로운 학생, 형제자매가 함께 다닐 학생, 학습 습관부터 잡아야 하는 학생에게 적합합니다.</p></article>
        {linked_schools}
      </div>
      <p class="lead" style="margin-top:18px;">수업 가능 학교 참고</p>
      <div class="chip-list">{school_chip_html}</div>
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

    fee_rows = FEE_TABLE_SEOUL if region == "서울" else FEE_TABLE_OTHER
    fee_region_label = "서울 지역 기준" if region == "서울" else "서울 외 지역 기준"
    fee_rows_html = "".join(
        f'<tr><td>{esc(freq)}</td><td>{esc(el)}</td><td>{esc(mid)}</td><td>{esc(hi)}</td></tr>'
        for freq, el, mid, hi in fee_rows
    )
    fee_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">TUITION</p>
        <h2>{esc(local)} {esc(CATEGORY)} 학습료 안내</h2>
        <p class="lead">{esc(fee_region_label)}으로 안내되는 학습료입니다. 실제 금액은 상담 시 학생 과정과 교육청 신고 기준에 따라 확인해 주세요.</p>
      </div>
      <div class="fee-table-wrap">
        <p class="fee-caption">{esc(fee_region_label)} · 1회 90~100분 수업</p>
        <table class="fee-table">
          <thead><tr><th>횟수</th><th>초등</th><th>중등</th><th>고등</th></tr></thead>
          <tbody>
            {fee_rows_html}
          </tbody>
        </table>
        <p class="fee-note">* 학습료는 지역, 수업 조건, 교육청 신고 기준에 따라 일부 차이가 있을 수 있습니다.</p>
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

    review_html = "\n".join(
        f'<article class="review-card"><span class="stars">{"★" * int(r["rating"])}{"☆" * (5 - int(r["rating"]))}</span><p>{esc(r["body"])}</p></article>'
        for r in reviews
    )
    review_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">PARENT REVIEW</p>
        <h2>{esc(local)} {esc(CATEGORY)} 상담 후기</h2>
      </div>
      <div class="review-grid">
        {review_html}
      </div>
    </section>"""

    related_html = "\n".join(
        f'<a href="{esc(url)}"><strong>{esc(name)} {esc(CATEGORY)}</strong><small>{esc(area)} 지역 페이지</small></a>'
        for name, url, area in related
    )
    other_link_html = cross_category_links_html(local, slug, CATEGORY)
    link_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">근처 학원페이지</p>
        <h2>{esc(local)} 주변 {esc(CATEGORY)} 페이지</h2>
        <p class="lead">같은 지역의 다른 과목과, 가까운 지역 페이지로 이동할 수 있도록 정리했습니다.</p>
      </div>
      <div class="link-grid">
        {other_link_html}
        <a href="../index.html"><strong>{esc(CATEGORY)} 전체</strong><small>카테고리 허브</small></a>
        <a href="../../index.html"><strong>전국학원</strong><small>전체 허브</small></a>
        {related_html}
      </div>
    </section>"""

    body = f"""{nav_html(3)}

  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../../index.html">홈</a><span>/</span><a href="../../index.html">전국학원</a><span>/</span><a href="../index.html">{esc(CATEGORY)}</a><span>/</span><span>{esc(local)}</span></p>
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

{review_section}

{link_section}
  </main>

{footer_html(3)}
"""
    return page_shell(head, body)


def root_hub() -> None:
    rep = "/assets/generated/academy-hero-v2.png"
    existing = [(name, desc) for name, desc in ALL_CATEGORIES if (SITE / "전국학원" / name).exists()]
    ld_root = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": "/전국학원/#webpage", "url": "/전국학원/", "name": "전국학원", "description": f"{SITE_NAME} 전국 학원 안내 허브입니다.", "inLanguage": "ko-KR"},
            {"@type": "BreadcrumbList", "@id": "/전국학원/#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": "/"}, {"@type": "ListItem", "position": 2, "name": "전국학원", "item": "/전국학원/"}]},
            {"@type": "ItemList", "@id": "/전국학원/#categories", "name": "전국학원 카테고리", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": name, "url": f"/전국학원/{name}/"} for i, (name, _) in enumerate(existing)]},
        ],
    }
    head = head_html(f"전국학원 | {SITE_NAME}", f"{SITE_NAME} 전국학원 허브입니다. 과목·학년 카테고리별로 지역 학습관리 안내 페이지로 이동할 수 있습니다.", 1, "/전국학원/", "website", rep, ld_root)
    category_cards = "".join(
        f'<a href="{esc(name)}/index.html"><strong>{esc(name)}</strong><small>{esc(desc)}</small></a>'
        for name, desc in existing
    )
    body = f"""{nav_html(1)}
  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../index.html">홈</a><span>/</span><span>전국학원</span></p>
      <p class="eyebrow">NATIONAL ACADEMY HUB</p>
      <h1>전국학원</h1>
      <p class="lead">과목과 학년 카테고리별로 지역 학습관리 페이지를 정리하는 허브입니다.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">전화 상담하기</a>
        <a class="btn btn-ghost" href="../상담문의/index.html">상담문의</a>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">ABOUT US</p>
        <h2>{esc(SITE_NAME)}는 이런 곳이에요</h2>
        <p class="lead">{esc(SITE_NAME)}는 성적표의 숫자보다 그 뒤에 있는 이유를 먼저 봐요. 상담, 진단, 플래너, 오답 재학습까지 아이에게 필요한 순서를 함께 찾아드립니다.</p>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">01</span><h3>지역 데이터 기반</h3><p>실제 센터 주소와 인근 학교 정보를 바탕으로, 지역마다 다른 상담 기준을 정리해 안내해요.</p></article>
        <article class="info-card"><span class="tag">02</span><h3>과목별 전문 관리</h3><p>수학, 영어처럼 과목마다 약점이 드러나는 지점이 다르기 때문에 과목별로 관리 방향을 나눠요.</p></article>
        <article class="info-card"><span class="tag">03</span><h3>학년별 우선순위</h3><p>자유학기제, 첫 내신, 고입 준비처럼 시기마다 필요한 게 달라 학년에 맞춰 순서를 정해요.</p></article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">구조 안내</p>
        <h2>카테고리에서 지역으로 이동하는 방식</h2>
        <p class="lead">예: 전국학원 / {CATEGORY} / 명일동</p>
      </div>
      <div class="category-grid">
        {category_cards}
      </div>
    </section>
  </main>
{footer_html(1)}"""
    out = SITE / "전국학원" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_shell(head, body), encoding="utf-8")


def category_hub(rows: list[dict[str, str]]) -> None:
    rep = "/assets/generated/academy-hero-v2.png"
    region_blocks = shared.region_blocks_html(rows, "전과목")
    ld_cat = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": f"/전국학원/{CATEGORY}/#webpage", "url": f"/전국학원/{CATEGORY}/", "name": CATEGORY, "description": f"{CATEGORY} 지역별 안내 허브입니다.", "inLanguage": "ko-KR"},
            {"@type": "BreadcrumbList", "@id": f"/전국학원/{CATEGORY}/#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": "/"}, {"@type": "ListItem", "position": 2, "name": "전국학원", "item": "/전국학원/"}, {"@type": "ListItem", "position": 3, "name": CATEGORY, "item": f"/전국학원/{CATEGORY}/"}]},
            {"@type": "ItemList", "@id": f"/전국학원/{CATEGORY}/#itemlist", "name": f"{CATEGORY} 지역 목록", "numberOfItems": len(rows), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f"{r['근처 수업가능 동네']} {CATEGORY}", "url": f"/전국학원/{CATEGORY}/{slug_ko(r['근처 수업가능 동네'])}/"} for i, r in enumerate(rows)]},
        ],
    }
    head = head_html(f"{CATEGORY} | {SITE_NAME}", f"전국 {len(rows)}개 지역의 {CATEGORY} 안내를 지역별로 정리한 허브입니다.", 2, f"/전국학원/{CATEGORY}/", "website", rep, ld_cat)
    body = f"""{nav_html(2)}
  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../index.html">홈</a><span>/</span><a href="../index.html">전국학원</a><span>/</span><span>{esc(CATEGORY)}</span></p>
      <p class="eyebrow">ALL-SUBJECT DIRECTORY</p>
      <h1>{esc(CATEGORY)}</h1>
      <p class="lead">지역별 전과목 상담 기준을 한눈에 찾을 수 있도록 정리했습니다. 각 페이지에는 지역·학년·추천학생, 학교 참고 정보, FAQ, 학부모 후기, 근처 학원페이지가 함께 구성됩니다.</p>
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
        <p class="eyebrow">총 지역</p>
        <h2>{len(rows)}개 지역</h2>
        <p class="lead">서울부터 지방까지 지역명 기준으로 {esc(CATEGORY)} 페이지를 생성했습니다.</p>
      </div>
      {region_blocks}
    </section>
  </main>
{footer_html(2)}"""
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
    root_hub()
    print(f"generated category={CATEGORY} local_pages={len(rows)}")


if __name__ == "__main__":
    main()
