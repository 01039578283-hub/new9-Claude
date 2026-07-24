from __future__ import annotations

import html
import json
import re
from pathlib import Path

from PIL import Image


SITE = Path(__file__).resolve().parents[1]
def clean_schema(value: object) -> object:
    if isinstance(value, dict):
        cleaned: dict[str, object] = {}
        for key, item in value.items():
            if key in {
                "openingHours",
                "openingHoursSpecification",
                "aggregateRating",
                "review",
            }:
                continue
            cleaned[key] = clean_schema(item)
        node_type = cleaned.get("@type")
        if (
            isinstance(node_type, list)
            and "LocalBusiness" in node_type
            and "address" not in cleaned
        ):
            cleaned["@type"] = [
                item for item in node_type if item != "LocalBusiness"
            ]
        return cleaned
    if isinstance(value, list):
        return [clean_schema(item) for item in value]
    if isinstance(value, str):
        if value == "후기":
            return "학습 상담 사례"
        return (
            value.replace("학부모 후기", "학습 상담 사례")
            .replace("PARENT REVIEW", "CONSULTATION CASES")
        )
    return value


def plain_text(fragment: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()


def visible_faqs(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(
        r'<details\b[^>]*class=["\'][^"\']*\bfaq-item\b[^"\']*["\'][^>]*>'
        r'.*?<summary>(.*?)</summary>\s*<p>(.*?)</p>.*?</details>',
        re.DOTALL | re.IGNORECASE,
    )
    return [(plain_text(question), plain_text(answer)) for question, answer in pattern.findall(text)]


def sync_faq_schema(value: object, faqs: list[tuple[str, str]]) -> None:
    if isinstance(value, dict):
        node_type = value.get("@type")
        types = node_type if isinstance(node_type, list) else [node_type]
        if "FAQPage" in types and faqs:
            value["mainEntity"] = [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in faqs
            ]
        for item in value.values():
            sync_faq_schema(item, faqs)
    elif isinstance(value, list):
        for item in value:
            sync_faq_schema(item, faqs)


def update_schema_scripts(text: str) -> str:
    faqs = visible_faqs(text)
    pattern = re.compile(
        r'(<script\s+type="application/ld\+json">)(.*?)(</script>)',
        re.DOTALL | re.IGNORECASE,
    )

    def replace(match: re.Match[str]) -> str:
        try:
            data = json.loads(html.unescape(match.group(2)))
        except json.JSONDecodeError:
            return match.group(0)
        cleaned = clean_schema(data)
        sync_faq_schema(cleaned, faqs)
        payload = json.dumps(cleaned, ensure_ascii=False, separators=(",", ":"))
        return f"{match.group(1)}{payload}{match.group(3)}"

    return pattern.sub(replace, text)


def local_image_path(page: Path, src: str) -> Path | None:
    clean = src.split("?", 1)[0].split("#", 1)[0]
    if clean.startswith(("http://", "https://", "data:", "//")):
        return None
    if clean.startswith("/"):
        target = SITE / clean.lstrip("/")
    else:
        target = page.parent / clean
    try:
        target = target.resolve()
        target.relative_to(SITE.resolve())
    except (OSError, ValueError):
        return None
    return target if target.is_file() else None


def update_images(page: Path, text: str) -> str:
    # Hidden representative images duplicate og:image/JSON-LD and still consume
    # browser bandwidth. The metadata references are retained.
    text = re.sub(
        r'\s*<img\b(?=[^>]*style=["\'][^"\']*display\s*:\s*none)[^>]*>\s*',
        "\n",
        text,
        flags=re.IGNORECASE,
    )
    pattern = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    visible_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal visible_index
        tag = match.group(0)
        src_match = re.search(r'\bsrc=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if not src_match:
            return tag
        source = html.unescape(src_match.group(1))
        target = local_image_path(page, source)
        if target and not re.search(r"\bwidth=", tag, re.IGNORECASE):
            try:
                with Image.open(target) as image:
                    width, height = image.size
                tag = tag[:-1] + f' width="{width}" height="{height}">'
            except OSError:
                pass
        if not re.search(r"\bdecoding=", tag, re.IGNORECASE):
            tag = tag[:-1] + ' decoding="async">'
        if not re.search(r"\b(?:loading|fetchpriority)=", tag, re.IGNORECASE):
            if visible_index == 0:
                tag = tag[:-1] + ' fetchpriority="high">'
            else:
                tag = tag[:-1] + ' loading="lazy">'
        visible_index += 1
        return tag

    return pattern.sub(replace, text)


def process(page: Path) -> bool:
    original = page.read_text(encoding="utf-8")
    text = (
        original.replace(
            "/assets/generated/academy-consultation-v2.png",
            "/assets/generated/academy-consultation-og.jpg",
        )
        .replace(
            "/assets/generated/academy-hero-v2.png",
            "/assets/generated/academy-og.jpg",
        )
    )
    text = re.sub(
        r'\s*<link\s+rel="preconnect"\s+href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>\s*',
        "\n",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'\s*<link\s+href="https://fonts\.googleapis\.com/css2\?[^"]+"\s+rel="stylesheet">\s*',
        "\n",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<a class="active"(?![^>]*aria-current)',
        '<a class="active" aria-current="page"',
        text,
    )
    text = update_schema_scripts(text)
    text = update_images(page, text)
    if text == original:
        return False
    page.write_text(text, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    changed = sum(process(page) for page in SITE.rglob("index.html"))
    print(f"postprocessed_html={changed}")


if __name__ == "__main__":
    main()
