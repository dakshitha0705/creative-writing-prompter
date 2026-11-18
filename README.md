# Creative Writing Prompter

[![Built with askThili](https://ask.thili.ai/api/v1/public/projects/3mtnrdjj4e/badge.svg)](https://ask.thili.ai/b/3mtnrdjj4e)

This Creative Writing Prompter is a CLI tool designed for aspiring writers. It leverages a next-word prediction engine built from scratch to analyze a corpus of short stories and provide contextually relevant suggestions, aiding in story development and overcoming writer's block.

## What you are building

**Goal.** You will build a command-line interface (CLI) tool that provides context-aware next-word suggestions to help aspiring writers overcome writer's block by sampling from a text corpus.

**Done when.** The CLI tool successfully takes user input, processes it using the n-gram model with add-k smoothing, and generates contextually relevant next-word suggestions from the loaded corpus.

## Milestones

Tick these off as you go, and commit after each one.

- [x] **1. Prepare a text corpus of short stories.**  
      Hint: Use text preprocessing and tokenization techniques.
- [x] **2. Implement n-gram counting and maximum-likelihood probabilities.**  
      Hint: Apply n-gram frequency counting and maximum-likelihood probability calculation.
- [x] **3. Add add-k smoothing to handle unseen n-grams.**  
      Hint: Implement add-k smoothing for robust probability estimates.
- [x] **4. Develop a function to generate text by sampling from the model.**  
      Hint: Develop a function for random sampling based on n-gram probabilities to generate text.
- [ ] **5. Create a CLI interface for users to input text and get suggestions.**  
      Hint: Design a command-line interface to handle user input and display suggestions.

## Run it

You need Python 3.12 and git.

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then choose a model; see the comments inside
python -m app.cli hello
pytest
```

Your work goes in `app/core.py` (one stub per milestone) and `tests/test_core.py`. The first tests pass already; they
check the plumbing.

## Settings and secrets

Model settings live in `.env`, which is ignored by git. **Never commit `.env` or paste a key into code.** If a key ever
reaches GitHub, treat it as leaked and make a new one.

## Stretch ideas

- Allow users to specify the number of next-word suggestions to display.
- Implement an option to switch between different pre-loaded text corpora or genres.
- Add a feature to generate a short sequence of words or a sentence based on a starting prompt.
