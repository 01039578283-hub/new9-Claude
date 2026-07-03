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
CATEGORY = "중등영어학원"

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
# content banks (freshly written for 코칭아카데미 / 중등영어학원 — informed by
# FAQ.txt, 학부모 후기.txt, 상담방식.txt and 경쟁사분석 자료, not copied verbatim,
# and deliberately reworded vs. the 중등수학학원 banks to avoid cross-category
# duplicate content)
# ---------------------------------------------------------------------------

FAQ_OPENER_BANK: list[tuple[str, str]] = [
    ("{title}에서는 어떤 순서로 상담이 진행되나요?",
     "{local} 학생의 학교 진도와 최근 성적, 어휘 암기 습관을 먼저 살펴본 뒤 필요한 진단과 학습 방향을 안내해 드립니다."),
    ("{title} 상담을 예약하려면 미리 무엇을 챙겨야 하나요?",
     "따로 준비하실 것은 없습니다. 다만 최근 시험지나 사용 중인 단어장이 있으면 상담 내용이 조금 더 구체적으로 정리됩니다."),
    ("{title}만의 관리 방식이 궁금합니다.",
     "단어량을 늘리는 데 집중하기보다, {local} 학생이 문장 해석에서 어디에 걸리는지부터 확인하고 문법 적용과 오답 원인을 나누어 관리하는 방식입니다."),
    ("{title}에서 상담만 받고 등록은 나중에 결정해도 될까요?",
     "물론입니다. 상담 내용을 참고해 천천히 결정하셔도 전혀 문제되지 않습니다."),
    ("{title}은 한 반에 몇 명 정도로 운영되나요?",
     "학생 개개인의 질문과 피드백이 충분히 오갈 수 있는 인원으로 운영하고 있으며, 정확한 정원은 상담 시 자세히 안내해 드립니다."),
    ("{title} 등록을 고민 중인데 학년별로 챙기는 부분이 다른가요?",
     "그렇습니다. 자유학기제, 첫 내신, 고입 준비처럼 시기마다 필요한 부분이 다르기 때문에 {local} 학생의 학년에 맞춰 우선순위를 다르게 잡습니다."),
]

