from __future__ import annotations

from pathlib import Path

import generate_grade1_math_pages as generator


generator.CATEGORY = "고1영어학원"
generator.SUBJECT_LABEL = "고1 영어"
generator.SUBJECT = "영어"
generator.SUBJECT_EN = "ENGLISH"
generator.FOCUS_LABEL = "내신·어휘·문법·독해"
generator.ZIP_PATH = (
    Path.home()
    / "Desktop"
    / "스터디와와.com 추가 원고"
    / "고1 영어학원.zip"
)


if __name__ == "__main__":
    generator.main()
