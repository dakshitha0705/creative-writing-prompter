# Data sources

All texts come from [Project Gutenberg](https://www.gutenberg.org), downloaded from the mirror
<https://gutenberg.pglaf.org> by `scripts/prepare_data.py`. They are **public domain in the USA**; check the
copyright law of your own country before reusing them. Use is also subject to the
[Project Gutenberg License](https://www.gutenberg.org/policy/license.html): the script strips the Gutenberg
header/footer and keeps only the story text, and this repository **does not redistribute** any of it —
`data/` is git-ignored and rebuilt locally.

| Genre   | PG id | Title                                        | Author              |
|---------|------:|----------------------------------------------|---------------------|
| mystery | 1661  | The Adventures of Sherlock Holmes            | Arthur Conan Doyle  |
| mystery | 834   | The Memoirs of Sherlock Holmes               | Arthur Conan Doyle  |
| mystery | 204   | The Innocence of Father Brown                | G. K. Chesterton    |
| horror  | 2147  | The Works of Edgar Allan Poe, Volume 1       | Edgar Allan Poe     |
| horror  | 2148  | The Works of Edgar Allan Poe, Volume 2       | Edgar Allan Poe     |
| horror  | 8486  | Ghost Stories of an Antiquary                | M. R. James         |
| scifi   | 11870 | The Country of the Blind, and Other Stories  | H. G. Wells         |
| scifi   | 27365 | Tales of Space and Time                      | H. G. Wells         |

## Processing

1. Keep the text between the `*** START/END OF THE PROJECT GUTENBERG EBOOK ***` markers.
2. Skip front matter: start at the first paragraph of 40+ words (drops title page and contents).
3. Normalise to ASCII (curly quotes, dashes, accents), drop `[Illustration ...]` notes, ALL-CAPS headings and
   the period after `Mr./Mrs./Dr./St.` so they don't end sentences.
4. Split into sentences on `.!?` and tokenize to lowercase words (`to_sentences` / `to_tokens` from the drill).
5. Shuffle sentences (seed 0) and hold out 10% per genre: `data/<genre>/train.txt`, `val.txt`,
   one space-separated sentence per line.

| Genre   | train sents | val sents | train tokens | train vocab |
|---------|------------:|----------:|-------------:|------------:|
| mystery | 15,547      | 1,727     | 252,710      | 13,446      |
| horror  | 9,552       | 1,061     | 209,677      | 15,400      |
| scifi   | 13,220      | 1,469     | 212,587      | 13,835      |

Known noise: Poe Volume 1 opens with a preface and biographical essays (Life/Death of Poe), which stay in the
horror corpus; Wells' collection keeps its short introduction.
