"""Command-line entry point: `python -m app.cli --help`.

    python -m app.cli suggest "The detective opened the" --n 5 --genre mystery
    python -m app.cli generate "At midnight the" --words 20 --genre horror --temperature 0.8 --seed 1
    python -m app.cli interactive --genre scifi
    python -m app.cli genres
"""
import argparse

from app import core

HELP = """Type some text and press Enter for next-word suggestions.
  :gen [N]        continue your last text with N sampled words
  :genre NAME     switch corpus (mystery, horror, scifi)
  :n N            number of suggestions
  :temp T         sampling temperature (0 = greedy)
  :help  :quit"""


def positive_int(s: str) -> int:
    if not s.isdigit() or int(s) < 1:
        raise argparse.ArgumentTypeError(f"expected a whole number >= 1, got {s!r}")
    return int(s)


def show_suggestions(model: core.NgramModel, text: str, n: int) -> None:
    print(f"{text} ...")
    for i, (w, p) in enumerate(model.suggest(text, n), 1):
        print(f"  {i}. {w:<16} p={p:.3f}")


def interactive(genre: str, n: int, words: int, temperature: float) -> None:
    print(HELP)
    try:
        model = core.load_model(genre)
    except core.PrompterError as e:
        model = None
        print(e)
    last = ""
    while True:
        try:
            line = input(f"[{genre}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        cmd, _, arg = line.partition(" ")
        arg = arg.strip()
        if not line:
            continue
        if cmd in (":q", ":quit", ":exit"):
            break
        if cmd == ":genre":
            try:
                model, genre = core.load_model(arg), arg.lower()
                print(f"Switched to {genre}.")
            except core.PrompterError as e:
                print(e)
        elif cmd == ":n" and arg.isdigit() and int(arg) > 0:
            n = int(arg)
        elif cmd == ":temp":
            try:
                temperature = float(arg)
            except ValueError:
                print("Usage: :temp 0.8")
        elif cmd == ":gen":
            if model is None or not last:
                print("Type some text first (and load a genre with :genre NAME).")
            else:
                count = int(arg) if arg.isdigit() and int(arg) > 0 else words
                print(f"{last} {model.generate(last, count, temperature)}")
        elif cmd.startswith(":"):
            print(HELP)
        elif model is None:
            print("No corpus loaded. Try :genre NAME (after python scripts/prepare_data.py).")
        elif not core.to_tokens(line):
            print("No words in that input; try some text.")
        else:
            last = line
            show_suggestions(model, line, n)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="creative-writing-prompter", description="Aspiring writers use this CLI tool to get context-aware next-word suggestions, helping them develop stories and overcome writer's block by sampling from a genre corpus.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("hello", help="check that everything is wired up")
    sub.add_parser("genres", help="list genres and whether their corpus is prepared")
    p_sug = sub.add_parser("suggest", help="top-N next-word suggestions for your text")
    p_gen = sub.add_parser("generate", help="continue your text by sampling from the model")
    p_int = sub.add_parser("interactive", help="type text, get suggestions, switch genres in a loop")
    for p in (p_sug, p_gen):
        p.add_argument("text", help="your text so far, in quotes")
    for p in (p_sug, p_gen, p_int):
        p.add_argument("--genre", default="mystery", help="corpus: mystery, horror or scifi (default mystery)")
    for p in (p_sug, p_int):
        p.add_argument("--n", type=positive_int, default=5, help="number of suggestions (default 5)")
    for p in (p_gen, p_int):
        p.add_argument("--words", type=positive_int, default=20, help="words to generate (default 20)")
        p.add_argument("--temperature", type=float, default=0.8, help="0 = greedy, <1 safer, >1 wilder")
    p_gen.add_argument("--seed", type=int, default=None, help="fix the random seed for repeatable output")
    args = parser.parse_args(argv)

    if args.command == "hello":
        print("Creative Writing Prompter is ready. Open README.md for your milestones.")
    elif args.command == "genres":
        for g in core.available_genres():
            ready = (core.data_dir() / g / "train.txt").exists()
            print(f"  {g:<8} {'ready' if ready else 'not prepared (python scripts/prepare_data.py)'}")
    elif args.command == "interactive":
        interactive(args.genre, args.n, args.words, args.temperature)
    else:
        try:
            text = core.check_prompt(args.text)
            model = core.load_model(args.genre)
        except core.PrompterError as e:
            raise SystemExit(f"error: {e}")
        if args.command == "suggest":
            show_suggestions(model, text, args.n)
        else:
            print(f"{text} {model.generate(text, args.words, args.temperature, args.seed)}")


if __name__ == "__main__":
    main()