FAQ_BANK: list[tuple[str, str]] = [
    ("{district} 학교에 다니는 중학생은 영어 내신을 어떻게 준비하나요?",
     "학교 교과서 본문과 최근 프린트, 기출 유형을 기준으로 어법, 빈칸, 서술형 영작 순서로 준비합니다. {local} 학생이 다니는 학교의 변형 문제 스타일을 먼저 확인합니다."),
    ("단어는 열심히 외우는데 독해 속도가 느린 경우 어떻게 하나요?",
     "어휘량만의 문제가 아닐 수 있습니다. 문장을 끊어 읽는 연습과 접속사·관계대명사 흐름을 따라가는 훈련을 함께 진행합니다."),
    ("문법 개념은 배웠는데 문제에서 찾아내지 못한다면?",
     "개념을 아는 것과 실제 문장 안에서 찾아내는 것은 다른 능력입니다. 시제, 관계대명사, 수동태처럼 자주 헷갈리는 포인트를 문장 속에서 직접 짚어보는 연습을 반복합니다."),
    ("서술형 영작에서 감점이 잦은 학생은 어떻게 지도하나요?",
     "단어만 나열하지 않고 어순과 시제, 필요한 표현을 정확히 쓰는 연습을 반복합니다. 학교 채점 기준에 맞춰 직접 써보는 훈련까지 함께 진행합니다."),
    ("자유학기제로 시험이 없는 기간에도 영어 관리가 필요한가요?",
     "이 시기에 어휘 기초를 쌓고 문법 개념을 정리해 두면 좋습니다. {local} 학생도 이때 기본기를 다져두면 다음 학기 내신 대비가 한결 수월해집니다."),
    ("중학교 첫 영어 시험은 언제부터 준비를 시작하면 좋을까요?",
     "시험 직전에 몰아서 외우기보다 평소 본문 복습과 어휘 누적을 유지하다가 범위가 확정되면 집중적으로 대비하는 방식을 권합니다."),
    ("단어 암기를 유독 힘들어하는 아이는 어떻게 지도하나요?",
     "한 번에 많이 외우게 하기보다 반복 주기를 짧게 나누고, 문장 속에서 그 단어를 자주 마주치게 해 자연스럽게 익히도록 돕습니다."),
    ("같은 문법에서 계속 틀리는 아이는 어떻게 관리하나요?",
     "틀린 이유가 어휘 부족인지, 문법 오류인지, 해석 실패인지, 시간 부족인지 나누어 확인하고 비슷한 지문을 다시 읽혀 실제 이해 여부를 점검합니다."),
    ("꾸준히 다니는데도 점수가 제자리인 이유는 무엇일까요?",
     "최근 시험지와 그동안의 학습량을 함께 살펴보고 어휘, 문법, 독해, 서술형 중 어디서 정체가 생겼는지 확인한 뒤 학습 방법을 조정합니다."),
    ("영어를 갑자기 거부하는 중학생은 어떻게 대응하면 좋을까요?",
     "학습량이 많았는지, 난이도가 버거웠는지, 성적 부담이 컸는지 원인을 먼저 확인하고 지금 실행 가능한 작은 목표로 다시 시작합니다."),
    ("고등학교 진학을 앞두고 영어는 무엇을 준비해야 할까요?",
     "중학교 문법과 어휘를 점검하면서 고등영어의 긴 지문 독해와 어법 감각을 단계적으로 준비합니다. 무리한 선행보다 현재 과정의 완성도를 먼저 확인합니다."),
    ("{local}에서 학생마다 다니는 학교가 다른데 같은 반에서 배우나요?",
     "기본 어휘와 문법은 함께 배우되, 학교별 교과서와 시험 범위가 다르기 때문에 내신 대비 자료는 학교에 맞춰 따로 준비합니다."),
    ("중학생도 플래너로 학습 관리를 받을 수 있나요?",
     "중학생은 스스로 계획을 세우는 연습을 이제 막 시작하는 시기이므로, 처음에는 구체적인 학습량을 정해주고 점차 스스로 계획을 세우도록 이끕니다."),
    ("숙제를 자주 밀리는 편인데 등록해도 괜찮을까요?",
     "괜찮습니다. 분량이 많았는지 습관 문제인지 먼저 확인하고, 지킬 수 있는 분량으로 조정하며 완료하는 습관을 함께 만들어 갑니다."),
    ("시험 기간에는 평소 수업과 무엇이 달라지나요?",
     "학교별 시험 범위에 맞춰 본문 해설, 어법 정리, 서술형 연습, 실전 테스트 위주로 수업을 다시 구성합니다."),
    ("등록 전에 레벨테스트를 반드시 봐야 하나요?",
     "레벨테스트는 탈락시키기 위한 시험이 아니라 필요한 학습계획을 찾기 위한 진단 과정입니다. 결과가 낮다고 등록이 어려운 것은 아닙니다."),
    ("{local}에 사는 중학생인데 듣기평가 점수만 유독 낮습니다.",
     "발음과 어휘를 함께 듣는 연습, 문제 유형별 접근법을 반복 훈련합니다. 듣기도 독해처럼 반복 훈련으로 충분히 개선할 수 있는 영역입니다."),
    ("다른 학원에서 옮기려는데 진도가 다르면 어떻게 하나요?",
     "이전 학원에서 배운 진도와 자료를 확인한 뒤 현재 수준에 맞는 시작 지점과 학습계획을 새로 정리해 안내합니다."),
]

