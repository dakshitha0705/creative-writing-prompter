# CLAUDE.md — Creative Writing Prompter

CLI that suggests the next word / generates text from a word n-gram model (bigram + trigram, add-k
smoothing, backoff) trained on public-domain short stories, one corpus per genre (mystery, horror, scifi).
Runs fully locally: pure-stdlib model, no API key, no `.env` needed.

## Plan (askThili milestones)
1. Corpus — `scripts/prepare_data.py` downloads Gutenberg books (mirror gutenberg.pglaf.org), strips
   header/footer/front matter, ASCII-normalises, sentence-splits, tokenizes, train/val split per genre
   into `data/<genre>/{train,val}.txt`. Sources + licences in `DATA.md`.
2. n-gram counts (<s>/</s>) + MLE probabilities + top-N next words.
3. Add-k smoothing (k tuned on val perplexity) + backoff; `scripts/evaluate.py` -> `results/perplexity.md`.
4. Temperature + seeded sampling; `scripts/make_samples.py` -> `results/samples.md`.
5. CLI: `suggest`, `generate`, `interactive`, `genres`; `--genre`, `--n`, `--words`; friendly errors.

## Layout / conventions
- `app/core.py` — one section per milestone (keep the starter stubs layout). `app/cli.py` — argparse entry.
- `app/ngram_lm.py` — vendored copy of the day-2 drill (`to_sentences`, `to_tokens`, `build`, `NgramLM`);
  reuse it, don't fork its logic.
- `app/llm.py`, `app/storage.py` are starter plumbing, unused by the model; leave them (smoke tests cover them).
- Tests use tiny made-up text only; CI has no dataset. Run `pytest -q`.
- Never commit `data/` or `.env`; `git add` files by name. Commit "Milestone N: <title> — <result>".
