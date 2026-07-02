from __future__ import annotations

import csv
import html
import json
import random
import re
import shutil
import zlib
from pathlib import Path


SITE = Path(__file__).resolve().parents[1]
BASE = SITE.parent
COMMON = BASE / "참고자료" / "공통자료"

SITE_NAME = "코칭아카데미"
CATEGORY = "중등수학학원"
PHONE_DISPLAY = "010-6839-8283"
PHONE_LINK = "01068398283"
CONSULT_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdb2oE5Qk5YS0TfYDxyV1w-IOTkhkjOCmmpAKTI9FmqpVj6Yg/viewform"
PUBLISH_DATE = "2026-07-02"


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def slug_ko(name: str) -> str:
    value = re.sub(r"\s+", "", name.strip())
    value = re.sub(r'[\\/:*?"<>|#%&+]', "", value)
    return value


def split_items(value: str) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in re.split(r"[,/·\n]+", value) if x.strip()]


def seed_for(*parts: str) -> int:
    return zlib.crc32("::".join(parts).encode("utf-8"))


def json_script(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def rel_prefix(depth: int) -> str:
    return "../" * depth


def has_batchim(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return True
    ch = text[-1]
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        return (code - 0xAC00) % 28 != 0
    return True


def eul_reul(text: str) -> str:
    return "을" if has_batchim(text) else "를"


def school_type(name: str) -> str:
    if name.endswith("초"):
        return "ElementarySchool"
    if name.endswith("중"):
        return "MiddleSchool"
    if name.endswith("고"):
        return "HighSchool"
    return "School"


# ---------------------------------------------------------------------------
# page shell (nav / footer / head)
# ---------------------------------------------------------------------------

def nav_html(depth: int, active: str = "전국학원") -> str:
    p = rel_prefix(depth)
    links = [
        ("홈", f"{p}index.html"),
        ("학습가이드", f"{p}학습가이드/index.html"),
        ("상담문의", f"{p}상담문의/index.html"),
        ("전국학원", f"{p}전국학원/index.html"),
    ]
    items = "\n".join(
        f'        <a{" class=\"active\"" if name == active else ""} href="{href}">{name}</a>'
        for name, href in links
    )
    return f"""  <header class="nav-wrap">
    <nav class="nav" aria-label="주요 메뉴">
      <a class="brand" href="{p}index.html"><span class="brand-mark">코</span><span>{SITE_NAME}</span></a>
      <div class="nav-links">
{items}
      </div>
    </nav>
  </header>"""


def footer_html(depth: int) -> str:
    p = rel_prefix(depth)
    return f"""  <footer class="footer">
    <p><strong>{SITE_NAME}</strong> · 아이 맞춤 학습관리 코칭 · 상담은 전화·문자로 편하게 문의해주세요.</p>
  </footer>

  <div class="floating-cta" aria-label="빠른 상담 버튼">
    <a href="tel:{PHONE_DISPLAY}">전화문의</a>
    <a href="sms:{PHONE_LINK}">문자문의</a>
    <a href="{CONSULT_FORM_URL}" target="_blank" rel="noopener noreferrer">상담문의</a>
  </div>"""


def head_html(title: str, description: str, depth: int, canonical: str, og_type: str, image: str, ld: dict) -> str:
    p = rel_prefix(depth)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:type" content="{esc(og_type)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(image)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="icon" type="image/png" href="{p}assets/favicon.png">
  <link rel="apple-touch-icon" href="{p}assets/favicon.png">
  <link rel="stylesheet" href="{p}assets/site.css">
  <script type="application/ld+json">{json_script(ld)}</script>
</head>"""


def page_shell(head: str, body: str) -> str:
    return f"""{head}
<body>
<div class="site-shell">
{body}
</div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# images
# ---------------------------------------------------------------------------

def find_map(row: dict[str, str]) -> str:
    maps_dir = SITE / "assets" / "maps"
    raw = row.get("동 영어", "").strip()
    candidates = [raw, raw.replace(" ", "-"), raw.replace(" ", ""), raw.replace("_", "-")]
    for base in candidates:
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            p = maps_dir / f"{base}{ext}"
            if p.exists():
                return f"assets/maps/{p.name}"
    return "assets/centers/common/local6839.jpg"


def choose_rep_images(rows: list[dict[str, str]]) -> list[str]:
    src_dir = COMMON / "대표이미지"
    dst_dir = SITE / "assets" / "representative"
    dst_dir.mkdir(parents=True, exist_ok=True)

    images = [p for p in src_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}]
    images.sort(key=lambda p: p.name)
    rng = random.Random(8283)
    rng.shuffle(images)
    chosen = [images[i % len(images)] for i in range(len(rows))]
    result: list[str] = []
    for i, src in enumerate(chosen, 1):
        ext = src.suffix.lower()
        dst = dst_dir / f"rep-{i:03d}{ext}"
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
        result.append(f"assets/representative/{dst.name}")
    return result


# ---------------------------------------------------------------------------
# content banks (freshly written for 코칭아카데미 / 중등수학학원 — not copied
# verbatim from any reference file; informed by 상담방식.txt, FAQ.txt,
# 학부모 후기.txt and 경쟁사분석 자료 patterns)
# ---------------------------------------------------------------------------

FAQ_OPENER_BANK: list[tuple[str, str]] = [
    ("{title}은 어떤 방식으로 진행되나요?",
     "학생의 학교, 최근 성적, 현재 학습 습관을 먼저 확인한 뒤 {local} 학생에게 필요한 진단과 관리 방향을 상담을 통해 안내합니다."),
    ("{title}에 처음 상담을 받으려면 무엇부터 준비하면 되나요?",
     "특별한 준비물이 없어도 괜찮습니다. 최근 시험지나 사용 중인 교재가 있으면 상담이 조금 더 구체적으로 진행됩니다."),
    ("{title}은 다른 수학학원과 무엇이 다른가요?",
     "문제 수를 늘리기보다 {local} 학생이 막힌 지점을 먼저 진단하고, 서술형과 오답 원인을 나누어 관리하는 방식에 가깝습니다."),
    ("{title} 등록 전 상담만 받아봐도 되나요?",
     "네, 가능합니다. 상담에서 들은 내용을 바탕으로 여유롭게 생각해 보신 뒤 등록 여부를 결정하셔도 됩니다."),
    ("{title}에서는 학생 몇 명이 함께 수업하나요?",
     "반별 정원은 학생별 질문과 피드백이 충분히 이루어질 수 있는 수준으로 제한해 운영하며, 정확한 인원은 상담 시 안내해 드립니다."),
    ("{title}을 고려 중인데 학년마다 관리가 다른가요?",
     "네, 자유학기제, 첫 내신, 고입 대비처럼 학년별로 필요한 관리가 다르기 때문에 {local} 학생의 학년에 맞춰 우선순위를 다르게 잡습니다."),
]

FAQ_BANK: list[tuple[str, str]] = [
    ("{title} 상담은 어떤 순서로 진행되나요?",
     "먼저 최근 학교 시험지와 현재 사용하는 교재를 확인하고, {local} 학생이 어느 단원에서 막히는지, 서술형과 계산 중 무엇이 더 약한지 함께 살펴봅니다. 이후 상담에서 정리한 우선순위를 바탕으로 진단과 학습계획을 안내합니다."),
    ("{district} 중학교 내신 대비는 어떻게 준비하나요?",
     "학교별 교과서와 프린트, 최근 기출 유형을 기준으로 시험 범위를 정리하고, 개념 확인과 서술형 답안 작성 연습을 함께 진행합니다. 학교마다 출제 방식이 다르기 때문에 {local} 학생이 다니는 학교의 시험 스타일을 먼저 확인합니다."),
    ("자유학기제 기간에도 수학 관리가 필요한가요?",
     "시험 부담이 적은 시기이기 때문에 오히려 기초 개념을 정리하고 스스로 계획을 세우는 습관을 만들기 좋은 시기입니다. {local} 학생의 경우 이 시기에 이전 학년 결손을 점검해 두면 다음 학기 내신 대비가 한결 수월해집니다."),
    ("중학교 첫 시험은 언제부터 준비해야 하나요?",
     "시험 직전에 몰아서 하기보다 평소 진도와 복습을 유지하다가 범위가 확정되면 집중적으로 대비하는 방식을 권장합니다. 첫 시험에서 학교 출제 스타일을 파악해 두면 다음 시험 계획을 세우기가 더 수월해집니다."),
    ("서술형 문제에서 감점이 많은 학생은 어떻게 지도하나요?",
     "정답만 맞히는 연습이 아니라 핵심 개념어와 풀이 순서, 조건을 빠짐없이 쓰는 방법을 반복해서 연습합니다. {title}에서는 채점 기준에 맞춰 실제로 쓰는 연습까지 함께 진행합니다."),
    ("수행평가 준비도 도와주시나요?",
     "학교별 수행평가 일정과 범위를 확인할 수 있는 경우, 필요한 준비 방향과 학습 방법을 함께 안내합니다. 다만 학교 공지사항은 학생과 학부모님께서 먼저 확인해 주셔야 정확한 대비가 가능합니다."),
    ("선행과 복습 중 무엇을 먼저 해야 할까요?",
     "현재 학년 개념이 충분히 이해되지 않은 상태라면 복습을 우선하고, 기초가 안정된 경우에만 다음 단원으로 단계적으로 넘어갑니다. {local} 학생의 진단 결과에 따라 우선순위를 다르게 정합니다."),
    ("오답을 반복해서 틀리는 아이는 어떻게 관리하나요?",
     "틀린 이유를 개념 부족, 계산 실수, 조건 누락, 시간 부족으로 나누어 확인하고, 같은 유형의 문제를 다시 풀어보게 하여 실제로 이해했는지 점검합니다."),
    ("성적이 오르지 않고 정체되어 있으면 어떻게 하나요?",
     "최근 시험지와 학습량을 함께 분석해 개념 이해, 문제 해석, 시간 관리 중 어디에서 정체가 생겼는지 확인한 뒤 학습 방법을 조정합니다."),
    ("중학생인데 수학을 갑자기 거부하면 어떻게 하나요?",
     "학습량이나 난이도, 성적에 대한 부담 등 원인을 먼저 확인하고, 지금 실행 가능한 작은 목표부터 다시 세워 부담을 줄이는 방향으로 접근합니다."),
    ("고등학교 진학을 앞두고 무엇을 준비해야 하나요?",
     "중학교 성적과 학습 성향을 확인하면서 고등수학에서 필요한 기초 개념과 학습 습관을 단계적으로 준비합니다. 무리한 선행보다 현재 과정의 완성도를 먼저 확인합니다."),
    ("{local}에 사는데 다니는 학교가 다른 학생들과 같은 반에서 배우나요?",
     "기본 개념은 함께 학습하되, 학교별 시험 범위와 출제 경향이 다르기 때문에 내신 대비 자료는 학교에 맞춰 구분해서 제공합니다."),
    ("플래너 관리는 중학생에게도 꼭 필요한가요?",
     "중학생은 스스로 계획을 세우는 연습이 막 시작되는 시기이기 때문에, 처음에는 구체적인 학습량을 제시하고 점차 스스로 계획을 세우도록 단계적으로 지도합니다."),
    ("숙제를 하지 않는 날이 많은 아이인데 등록해도 괜찮을까요?",
     "괜찮습니다. 미완료 원인이 분량 문제인지 습관 문제인지 먼저 확인하고, 실행 가능한 분량으로 조정하며 완료하는 습관을 함께 만들어 갑니다."),
    ("시험 기간에는 평소와 수업이 어떻게 달라지나요?",
     "학교별 시험 범위에 맞춰 개념 정리, 예상 문제, 서술형 연습과 실전 테스트 위주로 수업을 재구성합니다."),
    ("레벨테스트를 꼭 봐야 등록할 수 있나요?",
     "레벨테스트는 선발을 위한 시험이 아니라 적절한 학습계획을 세우기 위한 진단 과정입니다. 결과가 낮다고 해서 등록이 어려운 것은 아닙니다."),
    ("{local} 중학생 아이가 시험 때마다 시간이 부족하다고 하는데 어떻게 도와줄 수 있을까요?",
     "문제별 시간 배분과 풀이 순서를 정해 제한 시간 안에서 실전처럼 연습하는 훈련을 반복합니다. 쉬운 문제에서 실수하지 않도록 검산 습관도 함께 관리합니다."),
    ("학원을 옮기려고 하는데 이전 진도와 다르면 어떻게 하나요?",
     "이전 학원의 진도와 학습자료를 확인한 뒤 현재 수준에 맞는 시작 지점과 학습계획을 다시 정리해 안내합니다."),
]

ANSWER_BANK: list[tuple[str, str]] = [
    ("중학교 수학은 왜 갑자기 어려워질까요?",
     "문자와 식, 함수처럼 추상적인 개념이 한 번에 늘어나면서 초등 연산과는 접근 방식이 달라지기 때문입니다. {local} 학생 상담에서는 어느 단원부터 개념이 흔들리기 시작했는지를 먼저 확인합니다."),
    ("학원을 옮겨도 성적이 잘 오르지 않는 이유는 무엇일까요?",
     "문제 수를 늘리는 것만으로는 부족합니다. 오답의 원인을 구분하지 않고 같은 방식으로 반복하면 같은 실수가 이어질 수 있습니다."),
    ("시험 범위는 다 아는데 점수가 낮게 나온다면?",
     "이해와 실전 적용은 다른 문제일 수 있습니다. 조건을 놓치거나 시간 배분에 실패하는 경우가 많아, 실전 연습과 검산 습관을 함께 봅니다."),
    ("서술형 때문에 점수가 깎이는 게 걱정된다면?",
     "정답을 아는 것과 정확하게 서술하는 것은 다른 훈련이 필요합니다. 채점 기준에 맞춘 표현과 풀이 순서를 반복해서 연습합니다."),
    ("중학교 수학과 고등수학은 얼마나 연결되어 있나요?",
     "중학교 문자와 식, 함수, 도형 개념은 고등수학의 기초가 됩니다. 지금 흔들리는 단원을 방치하면 고등학교에서 더 크게 드러날 수 있습니다."),
    ("아이가 혼자 계획을 못 세우는데 괜찮을까요?",
     "처음부터 스스로 계획을 세우는 학생은 많지 않습니다. 구체적인 학습량을 먼저 제시하고, 익숙해지면 점차 스스로 계획을 세우도록 단계적으로 안내합니다."),
    ("학교마다 시험 범위가 달라서 걱정된다면?",
     "학교별 교과서와 출제 경향을 확인해 필요한 자료를 구분해서 준비하면, 같은 학년이라도 학교에 맞는 대비가 가능합니다."),
    ("문제집을 많이 풀어도 실력이 그대로인 것 같다면?",
     "양보다 같은 문제를 다시 맞힐 수 있는지가 더 중요합니다. 오답을 원인별로 나누고 복습 주기를 정해 반복하는 구조가 필요합니다."),
    ("갑자기 공부에 관심이 없어진 것 같다면?",
     "성적보다 원인을 먼저 봅니다. 학습량, 관계, 자신감 중 무엇이 영향을 주고 있는지 확인한 뒤 실행 가능한 목표부터 다시 세웁니다."),
    ("수학 학원을 고를 때 가장 먼저 확인해야 할 것은?",
     "수업 방식보다 지금 아이의 상태를 얼마나 구체적으로 진단하고, 그 결과를 어떻게 관리로 연결하는지를 먼저 확인하는 것이 좋습니다."),
]

CHECKLIST_BANK: list[tuple[str, str]] = [
    ("최근 시험지", "점수보다 어떤 단원에서 왜 틀렸는지를 확인하는 데 필요합니다."),
    ("현재 교재", "진도와 난이도를 확인해 바로 시작할 수 있는 지점을 잡습니다."),
    ("학교 시험 범위", "{local} 학생이 다니는 학교의 시험 범위와 수행평가 일정을 함께 확인합니다."),
    ("학습 습관", "숙제 완료율, 복습 시간, 집중이 흐트러지는 순간을 확인해 관리 강도를 정합니다."),
    ("오답노트 여부", "기존에 오답을 정리해 온 방식이 있다면 함께 확인해 이어갈 부분을 정합니다."),
    ("선행 여부", "지금 얼마나 앞서 있는지보다, 배우는 단원을 얼마나 정확히 이해했는지를 먼저 봅니다."),
    ("목표 우선순위", "성적 향상, 결손 보완, 습관 형성 중 지금 가장 필요한 부분을 정합니다."),
    ("학원 이동 이력", "이전에 다닌 학원이 있다면 진도와 학습 방식을 확인해 자연스럽게 이어갑니다."),
]

REVIEW_BANK: list[str] = [
    "처음 상담 때 아이가 어떤 단원에서 막혀 있는지 구체적으로 짚어주셔서 믿음이 갔습니다.",
    "서술형 문제에 자신 없어 하던 아이가 이제는 풀이 과정을 스스로 씁니다.",
    "오답을 그냥 넘기지 않고 원인을 나누어 설명해 주시니 같은 실수가 줄었습니다.",
    "학교 시험 범위에 맞춰 준비해 주셔서 내신 점수가 안정적으로 나오기 시작했습니다.",
    "플래너를 매일 확인해 주시니 아이가 스스로 계획을 지키려는 모습이 보입니다.",
    "숙제를 미루던 아이가 분량을 조절해 주신 뒤부터 꾸준히 해내고 있습니다.",
    "개념부터 차근차근 짚어주셔서 이전보다 문제를 이해하는 속도가 빨라졌습니다.",
    "시험 직전에 핵심 내용을 정리해 주셔서 큰 도움이 되었습니다.",
    "아이의 성향을 파악하고 눈높이에 맞춰 설명해 주시는 점이 좋았습니다.",
    "자유학기제 동안 기초를 다져주셔서 다음 학기 내신 대비가 한결 수월했습니다.",
    "중학교 첫 시험을 앞두고 무엇을 준비해야 할지 막막했는데 방향을 잡아주셨습니다.",
    "아이가 수학을 거부하던 시기에도 억지로 밀어붙이지 않고 천천히 다가가 주셨습니다.",
    "학교마다 시험 스타일이 다른데 그 부분까지 확인해서 준비해 주셨습니다.",
    "수행평가 일정까지 함께 챙겨주셔서 놓치는 부분이 줄었습니다.",
    "선생님께서 아이가 스스로 설명하게 하시니 이해도가 눈에 띄게 좋아졌습니다.",
    "성적보다 공부하는 태도가 먼저 바뀐 것 같아 만족스럽습니다.",
    "고등학교 진학을 앞두고 무리한 선행 대신 기초부터 다시 점검해 주셨습니다.",
    "상담할 때 과장 없이 현재 상태를 솔직하게 말씀해 주셔서 신뢰가 갔습니다.",
    "매번 같은 유형에서 틀리던 문제를 이제는 스스로 짚어냅니다.",
    "학원을 옮긴 뒤 적응을 걱정했는데 이전 진도를 확인하고 자연스럽게 이어주셨습니다.",
    "아이가 질문을 어려워했는데 편하게 물어볼 수 있는 분위기를 만들어 주셨습니다.",
    "시험 기간에는 평소보다 더 꼼꼼하게 챙겨주시는 게 느껴졌습니다.",
    "공부 습관이 없던 아이가 정해진 시간에 앉아서 공부하기 시작했습니다.",
    "학부모 입장에서 아이의 학습 상황을 구체적으로 전달받을 수 있어 안심이 됩니다.",
]

COMPARE_ROWS: list[dict[str, tuple[str, str]]] = [
    {"label": "교재", "A": ("학년별로 통일된 교재", "현재 단원과 오답 유형에 맞춘 교재"),
     "B": ("정해진 커리큘럼 그대로 진행", "진단 결과에 따라 시작 지점을 다르게 설정")},
    {"label": "진도", "A": ("반 전체가 같은 속도로 진행", "학생별 이해도에 맞춘 개인 진도"),
     "B": ("정해진 일정대로만 진행", "이해가 부족한 단원은 다시 짚고 넘어감")},
    {"label": "오답 관리", "A": ("틀린 문제만 다시 채점", "원인을 나누어 재학습까지 연결"),
     "B": ("답을 맞았는지만 확인", "풀이 과정과 재풀이까지 함께 점검")},
    {"label": "학부모 소통", "A": ("성적 결과만 전달", "진도, 태도, 다음 계획까지 함께 안내"),
     "B": ("정기 안내만 제공", "필요할 때마다 편하게 상담 가능")},
]

FEE_TABLE_SEOUL: list[tuple[str, str, str, str]] = [
    ("주 3회", "249,000원", "266,000원", "299,000원"),
    ("주 4회", "319,000원", "341,000원", "384,000원"),
    ("주 5회", "389,000원", "416,000원", "469,000원"),
]

FEE_TABLE_OTHER: list[tuple[str, str, str, str]] = [
    ("주 3회", "219,000원", "236,000원", "269,000원"),
    ("주 4회", "279,000원", "301,000원", "344,000원"),
    ("주 5회", "339,000원", "366,000원", "419,000원"),
]

SUMMARY_INTROS: list[str] = [
    "{local} 중학생에게 필요한 수학 관리는 단순 문제풀이보다 현재 단원, 이전 개념 결손, 학교 시험 범위, 오답 반복 이유를 함께 보는 것입니다.",
    "{local} 학생마다 막히는 지점이 다르기 때문에, 같은 학년이라도 먼저 확인해야 할 순서는 다를 수 있습니다.",
    "{local}에서 중등수학을 준비할 때는 점수 자체보다 그 점수가 나온 과정을 먼저 살펴보는 것이 방향을 잡는 데 도움이 됩니다.",
]

MANUSCRIPT_INTRO: list[str] = [
    "중학교 수학은 문자와 식, 함수, 도형처럼 추상적인 개념이 한 번에 늘어나는 시기입니다. 초등학교 때 연산 위주로 학습해 온 학생이라면 개념을 이해하는 방식 자체를 다시 익혀야 할 수 있습니다.",
    "같은 학년이라도 학교마다 시험 범위와 출제 경향이 다르기 때문에, 중등수학학원을 고를 때는 아이가 다니는 학교의 시험 스타일까지 확인해 주는 곳인지 살펴보는 것이 좋습니다.",
    "중학교 시기는 성적 관리뿐 아니라 스스로 공부하는 습관을 만드는 시작점이기도 합니다. 플래너로 계획과 실행을 확인하는 과정이 고등학교 진학 이후에도 이어질 수 있습니다.",
    "서술형 문제 비중이 늘어나면서 정답만 맞히는 것으로는 부족한 시대가 되었습니다. 풀이 과정을 정확하게 쓰는 연습이 되어 있는지가 내신 점수에 직접적인 영향을 줍니다.",
    "자유학기제처럼 시험 부담이 적은 시기를 어떻게 활용하느냐에 따라 다음 학기 성적이 크게 달라질 수 있습니다. 이 시기에 기초를 다지는 학생과 그렇지 않은 학생의 차이는 시험 범위가 확정된 뒤에 드러납니다.",
    "중학교 수학에서 흔들린 개념은 고등수학에서 더 크게 드러나는 경우가 많습니다. 지금 눈앞의 시험 점수만 보기보다, 다음 단계로 이어질 수 있는 학습 흐름을 함께 봐야 하는 이유입니다.",
]

MANUSCRIPT_OUTRO: list[str] = [
    "학원을 정할 때는 화려한 설명보다 아이의 현재 상태를 얼마나 구체적으로 봐주는지를 기준으로 삼는 것이 좋습니다.",
    "성적 향상은 결과이지 목표 그 자체는 아닙니다. 그 결과를 만드는 과정이 아이에게 맞는지를 먼저 확인해 보시길 권합니다.",
    "상담은 등록을 결정하는 자리가 아니라, 아이에게 필요한 관리 방향을 함께 찾아보는 자리로 생각해 주시면 좋겠습니다.",
    "학습관리는 한 번에 완성되지 않습니다. 상담, 진단, 실행, 재점검을 반복하며 조금씩 맞춰가는 과정이라는 점을 이해해 주시면 도움이 됩니다.",
    "무엇보다 아이가 부담 없이 질문할 수 있는 분위기인지가 꾸준한 학습으로 이어지는 데 중요한 역할을 합니다.",
    "지금 당장의 점수보다, 스스로 계획을 세우고 오답을 관리하는 습관이 만들어지고 있는지를 함께 지켜봐 주시길 바랍니다.",
]


def pick(bank: list, k: int, *seed_parts: str) -> list:
    rng = random.Random(seed_for(*seed_parts))
    if len(bank) <= k:
        items = bank[:]
        rng.shuffle(items)
        return items
    return rng.sample(bank, k)


def fmt_pair(pair: tuple[str, str], **kw) -> tuple[str, str]:
    return (pair[0].format(**kw), pair[1].format(**kw))


# ---------------------------------------------------------------------------
# row-level derived data
# ---------------------------------------------------------------------------

def school_names(row: dict[str, str]) -> list[str]:
    names: list[str] = []
    for key in ("타깃학교\n(중)", "타깃학교\n(초)", "타깃학교\n(고)"):
        names.extend(split_items(row.get(key, "")))
    seen: list[str] = []
    for name in names:
        if name not in seen:
            seen.append(name)
    return seen


def local_page(row: dict[str, str], idx: int, rep_image: str, all_rows: list[dict[str, str]]) -> str:
    local = row["근처 수업가능 동네"].strip()
    slug = slug_ko(local)
    region = row.get("지역", "").strip()
    district = row.get("시or구", "").strip()
    center = row.get("센터명", "").strip() or f"{local} 학습관리"
    address = row.get("센터 주소", "").strip()
    title = f"{local} 중등수학학원"
    description = f"{region} {district} {local} 중학생을 위한 중등수학학원 안내입니다. 학교 내신 범위, 서술형 대비, 오답 재학습, 플래너 실행 기준을 상담 전에 확인할 수 있습니다."
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
    grade_math = row.get("가능학년\n(수학)", "").strip()

    fee_link = row.get("센터 교습비", "").strip()
    reg_no = row.get("교육지원청 등록번호", "").strip()
    education_name = row.get("교육지원청명칭", "").strip()

    opener = fmt_pair(pick(FAQ_OPENER_BANK, 1, local, "faq-opener")[0],
                       local=local, district=district, title=title, region=region)
    faqs = [opener] + [fmt_pair(p, local=local, district=district, title=title, region=region)
                        for p in pick(FAQ_BANK, 5, local, "faq")]
    answers = [fmt_pair(p, local=local, district=district, title=title, region=region)
               for p in pick(ANSWER_BANK, 4, local, "answer")]
    checklist = [fmt_pair(p, local=local, district=district, title=title, region=region)
                 for p in pick(CHECKLIST_BANK, 4, local, "checklist")]
    review_lines = pick(REVIEW_BANK, 6, local, "review")
    summary_intro = pick(SUMMARY_INTROS, 1, local, "summary")[0].format(local=local)
    manu_intro = pick(MANUSCRIPT_INTRO, 1, local, "manu-intro")[0]
    manu_outro = pick(MANUSCRIPT_OUTRO, 1, local, "manu-outro")[0]
    location_ref = address if address else "상담 시 안내되는 위치"
    variant = "A" if seed_for(local, "compare") % 2 == 0 else "B"

    rng = random.Random(seed_for(local, "review-rating"))
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
        {"@type": "Thing", "name": "중등수학학원"},
        {"@type": "Thing", "name": "중학교 내신 대비"},
        {"@type": "Thing", "name": "서술형 답안 관리"},
        {"@type": "Thing", "name": "수학 오답 재학습"},
        {"@type": "Thing", "name": "플래너 관리"},
    ]
    mentions = [
        {"@type": "Place", "name": region},
        {"@type": "Place", "name": district},
        {"@type": "EducationalOrganization", "name": center},
    ] + [{"@type": school_type(s), "name": s} for s in schools]
    has_part = [
        "핵심 요약", "학원 선택 가이드", "답변형 중등수학 안내", "지역·학년·추천학생",
        "일반 학원과의 차이", "센터 기준 정보", "학습료 안내", "상담 전 체크리스트", "FAQ", "학부모 후기", "내부링크",
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
                "alternateName": [SITE_NAME, center, f"{local} 중등수학 학습관리"],
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
                "knowsAbout": ["중등수학", "중학교 내신 대비", "서술형 답안 작성", "오답 재학습", "플래너 관리", "중학생 학습 상담"],
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 중등수학 진단 상담", "serviceType": "TutoringService"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 중학교 내신 서술형 대비", "serviceType": "TutoringService"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 수학 오답 재학습 관리", "serviceType": "TutoringService"}},
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
                "description": f"{local} 중학생의 수학 개념, 서술형 답안, 학교별 내신 시험범위, 오답 재학습을 함께 관리합니다.",
                "provider": {"@id": org_id},
                "areaServed": {"@type": "Place", "name": local},
                "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
                "about": about,
                "mentions": mentions,
                "makesOffer": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 중등수학 개념 진단"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 중학교 내신 서술형 플래너"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{local} 수학 오답 원인 분석"}},
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
                "name": f"{local} 중등수학학원 관련 내부링크",
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

    # ---- render sections -------------------------------------------------
    badge_row = f'<div class="badge-row"><span>{esc(region)}</span><span>{esc(district)}</span><span>중등수학</span><span>내신·서술형·오답관리</span></div>'

    media_section = f"""    <section class="section">
      <img src="{esc(rep_rel)}" alt="{esc(title + ' ' + SITE_NAME + ' 대표')}" style="display:none;">
      <div class="media-row">
        <figure class="frame"><img src="{esc(center_rel)}" alt="{esc(title + ' 본문 ' + SITE_NAME)}"></figure>
        <figure class="frame"><img src="{esc(map_rel)}" alt="{esc(title + ' 지도 ' + SITE_NAME)}"></figure>
      </div>
      <p class="lead">{esc(center)} 기준으로 {esc(local)} 학생의 중등수학 상담 범위를 확인합니다. 실제 방문·상담 전에는 주소와 이동 동선을 함께 확인해 주세요.</p>
    </section>"""

    summary_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">핵심 요약</p>
        <h2>{esc(local)} 중등수학학원 선택 전 확인할 기준</h2>
        <p class="lead">{esc(summary_intro)}</p>
      </div>
      <div class="card-grid">
        <article class="info-card"><span class="tag">01</span><h3>개념 연결</h3><p>문자와 식, 함수, 도형처럼 단원 간 연결이 강한 내용은 이전 학년 개념까지 함께 확인합니다.</p></article>
        <article class="info-card"><span class="tag">02</span><h3>내신 범위</h3><p>{esc(district)} 학교별 시험 범위와 프린트, 수행평가 일정을 상담 시 함께 확인합니다.</p></article>
        <article class="info-card"><span class="tag">03</span><h3>서술형·오답</h3><p>정답 여부만이 아니라 풀이 과정과 서술형 표현, 오답 원인을 함께 봅니다.</p></article>
      </div>
    </section>"""

    manuscript_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">학원 선택 가이드</p>
        <h2>{esc(local)} 중등수학학원, 무엇을 기준으로 볼까요</h2>
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

    grade_text = grade_math if grade_math else "상담 시 학년별 가능 여부를 확인합니다."
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
        <article class="info-card"><span class="tag">지역</span><h3>{esc(region)} {esc(district)} {esc(local)}</h3><p>{esc(local)} 생활권 학생의 학교 진도와 시험 일정에 맞춰 중등수학 관리 방향을 상담합니다.</p></article>
        <article class="info-card"><span class="tag">학년</span><h3>중1~중3, 가능학년 {esc(grade_text)}</h3><p>학년별로 필요한 관리가 다르기 때문에 자유학기제, 첫 내신, 고입 대비 시기를 나누어 봅니다.</p></article>
        <article class="info-card"><span class="tag">추천</span><h3>이런 학생에게 추천</h3><p>내신 서술형이 약한 학생, 오답을 반복하는 학생, 혼자 계획을 지키기 어려운 학생에게 적합합니다.</p></article>
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
        <h2>{esc(local)} 중등수학, 무엇이 다른가요</h2>
        <p class="lead">일반적인 학원 운영 방식과 {esc(SITE_NAME)}의 중등수학 관리 방식을 같은 기준으로 비교했습니다.</p>
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
        <h2>{esc(local)} 중등수학학원 학습료 안내</h2>
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
        <h2>{esc(local)} 중등수학 상담 후기</h2>
      </div>
      <div class="review-grid">
        {review_html}
      </div>
    </section>"""

    related_html = "\n".join(
        f'<a href="{esc(url)}"><strong>{esc(name)} 중등수학학원</strong><small>{esc(area)} 지역 페이지</small></a>'
        for name, url, area in related
    )
    other_category = "중등영어학원"
    other_link_html = ""
    if (SITE / "전국학원" / other_category / slug).exists():
        other_link_html = f'<a href="/전국학원/{other_category}/{slug}/" class="cross-link"><strong>{esc(local)} {esc(other_category)}</strong><small>같은 지역 다른 과목 바로가기</small></a>'

    link_section = f"""    <section class="section">
      <div class="section-head">
        <p class="eyebrow">근처 학원페이지</p>
        <h2>{esc(local)} 주변 중등수학학원 페이지</h2>
        <p class="lead">같은 지역의 다른 과목과, 가까운 지역 페이지로 이동할 수 있도록 정리했습니다.</p>
      </div>
      <div class="link-grid">
        {other_link_html}
        <a href="../index.html"><strong>중등수학학원 전체</strong><small>카테고리 허브</small></a>
        <a href="../../index.html"><strong>전국학원</strong><small>전체 허브</small></a>
        {related_html}
      </div>
    </section>"""

    body = f"""{nav_html(3)}

  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../../index.html">홈</a><span>/</span><a href="../../index.html">전국학원</a><span>/</span><a href="../index.html">{esc(CATEGORY)}</a><span>/</span><span>{esc(local)}</span></p>
      <p class="eyebrow">MIDDLE SCHOOL MATH COACHING</p>
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
# hub pages
# ---------------------------------------------------------------------------

ALL_CATEGORIES: list[tuple[str, str]] = [
    ("중등수학학원", "중등수학 내신·서술형·오답관리 지역별 안내"),
    ("중등영어학원", "중등영어 어휘·문법·독해·내신 지역별 안내"),
]


def region_blocks_html(rows: list[dict[str, str]], subject_label: str) -> str:
    regions: dict[str, dict[str, list[dict[str, str]]]] = {}
    for row in rows:
        region = row.get("지역", "").strip() or "기타"
        district = row.get("시or구", "").strip() or "기타"
        regions.setdefault(region, {}).setdefault(district, []).append(row)

    blocks = []
    for region, districts in regions.items():
        total = sum(len(items) for items in districts.values())
        district_blocks = []
        for district, items in districts.items():
            links = "\n".join(
                f'<a href="{slug_ko(r["근처 수업가능 동네"])}/">{esc(r["근처 수업가능 동네"])}</a>'
                for r in items
            )
            district_blocks.append(
                f'<div class="district-block"><p class="district-title">{esc(district)}<small>{len(items)}곳</small></p>'
                f'<div class="local-button-grid">{links}</div></div>'
            )
        blocks.append(
            f'<div class="region-block"><div class="region-title"><h3>{esc(region)}</h3>'
            f'<span>{len(districts)}개 시군구 · {total}개 지역</span></div>{"".join(district_blocks)}</div>'
        )
    return "".join(blocks)


def hub_pages(rows: list[dict[str, str]]) -> None:
    rep = "/assets/generated/academy-hero-v2.png"
    existing = [(name, desc) for name, desc in ALL_CATEGORIES if (SITE / "전국학원" / name).exists() or name == CATEGORY]
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
        <p class="lead">예: 전국학원 / 중등수학학원 / 명일동</p>
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

    region_blocks = region_blocks_html(rows, "중등수학")
    ld_cat = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": f"/전국학원/{CATEGORY}/#webpage", "url": f"/전국학원/{CATEGORY}/", "name": CATEGORY, "description": "중등수학학원 지역별 안내 허브입니다.", "inLanguage": "ko-KR"},
            {"@type": "BreadcrumbList", "@id": f"/전국학원/{CATEGORY}/#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "홈", "item": "/"}, {"@type": "ListItem", "position": 2, "name": "전국학원", "item": "/전국학원/"}, {"@type": "ListItem", "position": 3, "name": CATEGORY, "item": f"/전국학원/{CATEGORY}/"}]},
            {"@type": "ItemList", "@id": f"/전국학원/{CATEGORY}/#itemlist", "name": "중등수학학원 지역 목록", "numberOfItems": len(rows), "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": f"{r['근처 수업가능 동네']} 중등수학학원", "url": f"/전국학원/{CATEGORY}/{slug_ko(r['근처 수업가능 동네'])}/"} for i, r in enumerate(rows)]},
        ],
    }
    head = head_html(f"{CATEGORY} | {SITE_NAME}", f"전국 {len(rows)}개 지역의 중등수학학원 학습관리 페이지를 지역별로 정리한 허브입니다.", 2, f"/전국학원/{CATEGORY}/", "website", rep, ld_cat)
    body = f"""{nav_html(2)}
  <main>
    <section class="page-hero">
      <p class="breadcrumb"><a href="../../index.html">홈</a><span>/</span><a href="../index.html">전국학원</a><span>/</span><span>{esc(CATEGORY)}</span></p>
      <p class="eyebrow">MIDDLE SCHOOL MATH DIRECTORY</p>
      <h1>{esc(CATEGORY)}</h1>
      <p class="lead">지역별 중등수학 상담 기준을 한눈에 찾을 수 있도록 정리했습니다. 각 페이지에는 지역·학년·추천학생, 학교 참고 정보, FAQ, 학부모 후기, 내부링크가 함께 구성됩니다.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{PHONE_DISPLAY}">전화 상담하기</a>
        <a class="btn btn-ghost" href="../../상담문의/index.html">상담문의</a>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">ABOUT US</p>
        <h2>{esc(SITE_NAME)}는 중등수학을 이렇게 관리해요</h2>
        <p class="lead">문제를 많이 풀리는 것보다, 지금 이 학생에게 필요한 순서를 먼저 찾는 것을 중요하게 생각합니다. 상담에서 시작해 진단, 플래너, 오답 재학습까지 하나의 흐름으로 이어갑니다.</p>
      </div>
      <div class="timeline">
        <article class="timeline-item">
          <div class="timeline-num">01</div>
          <div class="timeline-body"><h3>상담</h3><p>학교, 최근 성적, 현재 학습 습관을 먼저 듣고 우선순위를 함께 정합니다.</p></div>
        </article>
        <article class="timeline-item">
          <div class="timeline-num">02</div>
          <div class="timeline-body"><h3>진단</h3><p>개념 부족인지, 계산 실수인지, 문제 해석의 문제인지 원인을 나누어 확인합니다.</p></div>
        </article>
        <article class="timeline-item">
          <div class="timeline-num">03</div>
          <div class="timeline-body"><h3>플래너 관리</h3><p>학습량과 실행 결과를 기록하며 계획과 실제 공부 사이의 간격을 줄여갑니다.</p></div>
        </article>
        <article class="timeline-item">
          <div class="timeline-num">04</div>
          <div class="timeline-body"><h3>오답 재학습</h3><p>틀린 이유를 분류하고 비슷한 유형을 다시 풀어보며 반복되는 실수를 줄입니다.</p></div>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <p class="eyebrow">총 지역</p>
        <h2>{len(rows)}개 지역</h2>
        <p class="lead">서울부터 지방까지 지역명 기준으로 중등수학학원 페이지를 생성했습니다.</p>
      </div>
      {region_blocks}
    </section>
  </main>
{footer_html(2)}"""
    out = SITE / "전국학원" / CATEGORY / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_shell(head, body), encoding="utf-8")


def main() -> None:
    rows = read_csv(COMMON / "센터정보 정리.csv")
    reps = choose_rep_images(rows)
    hub_pages(rows)
    for idx, row in enumerate(rows):
        slug = slug_ko(row["근처 수업가능 동네"])
        out = SITE / "전국학원" / CATEGORY / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(local_page(row, idx, reps[idx], rows), encoding="utf-8")
    print(f"generated category={CATEGORY} local_pages={len(rows)}")


if __name__ == "__main__":
    main()