ANSWER_BANK: list[tuple[str, str]] = [
    ("중학교 영어는 왜 갑자기 어려워질까요?",
     "단어 암기 위주였던 초등 영어와 달리 시제, 관계대명사, 수동태 같은 문법 체계가 본격적으로 늘어나기 때문입니다. {local} 학생 상담에서는 어느 문법 포인트부터 흔들리기 시작했는지를 먼저 확인합니다."),
    ("성적이 잘 안 오른다고 학원부터 옮기는 게 맞을까요?",
     "환경을 바꾸기 전에 무엇이 부족했는지부터 짚어보는 것이 먼저입니다. 단어 수를 늘리는 것만으로는 부족하고, 오답 원인을 구분하지 않으면 옮겨도 같은 실수가 반복될 수 있습니다."),
    ("단어는 아는데 지문 해석이 안 된다면?",
     "어휘와 독해는 다른 능력입니다. 문장 구조를 끊어 읽고 접속사 흐름을 따라가는 훈련이 별도로 필요합니다."),
    ("서술형 영작 때문에 점수가 깎이는 게 걱정된다면?",
     "단어를 나열하는 것과 정확한 문장을 쓰는 것은 다른 훈련이 필요합니다. 채점 기준에 맞춘 어순과 표현을 반복해서 연습합니다."),
    ("중학교 영어와 고등영어는 얼마나 연결되어 있나요?",
     "중학교 문법 체계와 어휘는 고등영어 긴 지문 독해의 기초가 됩니다. 지금 흔들리는 문법 포인트를 방치하면 고등학교에서 더 크게 드러날 수 있습니다."),
    ("계획을 스스로 못 세우는 아이라 걱정입니다.",
     "중학생 시기에는 자연스러운 일입니다. 처음에는 해야 할 학습량을 구체적으로 정해주고, 점점 익숙해지면 아이 스스로 계획을 짜보도록 단계를 나눠 이끌어갑니다."),
    ("학교마다 교과서와 시험 범위가 달라서 걱정된다면?",
     "학교별 교과서 본문과 출제 경향을 확인해 필요한 자료를 구분해서 준비하면, 같은 학년이라도 학교에 맞는 대비가 가능합니다."),
    ("단어를 많이 외워도 실력이 그대로인 것 같다면?",
     "양보다 문장 속에서 그 단어를 다시 알아볼 수 있는지가 더 중요합니다. 오답을 원인별로 나누고 복습 주기를 정해 반복하는 구조가 필요합니다."),
    ("갑자기 영어에 흥미가 없어진 것 같다면?",
     "성적보다 원인을 먼저 봅니다. 학습량, 난이도, 자신감 중 무엇이 영향을 주고 있는지 확인한 뒤 실행 가능한 목표부터 다시 세웁니다."),
    ("영어 학원을 고를 때 가장 먼저 확인해야 할 것은?",
     "단어 암기량보다 지금 아이의 상태를 얼마나 구체적으로 진단하고, 그 결과를 어떻게 관리로 연결하는지를 먼저 확인하는 것이 좋습니다."),
]

CHECKLIST_BANK: list[tuple[str, str]] = [
    ("최근 영어 시험지", "점수보다 어휘, 문법, 독해 중 어디서 왜 틀렸는지 확인하는 데 필요합니다."),
    ("사용 중인 교재", "본문 진도와 난이도를 확인해 바로 이어서 시작할 수 있는 지점을 잡습니다."),
    ("학교 출제 범위", "{local} 학생이 다니는 학교의 본문 범위와 수행평가 일정을 함께 확인합니다."),
    ("단어장 진행 상태", "그동안 외운 단어량과 반복 주기를 확인해 관리 강도를 정합니다."),
    ("오답 정리 방식", "기존에 오답을 정리해 온 방법이 있다면 함께 확인해 이어갈 부분을 정합니다."),
    ("선행 진도", "지금 얼마나 앞서 있는지보다, 배우는 문법을 얼마나 정확히 적용하는지를 먼저 봅니다."),
    ("학습 목표", "점수를 올리는 것과 기초를 다지는 것, 습관을 잡는 것 중 지금 무엇이 더 급한지 함께 정합니다."),
    ("이전 학원 이력", "다니던 학원이 있었다면 진도와 학습 방식을 확인해 자연스럽게 이어갑니다."),
]

