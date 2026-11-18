"""Milestone 1: download public-domain short-story collections and build data/<genre>/{train,val}.txt.

    python scripts/prepare_data.py            # downloads into data/raw/ (cached), writes the splits

Uses the Project Gutenberg mirror at gutenberg.pglaf.org (the main site may be under maintenance).
Sources and licences: DATA.md.
"""
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core import clean_text, data_dir, tokenize_corpus, train_val_split, write_sentences  # noqa: E402

MIRROR = "https://gutenberg.pglaf.org"
BOOKS = {  # genre -> [(Gutenberg id, title)]
    "mystery": [(1661, "The Adventures of Sherlock Holmes"), (834, "The Memoirs of Sherlock Holmes"),
                (204, "The Innocence of Father Brown")],
    "horror": [(2147, "The Works of Edgar Allan Poe, Volume 1"), (2148, "The Works of Edgar Allan Poe, Volume 2"),
               (8486, "Ghost Stories of an Antiquary")],
    "scifi": [(11870, "The Country of the Blind, and Other Stories"), (27365, "Tales of Space and Time")],
}


def book_url(book_id: int, suffix: str) -> str:
    digits = str(book_id)
    path = "/".join(digits[:-1]) if len(digits) > 1 else "0"
    return f"{MIRROR}/{path}/{book_id}/{book_id}{suffix}.txt"


def download(book_id: int, raw_dir: Path) -> str:
    cached = raw_dir / f"{book_id}.txt"
    if cached.exists():
        return cached.read_text(encoding="utf-8")
    for suffix, enc in (("-0", "utf-8"), ("", "utf-8"), ("-8", "latin-1")):
        req = urllib.request.Request(book_url(book_id, suffix), headers={"User-Agent": "cwp-prepare-data/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                text = r.read().decode(enc, errors="replace")
        except OSError:
            continue
        raw_dir.mkdir(parents=True, exist_ok=True)
        cached.write_text(text, encoding="utf-8")
        return text
    raise SystemExit(f"Could not download Gutenberg book {book_id} from {MIRROR}")


def main() -> None:
    root = data_dir()
    print(f"{'genre':8} {'book':>6} {'sentences':>9} {'tokens':>8}  title [found in file?]")
    for genre, books in BOOKS.items():
        sents = []
        for book_id, title in books:
            raw = download(book_id, root / "raw")
            found = title.split(",")[0].lower() in raw[:3000].lower()   # sanity check: right book?
            book_sents = tokenize_corpus(clean_text(raw))
            sents += book_sents
            print(f"{genre:8} {book_id:>6} {len(book_sents):>9} {sum(map(len, book_sents)):>8}  "
                  f"{title} [{'title ok' if found else 'TITLE NOT FOUND'}]")
        train, val = train_val_split(sents, val_frac=0.1, seed=0)
        write_sentences(root / genre / "train.txt", train)
        write_sentences(root / genre / "val.txt", val)
        print(f"{genre:8} {'TOTAL':>6} train={len(train)} val={len(val)} sents, "
              f"{sum(map(len, train))} train tokens, vocab={len({t for s in train for t in s})}")


if __name__ == "__main__":
    main()
