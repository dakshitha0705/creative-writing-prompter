"""Milestone 3: train/val perplexity per genre, MLE vs add-k (+backoff), k tuned on val.

    python scripts/evaluate.py      # needs data/ from scripts/prepare_data.py; writes results/perplexity.md
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.core import GENRES, NgramModel, data_dir, read_sentences, tune_k  # noqa: E402


def fmt(x: float) -> str:
    return "inf" if x == float("inf") else f"{x:,.1f}"


def main() -> None:
    rows, sweeps = [], []
    for genre in GENRES:
        train = read_sentences(data_dir() / genre / "train.txt")
        val = read_sentences(data_dir() / genre / "val.txt")
        for order in (2, 3):
            m = NgramModel(train, order=order)
            mle_train, mle_val, zero = m.perplexity(train, 0), m.perplexity(val, 0), m.zero_prob_rate(val)
            best, scores = tune_k(m, val)
            rows.append(f"| {genre} | {order} | {fmt(mle_train)} | {fmt(mle_val)} ({zero:.0%} zero-prob) "
                        f"| {best:g} | {fmt(m.perplexity(train))} | **{fmt(scores[best])}** |")
            sweeps.append(f"| {genre} | {order} | " + " | ".join(fmt(scores[k]) for k in scores) + " |")
            print(rows[-1])
    ks = list(scores)
    md = ["# Perplexity: MLE vs add-k smoothing (lower is better)", "",
          "Trained on `data/<genre>/train.txt`, evaluated on the 10% held-out `val.txt` (every word + `</s>`).",
          "MLE = raw counts, no backoff: any unseen n-gram gets P=0, so held-out perplexity is infinite.",
          "Add-k backs off to a shorter context when the full one was never seen; k is tuned on val.", "",
          "| genre | n | MLE train | MLE val | best k | add-k train | add-k val |",
          "|---|--:|--:|--:|--:|--:|--:|", *rows, "",
          "**Reading it.** MLE fits train well (trigram ~5) but 28-73% of held-out tokens get P=0. Add-k makes",
          "every estimate finite. With ~200k training tokens per genre, the add-k *trigram* is worse on val than",
          "the bigram: most trigram contexts are seen only a few times, and add-k then spreads a lot of mass",
          "uniformly over the ~14k-word vocabulary. Interpolation or Kneser-Ney would fix that; the CLI still",
          "uses trigrams because ranking suggestions by the longest seen context reads better.", "",
          "## k sweep (validation perplexity)", "",
          "| genre | n | " + " | ".join(f"k={k:g}" for k in ks) + " |",
          "|---|--:|" + "--:|" * len(ks), *sweeps, ""]
    out = ROOT / "results" / "perplexity.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(md))
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