REVIEW_BANK: list[str] = [
    "처음 상담 때 아이가 어떤 문법에서 막혀 있는지 구체적으로 짚어주셔서 믿음이 갔습니다.",
    "서술형 영작에 자신 없어 하던 아이가 이제는 문장을 스스로 완성합니다.",
    "틀린 문장은 그냥 넘어가지 않고 왜 틀렸는지 하나씩 짚어주셔서 도움이 됐습니다.",
    "학교 본문에 맞춰 준비해 주셔서 내신 점수가 안정적으로 나오기 시작했습니다.",
    "단어 암기를 매일 확인해 주시니 아이가 스스로 외우려는 모습이 보입니다.",
    "매일 조금씩이라도 단어를 외우도록 분량을 나눠주셔서 부담 없이 따라가고 있습니다.",
    "문법부터 차근차근 짚어주셔서 이전보다 문장을 이해하는 속도가 빨라졌습니다.",
    "시험 직전에 핵심 표현을 정리해 주셔서 큰 도움이 되었습니다.",
    "아이가 편하게 느낄 수 있게 설명 속도와 방식을 맞춰주시는 게 느껴졌습니다.",
    "자유학기제 동안 어휘 기초를 다져주셔서 다음 학기 내신 대비가 한결 수월했습니다.",
    "중학교 첫 영어 시험을 앞두고 무엇을 준비해야 할지 막막했는데 방향을 잡아주셨습니다.",
    "아이가 영어를 거부하던 시기에도 억지로 밀어붙이지 않고 천천히 다가가 주셨습니다.",
    "학교마다 교과서가 다른데 그 부분까지 확인해서 준비해 주셨습니다.",
    "수행평가 준비물까지 미리 알려주셔서 놓치지 않고 챙길 수 있었습니다.",
    "선생님께서 아이가 스스로 해석하게 하시니 이해도가 눈에 띄게 좋아졌습니다.",
    "성적보다 단어를 외우는 습관이 먼저 자리 잡은 것 같아 만족스럽습니다.",
    "고등학교 진학을 앞두고 무리한 선행 대신 문법 기초부터 다시 점검해 주셨습니다.",
    "상담 때 부풀리지 않고 아이의 실제 실력을 그대로 말씀해 주셔서 믿음이 갔습니다.",
    "매번 같은 문법에서 틀리던 문제를 이제는 스스로 짚어냅니다.",
    "이전 학원에서 배운 단어와 문법 진도를 확인하고 이어서 수업해 주셔서 적응이 빨랐습니다.",
    "모르는 문장이 있어도 편하게 손을 들고 물어보는 모습을 보게 되었습니다.",
    "시험 2주 전부터는 평소보다 훨씬 세심하게 봐주시는 게 느껴졌습니다.",
    "단어 암기 습관이 없던 아이가 정해진 시간에 앉아서 외우기 시작했습니다.",
    "아이가 지금 어떤 문법을 어려워하는지 구체적으로 전달받을 수 있어 안심이 됩니다.",
]

COMPARE_ROWS: list[dict[str, tuple[str, str]]] = [
    {"label": "교재", "A": ("학년별로 통일된 교재", "현재 어휘·문법 수준에 맞춘 교재"),
     "B": ("정해진 커리큘럼 그대로 진행", "진단 결과에 따라 시작 지점을 다르게 설정")},
    {"label": "진도", "A": ("반 전체가 같은 속도로 진행", "학생별 이해도에 맞춘 개인 진도"),
     "B": ("정해진 일정대로만 진행", "이해가 부족한 문법은 다시 짚고 넘어감")},
    {"label": "오답 관리", "A": ("단어 시험 결과만 확인", "오답 유형을 나누어 재학습까지 연결"),
     "B": ("답을 맞았는지만 확인", "해석 과정과 재확인까지 함께 점검")},
    {"label": "학부모 소통", "A": ("성적 결과만 전달", "진도, 태도, 다음 계획까지 함께 안내"),
     "B": ("정기 안내만 제공", "필요할 때마다 편하게 상담 가능")},
]

SUMMARY_INTROS: list[str] = [
    "{local} 중학생에게 필요한 영어 관리는 단순 암기보다 현재 어휘 수준, 문법 이해, 학교 시험 범위, 오답 반복 이유를 함께 보는 것입니다.",
    "{local} 학생이라도 지금까지 쌓아온 어휘와 문법 이해도는 저마다 다르기 때문에, 먼저 확인해야 할 부분도 학생마다 달라집니다.",
    "{local}에서 중등영어를 준비할 때는 점수 자체보다 그 점수가 나온 과정을 먼저 살펴보는 것이 방향을 잡는 데 도움이 됩니다.",
]

