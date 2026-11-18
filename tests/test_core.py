"""Your tests. Each milestone in README.md gets one here: write the test first, then make it pass.

All tests use tiny made-up text, so they run on CI without the Gutenberg dataset.
"""
import io
import math

import pytest

from app import core

TINY = [s.split() for s in ("the detective opened the door", "the detective opened the letter",
                            "the cat sat on the mat", "the detective saw the cat")]


# Milestone 1: Prepare a text corpus of short stories.
def test_milestone_1():
    raw = ("Some licence text\n*** START OF THE PROJECT GUTENBERG EBOOK 1 ***\nA TITLE\n\nContents\n\n"
           + "Mr. Holmes said “I’ve seen it” — café [Illustration: a dog] ok. " * 8
           + "\n\nTHE END\n*** END OF THE PROJECT GUTENBERG EBOOK 1 ***\nmore licence")
    text = core.clean_text(raw)
    assert "licence" not in text and "Contents" not in text and "TITLE" not in text and "THE END" not in text
    assert text.isascii() and "Illustration" not in text
    sents = core.tokenize_corpus(text)
    assert len(sents) == 8                                  # "Mr." did not split a sentence
    assert sents[0] == ["mr", "holmes", "said", "i've", "seen", "it", "cafe", "ok"]
    train, val = core.train_val_split(list(range(100)), val_frac=0.1, seed=0)
    assert len(val) == 10 and sorted(train + val) == list(range(100))
    assert core.train_val_split(list(range(100)), seed=0) == (train, val)   # reproducible


# Milestone 2: Implement n-gram counting and maximum-likelihood probabilities.
def test_milestone_2():
    from app.ngram_lm import NgramLM
    m = core.NgramModel(TINY)
    assert m.counts[3][("detective", "opened")]["the"] == 2
    assert m.counts[2][("<s>",)]["the"] == 4 and m.counts[1][()]["</s>"] == 4
    assert m.mle("detective", ("the",)) == 3 / 8
    assert m.mle("door", ("opened", "the")) == 0.5
    assert m.mle("zebra", ("opened", "the")) == 0.0 and m.mle("the", ("never", "seen")) == 0.0
    assert math.isclose(sum(m.mle(w, ("the",)) for w in m.vocab), 1.0)
    assert dict(m.top_next("The detective opened the", n=5)) == {"door": 0.5, "letter": 0.5}
    # same answer as the day-2 drill's bigram model
    assert m.top_next("the", n=1, order=2)[0][0] == NgramLM(n=2).fit(". ".join(map(" ".join, TINY))).suggest_next("the", 1)[0]


# Milestone 3: Add add-k smoothing to handle unseen n-grams.
def test_milestone_3():
    m = core.NgramModel(TINY, k=0.5)
    for ctx in [("opened", "the"), ("the",), ()]:
        assert math.isclose(sum(m.prob(w, ctx) for w in m.vocab), 1.0)
    assert 0 < m.prob("zebra", ("opened", "the")) == m.prob(core.UNK, ("opened", "the"))
    assert m.prob("door", ("zebra", "the")) == m.prob("door", ("the",))      # backoff on unseen context
    val = [["the", "cat", "opened", "the", "door"]]                           # "cat opened" never seen
    assert m.perplexity(val, k=0) == math.inf and math.isfinite(m.perplexity(val))
    best, scores = core.tune_k(m, val, grid=(1.0, 0.1, 0.01))
    assert best in scores and scores[best] == min(scores.values()) and m.k == best
    assert [w for w, _ in m.suggest("the detective opened the", n=3)][:2] == ["door", "letter"]
    assert len(m.suggest("zebra unicorn", n=3)) == 3                          # backs off to unigrams


# Milestone 4: Develop a function to generate text by sampling from the model.
def test_milestone_4():
    m = core.NgramModel(TINY, k=0.1)
    assert m.generate("the detective", words=12, seed=7) == m.generate("the detective", words=12, seed=7)
    assert m.generate("the detective", words=1, temperature=0) == "opened"       # greedy
    assert len(m.generate("", words=9, seed=1).replace(".", " ").split()) == 9
    out = m.generate("the cat sat", words=30, temperature=0.5, seed=3)
    assert set(out.replace(".", " ").split()) <= m.vocab


# Milestone 5: Create a CLI interface for users to input text and get suggestions.
@pytest.mark.skip(reason="remove this line when you start milestone 5")
def test_milestone_5(tmp_path, monkeypatch, capsys):
    from app.cli import main
    monkeypatch.setenv("CWP_DATA_DIR", str(tmp_path))
    core.write_sentences(tmp_path / "mystery" / "train.txt", TINY)
    core.write_sentences(tmp_path / "mystery" / "val.txt", TINY[:1])

    main(["suggest", "The detective opened the", "--n", "2", "--genre", "mystery"])
    out = capsys.readouterr().out
    assert "door" in out and "letter" in out
    main(["generate", "the detective", "--words", "5", "--seed", "1"])
    assert capsys.readouterr().out.strip().startswith("the detective")

    for argv, msg in [(["suggest", "   "], "empty"), (["suggest", "hi", "--genre", "romance"], "Choose from"),
                      (["suggest", "hi", "--genre", "horror"], "prepare_data")]:
        with pytest.raises(SystemExit) as e:
            main(argv)
        assert msg in str(e.value)

    monkeypatch.setattr("sys.stdin", io.StringIO("the detective opened the\n:genre horror\n:gen 3\n:quit\n"))
    main(["interactive", "--genre", "mystery"])
    out = capsys.readouterr().out
    assert "door" in out and "prepare_data" in out                # horror missing: friendly, loop continues
