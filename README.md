# Creative Writing Prompter

[![Built with askThili](https://ask.thili.ai/api/v1/public/projects/3mtnrdjj4e/badge.svg)](https://ask.thili.ai/b/3mtnrdjj4e)
[![tests](https://github.com/dakshitha0705/creative-writing-prompter/actions/workflows/ci.yml/badge.svg)](https://github.com/dakshitha0705/creative-writing-prompter/actions/workflows/ci.yml)

A command-line writing buddy for getting past writer's block. Type the start of a sentence and it suggests the
next word, or continues the text for you, in the style of a genre: **mystery** (Conan Doyle, Chesterton),
**horror** (Poe, M. R. James) or **scifi** (H. G. Wells). Under the hood is a trigram language model with add-k
smoothing and backoff. I built it from scratch in pure Python (standard library only), and it trains on
public-domain short stories. It runs fully offline: no API key, no `.env`, no GPU.

```text
$ python -m app.cli suggest "The detective opened the" --n 5 --genre mystery
The detective opened the ...
  1. door             p=0.319
  2. case             p=0.058
  3. window           p=0.029
  4. salon            p=0.029
  5. stable           p=0.029
```

## Setup

Python 3.12+ and git.

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt                        # only pytest/httpx; the model is stdlib
python scripts/prepare_data.py                         # download 8 books (~5 MB), build data/<genre>/
pytest -q
```

Optional: `python scripts/evaluate.py` rebuilds `results/perplexity.md` (~15 s) and
`python scripts/make_samples.py` rebuilds `results/samples.md`.

## Commands

| Command | What it does |
|---|---|
| `python -m app.cli suggest "The detective opened the" --n 5 --genre mystery` | top-N next words with probabilities |
| `python -m app.cli generate "At midnight the" --words 20 --genre horror --temperature 0.8 --seed 1` | continue the text by sampling |
| `python -m app.cli interactive --genre scifi` | loop: type text for suggestions; `:gen 15`, `:genre horror`, `:n 3`, `:temp 1.2`, `:quit` |
| `python -m app.cli genres` | which corpora are prepared |

`--temperature 0` is greedy (always the most likely word), values below 1 play it safe, and values above 1 get
wilder. Without `--seed`, every run gives different output. Errors are friendly: empty input, an unknown genre
(it lists the valid ones) and missing data (it tells you to run `scripts/prepare_data.py`) each print a one-line
message, never a traceback. Set `CWP_DATA_DIR` to read the corpora from somewhere else.

## How it works

1. **Corpus** (`scripts/prepare_data.py`, `app/core.py` Milestone 1). Download Gutenberg texts, strip the
   header/footer and front matter, convert to ASCII, split into sentences, lowercase and tokenize, then hold
   out 10% per genre for validation.
2. **Counting + MLE**. Unigram, bigram and trigram counts with `<s>` / `</s>` padding, and
   P(w | u v) = c(u v w) / c(u v).
3. **Add-k + backoff**. P(w | ctx) = (c(ctx w) + k) / (c(ctx) + k|V|), using the longest context seen in
   training. Words not in the vocabulary map to `<unk>`. k is tuned on validation perplexity.
4. **Sampling**. Draw from the longest seen context's counts, reweighted as count^(1/T), with a seeded RNG. When
   it samples `</s>`, it ends the sentence and starts a new one.
5. **CLI** (`app/cli.py`). Suggestions start from the longest matching context and are topped up from shorter
   ones, so even an unseen phrase gets N suggestions.

## Results

Validation perplexity (lower is better; full table and k sweep in [results/perplexity.md](results/perplexity.md)):

| genre | MLE trigram val | add-k bigram val | add-k trigram val (best k) | MLE trigram train |
|---|--:|--:|--:|--:|
| mystery | inf (64% of tokens unseen) | 413.7 | 879.8 (k=0.001) | 6.2 |
| horror  | inf (73%) | 785.1 | 1,562.8 (k=0.005) | 4.9 |
| scifi   | inf (62%) | 508.8 | 797.1 (k=0.001) | 5.3 |

MLE memorises the training text (train perplexity ~5) but gives probability 0 to most held-out trigrams.
Smoothing makes every estimate finite. With only ~200k tokens per genre, the add-k trigram scores worse than
the bigram on held-out text: most trigram contexts are rare, and add-k spreads their mass over a ~14k-word
vocabulary. Interpolation or Kneser-Ney would do better. Horror is the hardest corpus because Poe's vocabulary
is the largest.

Sample outputs (more in [results/samples.md](results/samples.md)):

- mystery, T=0.5: *It was a dark* **lantern. i was off to france. i had been lounging in his hand.**
- horror, seed 1: *At midnight the* **whole structure with massy door sooner than open which in letters. while he spoke
  thus i commenced the passes**
- scifi, T=0.7: *The machine* **at work with day after passing the seventh standard of employment had fallen. he asked.**

## Limits

- Three words of memory: it is locally fluent but has no plot, characters or meaning over longer text.
- Output is lowercase, without punctuation other than sentence-ending periods. Digits are dropped.
- Small corpora (2–3 books per genre): it reuses phrases from the books and can echo them word for word.
- Sentence splitting is a simple `.!?` rule. Common titles (Mr./Dr.) are handled, but initials like "H. G." still
  split a sentence.
- Poe Volume 1 includes biographical essays, so some horror output sounds like literary criticism.
- The model is re-trained from `train.txt` on every command (~0.6 s), not cached.

## Builds on the day-2 drill

`app/ngram_lm.py` is my day-2 drill (`learnfast-gpt-from-scratch/work/ngram_lm.py`), copied unchanged so CI
can import it. This project reuses its `to_sentences` / `to_tokens` for preprocessing and its `build` for every
n-gram count table, and a test checks that the new model agrees with the drill's `NgramLM` bigram. On top of
that, it adds:
mixed orders with backoff, `<unk>` handling, pure-MLE vs add-k perplexity and k tuning, temperature sampling,
real corpora per genre, and a CLI.

## Data credits

Texts are from [Project Gutenberg](https://www.gutenberg.org), via the mirror gutenberg.pglaf.org, and are
public domain in the USA. See [DATA.md](DATA.md) for the books and licence notes. `data/` is never committed.

## Milestones

- [x] **1. Prepare a text corpus of short stories.**
- [x] **2. Implement n-gram counting and maximum-likelihood probabilities.**
- [x] **3. Add add-k smoothing to handle unseen n-grams.**
- [x] **4. Develop a function to generate text by sampling from the model.**
- [x] **5. Create a CLI interface for users to input text and get suggestions.**

Stretch ideas done: choose the number of suggestions (`--n`), switch genres (`--genre`, `:genre`), and
generate a short sequence (`generate`, `:gen`).

`app/llm.py` and `app/storage.py` are starter plumbing that this project does not use. Their smoke tests still
run.