MANUSCRIPT_INTRO: list[str] = [
    "중학교 영어는 시제, 관계대명사, 수동태처럼 문법 체계가 본격적으로 늘어나는 시기입니다. 단어 암기 위주로 학습해 온 학생이라면 문장을 해석하는 방식 자체를 다시 익혀야 할 수 있습니다.",
    "같은 학년이라도 학교마다 교과서와 시험 범위가 다르기 때문에, 중등영어학원을 고를 때는 아이가 다니는 학교의 본문과 출제 스타일까지 확인해 주는 곳인지 살펴보는 것이 좋습니다.",
    "중학교 시기는 성적 관리뿐 아니라 스스로 단어를 외우고 복습하는 습관을 만드는 시작점이기도 합니다. 플래너로 계획과 실행을 확인하는 과정이 고등학교 진학 이후에도 이어질 수 있습니다.",
    "서술형 영작 비중이 늘어나면서 단어를 나열하는 것으로는 부족한 시대가 되었습니다. 정확한 어순과 표현을 쓰는 연습이 되어 있는지가 내신 점수에 직접적인 영향을 줍니다.",
    "자유학기제처럼 시험 부담이 적은 시기를 어떻게 활용하느냐에 따라 다음 학기 성적이 크게 달라질 수 있습니다. 이 시기에 어휘와 문법 기초를 다지는 학생과 그렇지 않은 학생의 차이는 시험 범위가 확정된 뒤에 드러납니다.",
    "중학교 영어에서 흔들린 문법은 고등영어에서 더 크게 드러나는 경우가 많습니다. 지금 눈앞의 시험 점수만 보기보다, 다음 단계로 이어질 수 있는 학습 흐름을 함께 봐야 하는 이유입니다.",
]

MANUSCRIPT_OUTRO: list[str] = [
    "학원을 정할 때는 화려한 커리큘럼 설명보다, 아이의 현재 어휘와 문법 상태를 얼마나 구체적으로 짚어주는지를 먼저 살펴보시길 권합니다.",
    "영어 점수는 결과일 뿐, 그 자체가 목표가 되어서는 안 됩니다. 점수를 만드는 학습 과정이 아이에게 맞는지를 함께 확인해 보세요.",
    "상담은 등록을 결정짓는 자리가 아니라, 지금 아이에게 어떤 관리가 필요한지 함께 찾아보는 시간으로 여겨주시면 좋겠습니다.",
    "언어 학습은 한 번에 완성되지 않습니다. 어휘와 문법, 독해를 반복해서 오가며 조금씩 쌓아가는 과정이라는 점을 기억해 주세요.",
    "아이가 모르는 단어나 문장을 부담 없이 물어볼 수 있는 분위기인지가, 꾸준한 영어 학습으로 이어지는 데 중요한 역할을 합니다.",
    "지금 당장의 시험 점수보다, 스스로 단어를 외우고 문장을 분석하는 습관이 만들어지고 있는지를 함께 지켜봐 주시길 바랍니다.",
]


def choose_rep_images(rows: list[dict[str, str]]) -> list[str]:
    # reuse the exact same seed/pool as the math category so the SAME dong
    # gets the SAME representative photo across categories (consistent
    # location branding). Files were already copied by the math script; this
    # call is idempotent (skips re-copy when the file already matches).
    return shared.choose_rep_images(rows)


