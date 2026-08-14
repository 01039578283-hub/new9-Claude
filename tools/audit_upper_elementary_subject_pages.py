"""Strict audit for the upper-elementary subject-page delivery batch.

This module deliberately reuses the DOM, schema, source-rewrite, image, link,
and similarity validators from ``audit_grade3_elementary_subject_pages``.  It
only replaces the delivery contract: the five new categories below, their
source workbooks, and the complete 18-card parent hub inventory.

It is safe to run before generation.  Missing hubs/details are reported as
ordinary audit failures rather than causing the audit itself to crash.
"""

from __future__ import annotations

import sys

import audit_grade3_elementary_subject_pages as base


CATEGORIES = (
    base.Category("초4영어학원", "초", 4, "영어", "초4 영어학원 원고.xlsx"),
    base.Category("초5수학학원", "초", 5, "수학", "초5 수학학원 원고.xlsx"),
    base.Category("초5영어학원", "초", 5, "영어", "초5 영어학원 원고.xlsx"),
    base.Category("초6수학학원", "초", 6, "수학", "초6 수학학원 원고.xlsx"),
    base.Category("초6영어학원", "초", 6, "영어", "초6 영어학원 원고.xlsx"),
)

# This is the full parent-hub contract after this batch, not merely the five
# categories audited in detail by this file.
ALL_SUBJECT_CATEGORIES = (
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
    *(category.slug for category in CATEGORIES),
)

EXPECTED_HUBS = 5
EXPECTED_DETAILS = EXPECTED_HUBS * base.EXPECTED_LOCALS
EXPECTED_BATCH_URLS = EXPECTED_HUBS * (base.EXPECTED_LOCALS + 1)

# Derived from the current common CSV using the same split_grade_items logic
# as the page-level audit: 초4영 32 + 초5수 19 + 초5영 14 + 초6수 13 + 초6영 8.
EXPECTED_CONSULTATION_BRANCHES = 86
EXPECTED_LISTED_BRANCHES = EXPECTED_DETAILS - EXPECTED_CONSULTATION_BRANCHES


class UpperElementaryAudit(base.Audit):
    """Adds batch-level count assertions to the inherited page audit."""

    def finish(self, similarity: base.SimilarityResult | None = None) -> int:
        count_contracts = {
            "category_hubs": EXPECTED_HUBS,
            "detail_pages": EXPECTED_DETAILS,
            "source_documents": EXPECTED_DETAILS,
            "sitemap_urls": EXPECTED_BATCH_URLS,
            "support_consultation_branch": EXPECTED_CONSULTATION_BRANCHES,
            "support_listed": EXPECTED_LISTED_BRANCHES,
        }
        for check, expected in count_contracts.items():
            actual = self.checks[check]
            if actual != expected:
                self.fail(
                    f"batch_{check}_contract",
                    "batch",
                    f"actual={actual} expected={expected}",
                )

        print("=== 초4 영어·초5/6 수학·영어 신규 5카테고리 엄격 감사 ===")
        print("checks " + " ".join(
            f"{key}={self.checks[key]}" for key in sorted(self.checks)
        ))
        if similarity is not None:
            print(
                "similarity "
                f"documents={similarity.documents} candidates={similarity.candidates} "
                f"max={similarity.maximum:.4f} limit<{base.SIMILARITY_LIMIT:.2f}"
            )
            if similarity.maximum_pair:
                print(f"similarity_max_pair={' <> '.join(similarity.maximum_pair)}")
        if self.failures:
            print("AUDIT_FAILED " + " ".join(
                f"{code}={self.failures[code]}" for code in sorted(self.failures)
            ))
            for code in sorted(self.failures):
                print(f"\n[{code}] examples")
                for example in self.examples[code]:
                    print(f"- {example}")
            return 1
        print("AUDIT_OK failures=0")
        return 0


def configure_base_audit() -> None:
    if len(CATEGORIES) != EXPECTED_HUBS:
        raise RuntimeError(f"category contract drift: {len(CATEGORIES)} != {EXPECTED_HUBS}")
    if len(ALL_SUBJECT_CATEGORIES) != 18:
        raise RuntimeError(
            f"parent category contract drift: {len(ALL_SUBJECT_CATEGORIES)} != 18"
        )
    if len(set(ALL_SUBJECT_CATEGORIES)) != len(ALL_SUBJECT_CATEGORIES):
        raise RuntimeError("parent category contract contains duplicate slugs")

    base.CATEGORIES = CATEGORIES
    base.ALL_SUBJECT_CATEGORIES = ALL_SUBJECT_CATEGORIES
    base.Audit = UpperElementaryAudit


def main() -> int:
    configure_base_audit()
    return base.main()


if __name__ == "__main__":
    sys.exit(main())
