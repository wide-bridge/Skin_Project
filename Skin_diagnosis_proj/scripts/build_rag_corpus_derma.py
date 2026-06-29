from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from _common import PROCESSED_DIR, write_jsonl


def main() -> None:
    rows = [
        {
            "doc_id": "derma-placeholder-001",
            "title": "여드름 기본 안내",
            "category": "skin_disease",
            "content": "여드름은 면포, 붉은 구진, 농포 형태로 나타날 수 있으며 과도한 자극은 악화 요인이 될 수 있습니다.",
            "source": "placeholder",
        }
    ]
    write_jsonl(PROCESSED_DIR / "rag_corpus_derma.jsonl", rows)
    print(f"wrote {PROCESSED_DIR / 'rag_corpus_derma.jsonl'}")


if __name__ == "__main__":
    main()