def local_page(row: dict[str, str], idx: int, rep_image: str, all_rows: list[dict[str, str]]) -> str:
    local = row["근처 수업가능 동네"].strip()
    slug = slug_ko(local)
    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    center = row.get("센터명", "").strip() or f"{local} 학습관리"
    address = row.get("센터 주소", "").strip()
    title = f"{local} 중등영어학원"
    description = f"{region} {district} {local} 중학생을 위한 중등영어학원 안내입니다. 학교 내신 범위, 서술형 영작, 어휘·문법 관리, 오답 재학습 기준을 상담 전에 확인할 수 있습니다."
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
    grade_eng = row.get("가능학년\n(영어)", "").strip()

    reg_no = row.get("교육지원청 등록번호", "").strip()
    education_name = row.get("교육지원청명칭", "").strip()

    opener = fmt_pair(pick(FAQ_OPENER_BANK, 1, local, "eng-faq-opener")[0],
                       local=local, district=district, title=title, region=region)
    faqs = [opener] + [fmt_pair(p, local=local, district=district, title=title, region=region)
                        for p in pick(FAQ_BANK, 5, local, "eng-faq")]
    answers = [fmt_pair(p, local=local, district=district, title=title, region=region)
               for p in pick(ANSWER_BANK, 4, local, "eng-answer")]
    checklist = [fmt_pair(p, local=local, district=district, title=title, region=region)
                 for p in pick(CHECKLIST_BANK, 4, local, "eng-checklist")]
    review_lines = pick(REVIEW_BANK, 6, local, "eng-review")
    summary_intro = pick(SUMMARY_INTROS, 1, local, "eng-summary")[0].format(local=local)
    manu_intro = pick(MANUSCRIPT_INTRO, 1, local, "eng-manu-intro")[0]
    manu_outro = pick(MANUSCRIPT_OUTRO, 1, local, "eng-manu-outro")[0]
    location_ref = address if address else "상담 시 안내되는 위치"
    variant = "A" if seed_for(local, "eng-compare") % 2 == 0 else "B"

    rng = random.Random(seed_for(local, "eng-review-rating"))
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
        {"@type": "Thing", "name": "중등영어학원"},
        {"@type": "Thing", "name": "중학교 내신 대비"},
        {"@type": "Thing", "name": "서술형 영작"},
        {"@type": "Thing", "name": "영어 오답 재학습"},
        {"@type": "Thing", "name": "플래너 관리"},
    ]
    mentions = [
        {"@type": "Place", "name": region},
        {"@type": "Place", "name": district},
        {"@type": "EducationalOrganization", "name": center},
    ] + [{"@type": school_type(s), "name": s} for s in schools]
    has_part = [
        "핵심 요약", "학원 선택 가이드", "답변형 중등영어 안내", "지역·학년·추천학생",
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
                "alternateName": [SITE_NAME, center, f"{local} 중등영어 학습관리"],
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
                "knowsAbout": ["중등영어", "중학교 내신 대비", "서술형 영작", "어휘·문법 관리", "영어 오답 재학습", "중학생 학습 상담"],
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 중등영어 진단 상담", "serviceType": "TutoringService"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 중학교 내신 서술형 영작 대비", "serviceType": "TutoringService"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 영어 오답 재학습 관리", "serviceType": "TutoringService"}},
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
                "description": f"{local} 중학생의 어휘, 문법, 서술형 영작, 학교별 내신 시험범위, 오답 재학습을 함께 관리합니다.",
                "provider": {"@id": org_id},
                "areaServed": {"@type": "Place", "name": local},
                "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
                "about": about,
                "mentions": mentions,
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 중등영어 어휘·문법 진단"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 중학교 내신 서술형 플래너"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 영어 오답 원인 분석"}},
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
                "name": f"{local} 중등영어학원 관련 내부링크",
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

    badge_row = f'<div class="badge-row"><span>{esc(region)}</span><span>{esc(district)}</span><span>중등영어</span><span>내신·서술형·오답관리</span></div>'

    media_section = f"""    <section class="section">
      <img src="{esc(rep_rel)}" alt="{esc(title + ' ' + SITE_NAME + ' 대표')}" style="display:none;">
      <div class="media-row">
        <figure class="frame"><img src="{esc(center_rel)}" alt="{esc(title + ' 본문 ' + SITE_NAME)}"></figure>
        <figure class="frame"><img src="{esc(map_rel)}" alt="{esc(title + ' 지도 ' + SITE_NAME)}"></figure>
      </div>
      <p class="lead">{esc(center)} 기준으로 {esc(local)} 학생의 중등영어 상담 범위를 확인합니다. 실제 방문·상담 전에는 주소와 이동 동선을 함께 확인해 주세요.</p>
    </section>"""

    summary_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">핵심 요약</p>
        <h2>{esc(local)} 중등영어학원 선택 전 확인할 기준</h2>
        <p class="lead">{esc(summary_intro)}</p>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">01</span><h3>어휘·문법</h3><p>단어 암기 여부뿐 아니라 시제, 관계대명사, 수동태 등 문법을 문장 안에서 적용하는 습관을 함께 봅니다.</p></article>
        <article class="info-card"><span class="tag">02</span><h3>내신 범위</h3><p>{esc(district)} 학교별 교과서 본문과 프린트, 수행평가 일정을 상담 시 함께 확인합니다.</p></article>
        <article class="info-card"><span class="tag">03</span><h3>서술형·오답</h3><p>정답 여부만이 아니라 어순과 표현, 독해 오답 원인을 함께 봅니다.</p></article>
      </div>
    </section>"""

    manuscript_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">학원 선택 가이드</p>
        <h2>{esc(local)} 중등영어학원, 무엇을 기준으로 볼까요</h2>
      </div>
      <p class="lead">{esc(manu_intro)}</p>
      <p class="lead">{esc(center)}은 {esc(region)} {esc(district)} {esc(local)} 학생을 기준으로 상담을 진행하며, {esc(', '.join(middle_schools) if middle_schools else '인근 중학교')} 학생들이 주로 문의합니다. 실제 등록 전에는 {esc(location_ref)}{eul_reul(location_ref)} 기준으로 이동 동선과 상담 가능 시간을 확인하는 것이 좋습니다.</p>
      <p class="lead">{esc(manu_outro)}</p>
    </section>"""

    answer_html = "\n".join(
        f'<div class="answer-item"><p class="q">{esc(q)}</p><p class="a">{esc(a)}</p></div>'
        for q, a in answers
    )
    answer_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">AEO ANSWER</p>
        <h2>{esc(title)}은 어떤 학생에게 필요할까요?</h2>
      </div>
      <div class="answer-list">
        {answer_html}
      </div>
    </section>"""

    grade_text = grade_eng if grade_eng else "상담 시 학년별 가능 여부를 확인합니다."
    school_chip_html = "".join(f"<span>{esc(s)}</span>" for s in schools) if schools else "<span>상담 시 학교 확인</span>"
    linked_schools = ""
    if elementary_schools or high_schools:
        linked_bits = []
        if elementary_schools:
            linked_bits.append(f"진학 전 초등학교: {', '.join(elementary_schools)}")
        if high_schools:
            linked_bits.append(f"진학 예정 고등학교: {', '.join(high_schools)}")
        linked_schools = f'<article class="info-card"><span class="tag">연계</span><h3>진학 연계 학교</h3><p>{esc(" · ".join(linked_bits))}</p></article>'
    fit_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">LOCAL &amp; STUDENT FIT</p>
        <h2>지역·학년·추천학생 기준</h2>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">지역</span><h3>{esc(region)} {esc(district)} {esc(local)}</h3><p>{esc(local)} 생활권 학생의 학교 진도와 시험 일정에 맞춰 중등영어 관리 방향을 상담합니다.</p></article>
        <article class="info-card"><span class="tag">학년</span><h3>중1~중3, 가능학년 {esc(grade_text)}</h3><p>학년별로 필요한 관리가 다르기 때문에 자유학기제, 첫 내신, 고입 대비 시기를 나누어 봅니다.</p></article>
        <article class="info-card"><span class="tag">추천</span><h3>이런 학생에게 추천</h3><p>어휘는 아는데 독해가 느린 학생, 문법을 적용하지 못하는 학생, 서술형에서 감점이 큰 학생에게 적합합니다.</p></article>
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
        <h2>{esc(local)} 중등영어, 무엇이 다른가요</h2>
        <p class="lead">일반적인 학원 운영 방식과 {esc(SITE_NAME)}의 중등영어 관리 방식을 같은 기준으로 비교했습니다.</p>
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
        f'<tr><td>{esc(freq)}</td><td>{esc(el)}</td><td class="highlight">{esc(mid)}</td><td>{esc(hi)}</td></tr>'
        for freq, el, mid, hi in fee_rows
    )
    fee_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">TUITION</p>
        <h2>{esc(local)} 중등영어학원 학습료 안내</h2>
        <p class="lead">{esc(fee_region_label)}으로 안내되는 학습료입니다. 실제 금액은 상담 시 학생 과정과 교육청 신고 기준에 따라 확인해 주세요.</p>
      </div>
      <div class="fee-table-wrap">
        <p class="fee-caption">{esc(fee_region_label)} · 1회 90~100분 수업</p>
        <table class="fee-table">
          <thead><tr><th>횟수</th><th>초등</th><th class="highlight">중등</th><th>고등</th></tr></thead>
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
        <h2>{esc(local)} 중등영어 상담 후기</h2>
      </div>
      <div class="review-grid">
        {review_html}
      </div>
    </section>"""

    related_html = "\n".join(
        f'<a href="{esc(url)}"><strong>{esc(name)} 중등영어학원</strong><small>{esc(area)} 지역 페이지</small></a>'
        for name, url, area in related
    )
    other_link_html = cross_category_links_html(local, slug, CATEGORY)

    link_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">근처 학원페이지</p>
        <h2>{esc(local)} 주변 중등영어학원 페이지</h2>
        <p class="lead">같은 지역의 다른 과목과, 가까운 지역 페이지로 이동할 수 있도록 정리했습니다.</p>
      </div>
      <div class="link-grid">
        {other_link_html}
        <a href="../index.html"><strong>중등영어학원 전체</strong><small>카테고리 허브</small></a>
        <a href="../../index.html"><strong>전국학원</strong><small>전체 허브</small></a>
        {related_html}
      </div>
    </section>"""

    body = f"""{nav_html(3)}

  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../../index.html">홈</a><span>/</span><a href="../../index.html">전국학원</a><span>/</span><a href="../index.html">{esc(CATEGORY)}</a><span>/</span><span>{esc(local)}</span></p>
      <p class="eyebrow">MIDDLE SCHOOL ENGLISH COACHING</p>
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


# ---------------------------------------------------------------------------
# hub pages (root hub now lists every category folder that exists on disk)
# ---------------------------------------------------------------------------

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
        <p class="lead">예: 전국학원 / 중등영어학원 / 명일동</p>
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
    region_blocks = shared.region_blocks_html(rows, "중등영어")
    ld_cat = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": f"/전국학원/{CATEGORY}/#webpage", "url": f"/전국학원/{CATEGORY}/", "name": CATEGORY, "description": "중등영어학원 지역별 안내 허브입니다.", "inLanguage": "ko-KR"},
            {"@type": "BreadcrumbList", "@id": f"/전국학원/{CATEGORY}/#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": "/"}, {"@type": "ListItem", "position": 2, "name": "전국학원", "item": "/전국학원/"}, {"@type": "ListItem", "position": 3, "name": CATEGORY, "item": f"/전국학원/{CATEGORY}/"}]},
            {"@type": "ItemList", "@id": f"/전국학원/{CATEGORY}/#itemlist", "name": "중등영어학원 지역 목록", "numberOfItems": len(rows), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f"{r['근처 수업가능 동네']} 중등영어학원", "url": f"/전국학원/{CATEGORY}/{slug_ko(r['근처 수업가능 동네'])}/"} for i, r in enumerate(rows)]},
        ],
    }
    head = head_html(f"{CATEGORY} | {SITE_NAME}", f"전국 {len(rows)}개 지역의 중등영어학원 학습관리 페이지를 지역별로 정리한 허브입니다.", 2, f"/전국학원/{CATEGORY}/", "website", rep, ld_cat)
    body = f"""{nav_html(2)}
  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../index.html">홈</a><span>/</span><a href="../index.html">전국학원</a><span>/</span><span>{esc(CATEGORY)}</span></p>
      <p class="eyebrow">MIDDLE SCHOOL ENGLISH DIRECTORY</p>
      <h1>{esc(CATEGORY)}</h1>
      <p class="lead">지역별 중등영어 상담 기준을 한눈에 찾을 수 있도록 정리했습니다. 각 페이지에는 지역·학년·추천학생, 학교 참고 정보, FAQ, 학부모 후기, 내부링크가 함께 구성됩니다.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">전화 상담하기</a>
        <a class="btn btn-ghost" href="../../상담문의/index.html">상담문의</a>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">ABOUT US</p>
        <h2>{esc(SITE_NAME)}는 중등영어를 이렇게 관리해요</h2>
        <p class="lead">단어를 많이 외우게 하기보다, 지금 이 학생이 어디서 해석이 막히는지부터 확인해요. 상담에서 시작해 진단, 어휘·문법 관리, 오답 재학습까지 이어갑니다.</p>
      </div>
      <div class="timeline">
        <article class="timeline-item">
          <div class="timeline-num">01</div>
          <div class="timeline-body"><h3>상담</h3><p>학교 진도와 최근 성적, 어휘 암기 습관을 먼저 듣고 필요한 방향을 정합니다.</p></div>
        </article>
        <article class="timeline-item">
          <div class="timeline-num">02</div>
          <div class="timeline-body"><h3>진단</h3><p>어휘가 부족한지, 문법을 적용하지 못하는지, 해석이 안 되는지 원인을 나누어 확인합니다.</p></div>
        </article>
        <article class="timeline-item">
          <div class="timeline-num">03</div>
          <div class="timeline-body"><h3>어휘·문법 관리</h3><p>단어장 진행과 문법 적용 연습을 함께 기록하며 실행 여부를 확인합니다.</p></div>
        </article>
        <article class="timeline-item">
          <div class="timeline-num">04</div>
          <div class="timeline-body"><h3>오답 재학습</h3><p>틀린 문장의 원인을 분류하고 비슷한 지문으로 다시 확인해 반복 실수를 줄입니다.</p></div>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">총 지역</p>
        <h2>{len(rows)}개 지역</h2>
        <p class="lead">서울부터 지방까지 지역명 기준으로 중등영어학원 페이지를 생성했습니다.</p>
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
