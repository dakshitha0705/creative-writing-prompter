"""Your code. One stub per milestone; build them in order and keep each one small.

Builds on the day-2 drill (app/ngram_lm.py): its `to_sentences`, `to_tokens` and `build` do the
sentence splitting, tokenizing and n-gram counting; this file adds corpus prep, MLE, add-k + backoff,
temperature sampling and the pieces the CLI needs.
"""
import math
import os
import random
import re
import unicodedata
from pathlib import Path

from app.ngram_lm import build, to_sentences, to_tokens

GENRES = ("mystery", "horror", "scifi")


def data_dir() -> Path:
    """Where prepared corpora live (override with CWP_DATA_DIR)."""
    return Path(os.environ.get("CWP_DATA_DIR", "data"))


# --- Milestone 1: Prepare a text corpus of short stories.
# Hint: Use text preprocessing and tokenization techniques.
_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*", re.I)
_END = re.compile(r"(\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG|End of (?:the )?Project Gutenberg)", re.I)
_ASCII = {"‘": "'", "’": "'", "“": '"', "”": '"', "—": " - ", "–": "-",
          "…": "...", "_": ""}
_ABBREV = re.compile(r"\b(Mr|Mrs|Dr|St|Messrs|Mme|Mlle|Capt|Col|Prof|Rev|Lt|Sgt)\.")


def strip_gutenberg(text: str) -> str:
    """Keep only the book body between the Project Gutenberg START and END markers."""
    if m := _START.search(text):
        text = text[m.end():]
    if m := _END.search(text):
        text = text[:m.start()]
    return text


def skip_front_matter(text: str, min_words: int = 40) -> str:
    """Drop title page / contents: start at the first paragraph with at least `min_words` words."""
    paras = re.split(r"\n\s*\n", text)
    for i, p in enumerate(paras):
        if len(p.split()) >= min_words:
            return "\n\n".join(paras[i:])
    return text


def to_ascii(text: str) -> str:
    for src, dst in _ASCII.items():
        text = text.replace(src, dst)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def clean_text(raw: str) -> str:
    """Gutenberg book -> plain ASCII story text (no header/footer, front matter, headings, illustrations)."""
    text = to_ascii(skip_front_matter(strip_gutenberg(raw)))
    text = re.sub(r"\[[^\]]*\]", " ", text)                      # [Illustration: ...], [Footnote ...]
    text = re.sub(r"^[^a-z\n]*$", "", text, flags=re.M)          # ALL-CAPS headings, roman numerals
    return _ABBREV.sub(r"\1", text)                              # "Mr. Holmes" is not a sentence end


def tokenize_corpus(text: str) -> list[list[str]]:
    """Clean text -> list of sentences, each a list of lowercase word tokens (drill tokenizer)."""
    sents = []
    for s in to_sentences(text):
        toks = [t.strip("'") for t in to_tokens(s)]
        if toks := [t for t in toks if t]:
            sents.append(toks)
    return sents


def train_val_split(sents: list, val_frac: float = 0.1, seed: int = 0) -> tuple[list, list]:
    """Shuffle sentences reproducibly and hold out `val_frac` of them (at least one) for validation."""
    idx = list(range(len(sents)))
    random.Random(seed).shuffle(idx)
    n_val = max(1, round(len(sents) * val_frac)) if len(sents) > 1 else 0
    return [sents[i] for i in idx[n_val:]], [sents[i] for i in idx[:n_val]]


def write_sentences(path: Path, sents: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(" ".join(s) for s in sents) + "\n", encoding="ascii")


def read_sentences(path: Path) -> list[list[str]]:
    return [line.split() for line in path.read_text(encoding="ascii").splitlines() if line.strip()]


# --- Milestone 2: Implement n-gram counting and maximum-likelihood probabilities.
# Hint: Apply n-gram frequency counting and maximum-likelihood probability calculation.
BOS, EOS, UNK = "<s>", "</s>", "<unk>"


def context_of(tokens: list[str], order: int) -> tuple:
    """The (order-1)-word history for the next word, padded with <s> at the sentence start."""
    return tuple(([BOS] * (order - 1) + list(tokens))[len(tokens):]) if order > 1 else ()


