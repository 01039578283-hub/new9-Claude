from __future__ import annotations

from pathlib import Path

import generate_grade1_math_pages as generator


generator.CATEGORY = "고2수학학원"
generator.SUBJECT_LABEL = "고2 수학"
generator.SUBJECT = "수학"
generator.SUBJECT_EN = "MATH"
generator.FOCUS_LABEL = "내신·취약단원·오답관리"
generator.GRADE_NUMBER = 2
generator.GRADE_EN = "GRADE 11"
generator.ZIP_PATH = (
    Path.home()
    / "Desktop"
    / "스터디와와.com 추가 원고"
    / "고2 수학학원.zip"
)

import validate_grade1_math_pages as validator


if __name__ == "__main__":
    validator.main()
