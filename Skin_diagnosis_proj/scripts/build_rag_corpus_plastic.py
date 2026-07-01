from __future__ import annotations

from _common import processed_dir
from _rag_corpus import PLASTIC_DOMAIN_NAME, build_corpus_rows, default_label_root, write_corpus


def main() -> None:
    rows = build_corpus_rows(default_label_root(), PLASTIC_DOMAIN_NAME, "plastic_reconstruction")
    out = processed_dir() / "rag_corpus_plastic.jsonl"
    write_corpus(out, rows)
    print(f"wrote {out} with {len(rows)} rows")


if __name__ == "__main__":
    main()