class NgramModel:
    """Unigram..trigram counts over tokenized sentences; `mle` and `top_next` give MLE estimates."""

    def __init__(self, sents: list[list[str]], order: int = 3, k: float = 0.0):
        self.order, self.k = order, k
        lines = [" ".join(s) for s in sents]
        # drill's build(): context (n-1 words, <s>-padded) -> Counter of next words, with </s> at the end
        self.counts = {n: build(lines, n) for n in range(1, order + 1)}
        self.totals = {n: {ctx: sum(c.values()) for ctx, c in self.counts[n].items()} for n in self.counts}
        self.vocab = set(self.counts[1][()]) | {UNK}      # training words + </s> + <unk>

    def mle(self, word: str, context: tuple) -> float:
        """P_MLE(word | context) = count(context, word) / count(context); 0 if either is unseen."""
        n = len(context) + 1
        total = self.totals[n].get(tuple(context), 0)
        return self.counts[n][tuple(context)][word] / total if total else 0.0

    def top_next(self, text: str, n: int = 5, order: int | None = None) -> list[tuple[str, float]]:
        """MLE top-n next words after `text` using one fixed order (no backoff); [] if context unseen."""
        order = order or self.order
        ctx = context_of(to_tokens(text), order)
        c = self.counts[order].get(ctx)
        if not c:
            return []
        return [(w, cnt / self.totals[order][ctx]) for w, cnt in c.most_common() if w != EOS][:n]

    # -- Milestone 3 methods (add-k + backoff); see tune_k below.
    def backoff_context(self, context: tuple) -> tuple:
        """Drop the oldest word until the context was seen in training (the empty context always is)."""
        ctx = tuple(context)
        while ctx and ctx not in self.totals[len(ctx) + 1]:
            ctx = ctx[1:]
        return ctx

    def prob(self, word: str, context: tuple, k: float | None = None) -> float:
        """Add-k: (count(ctx, w) + k) / (count(ctx) + k|V|), at the longest seen context; OOV -> <unk>."""
        k = self.k if k is None else k
        word = word if word in self.vocab else UNK
        ctx = self.backoff_context(context)
        n = len(ctx) + 1
        return (self.counts[n][ctx][word] + k) / (self.totals[n][ctx] + k * len(self.vocab))

    def _scored(self, sents: list[list[str]], k: float):
        for s in sents:
            toks = [BOS] * (self.order - 1) + list(s) + [EOS]
            for i in range(self.order - 1, len(toks)):
                ctx = tuple(toks[i - self.order + 1:i])
                yield self.prob(toks[i], ctx, k) if k > 0 else self.mle(toks[i], ctx)

    def perplexity(self, sents: list[list[str]], k: float | None = None) -> float:
        """exp(-mean log P) over every word and </s>. k=0 is pure MLE (no backoff): inf if any P is 0."""
        k = self.k if k is None else k
        log_sum, n = 0.0, 0
        for p in self._scored(sents, k):
            if p == 0:
                return math.inf
            log_sum, n = log_sum + math.log(p), n + 1
        return math.exp(-log_sum / n)

    def zero_prob_rate(self, sents: list[list[str]]) -> float:
        """Share of held-out tokens that MLE gives probability 0 (why MLE perplexity is infinite)."""
        ps = list(self._scored(sents, 0))
        return sum(p == 0 for p in ps) / len(ps)

    def suggest(self, text: str, n: int = 5) -> list[tuple[str, float]]:
        """Top-n next words: best from the longest seen context, topped up from shorter ones (backoff).
        Probabilities are the smoothed P(word | full context)."""
        full = context_of(to_tokens(text), self.order)
        out: dict[str, float] = {}
        ctx = self.backoff_context(full)
        while len(out) < n:
            for w, _ in self.counts[len(ctx) + 1][ctx].most_common():
                if w not in (EOS, UNK) and w not in out:
                    out[w] = self.prob(w, full)
                    if len(out) == n:
                        break
            if not ctx:
                break
            ctx = self.backoff_context(ctx[1:])
        return list(out.items())

    # -- Milestone 4 method; see generate() below.
    def generate(self, prompt: str = "", words: int = 20, temperature: float = 1.0, seed: int | None = None) -> str:
        return generate(self, prompt, words, temperature, seed)


# --- Milestone 3: Add add-k smoothing to handle unseen n-grams.
# Hint: Implement add-k smoothing for robust probability estimates.
K_GRID = (1.0, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001)
BEST_K = {"mystery": 0.001, "horror": 0.005, "scifi": 0.001}   # trigram, from scripts/evaluate.py


def tune_k(model: NgramModel, val: list[list[str]], grid=K_GRID) -> tuple[float, dict[float, float]]:
    """Pick the k with the lowest validation perplexity; sets model.k and returns (best_k, {k: ppl})."""
    scores = {k: model.perplexity(val, k) for k in grid}
    model.k = min(scores, key=scores.get)
    return model.k, scores


# --- Milestone 4: Develop a function to generate text by sampling from the model.
# Hint: Develop a function for random sampling based on n-gram probabilities to generate text.
def sample_next(model: NgramModel, tokens: list[str], rng: random.Random, temperature: float = 1.0) -> str:
    """Draw the next word from the longest seen context's counts, reweighted as count**(1/T).
    T<=0 is greedy; T<1 sharper (safer), T>1 flatter (more surprising). May return </s>."""
    ctx = model.backoff_context(context_of(tokens, model.order))
    c = model.counts[len(ctx) + 1][ctx]
    if temperature <= 0:
        return c.most_common(1)[0][0]
    words = list(c)
    logw = [math.log(c[w]) / temperature for w in words]
    top = max(logw)
    return rng.choices(words, weights=[math.exp(x - top) for x in logw])[0]


def generate(model: NgramModel, prompt: str = "", words: int = 20, temperature: float = 1.0,
             seed: int | None = None) -> str:
    """Continue `prompt` with exactly `words` sampled words; a sampled </s> ends the sentence with '.'
    and the model starts a new sentence (context resets to <s> <s>)."""
    rng = random.Random(seed)
    history, out = to_tokens(prompt), []
    while sum(w != "." for w in out) < words:
        w = sample_next(model, history, rng, temperature)
        if w == EOS:
            if out and out[-1] != ".":
                out.append(".")
            history = []
        else:
            out.append(w)
            history.append(w)
    return " ".join(out).replace(" .", ".")


# --- Milestone 5: Create a CLI interface for users to input text and get suggestions.
# Hint: Design a command-line interface to handle user input and display suggestions.
def milestone_5():  # TODO(milestone 5)
    raise NotImplementedError("TODO(milestone 5)")
