from __future__ import annotations

from _common import processed_dir, write_jsonl
from _rag_corpus import (
    PLASTIC_DOMAIN_NAME,
    SKIN_DOMAIN_NAME,
    build_diff_rows,
    default_label_root,
    default_source_root,
)


def main() -> None:
    rows = []
    rows.extend(build_diff_rows(default_label_root(), default_source_root(), SKIN_DOMAIN_NAME, "dermatology"))
    rows.extend(build_diff_rows(default_label_root(), default_source_root(), PLASTIC_DOMAIN_NAME, "plastic_reconstruction"))
    out = processed_dir() / "rag_label_source_diff_report.jsonl"
    write_jsonl(out, rows)
    print(f"wrote {out} with {len(rows)} rows")


if __name__ == "__main__":
    main()
