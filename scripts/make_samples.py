"""Milestone 4: sample continuations per genre at a few temperatures -> results/samples.md.

    python scripts/make_samples.py   # needs data/ from scripts/prepare_data.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.core import BEST_K, NgramModel, data_dir, read_sentences  # noqa: E402

PROMPTS = {
    "mystery": ["The detective opened the", "It was a dark", "Holmes looked at the"],
    "horror": ["I heard a sound in the", "The corpse", "At midnight the"],
    "scifi": ["The machine", "We looked up at the stars and", "The Martians"],
}
TEMPS, SEED, WORDS = (0.5, 1.0, 1.5), 42, 20


def main() -> None:
    md = ["# Sample outputs", "",
          f"Trigram model with backoff, tuned k per genre, seed {SEED}, {WORDS} words each.",
          "Lower temperature = safer, more repetitive; higher = more surprising, less grammatical.", ""]
    for genre, prompts in PROMPTS.items():
        m = NgramModel(read_sentences(data_dir() / genre / "train.txt"), k=BEST_K[genre])
        md += [f"## {genre}", ""]
        for p in prompts:
            sugg = ", ".join(f"{w} ({pr:.2f})" for w, pr in m.suggest(p, 5))
            md += [f"**\"{p} ...\"** - next-word suggestions: {sugg}", ""]
            md += [f"- T={t}: {p} *{m.generate(p, WORDS, t, SEED)}*" for t in TEMPS] + [""]
    out = ROOT / "results" / "samples.md"
    out.write_text("\n".join(md))
    print("\n".join(md[5:16]))


if __name__ == "__main__":
    main()
