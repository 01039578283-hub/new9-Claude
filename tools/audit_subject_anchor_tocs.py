#!/usr/bin/env python3
"""Audit the subject-page TOC rollout and prove unrelated HTML is unchanged."""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from add_subject_anchor_tocs import (
    DETAIL_STYLESHEET_VERSION,
    KNOWN_TARGET_IDS,
    ROOT,
    TOC_REMOVE_RE,
    detail_pages,
    target_headings,
    validate_page,
)


def tracked_blob_ids() -> dict[str, str]:
    output = subprocess.check_output(
        ["git", "ls-tree", "-r", "-z", "HEAD", "--", "과목별학원"], cwd=ROOT
    )
    result: dict[str, str] = {}
    for record in output.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        _mode, object_type, blob_id = metadata.decode("ascii").split()
        if object_type != "blob":
            continue
        result[raw_path.decode("utf-8")] = blob_id
    return result


def baseline_blobs(blob_ids: list[str]) -> list[bytes]:
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    blobs: list[bytes] = []
    try:
        for blob_id in blob_ids:
            process.stdin.write(blob_id.encode("ascii") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().decode("ascii").strip().split()
            if len(header) != 3 or header[1] != "blob":
                raise RuntimeError(f"Unexpected git cat-file header: {header}")
            size = int(header[2])
            blobs.append(process.stdout.read(size))
            if process.stdout.read(1) != b"\n":
                raise RuntimeError("Missing git cat-file record separator")
    finally:
        process.stdin.close()
        process.wait(timeout=30)
    return blobs


def normalize_newlines(source: str) -> str:
    return source.replace("\r\n", "\n").replace("\r", "\n")


def remove_rollout_changes(source: str) -> str:
    source = normalize_newlines(source)
    source = TOC_REMOVE_RE.sub("", source, count=1)
    source = source.replace('<body class="subject-detail-page">', "<body>")
    source = source.replace(
        f"assets/site.css?v={DETAIL_STYLESHEET_VERSION}", "assets/site.css"
    )
    source = re.sub(
        r'\s+style="aspect-ratio: \d+ / \d+;"(?=>)',
        "",
        source,
        flags=re.IGNORECASE,
    )
    target_pattern = "|".join(re.escape(target_id) for target_id in KNOWN_TARGET_IDS)
    source = re.sub(
        rf'(<(?:section|article)\b[^>]*?)\s+id="(?:{target_pattern})"(?=[^>]*>)',
        r"\1",
        source,
        flags=re.IGNORECASE,
    )
    return source


def unchanged_hubs(blob_map: dict[str, str]) -> list[str]:
    failures: list[str] = []
    hubs = [ROOT / "과목별학원" / "index.html"] + sorted(
        (ROOT / "과목별학원").glob("*/index.html")
    )
    ids = []
    paths = []
    for hub in hubs:
        rel = hub.relative_to(ROOT).as_posix()
        if rel not in blob_map:
            failures.append(f"Untracked or missing hub baseline: {rel}")
            continue
        paths.append(hub)
        ids.append(blob_map[rel])
    for hub, baseline in zip(paths, baseline_blobs(ids)):
        if normalize_newlines(hub.read_text(encoding="utf-8")) != normalize_newlines(
            baseline.decode("utf-8")
        ):
            failures.append(f"Hub changed: {hub.relative_to(ROOT)}")
    return failures


def main() -> int:
    pages, category_counts = detail_pages()
    blob_map = tracked_blob_ids()
    failures: list[str] = []
    failures.extend(unchanged_hubs(blob_map))

    relative_paths = [path.relative_to(ROOT).as_posix() for path in pages]
    missing_baselines = [path for path in relative_paths if path not in blob_map]
    if missing_baselines:
        failures.extend(f"Missing baseline: {path}" for path in missing_baselines[:20])
        print(f"failures={len(failures)}", file=sys.stderr)
        return 1

    baselines = baseline_blobs([blob_map[path] for path in relative_paths])
    link_distribution: Counter[int] = Counter()
    total_links = 0
    for path, relative_path, baseline in zip(pages, relative_paths, baselines):
        current = path.read_text(encoding="utf-8")
        errors = validate_page(normalize_newlines(current))
        if errors:
            failures.append(f"{relative_path}: {'; '.join(errors)}")
            continue
        headings = target_headings(normalize_newlines(current))
        link_distribution[len(headings)] += 1
        total_links += len(headings)
        original = normalize_newlines(baseline.decode("utf-8"))
        comparable = (
            normalize_newlines(current)
            if "subject-page-anchor-toc:start" in original
            else remove_rollout_changes(current)
        )
        if comparable != original:
            failures.append(f"Unrelated HTML changed: {relative_path}")

    expected_counts = {category: 371 for category in category_counts}
    if category_counts != expected_counts:
        failures.append(f"Unexpected category counts: {category_counts}")
    if link_distribution != Counter({11: 1195, 12: 5483}):
        failures.append(f"Unexpected TOC distribution: {dict(link_distribution)}")
    if total_links != 78_941:
        failures.append(f"Unexpected total TOC links: {total_links}")

    print(f"detail_pages={len(pages)} category_hubs=18 parent_hubs=1")
    print(
        "toc_link_distribution="
        + ",".join(f"{count}:{total}" for count, total in sorted(link_distribution.items()))
    )
    print(f"total_toc_links={total_links}")
    print(f"unrelated_html_differences={sum('Unrelated HTML changed' in item for item in failures)}")
    print(f"failures={len(failures)}")
    if failures:
        for failure in failures[:50]:
            print(failure, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
